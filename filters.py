import pandas as pd

# SEARCH FUNCTION
def apply_search(df, query):
    if not query:
        return df
    query = query.lower()
    return df[
        df["Company"].str.lower().str.contains(query) |
        df["Job Title"].str.lower().str.contains(query) |
        df["Country"].str.lower().str.contains(query)
    ]

# FILTER FUNCTION
def apply_filters(df, country, status, visa, currency):
    if country != "All":
        df = df[df["Country"] == country]
    if status != "All":
        df = df[df["Status"] == status]
    if visa != "All":
        df = df[df["Visa"] == visa]
    if currency != "All":
        df = df[df["Currency"] == currency]
    return df
