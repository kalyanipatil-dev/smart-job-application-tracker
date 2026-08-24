from database import get_connection

# CREATE (Add Job)
def add_job(company, job_title, country, salary, currency, visa, job_url, application_date, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO jobs (company, job_title, country, salary, currency, visa, job_url, application_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (company, job_title, country, salary, currency, visa, job_url, application_date, status))
    conn.commit()
    conn.close()

# READ (Get all jobs)
def get_all_jobs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs")
    rows = cursor.fetchall()
    conn.close()
    return rows

# READ (Get single job by ID)
def get_job_by_id(job_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    row = cursor.fetchone()
    conn.close()
    return row

# UPDATE (Edit job)
def update_job(job_id, company, job_title, country, salary, currency, visa, job_url, application_date, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE jobs SET
            company=?, job_title=?, country=?, salary=?, currency=?, visa=?, job_url=?, application_date=?, status=?
        WHERE id=?
    """, (company, job_title, country, salary, currency, visa, job_url, application_date, status, job_id))
    conn.commit()
    conn.close()

# DELETE (Remove job)
def delete_job(job_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()
