CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    user_name VARCHAR(100) UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    mail_id VARCHAR(100) NOT NULL
);
CREATE TABLE user_notification(
    rem_id SERIAL PRIMARY KEY,
    detail JSONB,
    last_check_time TIMESTAMP WITH TIME ZONE,
    user_id INT,
    scrape_url TEXT,
    scrape_option TEXT,
    check_from_time INT,
    check_till_time INT,
    notification_frequency INT, -- IN hours
    notification_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES "user"(id)
);