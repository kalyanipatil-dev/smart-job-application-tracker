import pandas as pd
import streamlit as st

from crud import get_all_users, update_user_status, get_logs


def get_metrics(df):
    total = len(df)
    if total == 0:
        return {
            "total": 0, "saved": 0, "applied": 0, "assessment": 0,
            "interview": 0, "offer": 0, "rejected": 0,
            "interview_rate": 0.0, "offer_rate": 0.0,
        }

    def count(status):
        return int((df["Status"] == status).sum())

    interview = count("Interview")
    offer = count("Offer")

    return {
        "total": total,
        "saved": count("Saved"),
        "applied": count("Applied"),
        "assessment": count("Assessment"),
        "interview": interview,
        "offer": offer,
        "rejected": count("Rejected"),
        "interview_rate": (interview / total) * 100,
        "offer_rate": (offer / total) * 100,
    }


def admin_dashboard():
    st.title("👑 Admin Dashboard")
    st.caption("User management and audit activity")

    if st.button("← Back to Home", key="admin_dashboard_back"):
        st.session_state["show_admin_login"] = False
        # Keep admin session available; this is navigation, not logout.
        st.rerun()

    tab_users, tab_logs = st.tabs(["👥 Users", "📝 Activity Logs"])

    with tab_users:
        users = get_all_users()
        df_users = pd.DataFrame(users)

        if df_users.empty:
            st.info("No users found.")
        else:
            display_df = df_users.rename(columns={
                "id": "ID",
                "name": "Name",
                "username": "Username",
                "email": "Email",
                "role": "Role",
                "status": "Status",
                "created_at": "Created At",
            })
            st.dataframe(display_df, use_container_width=True, hide_index=True)

            st.subheader("Update User Status")
            selected_id = st.selectbox(
                "Select User ID",
                display_df["ID"].tolist(),
                key="admin_selected_user",
            )
            selected = display_df[display_df["ID"] == selected_id].iloc[0]
            current = selected["Status"]

            new_status = st.selectbox(
                "New Status",
                ["active", "inactive"],
                index=0 if current == "active" else 1,
            )

            if st.button("Update Status", key="admin_update_status"):
                admin_email = st.session_state.get("user_email", "admin")
                update_user_status(selected_id, new_status, admin_email)
                st.success("User status updated successfully.")
                st.rerun()

    with tab_logs:
        logs = get_logs()
        df_logs = pd.DataFrame(logs)
        if df_logs.empty:
            st.info("No activity logs found.")
        else:
            st.dataframe(df_logs, use_container_width=True, hide_index=True)
