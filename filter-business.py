import csv
from pathlib import Path
import sys

CSV_DIR = "./tabula_output"

# Prefixes
prefixes = ("9067", "PEMB", "IC_2", "ICBC", "BALANCE FORWARD")

# Dry run flag
dry_run = "-d" in sys.argv

for csv_path in Path(CSV_DIR).rglob("*.csv"):
    print(f"\nProcessing {csv_path}...")

    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))

    if not rows:
        print("Empty file, skipping.")
        continue

    cleaned_rows = []
    deleted_rows = []

    for row in rows:
        if not row:
            continue

        first_cell = row[0].strip()

        # Only one non-empty cell (in first column)
        only_first_filled = first_cell and all(cell.strip() == "" for cell in row[1:])

        # First cell starts with one of the prefixes
        starts_with_prefix = any(first_cell.startswith(prefix) for prefix in prefixes)

        if only_first_filled and starts_with_prefix:
            deleted_rows.append(row)
        else:
            cleaned_rows.append(row)

    # Show deleted rows
    if deleted_rows:
        print(f"{len(deleted_rows)} rows would be deleted in real run:")
        for dr in deleted_rows:
            print(dr)
    else:
        print("No rows matched deletion criteria.")

    # Write cleaned CSV back (only if not dry run)
    if not dry_run:
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(cleaned_rows)
    else:
        print("No changes written due to --dry-run.")

print("\nDone.")
