import streamlit as st
import pandas as pd
from database import get_connection

# ---------------- METRICS ----------------
def get_metrics(df):
    if df.empty:
        return {
            "total": 0,
            "saved": 0,
            "applied": 0,
            "assessment": 0,
            "interview": 0,
            "offer": 0,
            "rejected": 0,
            "interview_rate": 0,
            "offer_rate": 0,
        }

    total = len(df)
    saved = (df["Status"] == "Saved").sum()
    applied = (df["Status"] == "Applied").sum()
    assessment = (df["Status"] == "Assessment").sum()
    interview = (df["Status"] == "Interview").sum()
    offer = (df["Status"] == "Offer").sum()
    rejected = (df["Status"] == "Rejected").sum()

    interview_rate = (interview / total) * 100 if total else 0
    offer_rate = (offer / total) * 100 if total else 0

    return {
        "total": total,
        "saved": saved,
        "applied": applied,
        "assessment": assessment,
        "interview": interview,
        "offer": offer,
        "rejected": rejected,
        "interview_rate": interview_rate,
        "offer_rate": offer_rate,
    }

# ---------------- ADMIN HELPERS ----------------
def get_all_users():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, username, email, role, status FROM users")
    rows = c.fetchall()
    conn.close()
    return rows

def update_user_status(user_id, new_status):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET status=? WHERE id=?", (new_status, user_id))
    conn.commit()
    conn.close()

def get_logs():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_email, action, details, timestamp FROM logs ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

# ---------------- ADMIN DASHBOARD ----------------
def admin_dashboard():
    st.title("👑 Admin Dashboard")

    # ---------------- BACK TO HOME BUTTON ----------------
    back_col, _, _, _ = st.columns([1, 3, 1, 1])
    with back_col:
        if st.button("← Back to Home", key="admin_back_home"):
            # फक्त admin navigation flag clear करायचा
            if "show_admin_login" in st.session_state:
                del st.session_state["show_admin_login"]

            # Admin logout नको असेल तर खालील uncomment करू नकोस
            # for key in ["user_id", "user_email", "user_name", "role"]:
            #     if key in st.session_state:
            #         del st.session_state[key]

            st.rerun()

    # ---------------- TABS ----------------
    tab1, tab2 = st.tabs(["Users", "Activity Logs"])

    # ---------------- USERS TAB ----------------
    with tab1:
        st.subheader("Registered Users")

        users = get_all_users()
        df_users = pd.DataFrame(users, columns=["ID", "Name", "Username", "Email", "Role", "Status"])

        st.dataframe(df_users, use_container_width=True)

        st.subheader("Update User Status")

        if not df_users.empty:
            user_ids = df_users["ID"].tolist()
            selected_id = st.selectbox("Select User ID", user_ids)

            selected_user = df_users[df_users["ID"] == selected_id].iloc[0]
            current_status = selected_user["Status"]

            new_status = st.selectbox(
                "New Status",
                ["active", "inactive"],
                index=["active", "inactive"].index(current_status)
            )

            if st.button("Update Status"):
                update_user_status(selected_id, new_status)
                st.success("User status updated successfully!")
                st.rerun()

    # ---------------- LOGS TAB ----------------
    with tab2:
        st.subheader("Activity Logs")

        logs = get_logs()
        df_logs = pd.DataFrame(logs, columns=["User Email", "Action", "Details", "Timestamp"])

        st.dataframe(df_logs, use_container_width=True)
