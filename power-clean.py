import csv
from pathlib import Path
import re

# Directories
INPUT_DIR = Path("./tabula_output")
MONTHLY_DIR = Path("./monthly_cleaned")
YEARLY_DIR = Path("./yearly_merged")

MONTHLY_DIR.mkdir(exist_ok=True)
YEARLY_DIR.mkdir(exist_ok=True)

# Month mappings
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

month_names_full = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}

# Regex
pattern = re.compile(r"POWERCHEQUING_\d+_([A-Za-z]+)_(\d{4})_p([12])")

# Group CSVs by month
files_by_month = {}

for csv_path in INPUT_DIR.glob("*.csv"):
    match = pattern.match(csv_path.stem)
    if not match:
        print(f"Skipping {csv_path.name} (no match)")
        continue

    month_name, year, page_num = match.groups()
    month_num = month_map.get(month_name.lower())
    if not month_num:
        print(f"Unknown month: {month_name}")
        continue

    files_by_month.setdefault((year, month_num), {})[page_num] = csv_path

# Clean and merge p1 + p2 for each month
for (year, month_num), pages in sorted(files_by_month.items()):
    merged_rows = []
    # Track if we've already kept a header for this month
    header_seen = False

    for page in ["1", "2"]:  # TODO edit this depending on the input data as a flag?
        if page not in pages:
            continue

        with open(pages[page], "r", encoding="utf-8-sig", newline="") as f:
            rows = list(csv.reader(f))

        # Remove header from page 2 entirely
        if page == "2" and rows:
            rows = rows[1:]

        cleaned = []
        for row in rows:
            # nor=malize for comparison
            norm = [c.strip().lower() for c in row]

            # Remove known header rows
            if (
                len(norm) >= 4
                and (
                    (norm[2] == "amounts" and norm[3] == "amounts")
                    or norm[:5]
                    == [
                        "date",
                        "transactions",
                        "withdrawn ($)",
                        "deposited ($)",
                        "balance ($)",
                    ]
                )
            ):
                continue

            # Remove opening/closing balance rows
            if len(row) > 1 and row[1].strip().lower() in [
                "opening balance",
                "closing balance",
            ]:
                continue

            cleaned.append(row)

        # Merge spillover description rows into description col)
        final_rows = []
        for r in cleaned:
            if (
                len(r) > 1
                and r[0].strip() == ""  # No date
                and r[1].strip() != ""  # Has description text
                and all(cell.strip() == "" for cell in r[2:])  # No amounts
                and final_rows
            ):
                final_rows[-1][1] = final_rows[-1][1].strip() + " " + \
                    r[1].strip()
            else:
                final_rows.append(r)

        # Remove duplicate headers within the same month
        for r in final_rows:
            norm = [c.strip().lower() for c in r]
            if (
                len(norm) >= 5
                and norm[:5]
                == [
                    "date",
                    "transactions",
                    "withdrawn ($)",
                    "deposited ($)",
                    "balance ($)",
                ]
            ):
                if header_seen:
                    continue  # Skip duplicate header
                else:
                    header_seen = True
            merged_rows.append(r)

    # Save monthly cleaned file
    month_name_full = month_names_full[month_num]
    out_path = MONTHLY_DIR / f"{year}_{month_name_full}.csv"
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(merged_rows)

    print(f"Saved monthly file: {out_path}")

# Merge months into yearly CSVs
files_by_year = {}
for csv_path in MONTHLY_DIR.glob("*.csv"):
    match = re.match(r"(\d{4})_([A-Za-z]+)", csv_path.stem)
    if not match:
        continue

    year, month_name = match.groups()
    month_num = month_map.get(month_name.lower())
    if not month_num:
        continue

    files_by_year.setdefault(year, []).append((month_num, csv_path))

for year, month_files in files_by_year.items():
    month_files.sort(key=lambda x: x[0])  # Sort by month number
    merged_rows = []

    # Always set header at the start
    # set this as var later for changing TODO:
    master_header = [
        "Date",
        "Description",
        "Withdrawn ($)",
        "Deposited ($)",
        "Balance ($)",
    ]
    merged_rows.append(master_header)

    for month_num, csv_path in month_files:
        with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
            rows = list(csv.reader(f))

        if not rows:
            continue

        for row in rows:
            norm = [c.strip().lower() for c in row]
            is_header = norm[:5] == [
                "date",
                "transactions",
                "withdrawn ($)",
                "deposited ($)",
                "balance ($)",
            ]
            if not is_header:
                merged_rows.append(row)

    out_path = YEARLY_DIR / f"{year}.csv"
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(merged_rows)

    print(f"Saved yearly file: {out_path}")

print("\nAll monthly and yearly files created.")
