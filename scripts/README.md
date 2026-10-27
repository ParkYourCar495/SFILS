# Database Scripts

This folder contains all the initialization scripts that helps us (perhaps convert and) load the Excel sheet into the database tables.

The scripts that are used to modify (indexing, moving, updating, data cleaning, ...) the database tables (after the data is loaded into the database) are also included here.

Run these files in order:

1. `01_create_database.sql`
2. `02_create_tables.sql`
3. `03_load_data.py` (run with Python, not inside MySQL)
4. `04_create_indexes.sql`
5. `05_analysis_queries.sql`

**Warning:** `03_load_data.py` clears the four tables before reloading them, so repeated imports do not duplicate rows.
