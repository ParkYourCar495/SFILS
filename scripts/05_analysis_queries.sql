USE sfils;

-- 1. Check how many records were imported.
SELECT COUNT(*) AS usage_record_count
FROM library_usage;

-- 2. Count by age range.
SELECT age_range, COUNT(*) AS record_count
FROM library_usage
GROUP BY age_range
ORDER BY record_count DESC;

-- 3. Total checkouts and renewals by patron type.
SELECT
    pt.patron_type_definition,
    COUNT(*) AS record_count,
    SUM(lu.checkout_total) AS total_checkouts,
    SUM(lu.renewal_total) AS total_renewals,
    AVG(lu.checkout_total) AS average_checkouts_per_record
FROM library_usage AS lu
LEFT JOIN patron_type AS pt ON lu.patron_type_code = pt.patron_type_code
GROUP BY pt.patron_type_code, pt.patron_type_definition
ORDER BY total_checkouts DESC;

-- 4. Libraries with the most recorded checkouts.
SELECT
    hl.home_library_code,
    hl.home_library_definition,
    COUNT(lu.usage_id) AS record_count,
    SUM(lu.checkout_total) AS total_checkouts
FROM home_library AS hl
LEFT JOIN library_usage AS lu ON hl.home_library_code = lu.home_library_code
GROUP BY hl.home_library_code, hl.home_library_definition
ORDER BY total_checkouts DESC;

-- 5. Records by whether an email address was provided.
SELECT
    provided_email_address,
    COUNT(*) AS record_count
FROM library_usage
GROUP BY provided_email_address;

-- 6. Count records by notification type.
SELECT
    nm.notification_medium_code,
    nm.notification_medium_definition,
    COUNT(lu.usage_id) AS record_count
FROM notification_medium AS nm
LEFT JOIN library_usage AS lu ON nm.notification_medium_code = lu.notification_medium_code
GROUP BY nm.notification_medium_code, nm.notification_medium_definition
ORDER BY record_count DESC;

-- 7. Registration records by year.
SELECT
    year_patron_registered,
    COUNT(*) AS record_count
FROM library_usage
GROUP BY year_patron_registered
ORDER BY year_patron_registered;

-- 8. Performance experiment: inspect the plan for a common filter.
EXPLAIN
SELECT *
FROM library_usage
WHERE patron_type_code = '0';