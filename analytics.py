import pandas as pd
import streamlit as st
import plotly.express as px

# ---------------- STATUS PIE CHART ----------------
def status_pie_chart(df):
    if df.empty:
        st.info("No data available for charts.")
        return

    status_count = df["Status"].value_counts().reset_index()
    status_count.columns = ["Status", "Count"]

    fig = px.pie(
        status_count,
        names="Status",
        values="Count",
        title="Application Status Distribution",
        color="Status",
        color_discrete_map={
            "Saved": "#ADD8E6",
            "Applied": "#FFA500",
            "Assessment": "#FFFF00",
            "Interview": "#00BFFF",
            "Offer": "#90EE90",
            "Rejected": "#FF7F7F",
        }
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- COUNTRY BAR CHART ----------------
def country_bar_chart(df):
    if df.empty:
        return

    country_count = df["Country"].value_counts().reset_index()
    country_count.columns = ["Country", "Count"]

    fig = px.bar(
        country_count,
        x="Country",
        y="Count",
        title="Applications by Country",
        text="Count",
        color="Country"
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

# ---------------- MONTHLY APPLICATION TREND ----------------
def monthly_trend(df):
    if df.empty:
        return

    df["Application Date"] = pd.to_datetime(df["Application Date"], errors="coerce")
    df["Month"] = df["Application Date"].dt.strftime("%Y-%m")

    monthly_count = df["Month"].value_counts().reset_index()
    monthly_count.columns = ["Month", "Count"]
    monthly_count = monthly_count.sort_values("Month")

    fig = px.line(
        monthly_count,
        x="Month",
        y="Count",
        markers=True,
        title="Monthly Application Trend"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- MAIN ANALYTICS SECTION ----------------
def show_analytics(df):
    st.header("📈 Analytics")

    if df.empty:
        st.info("No applications available for analytics.")
        return

    col1, col2 = st.columns(2)
    with col1:
        status_pie_chart(df)
    with col2:
        country_bar_chart(df)

    st.subheader("📅 Monthly Trend")
    monthly_trend(df)
