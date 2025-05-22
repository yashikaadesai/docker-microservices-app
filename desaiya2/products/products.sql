-- products.sql
DROP TABLE IF EXISTS products;

CREATE TABLE products (
    -- id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    price REAL NOT NULL,
    category TEXT NOT NULL
);