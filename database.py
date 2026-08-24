import sqlite3

DB_NAME = "jobs.db"

def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # ---------------- JOBS TABLE (original) ----------------
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

    # ---------------- USERS TABLE (new) ----------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            address TEXT,
            phone TEXT,
            role TEXT,
            status TEXT
        )
    """)

    # ---------------- LOGS TABLE (new) ----------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            action TEXT,
            details TEXT,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()

# Run once
create_database()

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)
