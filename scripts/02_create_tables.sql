USE sfils;

CREATE TABLE IF NOT EXISTS patron_type (
    patron_type_code CHAR(30) PRIMARY KEY,
    patron_type_definition CHAR(100)
);

CREATE TABLE IF NOT EXISTS home_library (
    home_library_code CHAR(30) PRIMARY KEY,
    home_library_definition CHAR(150)
);

CREATE TABLE IF NOT EXISTS notification_medium (
    notification_medium_code CHAR(30) PRIMARY KEY,
    notification_medium_definition CHAR(100)
);

CREATE TABLE IF NOT EXISTS library_usage (
    usage_id INT AUTO_INCREMENT PRIMARY KEY,
    patron_type_code CHAR(30),
    checkout_total INT,
    renewal_total INT,
    age_range CHAR(50),
    home_library_code CHAR(30) NULL,
    circulation_active_month INT NULL,
    circulation_active_year INT NULL,
    notification_medium_code CHAR(30),
    provided_email_address BOOLEAN NULL,
    within_san_francisco_county BOOLEAN NULL,
    year_patron_registered INT NULL,

    CONSTRAINT fk_usage_patron_type FOREIGN KEY (patron_type_code) REFERENCES patron_type(patron_type_code),
    CONSTRAINT fk_usage_home_library FOREIGN KEY (home_library_code) REFERENCES home_library(home_library_code),
    CONSTRAINT fk_usage_notification_medium FOREIGN KEY (notification_medium_code) REFERENCES notification_medium(notification_medium_code),

    CONSTRAINT chk_checkout_nonnegative CHECK (checkout_total IS NULL OR checkout_total >= 0),
    CONSTRAINT chk_renewal_nonnegative CHECK (renewal_total IS NULL OR renewal_total >= 0),
    CONSTRAINT chk_month_range CHECK (circulation_active_month IS NULL OR circulation_active_month BETWEEN 1 AND 12)
);