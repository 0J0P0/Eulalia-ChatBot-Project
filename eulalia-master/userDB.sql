DROP TABLE IF EXISTS users_login;

CREATE TABLE IF NOT EXISTS users_login (
    username VARCHAR(255) NOT NULL PRIMARY KEY,
    password VARCHAR(255) NOT NULL
);


DROP TABLE IF EXISTS messages;

CREATE TABLE IF NOT EXISTS messages (
    user_id VARCHAR(255) NOT NULL,
    user_message VARCHAR(255),
    chat_message VARCHAR(255),
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES users_login(username)
);

DROP TABLE IF EXISTS contact_messages;

CREATE TABLE IF NOT EXISTS contact_messages (
    user_id VARCHAR(255) NOT NULL,
    user_contact_message VARCHAR(255),
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES users_login(username)
);
)