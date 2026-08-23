import streamlit as st
import pandas as pd
from database import create_database
import sqlite3

st.set_page_config(page_title="Job Application Tracker", layout="wide")

st.title("📌 Smart Job Application Tracker")

# Sidebar
st.sidebar.header("Add New Job")

company = st.sidebar.text_input("Company")
job_title = st.sidebar.text_input("Job Title")
country = st.sidebar.text_input("Country")
salary = st.sidebar.text_input("Salary")
currency = st.sidebar.text_input("Currency")
visa = st.sidebar.selectbox("Visa Sponsorship", ["Yes", "No", "Unknown"])
job_url = st.sidebar.text_input("Job URL")
application_date = st.sidebar.date_input("Application Date")
status = st.sidebar.selectbox(
    "Status",
    ["Saved", "Applied", "Assessment", "Interview", "Offer", "Rejected"]
)

if st.sidebar.button("Save Job"):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO jobs (company, job_title, country, salary, currency, visa, job_url, application_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (company, job_title, country, salary, currency, visa, job_url, str(application_date), status))

    conn.commit()
    conn.close()

    st.success("Job saved successfully!")

st.header("📄 Saved Job Applications")

conn = sqlite3.connect("jobs.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM jobs")
rows = cursor.fetchall()

conn.close()

if rows:
    df = pd.DataFrame(rows, columns=[
        "ID", "Company", "Job Title", "Country", "Salary", "Currency",
        "Visa", "Job URL", "Application Date", "Status"
    ])
    st.dataframe(df)
else:
    st.info("No jobs saved yet.")

