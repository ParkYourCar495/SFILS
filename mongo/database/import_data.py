"""Import the SFILS Excel workbook into the MongoDB database.

Run from the project root:
    python mongo/database/import_data.py

This performs a full reload: existing documents in the four SFILS
collections are deleted before the workbook is imported.
"""
import os
import sys
from pathlib import Path

import pandas as pd

MONGO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = MONGO_ROOT.parent
sys.path.insert(0, str(MONGO_ROOT))

from config import MONGO_DB_NAME, get_client  # noqa: E402

DEFAULT_EXCEL_FILE = "data/SFPL_DataSF_library-usage_Jan 2023.xlsx"

EXPECTED_COLUMNS = [
    "Patron Type Code",
    "Patron Type Definition",
    "Total Checkouts",
    "Total Renewals",
    "Age Range",
    "Home Library Code",
    "Home Library Definition",
    "Circulation Active Month",
    "Circulation Active Year",
    "Notification Preference Code",
    "Notification Code Definition",
    "Provided Email Address",
    "Within San Francisco County",
    "Year Patron Registered",
]


def clean_text(value):
    """Return trimmed text, or None for an actually empty value."""
    if pd.isna(value):
        return None
    cleaned = str(value).strip()
    return cleaned if cleaned else None


def clean_code(value):
    """Clean a code without changing literal values such as '-'."""
    return clean_text(value)


def clean_integer(value):
    """Convert a numeric Excel value to an integer, or None if empty."""
    if pd.isna(value) or str(value).strip() == "":
        return None
    number = float(value)
    if not number.is_integer():
        raise ValueError(f"Expected a whole number, but found {value!r}")
    return int(number)


def clean_boolean(value):
    """Convert common Excel boolean values to True, False, or None."""
    if pd.isna(value) or str(value).strip() == "":
        return None
    if isinstance(value, bool):
        return value

    cleaned = str(value).strip().lower()
    if cleaned in ("true", "1", "yes", "y"):
        return True
    if cleaned in ("false", "0", "no", "n"):
        return False
    raise ValueError(f"Cannot interpret {value!r} as a Boolean value")


def get_excel_path():
    """Resolve EXCEL_FILE from the project .env or use the default path."""
    excel_file = os.getenv("EXCEL_FILE", DEFAULT_EXCEL_FILE)
    path = Path(excel_file)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def build_documents(data):
    """Convert workbook rows into reference and usage documents."""
    patron_types = {}
    home_libraries = {}
    notification_media = {}

    for _, row in data.iterrows():
        patron_code = clean_code(row["Patron Type Code"])
        patron_definition = clean_text(row["Patron Type Definition"])
        if patron_code is not None:
            patron_types[patron_code] = {
                "patron_type_code": patron_code,
                "patron_type_definition": patron_definition,
            }

        library_code = clean_code(row["Home Library Code"])
        library_definition = clean_text(row["Home Library Definition"])
        if library_code is not None:
            home_libraries[library_code] = {
                "home_library_code": library_code,
                "home_library_definition": library_definition,
            }

        notification_code = clean_code(row["Notification Preference Code"])
        notification_definition = clean_text(row["Notification Code Definition"])
        if notification_code is not None:
            notification_media[notification_code] = {
                "notification_medium_code": notification_code,
                "notification_medium_definition": notification_definition,
            }

    usage_documents = []
    for usage_id, (_, row) in enumerate(data.iterrows(), start=1):
        usage_documents.append({
            "usage_id": usage_id,
            "patron_type_code": clean_code(row["Patron Type Code"]),
            "checkout_total": clean_integer(row["Total Checkouts"]),
            "renewal_total": clean_integer(row["Total Renewals"]),
            "age_range": clean_text(row["Age Range"]),
            "home_library_code": clean_code(row["Home Library Code"]),
            "circulation_active_month": clean_integer(
                row["Circulation Active Month"]
            ),
            "circulation_active_year": clean_integer(
                row["Circulation Active Year"]
            ),
            "notification_medium_code": clean_code(
                row["Notification Preference Code"]
            ),
            "provided_email_address": clean_boolean(
                row["Provided Email Address"]
            ),
            "within_san_francisco_county": clean_boolean(
                row["Within San Francisco County"]
            ),
            "year_patron_registered": clean_integer(
                row["Year Patron Registered"]
            ),
        })

    return (
        list(patron_types.values()),
        list(home_libraries.values()),
        list(notification_media.values()),
        usage_documents,
    )


def main():
    excel_path = get_excel_path()
    if not excel_path.exists():
        print(f"Excel workbook not found: {excel_path}")
        print("Check the EXCEL_FILE setting in your project .env file.")
        raise SystemExit(1)

    try:
        # Read as objects first so codes retain their original formatting.
        data = pd.read_excel(excel_path, dtype=object)

        missing_columns = [
            column for column in EXPECTED_COLUMNS if column not in data.columns
        ]
        if missing_columns:
            print("The workbook is missing expected columns:")
            for column in missing_columns:
                print(f" - {column}")
            raise SystemExit(1)

        data = data[EXPECTED_COLUMNS].copy()
        (
            patron_documents,
            library_documents,
            notification_documents,
            usage_documents,
        ) = build_documents(data)

        client = get_client()
        try:
            database = client[MONGO_DB_NAME]

            # Full reload, matching the behavior of the Assignment 1 importer.
            database.library_usage.delete_many({})
            database.patron_types.delete_many({})
            database.home_libraries.delete_many({})
            database.notification_media.delete_many({})

            if patron_documents:
                database.patron_types.insert_many(patron_documents)
            if library_documents:
                database.home_libraries.insert_many(library_documents)
            if notification_documents:
                database.notification_media.insert_many(notification_documents)
            if usage_documents:
                database.library_usage.insert_many(usage_documents)

            print("MongoDB import completed successfully.")
            print(f"Source rows read: {len(data)}")
            print(f"Patron types loaded: {len(patron_documents)}")
            print(f"Home libraries loaded: {len(library_documents)}")
            print(f"Notification media loaded: {len(notification_documents)}")
            print(f"Usage documents inserted: {len(usage_documents)}")
            print(f"Database: {MONGO_DB_NAME}")
        finally:
            client.close()

    except SystemExit:
        raise
    except Exception as error:
        print(f"Import failed: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
