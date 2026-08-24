import sqlite3

def create_database():
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            job_title TEXT,
            country TEXT,
            salary TEXT,
            currency TEXT,
            visa TEXT,
            job_url TEXT,
            application_date TEXT,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()

create_database()

def get_connection():
    return sqlite3.connect("jobs.db")
