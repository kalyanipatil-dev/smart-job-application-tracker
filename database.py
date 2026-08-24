import sqlite3

DB_NAME = "jobs.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # ---------------- USERS TABLE ----------------
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            mobile TEXT,
            password TEXT,
            role TEXT DEFAULT 'user',
            status TEXT DEFAULT 'active',
            first_login INTEGER DEFAULT 1,
            otp_code TEXT
        )
    """)

    # ---------------- JOBS TABLE ----------------
    c.execute("""
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
            status TEXT,
            user_email TEXT
        )
    """)

    # ---------------- LOGS TABLE ----------------
    c.execute("""
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
