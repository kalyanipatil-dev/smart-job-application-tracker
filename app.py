import streamlit as st
import pandas as pd

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
    st.success("Job saved (MVP — not stored yet)")
