import streamlit as st
import pandas as pd

from auth import signup_form, login_form, admin_first_login, admin_normal_login
from crud import add_job, get_all_jobs, get_job_by_id, update_job, delete_job
from filters import apply_search, apply_filters
from export import export_excel, export_word
from dashboard import get_metrics, admin_dashboard
from database import get_connection, init_db

st.set_page_config(page_title="Job Application Tracker", layout="wide")
init_db()

def main():

    # ---------------- HEADER BAR (Admin button only) ----------------
    col1, col2, col3, col4 = st.columns([1, 3, 1, 1])

    # BACK BUTTON → फक्त logged-in असताना
    if "user_email" in st.session_state:
        with col1:
            if st.button("← Back"):
                for key in ["user_email", "user_id", "user_name", "role"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

    # ADMIN BUTTON → नेहमी दिसेल
    with col4:
        admin_clicked = st.button("Admin", key="admin_header_button")

    if admin_clicked:
        st.session_state["show_admin_login"] = True

    # ---------------- ADMIN LOGIN FLOW ----------------
    if st.session_state.get("show_admin_login"):
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id, first_login FROM users WHERE role='admin' LIMIT 1")
        row = c.fetchone()
        conn.close()

        if row and row[1] == 1:
            admin_first_login()
        else:
            admin_normal_login()

        st.stop()   # 🔥 IMPORTANT FIX

    # ---------------- USER / SIGNUP ROUTING ----------------
    if "user_email" not in st.session_state:
        st.title("Welcome to Smart Job Application Tracker")

        tab1, tab2 = st.tabs(["Sign Up", "Login"])

        with tab1:
            signup_form()

        with tab2:
            login_form()

        return

    # ---------------- ROLE CHECK ----------------
    role = st.session_state.get("role", "user")
    user_email = st.session_state.get("user_email")

    # ---------------- ADMIN DASHBOARD ----------------
    if role == "admin":
        admin_dashboard()
        return

    # ---------------- USER DASHBOARD ----------------
    st.title("📌 Smart Job Application Tracker")

    rows = get_all_jobs(user_email)

    if rows:
        df = pd.DataFrame(
            rows,
            columns=[
                "ID",
                "Company",
                "Job Title",
                "Country",
                "Salary",
                "Currency",
                "Visa",
                "Job URL",
                "Application Date",
                "Status",
            ],
        )
    else:
        df = pd.DataFrame(
            columns=[
                "ID",
                "Company",
                "Job Title",
                "Country",
                "Salary",
                "Currency",
                "Visa",
                "Job URL",
                "Application Date",
                "Status",
            ]
        )

    # ---------------- Dashboard ----------------
    st.header("📊 Dashboard")

    if not df.empty:
        metrics = get_metrics(df)
        c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
        c1.metric("Total", metrics["total"])
        c2.metric("Saved", metrics["saved"])
        c3.metric("Applied", metrics["applied"])
        c4.metric("Assessment", metrics["assessment"])
        c5.metric("Interview", metrics["interview"])
        c6.metric("Offer", metrics["offer"])
        c7.metric("Rejected", metrics["rejected"])

        c8, c9 = st.columns(2)
        c8.metric("Interview Rate", f"{metrics['interview_rate']:.1f}%")
        c9.metric("Offer Rate", f"{metrics['offer_rate']:.1f}%")
    else:
        st.info("No applications yet. Add a job to see dashboard metrics.")

    # ---------------- Add New Job ----------------
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
        ["Saved", "Applied", "Assessment", "Interview", "Offer", "Rejected"],
    )

    if st.sidebar.button("Save Job"):
        if not company or not job_title or not country or not status:
            st.sidebar.error("Company, Job Title, Country and Status are required.")
        else:
            add_job(
                company,
                job_title,
                country,
                salary,
                currency,
                visa,
                job_url,
                str(application_date),
                status,
                user_email
            )
            st.sidebar.success("Job saved successfully!")
            st.rerun()

    # ---------------- Search & Filters ----------------
    st.header("🔍 Search & Filters")

    search_query = st.text_input("Search by Company, Job Title or Country")

    country_options = ["All"] + sorted(df["Country"].dropna().unique().tolist())
    status_options = ["All"] + sorted(df["Status"].dropna().unique().tolist())
    visa_options = ["All"] + sorted(df["Visa"].dropna().unique().tolist())
    currency_options = ["All"] + sorted(df["Currency"].dropna().unique().tolist())

    fc1, fc2, fc3, fc4 = st.columns(4)
    selected_country = fc1.selectbox("Country", country_options)
    selected_status = fc2.selectbox("Status", status_options)
    selected_visa = fc3.selectbox("Visa", visa_options)
    selected_currency = fc4.selectbox("Currency", currency_options)

    filtered_df = df.copy()
    filtered_df = apply_search(filtered_df, search_query)
    filtered_df = apply_filters(
        filtered_df, selected_country, selected_status, selected_visa, selected_currency
    )

    # ---------------- Applications Table ----------------
    st.header("📄 Applications")

    if filtered_df.empty:
        st.info("No applications match the current search/filters.")
    else:
        st.dataframe(filtered_df, use_container_width=True)

    # ---------------- Edit / Delete ----------------
    st.subheader("✏️ Edit / 🗑 Delete Application")

    if not filtered_df.empty:
        ids = filtered_df["ID"].tolist()
        selected_id = st.selectbox("Select Application ID", ids)

        if selected_id:
            job = get_job_by_id(selected_id)
            if job:
                (
                    _id,
                    c_company,
                    c_job_title,
                    c_country,
                    c_salary,
                    c_currency,
                    c_visa,
                    c_job_url,
                    c_application_date,
                    c_status,
                ) = job

                with st.form("edit_form"):
                    e_company = st.text_input("Company", c_company)
                    e_job_title = st.text_input("Job Title", c_job_title)
                    e_country = st.text_input("Country", c_country)
                    e_salary = st.text_input("Salary", c_salary)
                    e_currency = st.text_input("Currency", c_currency)
                    e_visa = st.selectbox(
                        "Visa Sponsorship",
                        ["Yes", "No", "Unknown"],
                        index=["Yes", "No", "Unknown"].index(c_visa),
                    )
                    e_job_url = st.text_input("Job URL", c_job_url)
                    e_application_date = st.date_input(
                        "Application Date", pd.to_datetime(c_application_date)
                    )
                    e_status = st.selectbox(
                        "Status",
                        ["Saved", "Applied", "Assessment", "Interview", "Offer", "Rejected"],
                        index=[
                            "Saved",
                            "Applied",
                            "Assessment",
                            "Interview",
                            "Offer",
                            "Rejected",
                        ].index(c_status),
                    )

                    col_update, col_delete = st.columns(2)
                    update_clicked = col_update.form_submit_button("Update Job")
                    delete_clicked = col_delete.form_submit_button("Delete Job")

                    if update_clicked:
                        update_job(
                            _id,
                            e_company,
                            e_job_title,
                            e_country,
                            e_salary,
                            e_currency,
                            e_visa,
                            e_job_url,
                            str(e_application_date),
                            e_status,
                            user_email
                        )
                        st.success("Job updated successfully!")
                        st.rerun()

                    if delete_clicked:
                        confirm = st.checkbox("Confirm delete", value=False)
                        if confirm:
                            delete_job(_id, user_email)
                            st.success("Job deleted successfully!")
                            st.rerun()

    # ---------------- Export ----------------
    st.header("📤 Export Applications")

    if filtered_df.empty:
        st.info("No data to export.")
    else:
        filtered_df = filtered_df[
            [
                "ID",
                "Company",
                "Job Title",
                "Country",
                "Salary",
                "Currency",
                "Visa",
                "Job URL",
                "Application Date",
                "Status",
            ]
        ]

        word_data = export_word(filtered_df)
        excel_bytes = export_excel(filtered_df)

        ec1, ec2 = st.columns(2)

        ec1.download_button(
            "Download Excel",
            data=excel_bytes,
            file_name="applications.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        ec2.download_button(
            "Download Word",
            data=word_data,
            file_name="applications.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )


if __name__ == "__main__":
    main()
