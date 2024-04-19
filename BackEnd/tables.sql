DROP TABLE IF EXISTS users_login;

CREATE TABLE IF NOT EXISTS users_login (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

DROP TABLE IF EXISTS messages;

CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    user_message VARCHAR(255),
    chat_message VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users_login(id)
);

DROP TABLE IF EXISTS contact_messages;

CREATE TABLE IF NOT EXISTS contact_messages (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    user_contact_message VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users_login(id)
);