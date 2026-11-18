"""Shared MongoDB configuration for the SFILS MongoDB project."""
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

MONGO_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = MONGO_ROOT.parent

# Read the existing project-level .env file. MongoDB settings are separate
# from the MySQL settings used by Assignment 1.
load_dotenv(PROJECT_ROOT / ".env")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "sfils_mongo")


def get_client():
    """Create and verify a connection to the local MongoDB server."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    return client
