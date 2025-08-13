import csv
from pathlib import Path
import re

CSV_DIR = "./tabula_output"
OUTPUT_DIR = "./merged_output"
Path(OUTPUT_DIR).mkdir(exist_ok=True)

# Month mapping
month_map = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}

# Regex to extract month and year
pattern = re.compile(r"([A-Za-z]+)_(20\d{2})")

# Group files by year
files_by_year = {}
for csv_path in Path(CSV_DIR).rglob("*.csv"):
    match = pattern.search(csv_path.stem)
    if match:
        month_name, year = match.groups()
        month_num = month_map.get(month_name.lower())
        if month_num:
            files_by_year.setdefault(year, []).append((month_num, csv_path))
        else:
            print(f"Unknown month/date in filename: {csv_path}")
    else:
        print(f"Skipping {csv_path} (no month/year found)")

# Process each year
for year, month_file_pairs in files_by_year.items():
    print(f"\nProcessing year {year}...")

    # Sort by month number
    month_file_pairs.sort(key=lambda x: x[0])

    merged_rows = []
    for i, (month_num, csv_path) in enumerate(month_file_pairs):
        with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
            rows = list(csv.reader(f))

        if not rows:
            print(f"Empty file: {csv_path}")
            continue

        if i == 0:
            # First month → keep header
            merged_rows.extend(rows)
            print(f"Added {csv_path.name} (kept header)")
        else:
            # Other months → skip first row
            merged_rows.extend(rows[1:])
            print(f"Added {csv_path.name} (skipped header)")

    # Write merged file for the year
    output_path = Path(OUTPUT_DIR) / f"{year}_merged.csv"
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(merged_rows)

    print(f"Saved merged file: {output_path}")

print(f"One merged file per year created in {OUTPUT_DIR}")
