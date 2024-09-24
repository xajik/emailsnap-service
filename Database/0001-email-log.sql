CREATE TABLE
    email_log (
        id INT AUTO_INCREMENT PRIMARY KEY, -- Unique ID for each log entry
        message_id VARCHAR(512) NOT NULL, -- Unique identifier of the email (e.g., SES message ID)
        done BOOLEAN DEFAULT FALSE, -- Indicates if the email has been processed
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP, -- The date and time the email was received
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );