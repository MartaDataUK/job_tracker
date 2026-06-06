import csv
import re
import os
import time
import requests
from bs4 import BeautifulSoup

def get_existing_job_links(csv_filepath):
    """Pre-reads the master CSV file to compile a set of existing unique job links."""
    existing_links = set()
    if not os.path.exists(csv_filepath):
        return existing_links
    try:
        with open(csv_filepath, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                link = row.get("job_link")
                if link:
                    existing_links.add(link.strip())
    except Exception as e:
        print(f"⚠️ Note: Error reading existing CSV links ({e}). Starting fresh.")
    return existing_links

def clean_html(text):
    """Helper to strip out HTML formatting tags like <strong> from API text strings."""
    if not text:
        return ""
    return re.sub(r"<[^>]*>", "", text)

def clean_scraped_description(text):
    if not text:
        return ""

    # 1. Remove obvious navigation artifacts and web junk strings ([\s\S]* allows multi-line crossing)
    junk_patterns = [
        r"What\?\s*Where\?\s*Search\s*Advanced",
        r"â®\s*back to last search",
        r"Receive similar jobs by email[\s\S]*?Create alert",
        r"By creating an alert, you agree to our[\s\S]*",
        r"No thanks, take me to the job",
        r"Stats for this job[\s\S]*",
        r"Popular searches[\s\S]*",
        r"Similar jobs[\s\S]*"
    ]
    for pattern in junk_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # 2. Fix broken character encodings (like â€™ turning into ')
    text = text.replace("â€™", "'").replace("â€“", "–").replace("Â£", "£").replace("â®", "").replace("Â", "")

    # 3. Collapse multiple consecutive empty lines/spaces into single spaces/newlines
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Clean up giant vertical gaps
    text = re.sub(r'[ \t]+', ' ', text)       # Clean up massive horizontal spaces

    return text.strip()

def fetch_full_description_from_web(url):
    """
    Follows the job link and parses the raw webpage HTML
    to extract the real, un-truncated description block.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=12, allow_redirects=True)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # TARGET IDENTIFICATION: Common container classes for job descriptions
        target_selectors = [
            {"class_": "job-description"}, {"class_": "jobDescription"},
            {"id": "job-description"}, {"class_": "description__text"},
            {"class_": "job_description"}, {"itemprop": "description"}
        ]

        for selector in target_selectors:
            element = soup.find(attrs=selector)
            if element and len(element.text.strip()) > 200:
                return element.text.strip()

        # Fallback Strategy: Grab the largest coherent text paragraph block
        paragraphs = soup.find_all(["p", "div", "section"])
        longest_block = ""
        for p in paragraphs:
            text = p.text.strip()
            if len(text) > len(longest_block):
                longest_block = text

        if len(longest_block) > 300:
            return longest_block

    except Exception:
        pass
    return None

def run_adzuna_matrix_pipeline():
    url = "https://api.adzuna.com/v1/api/jobs/gb/search/1"
    output_csv = "adzuna_jobs.csv"

    unified_columns = [
        "job_link", "platform", "job_title", "location", "job_employment_type",
        "job_maturity", "job_min_salary", "job_max_salary", "job_salary_period",
        "job_description", "employer_name", "employer_rating", "job_posted_date"
    ]

    ADZUNA_APP_ID = "YOUR_APP_ID"
    ADZUNA_APP_KEY = "YOUR_APP_KEY"

    target_locations = [
        "Edinburgh", "Glasgow", "Livingston", "Dundee", "Aberdeen",
        "London", "Manchester", "Birmingham", "Bristol", "Leeds", "Newcastle"
    ]

    target_queries = [
        "analytics engineer", "data analyst", "data engineer", "data scientist",
        "dbt", "BigQuery", "Data modelling", "Data Product Developer"
    ]

    seen_links = get_existing_job_links(output_csv)
    file_exists = os.path.exists(output_csv)

    print(f"📊 Adzuna Full-Text Aggregator Active. Pre-scanned {len(seen_links)} rows.")

    with open(output_csv, mode="a", newline="", encoding="utf-8") as csv_f:
        writer = csv.DictWriter(csv_f, fieldnames=unified_columns)
        if not file_exists:
            writer.writeheader()

        total_new_rows_session = 0

        for location in target_locations:
            print(f"\n🏹 ========================================================")
            print(f"🇬🇧 DEEP SWEEPING ADZUNA REGION: [ {location.upper()}, UK ]")
            print(f"==========================================================")

            for query in target_queries:
                print(f"\n📡 Requesting payload for: '{query}'...")

                for page in range(1, 4):
                    query_params = {
                        "app_id": ADZUNA_APP_ID,
                        "app_key": ADZUNA_APP_KEY,
                        "what": query,  # Removed extra double quotes to improve hit rates
                        "where": location,
                        "results_per_page": 20,
                        "content-type": "application/json",
                        "max_days_old": 2,
                    }

                    paginated_url = url.replace("/search/1", f"/search/{page}")

                    try:
                        response = requests.get(paginated_url, params=query_params, timeout=30)
                        response.raise_for_status()
                        raw_data = response.json()
                        listings = raw_data.get("results", [])
                    except Exception as e:
                        print(f"    ⚠️ Adzuna network slice faulted ({e}). Skipping page.")
                        continue

                    if len(listings) == 0:
                        break

                    for job in listings:
                        if not isinstance(job, dict):
                            continue

                        job_link_clean = job.get("redirect_url", "").strip()
                        if not job_link_clean or job_link_clean in seen_links:
                            continue

                        job_title_clean = clean_html(job.get("title", ""))
                        title_lower = job_title_clean.lower()

                        # 🆕 ADD THESE LINES HERE TO CAPTURE THE DATE POSTED:
                        raw_created_date = job.get("created", "")  # e.g., "2026-06-05T14:30:22Z"
                        if raw_created_date and len(raw_created_date) >= 10:
                            cleaned_posted_date = raw_created_date[:10]  # Cuts it down cleanly to "2026-06-05"
                        else:
                            cleaned_posted_date = None

                        # Profile Exclusion Guardrails
                        excluded_terms = ["apprentice", "manager", "junior", "principal", "trainee", "placement", "sc cleared", "sc-cleared"]
                        if any(banned_word in title_lower for banned_word in excluded_terms):
                            continue

                        api_snippet = clean_html(job.get("description")) or "Open link to read requirements."

                        print(f"    📥 Found unique role: '{job_title_clean[:35]}...' -> Enriching...")

                        full_description = fetch_full_description_from_web(job_link_clean)

                        cleaned_scrape = clean_scraped_description(full_description)
                        scraped_test = cleaned_scrape.lower()

                        # Hybrid Fallback Logic (Keeps 100% of rows)
                        if not cleaned_scrape or len(scraped_test) < 150:
                            final_description = api_snippet
                            print("      箱️ Web text unavailable. Using Adzuna preview snippet safely.")
                        else:
                            final_description = cleaned_scrape
                            print("      ✅ Rich web text successfully cleaned and kept!")

                        company_obj = job.get("company") or {}
                        location_obj = job.get("location") or {}
                        contract_time = job.get("contract_time", "full_time")
                        employment_type = "Full-Time" if contract_time == "full_time" else "Part-Time"

                        transformed_row = {
                            "job_link": job_link_clean,
                            "platform": "Adzuna",
                            "job_title": job_title_clean,
                            "location": location_obj.get("display_name") or location,
                            "job_employment_type": employment_type,
                            "job_maturity": job.get("created") or "Recent",
                            "job_min_salary": job.get("salary_min"),
                            "job_max_salary": job.get("salary_max"),
                            "job_salary_period": "annum" if job.get("salary_min") else None,
                            "job_description": final_description,
                            "employer_name": company_obj.get("display_name") or "Hidden Employer",
                            "employer_rating": None,
                            "job_posted_date": cleaned_posted_date
                        }

                        writer.writerow(transformed_row)
                        seen_links.add(job_link_clean)
                        total_new_rows_session += 1

                        time.sleep(1.5)

                    time.sleep(2.0)

    print(f"\n🏁 Complete! Deep extracted {total_new_rows_session} full-length records into staging.")

if __name__ == "__main__":
    run_adzuna_matrix_pipeline()