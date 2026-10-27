"""Simple beginner-friendly terminal interface for SFILS."""
from db import get_connection
import queries


def show_rows(rows):
    """Print rows one per line, or explain when no rows were found."""
    if not rows:
        print("No records found.")
        return

    for row in rows:
        print(row)


def main():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        print("\nSFILS — San Francisco Integrated Library System")

        while True:
            print("\nMenu")
            print("1. View patron types")
            print("2. View home libraries")
            print("3. View notification methods")
            print("4. Search by age range")
            print("5. Search by home library code")
            print("6. View checkout and renewal summary")
            print("7. Update a row's checkout total")
            print("0. Exit")

            choice = input("Choose an option: ").strip()

            if choice == "1":
                show_rows(queries.get_reference_data(cursor, "patron_type"))

            elif choice == "2":
                show_rows(queries.get_reference_data(cursor, "home_library"))

            elif choice == "3":
                show_rows(queries.get_reference_data(cursor, "notification_medium"))

            elif choice == "4":
                age = input("Enter an age range (for example, 25-34 Years): ").strip()
                show_rows(queries.search_by_age(cursor, age))

            elif choice == "5":
                code = input("Enter a home library code: ").strip()
                show_rows(queries.search_by_library(cursor, code))

            elif choice == "6":
                show_rows(queries.get_usage_summary(cursor))

            elif choice == "7":
                try:
                    usage_id = int(input("Enter usage_id of the row to update: "))
                    new_total = int(input("Enter the new checkout total (0 or greater): "))
                    if new_total < 0:
                        print("Checkout total cannot be negative.")
                        continue

                    changed = queries.update_checkout_total(
                        cursor, usage_id, new_total
                    )
                    if changed == 0:
                        print("No row was changed. Check the usage_id.")
                    else:
                        confirm = input(
                            "Save this change? Type yes to commit: "
                        ).strip().lower()
                        if confirm == "yes":
                            connection.commit()
                            print("Update saved.")
                        else:
                            connection.rollback()
                            print("Update cancelled.")
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
        print("Check that MySQL is running and your .env settings are correct.")

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    main()
