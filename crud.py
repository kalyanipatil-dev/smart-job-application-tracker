from datetime import datetime

from database import get_connection


def add_log(user_email, action, details):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO logs (user_email, action, details, timestamp)
        VALUES (?, ?, ?, ?)
        """,
        (
            user_email,
            action,
            details,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    conn.commit()
    conn.close()


def add_job(company, job_title, country, salary, currency, visa,
            job_url, application_date, status, user_email):
    conn = get_connection()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        """
        INSERT INTO jobs
        (company, job_title, country, salary, currency, visa, job_url,
         application_date, status, user_email, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            company, job_title, country, salary, currency, visa,
            job_url, application_date, status, user_email, now, now
        ),
    )
    conn.commit()
    conn.close()
    add_log(user_email, "ADD_JOB", f"{company} - {job_title}")


def get_all_jobs(user_email):
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT id AS ID, company AS Company, job_title AS "Job Title",
               country AS Country, salary AS Salary, currency AS Currency,
               visa AS Visa, job_url AS "Job URL",
               application_date AS "Application Date", status AS Status
        FROM jobs
        WHERE LOWER(user_email) = LOWER(?)
        ORDER BY id DESC
        """,
        (user_email,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_job_by_id(job_id, user_email):
    conn = get_connection()
    row = conn.execute(
        """
        SELECT id, company, job_title, country, salary, currency, visa,
               job_url, application_date, status
        FROM jobs
        WHERE id=? AND LOWER(user_email)=LOWER(?)
        """,
        (job_id, user_email),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def update_job(job_id, company, job_title, country, salary, currency,
               visa, job_url, application_date, status, user_email):
    conn = get_connection()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor = conn.execute(
        """
        UPDATE jobs
        SET company=?, job_title=?, country=?, salary=?, currency=?, visa=?,
            job_url=?, application_date=?, status=?, updated_at=?
        WHERE id=? AND LOWER(user_email)=LOWER(?)
        """,
        (
            company, job_title, country, salary, currency, visa,
            job_url, application_date, status, now, job_id, user_email
        ),
    )
    conn.commit()
    changed = cursor.rowcount
    conn.close()

    if changed:
        add_log(user_email, "UPDATE_JOB", f"Updated job ID {job_id}")
    return changed > 0


def delete_job(job_id, user_email):
    conn = get_connection()
    cursor = conn.execute(
        "DELETE FROM jobs WHERE id=? AND LOWER(user_email)=LOWER(?)",
        (job_id, user_email),
    )
    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted:
        add_log(user_email, "DELETE_JOB", f"Deleted job ID {job_id}")
    return deleted > 0


def get_all_users():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, name, username, email, role, status, created_at FROM users ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_user_status(user_id, new_status, admin_email):
    conn = get_connection()
    cursor = conn.execute(
        "UPDATE users SET status=? WHERE id=?",
        (new_status, user_id),
    )
    conn.commit()
    changed = cursor.rowcount
    conn.close()

    if changed:
        add_log(admin_email, "UPDATE_USER_STATUS",
                 f"User ID {user_id} -> {new_status}")
    return changed > 0


def get_logs():
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT user_email AS "User Email",
               action AS Action,
               details AS Details,
               timestamp AS Timestamp
        FROM logs
        ORDER BY id DESC
        """
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
