from datetime import datetime, date


def date_to_datetime(d: date):
    return datetime.combine(d, datetime.min.time())
