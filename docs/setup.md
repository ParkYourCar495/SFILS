# SFILS setup instructions

## 1. Install requirements

Install MySQL and Python 3.

## 2. Get the dataset

Obtain `SFPL_DataSF_library-usage_Jan 2023.xlsx`.

## 3. Install Python packages

```
python -m pip install -r requirements.txt
```

## 4. Create the database

Open MySQL Workbench and run:

```
scripts/01_create_database.sql
scripts/02_create_tables.sql
```

Run each SQL file in order.

## 5. Load the Excel data

From the project root, run:

```
python scripts/03_load_data.py
```

The script clears existing table data before importing the workbook.

## 6. Verify the import

Run these in MySQL:

```
USE sfils;
SHOW TABLES;
SELECT COUNT(*) FROM patron_type;
SELECT COUNT(*) FROM home_library;
SELECT COUNT(*) FROM notification_medium;
SELECT COUNT(*) FROM library_usage;
```

## 7. Add indexes

Run `scripts/04_create_indexes.sql`.

## 8. Run analysis queries

Open and run in `scripts/05_analysis_queries.sql`.

## 9. Run the Python application

From the project root:

```
python app/main.py
```

Use the menu to view data, search usage records, and see summaries.