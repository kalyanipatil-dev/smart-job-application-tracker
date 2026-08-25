import pandas as pd


def apply_search(df, query):
    if df.empty or not query or not query.strip():
        return df.copy()

    query = query.strip().lower()

    company = df["Company"].fillna("").astype(str).str.lower()
    title = df["Job Title"].fillna("").astype(str).str.lower()
    country = df["Country"].fillna("").astype(str).str.lower()

    mask = (
        company.str.contains(query, regex=False)
        | title.str.contains(query, regex=False)
        | country.str.contains(query, regex=False)
    )
    return df.loc[mask].copy()


def apply_filters(df, country="All", status="All", visa="All", currency="All"):
    filtered = df.copy()

    if country != "All":
        filtered = filtered[filtered["Country"] == country]
    if status != "All":
        filtered = filtered[filtered["Status"] == status]
    if visa != "All":
        filtered = filtered[filtered["Visa"] == visa]
    if currency != "All":
        filtered = filtered[filtered["Currency"] == currency]

    return filtered.copy()
