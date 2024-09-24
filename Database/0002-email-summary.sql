-- Create the email_summary table
CREATE TABLE email_summary (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email_id VARCHAR(512) NOT NULL,
    message_id VARCHAR(512) NOT NULL,
    sender_email VARCHAR(512) NOT NULL,
    sender_name VARCHAR(512),
    receiver_email VARCHAR(512) NOT NULL,
    receiver_name VARCHAR(512),
    forwarded_sender_email VARCHAR(512),
    forwarded_sender_name VARCHAR(512),
    forwarded_receiver_email VARCHAR(512),
    forwarded_receiver_name VARCHAR(512),
    forwarded_email_subject VARCHAR(512),
    forwarded_email_short_summary TEXT NOT NULL,
    forwarded_email_summary TEXT NOT NULL,
    email_priority INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE(email_id),                    -- Ensure email_id is unique
    INDEX(email_id)    
);