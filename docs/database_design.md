# Database design

## Overview

SFILS stores the library in four tables: three reference tables and one main usage table.

## Tables

- `patron_type`
- `home_library`
- `notification_medium`
- `library_usage`

## Missing values and codes

- Empty Excel cells are imported as SQL `NULL` where appropriate.
- The `-` is preserved rather than converted to `NULL`.
