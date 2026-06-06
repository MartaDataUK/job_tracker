import csv
import os
import time
import requests
from requests.auth import HTTPBasicAuth

def get_existing_job_links(csv_filepath):
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
        print(f"⚠️ Note: Error reading existing CSV links ({e}).")
    return existing_links

def run_reed_pipeline():
    url = "https://www.reed.co.uk/api/1.0/search"
    output_csv = "reed_jobs.csv" # Standardized Naming

    # 🔑 REED API KEY (Leave password blank as Reed handles auth via Username only)
    REED_API_KEY = "YOUR_API_KEY_HERE"

    unified_columns = [
        "job_link", "platform", "job_title", "location", "job_employment_type",
        "job_maturity", "job_min_salary", "job_max_salary", "job_salary_period",
        "job_description", "employer_name", "employer_rating"
    ]

    target_locations = ["Edinburgh", "Glasgow", "Livingston", "Dundee", "Aberdeen", "London", "Manchester"]
    target_queries = ["analytics engineer", "data analyst", "data engineer", "dbt", "BigQuery"]

    seen_links = get_existing_job_links(output_csv)
    file_exists = os.path.exists(output_csv)

    print(f"📊 Reed Aggregator Engine Active. Pre-scanned {len(seen_links)} rows.")

    with open(output_csv, mode="a", newline="", encoding="utf-8") as csv_f:
        writer = csv.DictWriter(csv_f, fieldnames=unified_columns)
        if not file_exists:
            writer.writeheader()

        total_new_rows_session = 0

        for location in target_locations:
            print(f"\n🏹 SWEEPING REED REGION: [ {location.upper()}, UK ]")
            for query in target_queries:
                print(f"📡 Querying Reed for: '{query}'...")

                query_params = {
                    "keywords": query,
                    "locationName": location,
                    "distanceFromLocation": 15,
                    "minimumDaysSincePosted": 0,
                    "maximumDaysSincePosted": 7
                }

                try:
                    response = requests.get(url, params=query_params, auth=HTTPBasicAuth(REED_API_KEY, ''), timeout=30)
                    response.raise_for_status()
                    raw_data = response.json()
                    listings = raw_data.get("results", [])
                except Exception as e:
                    print(f"    ⚠️ Reed call defaulted ({e}). Skipping page.")
                    continue

                for job in listings:
                    job_link = job.get("jobUrl", "").strip()
                    if not job_link or job_link in seen_links:
                        continue

                    title_lower = job.get("jobTitle", "").lower()
                    excluded_terms = ["apprentice", "manager", "junior", "principal", "trainee", "placement"]
                    if any(banned_word in title_lower for banned_word in excluded_terms):
                        continue

                    transformed_row = {
                        "job_link": job_link,
                        "platform": "Reed",
                        "job_title": job.get("jobTitle"),
                        "location": job.get("locationName") or location,
                        "job_employment_type": "Full-Time",
                        "job_maturity": job.get("date") or "Recent",
                        "job_min_salary": job.get("minimumSalary"),
                        "job_max_salary": job.get("maximumSalary"),
                        "job_salary_period": "annum",
                        "job_description": job.get("jobDescription") or "Open target link.",
                        "employer_name": job.get("employerName") or "Hidden Employer",
                        "employer_rating": None,
                    }

                    writer.writerow(transformed_row)
                    seen_links.add(job_link)
                    total_new_rows_session += 1

                time.sleep(2.0) # Rate limiting throttle

    print(f"\n🏁 Reed Sweeper Completed! Consolidated {total_new_rows_session} new rows.")

if __name__ == "__main__":
    run_reed_pipeline()