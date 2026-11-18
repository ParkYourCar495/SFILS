"""Create indexes used by the SFILS MongoDB application."""
import sys
from pathlib import Path

MONGO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MONGO_ROOT))

from config import MONGO_DB_NAME, get_client  # noqa: E402


def main():
    client = None
    try:
        client = get_client()
        database = client[MONGO_DB_NAME]

        # Unique indexes preserve the identifying values from the MySQL schema.
        database.patron_types.create_index(
            "patron_type_code", unique=True, name="uq_patron_type_code"
        )
        database.home_libraries.create_index(
            "home_library_code", unique=True, name="uq_home_library_code"
        )
        database.notification_media.create_index(
            "notification_medium_code",
            unique=True,
            name="uq_notification_medium_code",
        )
        database.library_usage.create_index(
            "usage_id", unique=True, name="uq_usage_id"
        )

        # These indexes support the application's two search operations.
        database.library_usage.create_index("age_range", name="idx_age_range")
        database.library_usage.create_index(
            "home_library_code", name="idx_home_library_code"
        )

        # This index can help when joining usage documents to patron types.
        database.library_usage.create_index(
            "patron_type_code", name="idx_usage_patron_type_code"
        )

        print("SFILS MongoDB indexes created successfully.")
    except Exception as error:
        print(f"Could not create indexes: {error}")
        raise SystemExit(1)
    finally:
        if client is not None:
            client.close()


if __name__ == "__main__":
    main()
