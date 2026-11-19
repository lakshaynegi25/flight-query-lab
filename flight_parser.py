
"""Flight Schedule Parser and Query Tool."""

import argparse
import json
import logging
from pathlib import Path
import sys

from csv_loader import parse_files
from validator import load_airports
from datetime import datetime
from query import run_queries

STUDENT_ID = "241ADB131"
FIRST_NAME = "Lakshay"
LAST_NAME = "Negi"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Flight schedule parser")

    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-i", metavar="FILE", help="Input CSV file")
    source.add_argument("-d", metavar="FOLDER", help="Folder with CSV files")
    source.add_argument("-j", metavar="FILE", help="Existing JSON database")

    parser.add_argument("-a", metavar="FILE", help="Airport list")
    parser.add_argument("-o", metavar="FILE", help="Database output path")
    parser.add_argument("-q", metavar="FILE", help="Queries JSON file")
    parser.add_argument("-r", metavar="FOLDER", help="Query output folder")

    args = parser.parse_args(argv)

    if (args.i or args.d) and not args.a:
        parser.error("-a is required with -i or -d")

    if args.j and args.o:
        parser.error("-o cannot be used with -j")

    logger = logging.getLogger("flight_parser")
    logger.setLevel(logging.INFO)
    handler = None

    try:
        if args.j:
            with open(args.j, "r", encoding="utf-8") as file:
                db = json.load(file)

            if not isinstance(db, list) or any(
                not isinstance(row, dict) for row in db
            ):
                raise ValueError("database must be an array of objects")

        else:
            if args.i:
                paths = [args.i]
            else:
                folder = Path(args.d)
                paths = [
                    str(path) for path in sorted(folder.iterdir())
                    if path.is_file() and path.name.endswith(".csv")
                ]
                if not paths:
                    raise ValueError("no CSV files found")

            airports = load_airports(args.a)
            db, errors = parse_files(paths, airports)

            output_path = Path(args.o or "db.json")
            log_path = output_path.parent / "errors.log"

            handler = logging.FileHandler(
                log_path, mode="w", encoding="utf-8"
            )
            handler.setFormatter(logging.Formatter(
                "%(asctime)s %(levelname)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            ))
            logger.addHandler(handler)

            for message in errors:
                logger.warning(message)

            with open(output_path, "w", encoding="utf-8") as file:
                json.dump(db, file, indent=2)

        # Query execution will be added in the next stage.
       
        if args.q:
            with open(args.q, "r", encoding="utf-8") as file:
                queries = json.load(file)

            if not isinstance(queries, (dict, list)):
                raise ValueError("invalid query file")

            if isinstance(queries, list):
                if any(not isinstance(q, dict) for q in queries):
                    raise ValueError("invalid query file")

            responses = run_queries(db, queries)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            filename = (
                f"response_{STUDENT_ID}_{FIRST_NAME}_"
                f"{LAST_NAME}_{timestamp}.json"
            )

            output_folder = Path(args.r or ".")
            response_path = output_folder / filename

            with open(response_path, "w", encoding="utf-8") as file:
                json.dump(responses, file, indent=2)

        return 0

    except (OSError, ValueError, UnicodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    finally:
        if handler is not None:
            logger.removeHandler(handler)
            handler.close()


if __name__ == "__main__":
    sys.exit(main())
