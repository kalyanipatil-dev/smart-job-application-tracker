import streamlit as st
import pandas as pd

from auth import (
    signup_form,
    login_form,
    admin_normal_login,
    logout_user
)

from crud import (
    add_job,
    get_all_jobs,
    get_job_by_id,
    update_job,
    delete_job
)

from filters import (
    apply_search,
    apply_filters
)

from export import (
    export_csv,
    export_excel,
    export_word,
    export_pdf
)

from dashboard import (
    get_metrics,
    admin_dashboard
)

from analytics import show_analytics
from database import init_db


st.set_page_config(
    page_title="Smart Job Application Tracker",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()


STATUS_OPTIONS = [
    "Saved",
    "Applied",
    "Assessment",
    "Interview",
    "Offer",
    "Rejected"
]

VISA_OPTIONS = [
    "Yes",
    "No",
    "Unknown"
]


def clear_navigation_flags():
    st.session_state.pop(
        "show_admin_login",
        None
    )

    st.session_state.pop(
        "admin_otp_user_id",
        None
    )


def back_to_home():
    clear_navigation_flags()

    # Admin session मधून बाहेर येऊन Home page वर जा
    st.session_state.pop("user_id", None)
    st.session_state.pop("user_name", None)
    st.session_state.pop("user_email", None)
    st.session_state.pop("role", None)

    st.session_state["page"] = "home"

    st.rerun()

def render_header():
    left, spacer, logout_col, admin_col = st.columns(
        [1, 5, 1, 1]
    )

    with left:
        if st.button(
            "← Home",
            key="header_home"
        ):
            back_to_home()

    with logout_col:
        if st.session_state.get("user_email"):
            if st.button(
                "Logout",
                key="header_logout"
            ):
                logout_user()
                st.rerun()

    with admin_col:
        if st.button(
            "Admin",
            key="admin_header_button"
        ):
            st.session_state[
                "show_admin_login"
            ] = True

            st.session_state[
                "page"
            ] = "admin_login"

            st.rerun()


def render_admin_login():
    st.title("🔐 Admin Access")
    st.caption("Administrator authentication")

    if st.button(
        "← Back to Home",
        key="admin_login_back"
    ):
        clear_navigation_flags()

        st.session_state[
            "page"
        ] = "home"

        st.rerun()

    from database import get_admin_account

    admin = get_admin_account()

    if not admin:
        st.error(
            "Admin account could not be created."
        )
        return

    admin_normal_login(admin)


def render_add_job(user_email):
    with st.expander(
        "➕ Add New Job",
        expanded=False
    ):
        with st.form(
            "add_job_form",
            clear_on_submit=True
        ):
            c1, c2, c3 = st.columns(3)

            company = c1.text_input(
                "Company *"
            )

            job_title = c2.text_input(
                "Job Title *"
            )

            country = c3.text_input(
                "Country *"
            )

            c4, c5, c6 = st.columns(3)

            salary = c4.text_input(
                "Salary"
            )

            currency = c5.text_input(
                "Currency"
            )

            visa = c6.selectbox(
                "Visa Sponsorship",
                VISA_OPTIONS
            )

            c7, c8 = st.columns(2)

            job_url = c7.text_input(
                "Job URL"
            )

            application_date = c8.date_input(
                "Application Date"
            )

            status = st.selectbox(
                "Status",
                STATUS_OPTIONS
            )

            submitted = st.form_submit_button(
                "Save Job",
                type="primary"
            )

            if submitted:
                if (
                    not company.strip()
                    or not job_title.strip()
                    or not country.strip()
                ):
                    st.error(
                        "Company, Job Title and Country are required."
                    )
                    return

                add_job(
                    company.strip(),
                    job_title.strip(),
                    country.strip(),
                    salary.strip(),
                    currency.strip(),
                    visa,
                    job_url.strip(),
                    str(application_date),
                    status,
                    user_email
                )

                st.success(
                    "Job saved successfully!"
                )

                st.rerun()


def render_edit_delete(
    filtered_df,
    user_email
):
    if filtered_df.empty:
        return

    st.subheader(
        "✏️ Manage Application"
    )

    ids = filtered_df["ID"].tolist()

    selected_id = st.selectbox(
        "Select Application",
        ids,
        key="selected_job_id"
    )

    job = get_job_by_id(
        selected_id,
        user_email
    )

    if not job:
        st.error(
            "Application not found or you do not have permission to access it."
        )
        return

    with st.form(
        "edit_job_form"
    ):
        c1, c2, c3 = st.columns(3)

        e_company = c1.text_input(
            "Company *",
            job["company"]
        )

        e_job_title = c2.text_input(
            "Job Title *",
            job["job_title"]
        )

        e_country = c3.text_input(
            "Country *",
            job["country"]
        )

        c4, c5, c6 = st.columns(3)

        e_salary = c4.text_input(
            "Salary",
            job["salary"] or ""
        )

        e_currency = c5.text_input(
            "Currency",
            job["currency"] or ""
        )

        e_visa = c6.selectbox(
            "Visa Sponsorship",
            VISA_OPTIONS,
            index=(
                VISA_OPTIONS.index(job["visa"])
                if job["visa"] in VISA_OPTIONS
                else 2
            )
        )

        c7, c8 = st.columns(2)

        e_job_url = c7.text_input(
            "Job URL",
            job["job_url"] or ""
        )

        current_date = pd.to_datetime(
            job["application_date"],
            errors="coerce"
        )

        if pd.isna(current_date):
            current_date = pd.Timestamp.today()

        e_application_date = c8.date_input(
            "Application Date",
            current_date.date()
        )

        e_status = st.selectbox(
            "Status",
            STATUS_OPTIONS,
            index=(
                STATUS_OPTIONS.index(job["status"])
                if job["status"] in STATUS_OPTIONS
                else 0
            )
        )

        u1, u2 = st.columns(2)

        update_clicked = u1.form_submit_button(
            "💾 Update Job",
            type="primary"
        )

        delete_clicked = u2.form_submit_button(
            "🗑️ Delete Job"
        )

        if update_clicked:
            if (
                not e_company.strip()
                or not e_job_title.strip()
                or not e_country.strip()
            ):
                st.error(
                    "Company, Job Title and Country are required."
                )
                return

            update_job(
                selected_id,
                e_company.strip(),
                e_job_title.strip(),
                e_country.strip(),
                e_salary.strip(),
                e_currency.strip(),
                e_visa,
                e_job_url.strip(),
                str(e_application_date),
                e_status,
                user_email
            )

            st.success(
                "Job updated successfully!"
            )

            st.rerun()

        if delete_clicked:
            st.session_state[
                "confirm_delete_id"
            ] = selected_id

            st.rerun()

    if (
        st.session_state.get(
            "confirm_delete_id"
        ) == selected_id
    ):
        st.warning(
            "Are you sure you want to permanently delete this application?"
        )

        c1, c2 = st.columns(2)

        if c1.button(
            "Yes, Delete",
            key=f"confirm_delete_{selected_id}",
            type="primary"
        ):
            delete_job(
                selected_id,
                user_email
            )

            st.session_state.pop(
                "confirm_delete_id",
                None
            )

            st.success(
                "Job deleted successfully!"
            )

            st.rerun()

        if c2.button(
            "Cancel",
            key=f"cancel_delete_{selected_id}"
        ):
            st.session_state.pop(
                "confirm_delete_id",
                None
            )

            st.rerun()


def render_export(filtered_df):
    st.subheader(
        "📤 Export Applications"
    )

    if filtered_df.empty:
        st.info(
            "No data available to export."
        )
        return

    export_df = filtered_df.copy()

    export_df.columns = [
        str(c)
        for c in export_df.columns
    ]

    c1, c2, c3, c4 = st.columns(4)

    c1.download_button(
        "📋 CSV",
        data=export_csv(export_df),
        file_name="job_applications.csv",
        mime="text/csv",
        use_container_width=True
    )

    c2.download_button(
        "📊 Excel",
        data=export_excel(export_df),
        file_name="job_applications.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        use_container_width=True
    )

    c3.download_button(
        "📝 Word",
        data=export_word(export_df),
        file_name="job_applications.docx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
        use_container_width=True
    )

    c4.download_button(
        "📄 PDF",
        data=export_pdf(export_df),
        file_name="job_applications.pdf",
        mime="application/pdf",
        use_container_width=True
    )


def render_user_dashboard():
    user_email = st.session_state[
        "user_email"
    ]

    st.title(
        "💼 Smart Job Application Tracker"
    )

    st.caption(
        f"Logged in as {user_email}"
    )

    rows = get_all_jobs(
        user_email
    )

    df = pd.DataFrame(rows)

    if df.empty:
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
                "Status"
            ]
        )

    st.header(
        "📊 Dashboard"
    )

    metrics = get_metrics(df)

    cols = st.columns(9)

    for col, label, key in zip(
        cols,
        [
            "Total",
            "Saved",
            "Applied",
            "Assessment",
            "Interview",
            "Offer",
            "Rejected",
            "Interview Rate",
            "Offer Rate"
        ],
        [
            "total",
            "saved",
            "applied",
            "assessment",
            "interview",
            "offer",
            "rejected",
            "interview_rate",
            "offer_rate"
        ]
    ):
        value = metrics[key]

        if "Rate" in label:
            value = f"{value:.1f}%"

        col.metric(
            label,
            value
        )

    render_add_job(
        user_email
    )

    st.header(
        "🔍 Search & Filters"
    )

    search_query = st.text_input(
        "Search by Company, Job Title or Country",
        key="job_search"
    )

    if not df.empty:
        country_options = (
            ["All"]
            + sorted(
                df["Country"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )
        )

        status_options = (
            ["All"]
            + sorted(
                df["Status"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )
        )

        visa_options = (
            ["All"]
            + sorted(
                df["Visa"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )
        )

        currency_options = (
            ["All"]
            + sorted(
                df["Currency"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )
        )

    else:
        country_options = ["All"]
        status_options = ["All"]
        visa_options = ["All"]
        currency_options = ["All"]

    f1, f2, f3, f4 = st.columns(4)

    selected_country = f1.selectbox(
        "Country",
        country_options
    )

    selected_status = f2.selectbox(
        "Status",
        status_options
    )

    selected_visa = f3.selectbox(
        "Visa",
        visa_options
    )

    selected_currency = f4.selectbox(
        "Currency",
        currency_options
    )

    filtered_df = apply_search(
        df,
        search_query
    )

    filtered_df = apply_filters(
        filtered_df,
        selected_country,
        selected_status,
        selected_visa,
        selected_currency
    )

    st.header(
        "📄 Applications"
    )

    if filtered_df.empty:
        st.info(
            "No applications match the current search/filters."
        )
    else:
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )

        render_edit_delete(
            filtered_df,
            user_email
        )

    render_export(
        filtered_df
    )

    st.header(
        "📈 Analytics"
    )

    show_analytics(
        filtered_df
    )


def main():
    render_header()

    if st.session_state.get(
        "show_admin_login"
    ):
        render_admin_login()
        return

    if "user_email" not in st.session_state:
        st.title(
            "Welcome to Smart Job Application Tracker"
        )

        st.caption(
            "Track applications, analyze progress and keep your job search organized."
        )

        tab1, tab2 = st.tabs(
            [
                "Create Account",
                "Login"
            ]
        )

        with tab1:
            signup_form()

        with tab2:
            login_form()

        return

if st.session_state.get("role") == "admin":
   admin_dashboard()

   if st.button(
      "← Back to Home",
      key="admin_dashboard_back_home"
   ):
      back_to_home()

   return

    render_user_dashboard()


if __name__ == "__main__":
    main()
