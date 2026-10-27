USE sfils;

CREATE INDEX idx_usage_patron_type ON library_usage (patron_type_code);
CREATE INDEX idx_usage_home_library ON library_usage (home_library_code);
CREATE INDEX idx_usage_notification_medium ON library_usage (notification_medium_code);
CREATE INDEX idx_usage_age_range ON library_usage (age_range);
CREATE INDEX idx_usage_registration_year ON library_usage (year_patron_registered);