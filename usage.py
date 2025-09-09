import os
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
import pytz

load_dotenv()
fname = os.environ.get("USAGE_DATABASE")
tz = os.environ.get("TIME_ZONE")

def add_log(message):
    current_time = datetime.now(pytz.timezone(tz))
    data = [
        tz,
        str(current_time.time()),
        str(current_time.date()),
        message
    ]
    try:
        with open(fname, 'a') as file:
            file.writelines([','.join(data) + "\n"])
    except:
        print("Something went wrong adding a log to usage database.")

def summarise():
    df = pd.read_csv(fname, names=['time_zone', 'time', 'date', 'message'])
    counts = df.groupby('date')['message'].value_counts().unstack(fill_value=0)
    print(counts)
