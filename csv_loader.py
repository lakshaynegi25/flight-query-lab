
"""Reading CSV files into flight records and error messages."""

import csv
from pathlib import Path
from validator import validate_row, to_record


def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    records = []
    errors = []
    seen = set()

    for path in paths:
        with open(path, "r", encoding="utf-8", newline="") as file:
            for line_number, line in enumerate(file, start=1):
                if line_number == 1:
                    continue

                if not line.strip() or line.lstrip().startswith("#"):
                    continue

                fields = next(csv.reader([line]))
                error = validate_row(fields, airports)

                if error is None:
                    clean = [field.strip() for field in fields]
                    key = (clean[0], clean[3])

                    if key in seen:
                        error = "DUPLICATE_FLIGHT"
                    else:
                        seen.add(key)
                        records.append(to_record(fields))

                if error is not None:
                    filename = Path(path).name
                    original = line.rstrip("\r\n")
                    errors.append(
                        f"{filename}:{line_number}: {error} | {original}"
                    )

    return records, errors
