-- Drop and recreate users_login table
DROP TABLE IF EXISTS users_login;

CREATE TABLE IF NOT EXISTS users_login (
    username VARCHAR(255) PRIMARY KEY,
    password VARCHAR(255) NOT NULL
);

-- Drop and recreate messages table
DROP TABLE IF EXISTS messages;

CREATE TABLE IF NOT EXISTS messages (
    user_id VARCHAR(255),
    user_message_id TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_message VARCHAR(255),
    chat_message VARCHAR(255),
    PRIMARY KEY (user_id, user_message_id),
    FOREIGN KEY (user_id) REFERENCES users_login(username)
);

-- Drop and recreate contact_messages table
DROP TABLE IF EXISTS contact_messages;

CREATE TABLE IF NOT EXISTS contact_messages (
    user_id VARCHAR(255),
    contact_message_id TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_contact_message VARCHAR(255),
    PRIMARY KEY (user_id, contact_message_id),
    FOREIGN KEY (user_id) REFERENCES users_login(username)
);

