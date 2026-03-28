from datetime import datetime


def get_data_age(transactions):
    dates = [datetime.strptime(t["date"], "%Y-%m-%d") for t in transactions]
    return (max(dates) - min(dates)).days


def detect_phase(transactions):
    days = get_data_age(transactions)

    if days < 30:
        return "cold_start"
    elif days < 60:
        return "learning"
    else:
        return "mature"
