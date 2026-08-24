import sqlite3
from database import get_connection
from datetime import datetime

# ---------------- LOG HELPER ----------------
def add_log(user_email, action, details):
    conn = get_connection()
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    c.execute("""
        INSERT INTO logs (user_email, action, details, timestamp)
        VALUES (?, ?, ?, ?)
    """, (user_email, action, details, timestamp))

    conn.commit()
    conn.close()

# ---------------- ADD JOB ----------------
def add_job(company, job_title, country, salary, currency, visa, job_url, application_date, status, user_email):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        INSERT INTO jobs (company, job_title, country, salary, currency, visa, job_url, application_date, status, user_email)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (company, job_title, country, salary, currency, visa, job_url, application_date, status, user_email))

    conn.commit()
    conn.close()

    add_log(user_email, "ADD JOB", f"{company} - {job_title}")

# ---------------- GET ALL JOBS (USER SPECIFIC) ----------------
def get_all_jobs(user_email):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT id, company, job_title, country, salary, currency, visa, job_url, application_date, status
        FROM jobs
        WHERE user_email = ?
        ORDER BY id DESC
    """, (user_email,))

    rows = c.fetchall()
    conn.close()
    return rows

# ---------------- GET JOB BY ID ----------------
def get_job_by_id(job_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT id, company, job_title, country, salary, currency, visa, job_url, application_date, status
        FROM jobs
        WHERE id=?
    """, (job_id,))

    row = c.fetchone()
    conn.close()
    return row

# ---------------- UPDATE JOB ----------------
def update_job(job_id, company, job_title, country, salary, currency, visa, job_url, application_date, status, user_email):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        UPDATE jobs
        SET company=?, job_title=?, country=?, salary=?, currency=?, visa=?, job_url=?, application_date=?, status=?
        WHERE id=?
    """, (company, job_title, country, salary, currency, visa, job_url, application_date, status, job_id))

    conn.commit()
    conn.close()

    add_log(user_email, "UPDATE JOB", f"Updated job ID {job_id}")

# ---------------- DELETE JOB ----------------
def delete_job(job_id, user_email):
    conn = get_connection()
    c = conn.cursor()

    c.execute("DELETE FROM jobs WHERE id=?", (job_id,))
    conn.commit()
    conn.close()

    add_log(user_email, "DELETE JOB", f"Deleted job ID {job_id}")
