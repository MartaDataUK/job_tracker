import csv
import os
import time
import random
from curl_cffi import requests
from bs4 import BeautifulSoup

def enrich_descriptions_via_mobile_backdoor():
    # Input/Output database mapping
    csv_filepath = "indeed_jobs.csv"
    temp_filepath = "indeed_jobs_enriched_final.csv"

    # Verify the source database exists before executing
    if not os.path.exists(csv_filepath):
        print(f"❌ Error: Your source file '{csv_filepath}' was not found in this directory.")
        print(f"   Current Directory path is: {os.getcwd()}")
        return

    # Read rows into memory from existing dataset
    with open(csv_filepath, mode="r", newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        rows = list(reader)

    # Filter out records that are already populated to save execution overhead
    target_rows = [r for r in rows if len(r.get("job_description", "")) < 200 or r.get("job_description") == "Open link to read requirements."]
    print(f"📡 Initializing Mobile Interface Backdoor Engine...")
    print(f"📊 Total jobs in database: {len(rows)} | Missing description text: {len(target_rows)}")

    if not target_rows:
        print("✅ All descriptions are already fully populated! Ready for scoring engine.")
        return

    processed_count = 0
    repaired_count = 0

    try:
        with open(temp_filepath, mode="w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in rows:
                # Process only the records that matched our missing text filter criteria
                if len(row.get("job_description", "")) < 200 or row.get("job_description") == "Open link to read requirements.":
                    url = row.get("job_link", "")
                    processed_count += 1

                    if url:
                        # Parse out the unique Indeed Job Key (jk parameter)
                        job_id = None
                        if "jk=" in url:
                            job_id = url.split("jk=")[-1].split("&")[0].strip()

                        if job_id:
                            # 📱 Convert desktop link structure into an alternate mobile app interface route
                            mobile_gateway_url = f"https://uk.indeed.com/m/viewjob?jk={job_id}"
                            print(f"🔄 Fetching [{processed_count}/{len(target_rows)}] -> Mobile Gateway for ID: {job_id}")

                            try:
                                # impersonate="chrome" forces curl_cffi to scramble its TLS signatures to match desktop Chrome,
                                # but the mobile User-Agent combined with the /m/ URL tells Indeed to serve the unprotected view.
                                response = requests.get(
                                    mobile_gateway_url,
                                    impersonate="chrome",
                                    timeout=15,
                                    headers={"User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"}
                                )

                                if response.status_code == 200:
                                    soup = BeautifulSoup(response.text, "html.parser")

                                    # Sequential check for known mobile and desktop content containers
                                    desc_element = (
                                        soup.find(id="jobDescriptionText") or
                                        soup.find(class_="jobsearch-JobComponent-description") or
                                        soup.find(id="id_jobDescriptionText")
                                    )

                                    if desc_element:
                                        full_text = desc_element.get_text(separator=" ").strip()
                                    else:
                                        # Strict structural text assembly fallback if tag markers are changed
                                        paragraphs = soup.find_all(["p", "div"])
                                        full_text = " ".join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 40])

                                    # Verify the payload contains actual content and not an error snippet
                                    if len(full_text) > 250:
                                        row["job_description"] = " ".join(full_text.split())
                                        repaired_count += 1
                                        print(f"   ✅ Real Text Recovered! ({len(row['job_description'])} chars)")
                                    else:
                                        print("   ⚠️ Text block payload was too short. Skipping.")
                                else:
                                    print(f"   ⚠️ Connection blocked by gateway. HTTP Status Code: {response.status_code}")

                            except Exception as e:
                                print(f"   ❌ Network connection timed out or dropped.")

                            # Safe human-like pacing delay to protect against rate limits
                            time.sleep(random.uniform(3.0, 5.5))
                        else:
                            print(f"   ⚠️ Could not parse unique job key from link.")

                # Write row down to disk (keeps data structure valid row-by-row)
                writer.writerow(row)

    except KeyboardInterrupt:
        print("\n🛑 Execution paused by user. Safely flushing remaining rows to prevent data loss...")
        with open(temp_filepath, mode="a", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            for remaining_row in rows[processed_count:]:
                writer.writerow(remaining_row)

    # Replace old data file atomically with our fully updated file
    if os.path.exists(temp_filepath):
        os.replace(temp_filepath, csv_filepath)

    print(f"\n🏁 Complete! Successfully matched and recovered {repaired_count} job description fields completely for free.")

if __name__ == "__main__":
    enrich_descriptions_via_mobile_backdoor()