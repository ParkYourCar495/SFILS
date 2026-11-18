# MISFILS
MISFILS: The MongoDB-based Implementation for the San Francisco Integrated Library System.

This folder contains the submission files for Assignment 2. The remaining folders contain the files from Assignment 1.

Make sure to keep all your Assignment 2 files inside this folder to keep the rest of the folders free from clutter. That way, it will be easier to grade both Assignment 1 and Assignment 2.

This folder contains the MongoDB version of the SFILS application. 
The original MySQL in the project root is not modified.

## Requirements

- Python
- MongoDB Community Server running locally
- The SFILS Excel workbook used by Assignment 1

Install Python from the project root:

```
python -m pip install -r mongo/requirements.txt
```

## Configuration

The application reads the project-root `.env` file. 
Add these MongoDB settings to that file:

```
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=sfils_mongo
```

The importer also reads `EXCEL_FILE`. 
If Assignment 1 already defines this setting, it can be reused.
Otherwise, the default workbook path is:

```
data/SFPL_DataSF_library-usage_Jan 2023.xlsx
```

## Setup

Run these commands from the root folder (the folder containing `mongo/`):

```
python mongo/database/setup.py
python mongo/database/import_data.py
python mongo/database/indexes.py
```

The import script performs a full reload. 
It deletes the existing documents in the four SFILS collections before importing the workbook.

The importer preserves the Assignment 1 data-cleaning behavior:
- Empty Excel cells become MongoDB `null` values.
- Literal values such as `-` are preserved.
- Numeric fields are converted to integers.
- Boolean fields are converted to `true`, `false`, or `null`.
- `usage_id` is assigned sequentially starting at 1.

## Running the application

From the project root:

```
python mongo/app/main.py
```

The terminal menu supports:
1. View patron types
2. View home libraries
3. View notification methods
4. Search by age range
5. Search by home library code
6. View checkout and renewal summary
7. Update a usage document's checkout total
0. Exit

## MongoDB Design

The database contains four collections:

- `patron_types`
- `home_libraries`
- `notification_media`
- `library_usage`

Indexes are created for the reference codes, `usage_id`, `age_range`, `home_library_code`, and `patron_type_code`.

## Notes

- The MongoDB database name defaults to `sfils_mongo`.
- MongoDB's automatically generated `_id` is retained in each document.
- The original `usage_id` field is also retained so the application can find and update a usage document.

AI was used to assist in the writing of the Python code.
