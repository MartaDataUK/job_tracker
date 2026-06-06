import csv
import re
import os

def clean_scraped_description(text):
    if not text:
        return ""

    # 1. Remove obvious navigation artifacts and web junk strings (using multi-line matching)
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

    # 2. Fix broken character encodings visually instantly
    text = text.replace("â€™", "'").replace("â€“", "–").replace("Â£", "£").replace("â®", "").replace("Â", "")

    # 3. Collapse multiple consecutive empty lines/spaces into single spaces/newlines
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Clean up giant vertical gaps
    text = re.sub(r'[ \t]+', ' ', text)       # Clean up massive horizontal spaces

    return text.strip()

def clean_existing_csv():
    input_csv = "adzuna_jobs.csv"
    output_csv = "adzuna_jobs_cleaned.csv"

    if not os.path.exists(input_csv):
        print(f"❌ Error: Could not find your existing source file '{input_csv}' in this directory.")
        return

    print(f"🔄 Reading raw data from '{input_csv}'...")

    processed_rows = []

    # Read existing file
    with open(input_csv, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        for row in reader:
            # Grab the messy description field
            raw_desc = row.get("job_description", "")

            # Clean it surgically without dropping any data or losing rows
            cleaned_desc = clean_scraped_description(raw_desc)

            # Update the row dictionary with the pristine text
            row["job_description"] = cleaned_desc
            processed_rows.append(row)

    # Write perfectly cleaned data out to the new file
    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_rows)

    print(f"✨ Success! Kept all {len(processed_rows)} rows and saved clean versions to: '{output_csv}'")

if __name__ == "__main__":
    clean_existing_csv()