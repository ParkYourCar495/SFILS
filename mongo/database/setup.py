"""Create the SFILS MongoDB database collections."""
import sys
from pathlib import Path

MONGO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MONGO_ROOT))

from config import MONGO_DB_NAME, get_client  # noqa: E402

COLLECTIONS = [
    "patron_types",
    "home_libraries",
    "notification_media",
    "library_usage",
]


def main():
    client = None
    try:
        client = get_client()
        database = client[MONGO_DB_NAME]

        existing = set(database.list_collection_names())
        for name in COLLECTIONS:
            if name not in existing:
                database.create_collection(name)
                print(f"Created collection: {name}")
            else:
                print(f"Collection already exists: {name}")

        print(f"\nMongoDB database is ready: {MONGO_DB_NAME}")
    except Exception as error:
        print(f"Could not set up MongoDB: {error}")
        raise SystemExit(1)
    finally:
        if client is not None:
            client.close()


if __name__ == "__main__":
    main()
