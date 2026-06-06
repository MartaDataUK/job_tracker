import csv
import os
import time
import random
import pandas as pd
from jobspy import scrape_jobs
import re
from datetime import datetime, timedelta

def parse_linkedin_relative_date(relative_str):
    """
    Converts LinkedIn relative time strings (e.g., '3 days ago', '1 week ago')
    into a clean YYYY-MM-DD string based on the current date.
    """
    if not relative_str or not isinstance(relative_str, str):
        return datetime.now().strftime("%Y-%m-%d") # Default to today if empty

    text = relative_str.lower().strip()
    today = datetime.now()

    try:
        # Match "X days ago" or "X day ago"
        day_match = re.search(r'(\d+)\s*day', text)
        if day_match:
            days = int(day_match.group(1))
            return (today - timedelta(days=days)).strftime("%Y-%m-%d")

        # Match "X weeks ago" or "X week ago"
        week_match = re.search(r'(\d+)\s*week', text)
        if week_match:
            weeks = int(week_match.group(1))
            return (today - timedelta(weeks=weeks)).strftime("%Y-%m-%d")

        # Match "X hours ago" or "X hour ago" or "just now"
        if "hour" in text or "minute" in text or "now" in text:
            return today.strftime("%Y-%m-%d")

        # Match "X months ago"
        month_match = re.search(r'(\d+)\s*month', text)
        if month_match:
            months = int(month_match.group(1))
            return (today - timedelta(days=months * 30)).strftime("%Y-%m-%d")

    except Exception:
        pass

    return today.strftime("%Y-%m-%d") # Fallback to today's date if parsing fails

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
    linkedin_csv = "linkedin_and_jobserve_jobs.csv"

    unified_columns = [
        "job_link", "platform", "job_title", "location", "job_employment_type",
        "job_maturity", "job_min_salary", "job_max_salary", "job_salary_period",
        "job_description", "employer_name", "employer_rating", "job_posted_date"
    ]

    target_locations = ["Edinburgh", "Glasgow", "Livingston", "Dundee", "Aberdeen",
                        "London", "Manchester", "Birmingham", "Bristol", "Leeds", "Newcastle", "Remote"]

    target_queries = ["analytics engineer", "data engineer", "data analyst", "data scientist"]

    seen_linkedin_links = get_existing_job_links(linkedin_csv)

    print(f"📊 Dual-Engine Contract Aggregator Initialized.")
    print(f"   ↳ Master Registry: {len(seen_linkedin_links)} existing leads cached.")

    if not os.path.exists(linkedin_csv):
        with open(linkedin_csv, mode="w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=unified_columns).writeheader()

    with open(linkedin_csv, mode="a", newline="", encoding="utf-8") as li_f:
        li_writer = csv.DictWriter(li_f, fieldnames=unified_columns)

        for location in target_locations:
            print(f"\n🏹 ========================================================")
            print(f"🇬🇧 JOBSPY SWEEPING MATRIX BLOCK: [ {location.upper()}, UK ]")
            print(f"==========================================================")

            for query in target_queries:
                print(f"\n📡 Deploying JobSpy vector for: '{query}' in {location}...")
                jobs_df = pd.DataFrame()

                # Strategy 1: Attempt the Combined Direct Broadcast Sweep
                try:
                    jobs_df = scrape_jobs(
                        site_name=["linkedin", "indeed"],
                        search_term=query,
                        location=f"{location}, UK" if location != "Remote" else "Remote, UK",
                        results_per_page=25,
                        hours_old=48,
                        country_enum="uk",
                        linkedin_fetch_description=True,
                        linkedin_cookies={"li_at": "AQEDAR-Lma4D15amAAABnW4-afsAAAGenPxNl04AnmZDTddBsaFldGHVmDnm8EQ5ReDcJpG-yMf6foyyu-0eJ2O7AeY0CISOiQJFfncMPY_ngYq_yj3LWG5qkrtn_EzKa8JntNQOTSdsUtS-QswPgbv2"}
                    )
                except Exception as e:
                    print(f"   ⚠️ Dual-vector stream faulted ({e}). Falling back strictly to LinkedIn...")

                    # 💡 FIX: Nesting this block inside the exception ensures it only runs if the primary dual-sweep fails!
                    try:
                        time.sleep(2)
                        jobs_df = scrape_jobs(
                            site_name=["linkedin"],
                            search_term=query,
                            location=f"{location}, UK" if location != "Remote" else "Remote, UK",
                            results_per_page=15,
                            hours_old=48,
                            country_enum="uk",
                            linkedin_fetch_description=True,
                            linkedin_cookies={"li_at": "AQEDAR-Lma4D15amAAABnW4-afsAAAGenPxNl04AnmZDTddBsaFldGHVmDnm8EQ5ReDcJpG-yMf6foyyu-0eJ2O7AeY0CISOiQJFfncMPY_ngYq_yj3LWG5qkrtn_EzKa8JntNQOTSdsUtS-QswPgbv2"}
                        )
                    except Exception as fatal_e:
                        print(f"   ❌ Critical failure on backup matrix block ({fatal_e}). Skipping sector entirely.")
                        continue

                if jobs_df is None or jobs_df.empty:
                    print("    🔍 Zero matching records pulled from vector array.")
                    continue

                records_added = 0

                for _, row in jobs_df.iterrows():
                    job_link = str(row.get("job_url", "")).strip()
                    if not job_link or job_link in seen_linkedin_links:
                        continue

					# Deep Contract Context Interception
                    raw_interval = str(row.get("interval", "")).lower()
                    desc_lower = str(row.get("description", "")).lower()

                    salary_period = None
                    if row.get("min_amount"):
                        if "day" in raw_interval or "daily" in raw_interval or any(k in desc_lower for k in ["inside ir35", "day rate", "p.d.", "per day", "umbrella"]):
                            salary_period = "daily"
                        else:
                            salary_period = "annual"

                    # 🆕 ADD THESE TWO LINES HERE:
                    raw_jobspy_date = str(row.get("date_posted", ""))
                    cleaned_posted_date = parse_linkedin_relative_date(raw_jobspy_date)

                    raw_title = str(row.get("title", ""))
                    title_lower = raw_title.lower()

                    excluded_terms = ["apprentice", "manager", "junior", "principal", "trainee", "placement", "intern", "graduate"]
                    if any(banned_word in title_lower for banned_word in excluded_terms):
                        continue

                    # Dynamic Site Allocation Logic
                    raw_site = str(row.get("site", "linkedin")).lower()
                    resolved_platform = "Indeed" if "indeed" in raw_site else "LinkedIn"

                    # Deep Contract Context Interception
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
                        "platform": resolved_platform,
                        "job_title": raw_title,
                        "location": row.get("location") or location,
                        "job_employment_type": str(row.get("job_type", "Contract" if resolved_platform == "Indeed" else "Full-Time")).capitalize(),
                        "job_maturity": "Recent",
                        "job_min_salary": row.get("min_amount"),
                        "job_max_salary": row.get("max_amount"),
                        "job_salary_period": salary_period,
                        "job_description": row.get("description") or "Open target link to view core requirements.",
                        "employer_name": row.get("company") or "Hidden Employer",
                        "employer_rating": None,
                        "job_posted_date": cleaned_posted_date
                    }

                    li_writer.writerow(transformed_row)
                    seen_linkedin_links.add(job_link)
                    records_added += 1

                print(f"    📥 Sector Complete -> Saved New Entries: +{records_added}")

                # Defensive pacing delay to preserve pipeline automation health
                sleep_duration = random.uniform(14.0, 26.0)
                print(f"    ⏳ Cooling down data vectors for {sleep_duration:.1f}s...")
                time.sleep(sleep_duration)

if __name__ == "__main__":
    run_jobspy_pipeline()