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
