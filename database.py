import sqlite3
import hashlib
import os

DB_NAME = "jobs.db"

ADMIN_USERNAME = "Kat"
ADMIN_NAME = "Kalyani Patil"
ADMIN_EMAIL = "admin@jobtracker.local"
ADMIN_MOBILE = "0000000000"
ADMIN_PASSWORD = "Kat@2026"


def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def hash_admin_password(password):
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        120000
    )

    return "pbkdf2_sha256$120000$%s$%s" % (
        salt.hex(),
        digest.hex()
    )


def _add_column_if_missing(cursor, table, column, definition):
    columns = {
        row[1]
        for row in cursor.execute(
            f"PRAGMA table_info({table})"
        ).fetchall()
    }

    if column not in columns:
        cursor.execute(
            f"ALTER TABLE {table} ADD COLUMN {column} {definition}"
        )


def _ensure_admin_account(conn):
    admin = conn.execute(
        """
        SELECT id
        FROM users
        WHERE role = 'admin'
        ORDER BY id
        LIMIT 1
        """
    ).fetchone()

    password_hash = hash_admin_password(ADMIN_PASSWORD)

    if admin:
        conn.execute(
            """
            UPDATE users
            SET name=?,
                username=?,
                email=?,
                mobile=?,
                password=?,
                role='admin',
                status='active',
                first_login=0,
                otp_code=NULL
            WHERE id=?
            """,
            (
                ADMIN_NAME,
                ADMIN_USERNAME,
                ADMIN_EMAIL,
                ADMIN_MOBILE,
                password_hash,
                admin["id"]
            )
        )
        return

    existing = conn.execute(
        """
        SELECT id
        FROM users
        WHERE LOWER(username)=LOWER(?)
        LIMIT 1
        """,
        (ADMIN_USERNAME,)
    ).fetchone()

    if existing:
        conn.execute(
            """
            UPDATE users
            SET name=?,
                email=?,
                mobile=?,
                password=?,
                role='admin',
                status='active',
                first_login=0,
                otp_code=NULL
            WHERE id=?
            """,
            (
                ADMIN_NAME,
                ADMIN_EMAIL,
                ADMIN_MOBILE,
                password_hash,
                existing["id"]
            )
        )
    else:
        conn.execute(
            """
            INSERT INTO users
            (
                name,
                username,
                email,
                mobile,
                password,
                role,
                status,
                first_login,
                otp_code
            )
            VALUES (?, ?, ?, ?, ?, 'admin', 'active', 0, NULL)
            """,
            (
                ADMIN_NAME,
                ADMIN_USERNAME,
                ADMIN_EMAIL,
                ADMIN_MOBILE,
                password_hash
            )
        )


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            mobile TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            status TEXT DEFAULT 'active',
            first_login INTEGER DEFAULT 1,
            otp_code TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            job_title TEXT NOT NULL,
            country TEXT NOT NULL,
            salary TEXT,
            currency TEXT,
            visa TEXT,
            job_url TEXT,
            application_date TEXT,
            status TEXT NOT NULL,
            user_email TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            action TEXT NOT NULL,
            details TEXT,
            timestamp TEXT NOT NULL
        )
        """
    )

    _add_column_if_missing(
        c, "users", "first_login", "INTEGER DEFAULT 1"
    )

    _add_column_if_missing(
        c, "users", "otp_code", "TEXT"
    )

    _add_column_if_missing(
        c, "users", "created_at", "TEXT"
    )

    _add_column_if_missing(
        c, "jobs", "created_at", "TEXT"
    )

    _add_column_if_missing(
        c, "jobs", "updated_at", "TEXT"
    )

    c.execute(
        "CREATE INDEX IF NOT EXISTS idx_jobs_user_email "
        "ON jobs(user_email)"
    )

    c.execute(
        "CREATE INDEX IF NOT EXISTS idx_logs_user_email "
        "ON logs(user_email)"
    )

    c.execute(
        "CREATE INDEX IF NOT EXISTS idx_users_email "
        "ON users(email)"
    )

    c.execute(
        "CREATE INDEX IF NOT EXISTS idx_users_role "
        "ON users(role)"
    )

    _ensure_admin_account(conn)

    conn.commit()
    conn.close()


def get_admin_account():
    conn = get_connection()

    row = conn.execute(
        """
        SELECT
            id,
            name,
            username,
            email,
            mobile,
            password,
            role,
            status,
            first_login,
            otp_code
        FROM users
        WHERE role = 'admin'
        ORDER BY id
        LIMIT 1
        """
    ).fetchone()

    conn.close()

    return row
