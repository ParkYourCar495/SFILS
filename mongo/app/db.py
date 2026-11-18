"""MongoDB connection helper for the SFILS application."""
import sys
from pathlib import Path

MONGO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MONGO_ROOT))

from config import MONGO_DB_NAME, get_client  # noqa: E402


def get_database():
    """Return an open MongoDB client and the SFILS database."""
    client = get_client()
    return client, client[MONGO_DB_NAME]
