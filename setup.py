import sqlite3

CONN = sqlite3.connect("database.sqlite")
CURSOR = CONN.cursor()

CURSOR.executescript("""
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY,
    user_state VARCHAR(20),
    desired_type VARCHAR(20),
    desired_model VARCHAR(20),
    money INTEGER
);

CREATE TABLE IF NOT EXISTS device (
    id INTEGER PRIMARY KEY,
    device_type VARCHAR(20),
    model VARCHAR(50),
    price INTEGER,
    months INTEGER,
    seller_id INTEGER REFERENCES user(id) ON DELETE CASCADE
);
""")
CONN.commit()
CONN.close()
