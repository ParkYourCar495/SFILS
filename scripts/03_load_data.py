"""
Load the provided Excel workbook into the SFILS MySQL database.

Run from the project root:
    python scripts/03_load_data.py

This script clears existing SFILS table data before reloading it.
It does not identify individual patrons: usage_id is only a row identifier.
"""
import os
import sys
from pathlib import Path

import pandas as pd
import mysql.connector
from dotenv import load_dotenv

# The project root is the folder one level above scripts/.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

EXCEL_FILE = os.getenv(
    "EXCEL_FILE",
    "data/SFPL_DataSF_library-usage_Jan 2023.xlsx"
)
EXCEL_PATH = Path(EXCEL_FILE)
if not EXCEL_PATH.is_absolute():
    EXCEL_PATH = PROJECT_ROOT / EXCEL_PATH

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
    text = str(value).strip()
    if text == "":
        return None
    return text


def clean_code(value):
    """
    Clean a code without changing its meaning.
    A genuinely empty cell becomes None. Literal values such as '-' and
    '(blank)' are kept as they appear in the source.
    """
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
    """Convert common Excel boolean values to True/False or None."""
    if pd.isna(value) or str(value).strip() == "":
        return None
    if isinstance(value, bool):
        return value

    text = str(value).strip().lower()
    if text in ("true", "1", "yes", "y"):
        return True
    if text in ("false", "0", "no", "n"):
        return False
    raise ValueError(f"Cannot interpret {value!r} as a Boolean value")


def connect_to_database():
    """Open a MySQL connection using the local .env settings."""
    required = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError(
            "Missing settings in .env: " + ", ".join(missing)
        )

    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


def main():
    if not EXCEL_PATH.exists():
        print(f"Excel file not found: {EXCEL_PATH}")
        print("Check EXCEL_FILE in your .env file.")
        sys.exit(1)

    # Read every column as an object first so codes are not accidentally
    # changed into numbers or lose formatting.
    data = pd.read_excel(EXCEL_PATH, dtype=object)

    missing_columns = [col for col in EXPECTED_COLUMNS if col not in data.columns]
    if missing_columns:
        print("The workbook is missing expected columns:")
        for col in missing_columns:
            print(f" - {col}")
        sys.exit(1)

    # Keep the expected columns in a known order.
    data = data[EXPECTED_COLUMNS].copy()

    connection = None
    cursor = None

    try:
        connection = connect_to_database()
        cursor = connection.cursor()

        # Clear child table first, then its reference tables, so foreign
        # key constraints are respected. This is a full reload.
        cursor.execute("DELETE FROM library_usage")
        cursor.execute("DELETE FROM patron_type")
        cursor.execute("DELETE FROM home_library")
        cursor.execute("DELETE FROM notification_medium")
        cursor.execute("ALTER TABLE library_usage AUTO_INCREMENT = 1")

        # Build lookup dictionaries. Empty codes are not inserted into
        # reference tables; their corresponding foreign key remains NULL.
        patron_types = {}
        home_libraries = {}
        notification_media = {}

        for _, row in data.iterrows():
            p_code = clean_code(row["Patron Type Code"])
            p_def = clean_text(row["Patron Type Definition"])
            if p_code is not None:
                patron_types[p_code] = p_def

            h_code = clean_code(row["Home Library Code"])
            h_def = clean_text(row["Home Library Definition"])
            if h_code is not None:
                home_libraries[h_code] = h_def

            n_code = clean_code(row["Notification Preference Code"])
            n_def = clean_text(row["Notification Code Definition"])
            if n_code is not None:
                notification_media[n_code] = n_def

        cursor.executemany(
            """
            INSERT INTO patron_type
                (patron_type_code, patron_type_definition)
            VALUES (%s, %s)
            """,
            list(patron_types.items()),
        )

        cursor.executemany(
            """
            INSERT INTO home_library
                (home_library_code, home_library_definition)
            VALUES (%s, %s)
            """,
            list(home_libraries.items()),
        )

        cursor.executemany(
            """
            INSERT INTO notification_medium
                (notification_medium_code, notification_medium_definition)
            VALUES (%s, %s)
            """,
            list(notification_media.items()),
        )

        usage_rows = []
        for _, row in data.iterrows():
            usage_rows.append((
                clean_code(row["Patron Type Code"]),
                clean_integer(row["Total Checkouts"]),
                clean_integer(row["Total Renewals"]),
                clean_text(row["Age Range"]),
                clean_code(row["Home Library Code"]),
                clean_integer(row["Circulation Active Month"]),
                clean_integer(row["Circulation Active Year"]),
                clean_code(row["Notification Preference Code"]),
                clean_boolean(row["Provided Email Address"]),
                clean_boolean(row["Within San Francisco County"]),
                clean_integer(row["Year Patron Registered"]),
            ))

        cursor.executemany(
            """
            INSERT INTO library_usage (
                patron_type_code,
                checkout_total,
                renewal_total,
                age_range,
                home_library_code,
                circulation_active_month,
                circulation_active_year,
                notification_medium_code,
                provided_email_address,
                within_san_francisco_county,
                year_patron_registered
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            usage_rows,
        )

        connection.commit()

        print("Import completed successfully.")
        print(f"Source rows read: {len(data)}")
        print(f"Patron types loaded: {len(patron_types)}")
        print(f"Home libraries loaded: {len(home_libraries)}")
        print(f"Notification media loaded: {len(notification_media)}")
        print(f"Usage rows inserted: {len(usage_rows)}")

    except Exception as error:
        if connection is not None:
            connection.rollback()
        print("Import failed. Database changes were rolled back.")
        print(f"Reason: {error}")
        sys.exit(1)

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    main()
