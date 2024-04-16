CREATE TABLE IF NOT EXISTS users_login (
    id INT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id INT PRIMARY KEY,
    user_id INT NOT NULL,
    user_message VARCHAR(255),
    chat_message VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users_login(id)
);

CREATE TABLE IF NOT EXISTS contact_messages (
    id INT PRIMARY KEY,
    user_id INT NOT NULL,
    user_contact_message VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users_login(id)
);
)