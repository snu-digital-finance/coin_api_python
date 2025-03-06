import os
from datetime import datetime, timezone, timedelta

def creat_folders(periods, exchanges):
    for period in periods:
        os.makedirs(f"data/{period}", exist_ok=True)
        for exchange in exchanges:
            os.makedirs(f"data/{period}/{exchange}", exist_ok=True)


def kst_to_utc(iso_time_str: str):
    kst_time = datetime.fromisoformat(iso_time_str).astimezone(timezone(timedelta(hours=9)))
    utc_time = kst_time.astimezone(timezone.utc)
    return utc_time.isoformat().replace("+00:00", "0Z")
