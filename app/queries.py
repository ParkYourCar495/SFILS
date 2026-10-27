"""Functions that run SQL queries for the SFILS application."""


def get_reference_data(cursor, table_name):
    """Show rows from one of the allowed reference tables."""
    allowed_tables = {
        "patron_type": "patron_type_code, patron_type_definition",
        "home_library": "home_library_code, home_library_definition",
        "notification_medium": (
            "notification_medium_code, notification_medium_definition"
        ),
    }
    if table_name not in allowed_tables:
        raise ValueError("Unknown reference table")

    cursor.execute(f"SELECT {allowed_tables[table_name]} FROM {table_name} ORDER BY 1")
    return cursor.fetchall()


def search_by_age(cursor, age_range):
    """Find usage records with the selected age range."""
    cursor.execute(
        """
        SELECT usage_id, age_range, checkout_total, renewal_total,
               patron_type_code, home_library_code
        FROM library_usage
        WHERE age_range = %s
        ORDER BY usage_id
        LIMIT 100
        """,
        (age_range,),
    )
    return cursor.fetchall()


def search_by_library(cursor, library_code):
    """Find usage records for a home library code."""
    cursor.execute(
        """
        SELECT usage_id, age_range, checkout_total, renewal_total,
               patron_type_code, home_library_code
        FROM library_usage
        WHERE home_library_code = %s
        ORDER BY usage_id
        LIMIT 100
        """,
        (library_code,),
    )
    return cursor.fetchall()


def get_usage_summary(cursor):
    """Summarize checkout and renewal totals by patron type."""
    cursor.execute(
        """
        SELECT pt.patron_type_definition,
               COUNT(*) AS record_count,
               SUM(lu.checkout_total) AS total_checkouts,
               SUM(lu.renewal_total) AS total_renewals
        FROM library_usage AS lu
        LEFT JOIN patron_type AS pt
            ON lu.patron_type_code = pt.patron_type_code
        GROUP BY pt.patron_type_code, pt.patron_type_definition
        ORDER BY total_checkouts DESC
        """
    )
    return cursor.fetchall()


def update_checkout_total(cursor, usage_id, new_total):
    """Update a checkout total for one database row."""
    cursor.execute(
        """
        UPDATE library_usage
        SET checkout_total = %s
        WHERE usage_id = %s
        """,
        (new_total, usage_id),
    )
    return cursor.rowcount
