
import sqlite3

conn = sqlite3.connect("database/database.db")

cursor = conn.cursor()

cursor.execute("""

CREATE TABLE IF NOT EXISTS beneficiaries (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    full_name TEXT NOT NULL,

    organization TEXT,

    letter_number TEXT,

    letter_date TEXT,

    request_description TEXT,

    created_at TEXT

)

""")

conn.commit()

conn.close()

print("Database Created Successfully")