"""Beginner-friendly terminal interface for the SFILS MongoDB application."""
import sys
from pathlib import Path

MONGO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MONGO_ROOT))

from database import queries  # noqa: E402
from app.db import get_database  # noqa: E402


def show_rows(rows):
    """Print returned documents in a readable format."""
    if not rows:
        print("No records found.")
        return

    for row in rows:
        print(row)


def main():
    client = None
    try:
        client, database = get_database()
        print("\nSFILS — San Francisco Integrated Library System (MongoDB)")

        while True:
            print("\nMenu")
            print("1. View patron types")
            print("2. View home libraries")
            print("3. View notification methods")
            print("4. Search by age range")
            print("5. Search by home library code")
            print("6. View checkout and renewal summary")
            print("7. Update a document's checkout total")
            print("0. Exit")

            choice = input("Choose an option: ").strip()

            if choice == "1":
                show_rows(queries.get_reference_data(database, "patron_type"))

            elif choice == "2":
                show_rows(queries.get_reference_data(database, "home_library"))

            elif choice == "3":
                show_rows(
                    queries.get_reference_data(database, "notification_medium")
                )

            elif choice == "4":
                age = input(
                    "Enter an age range (for example, 25-34 Years): "
                ).strip()
                show_rows(queries.search_by_age(database, age))

            elif choice == "5":
                code = input("Enter a home library code: ").strip()
                show_rows(queries.search_by_library(database, code))

            elif choice == "6":
                show_rows(queries.get_usage_summary(database))

            elif choice == "7":
                try:
                    usage_id = int(input("Enter usage_id of the document to update: "))
                    new_total = int(
                        input("Enter the new checkout total (0 or greater): ")
                    )
                    if new_total < 0:
                        print("Checkout total cannot be negative.")
                        continue

                    confirm = input(
                        "Save this change? Type yes to continue: "
                    ).strip().lower()
                    if confirm != "yes":
                        print("Update cancelled.")
                        continue

                    matched = queries.update_checkout_total(
                        database, usage_id, new_total
                    )
                    if matched == 0:
                        print("No document found. Check the usage_id.")
                    else:
                        print("Update saved.")
                except ValueError:
                    print("Please enter whole numbers for usage_id and checkout total.")

            elif choice == "0":
                print("Goodbye.")
                break

            else:
                print("Please choose one of the listed options.")

    except Exception as error:
        print("The application could not complete the operation.")
        print(f"Details: {error}")
        print("Check that MongoDB is running and your MongoDB settings are correct.")
    finally:
        if client is not None:
            client.close()


if __name__ == "__main__":
    main()
