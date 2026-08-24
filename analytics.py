import plotly.express as px

# Applications by Status
def chart_status(df):
    if df.empty:
        return None
    return px.bar(df, x="Status", title="Applications by Status")

# Applications by Country
def chart_country(df):
    if df.empty:
        return None
    return px.bar(df, x="Country", title="Applications by Country")

# Applications by Visa Sponsorship
def chart_visa(df):
    if df.empty:
        return None
    return px.bar(df, x="Visa", title="Applications by Visa Sponsorship")

# Applications Over Time
def chart_time(df):
    if df.empty:
        return None
    return px.line(df, x="Application Date", title="Applications Over Time")
