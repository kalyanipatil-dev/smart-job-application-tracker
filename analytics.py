import pandas as pd
import plotly.express as px
import streamlit as st


STATUS_COLORS = {
    "Saved": "#ADD8E6",
    "Applied": "#FFA500",
    "Assessment": "#FFFF00",
    "Interview": "#00BFFF",
    "Offer": "#90EE90",
    "Rejected": "#FF7F7F",
}


def status_pie_chart(df):
    if df.empty:
        st.info("No data available for status analytics.")
        return

    counts = df["Status"].value_counts().reset_index()
    counts.columns = ["Status", "Count"]

    fig = px.pie(
        counts,
        names="Status",
        values="Count",
        title="Application Status Distribution",
        color="Status",
        color_discrete_map=STATUS_COLORS,
        hole=0.35,
    )
    st.plotly_chart(fig, use_container_width=True)


def country_bar_chart(df):
    if df.empty:
        st.info("No data available for country analytics.")
        return

    counts = (
        df["Country"]
        .fillna("Unknown")
        .astype(str)
        .value_counts()
        .reset_index()
    )
    counts.columns = ["Country", "Count"]

    fig = px.bar(
        counts,
        x="Country",
        y="Count",
        title="Applications by Country",
        text="Count",
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)


def monthly_trend(df):
    if df.empty:
        st.info("No data available for monthly analytics.")
        return

    work = df.copy()
    dates = pd.to_datetime(work["Application Date"], errors="coerce")
    work = work.loc[dates.notna()].copy()
    work["Month"] = dates.loc[work.index].dt.to_period("M").astype(str)

    counts = (
        work.groupby("Month")
        .size()
        .reset_index(name="Count")
        .sort_values("Month")
    )

    if counts.empty:
        st.info("No valid application dates available.")
        return

    fig = px.line(
        counts,
        x="Month",
        y="Count",
        markers=True,
        title="Monthly Application Trend",
    )
    st.plotly_chart(fig, use_container_width=True)


def visa_chart(df):
    if df.empty:
        return

    counts = df["Visa"].fillna("Unknown").value_counts().reset_index()
    counts.columns = ["Visa Sponsorship", "Count"]

    fig = px.bar(
        counts,
        x="Visa Sponsorship",
        y="Count",
        title="Applications by Visa Sponsorship",
        text="Count",
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)


def show_analytics(df):
    if df.empty:
        st.info("Add applications to see analytics.")
        return

    c1, c2 = st.columns(2)
    with c1:
        status_pie_chart(df)
    with c2:
        country_bar_chart(df)

    c3, c4 = st.columns(2)
    with c3:
        monthly_trend(df)
    with c4:
        visa_chart(df)
