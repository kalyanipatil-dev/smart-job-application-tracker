import pandas as pd

# ---------------- SEARCH FILTER ----------------
def apply_search(df, query):
    if not query:
        return df

    query = query.lower()

    return df[
        df["Company"].str.lower().str.contains(query, na=False)
        | df["Job Title"].str.lower().str.contains(query, na=False)
        | df["Country"].str.lower().str.contains(query, na=False)
    ]

# ---------------- ADVANCED FILTERS ----------------
def apply_filters(df, country, status, visa, currency):
    filtered = df.copy()

    if country != "All":
        filtered = filtered[filtered["Country"] == country]

    if status != "All":
        filtered = filtered[filtered["Status"] == status]

    if visa != "All":
        filtered = filtered[filtered["Visa"] == visa]

    if currency != "All":
        filtered = filtered[filtered["Currency"] == currency]

    return filtered
