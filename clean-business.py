import csv
from pathlib import Path

CSV_DIR = "./tabula_output"

for csv_path in Path(CSV_DIR).rglob("*.csv"):
    print(f"\nProcessing {csv_path}...")

    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = list(csv.reader(f))

    if not reader:
        print("skipping empty file")
        continue

    expected_cols = len(reader[0])
    deleted_rows = []
    cleaned_rows = []

    for i, row in enumerate(reader):
        # Remove commas from all cells (otherwise bugged CSV)
        row = [cell.replace(",", "") for cell in row]

        # skip empty rows
        if not row or all(cell.strip() == "" for cell in row):
            deleted_rows.append(row)
            continue

        first_cell = row[0].strip().replace("\u00A0", " ")

        # Remove second row
        if i == 1:
            deleted_rows.append(row)
            continue

        # Remove trash rows by detecting first cell values
        if first_cell in {"NO. OF", "TOTAL AMOUNT - DEBITS", "DEBITS"}:
            deleted_rows.append(row)
            continue

        # Remove last row
        if i == len(reader) - 1:
            deleted_rows.append(row)
            continue

        # Remove rows where first cell starts and ends with a quote (bank msg)
        if first_cell.startswith('"') and first_cell.endswith('"'):
            deleted_rows.append(row)
            continue

        # Remove rows where first cell starts and ends with * (bank msg)
        if first_cell.startswith("*") and first_cell.endswith("*"):
            deleted_rows.append(row)
            continue

        # Ensure column count matches header !TODO: not sure about this?
        if len(row) != expected_cols:
            print(f"Skipping malformed row (expected {expected_cols} cols): {row}")
            deleted_rows.append(row)
            continue

        cleaned_rows.append(row)

    # Print deleted rows
    if deleted_rows:
        print("Deleted rows:")
        for dr in deleted_rows:
            print(dr)
    else:
        print("No rows deleted.")

    # Write cleaned CSV back
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerows(cleaned_rows)

print("\nAll CSV files cleaned.")
