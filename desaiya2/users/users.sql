DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    email_address TEXT UNIQUE NOT NULL,
    current_password TEXT NOT NULL,
    salt TEXT NOT NULL,
    employee INTEGER NOT NULL CHECK (employee IN (0, 1))

);