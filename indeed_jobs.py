import csv
import os
import time
import random
import pandas as pd
from jobspy import scrape_jobs

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

def run_jobspy_pipeline():
    # Appending directly to your master file matrix
    output_csv = "linkedin_and_jobserve_jobs.csv"

    unified_columns = [
        "job_link", "platform", "job_title", "location", "job_employment_type",
        "job_maturity", "job_min_salary", "job_max_salary", "job_salary_period",
        "job_description", "employer_name", "employer_rating"
    ]

    target_locations = ["Edinburgh", "Glasgow", "Livingston", "Dundee", "Aberdeen",
                        "London", "Manchester", "Birmingham", "Bristol", "Leeds", "Newcastle", "Remote"]

    target_queries = ["analytics engineer", "data engineer", "data analyst"]

    seen_links = get_existing_job_links(output_csv)

    print(f"📊 Dedicated Indeed Contract Aggregator Initialized.")
    print(f"   ↳ Master Registry: {len(seen_links)} existing leads cached.")

    if not os.path.exists(output_csv):
        with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=unified_columns).writeheader()

    with open(output_csv, mode="a", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=unified_columns)

        for location in target_locations:
            print(f"\n🏹 ========================================================")
            print(f"🇬🇧 JOBSPY SWEEPING MATRIX BLOCK: [ {location.upper()}, UK ]")
            print(f"==========================================================")

            for query in target_queries:
                print(f"\n📡 Deploying JobSpy vector for: '{query}' in {location}...")
                jobs_df = pd.DataFrame()

                try:
                    # Target strictly Indeed for fast contract data gathering
                    jobs_df = scrape_jobs(
                        site_name=["indeed"],
                        search_term=query,
                        location=f"{location}, UK" if location != "Remote" else "Remote, UK",
                        results_per_page=25,
                        hours_old=48,
                        country_enum="uk"
                    )
                except Exception as e:
                    print(f"   ❌ Indeed stream faulted for this sector ({e}). Skipping matrix block.")
                    continue

                if jobs_df is None or jobs_df.empty:
                    print("    🔍 Zero matching records pulled from vector array.")
                    continue

                records_added = 0

                for _, row in jobs_df.iterrows():
                    job_link = str(row.get("job_url", "")).strip()
                    if not job_link or job_link in seen_links:
                        continue

                    raw_title = str(row.get("title", ""))
                    title_lower = raw_title.lower()

                    excluded_terms = ["apprentice", "manager", "junior", "principal", "trainee", "placement", "intern", "graduate"]
                    if any(banned_word in title_lower for banned_word in excluded_terms):
                        continue

                    # Deep Contract & Day Rate Keyword Interception
                    raw_interval = str(row.get("interval", "")).lower()
                    desc_lower = str(row.get("description", "")).lower()

                    salary_period = None
                    if row.get("min_amount"):
                        if "day" in raw_interval or "daily" in raw_interval or any(k in desc_lower for k in ["inside ir35", "day rate", "p.d.", "per day", "umbrella"]):
                            salary_period = "daily"
                        else:
                            salary_period = "annual"

                    transformed_row = {
                        "job_link": job_link,
                        "platform": "Indeed",
                        "job_title": raw_title,
                        "location": row.get("location") or location,
                        "job_employment_type": str(row.get("job_type", "Contract" if salary_period == "daily" else "Full-Time")).capitalize(),
                        "job_maturity": "Recent",
                        "job_min_salary": row.get("min_amount"),
                        "job_max_salary": row.get("max_amount"),
                        "job_salary_period": salary_period,
                        "job_description": row.get("description") or "Open target link to view core requirements.",
                        "employer_name": row.get("company") or "Hidden Employer",
                        "employer_rating": None,
                    }

                    writer.writerow(transformed_row)
                    seen_links.add(job_link)
                    records_added += 1

                print(f"    📥 Sector Complete -> Saved New Indeed Entries: +{records_added}")

                # Random human-like throttling to prevent Indeed firewall triggers
                sleep_duration = random.uniform(8.0, 15.0)
                print(f"    ⏳ Cooling down data vectors for {sleep_duration:.1f}s...")
                time.sleep(sleep_duration)

if __name__ == "__main__":
    run_jobspy_pipeline()