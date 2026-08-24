import streamlit as st
import pandas as pd
from database import get_connection

# ---------------- USER METRICS (YOUR EXISTING CODE) ----------------
def get_metrics(df):
    total = len(df)
    saved = len(df[df["Status"] == "Saved"])
    applied = len(df[df["Status"] == "Applied"])
    assessment = len(df[df["Status"] == "Assessment"])
    interview = len(df[df["Status"] == "Interview"])
    offer = len(df[df["Status"] == "Offer"])
    rejected = len(df[df["Status"] == "Rejected"])

    interview_rate = (interview / total * 100) if total else 0
    offer_rate = (offer / total * 100) if total else 0

    return {
        "total": total,
        "saved": saved,
        "applied": applied,
        "assessment": assessment,
        "interview": interview,
        "offer": offer,
        "rejected": rejected,
        "interview_rate": interview_rate,
        "offer_rate": offer_rate
    }

# ---------------- USER DASHBOARD WRAPPER ----------------
def user_dashboard():
    st.title("📌 Smart Job Application Tracker (User Dashboard)")
    st.info("User logged in. Your job tracking dashboard is active.")
    # Actual UI is inside app.py (we don't duplicate it here)
    # app.py handles full user UI


# ---------------- ADMIN DASHBOARD ----------------
def admin_dashboard():
    st.title("👑 Admin Dashboard")

    conn = get_connection()
    c = conn.cursor()

    # ---------------- USER COUNT METRICS ----------------
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM users WHERE status='active'")
    active_users = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM users WHERE status='inactive'")
    inactive_users = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM users WHERE role='user'")
    normal_users = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
    admin_count = c.fetchone()[0]

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Users", total_users)
    m2.metric("Active Users", active_users)
    m3.metric("Inactive Users", inactive_users)
    m4.metric("Normal Users", normal_users)
    m5.metric("Admins", admin_count)

    st.divider()

    # ---------------- USER LIST ----------------
    st.header("👥 All Users")

    c.execute("SELECT id, name, email, phone, role, status FROM users")
    users = c.fetchall()

    df_users = pd.DataFrame(
        users,
        columns=["ID", "Name", "Email", "Phone", "Role", "Status"]
    )

    st.dataframe(df_users, use_container_width=True)

    st.divider()

    # ---------------- DEACTIVATE / ACTIVATE USER ----------------
    st.header("⚠️ Activate / Deactivate User")

    user_ids = df_users["ID"].tolist()
    selected_user = st.selectbox("Select User ID", user_ids)

    if selected_user:
        c.execute("SELECT name, email, status FROM users WHERE id=?", (selected_user,))
        u_name, u_email, u_status = c.fetchone()

        st.write(f"**Name:** {u_name}")
        st.write(f"**Email:** {u_email}")
        st.write(f"**Current Status:** {u_status}")

        if u_status == "active":
            if st.button("Deactivate User"):
                c.execute("UPDATE users SET status='inactive' WHERE id=?", (selected_user,))
                conn.commit()
                st.success("User deactivated successfully!")
                st.rerun()
        else:
            if st.button("Activate User"):
                c.execute("UPDATE users SET status='active' WHERE id=?", (selected_user,))
                conn.commit()
                st.success("User activated successfully!")
                st.rerun()

    st.divider()

    # ---------------- ACTIVITY LOGS ----------------
    st.header("📜 User Activity Logs")

    c.execute("SELECT user_email, action, details, timestamp FROM logs ORDER BY id DESC")
    logs = c.fetchall()

    if logs:
        df_logs = pd.DataFrame(
            logs,
            columns=["User", "Action", "Details", "Time"]
        )
        st.dataframe(df_logs, use_container_width=True)
    else:
        st.info("No logs available.")

    conn.close()
