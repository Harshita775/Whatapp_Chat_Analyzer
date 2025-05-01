import re
import pandas as pd
from dateutil import parser

def preprocess(data):
    # Combined pattern: matches Android or iPhone-style timestamps
    pattern = r"(?:\[\d{1,2}/\d{1,2}/\d{2,4},\s+\d{1,2}:\d{2}:\d{2}(?:\u202f|\s)?[APMapm]{2}\])|(?:\d{1,2}/\d{1,2}/\d{2,4},\s+\d{1,2}:\d{2}(?:\s*[APMapm]{2})?\s*-\s)"

    # Extract date strings and messages
    date_matches = re.findall(pattern, data)
    messages = re.split(pattern, data)[1:]

    parsed_dates = []
    for date_str in date_matches:
        if date_str.startswith('['):
            cleaned = date_str.strip('[]').replace('\u202f', ' ')
        else:
            cleaned = date_str.strip().rstrip(" -")
        try:
            dt = parser.parse(cleaned)
            parsed_dates.append(dt)
        except Exception as e:
            print(f"Failed to parse date: {cleaned} — {e}")
            parsed_dates.append(None)

    # Create DataFrame
    df = pd.DataFrame({'user_message': messages, 'date': parsed_dates})

    # Separate users from messages
    users = []
    msgs = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if len(entry) >= 3:
            users.append(entry[1])

            msgs.append(entry[2])
        else:
            users.append('group_notification')
            msgs.append(entry[0])

    df['user'] = users
    df['message'] = msgs
    df.drop(columns=['user_message'], inplace=True)

    # Extract time-based features
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['month_num'] = df['date'].dt.month
    df['only_date'] = df['date'].dt.date
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Create period column
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append(f"{hour}-00")
        elif hour == 0:
            period.append("00-1")
        else:
            period.append(f"{hour}-{hour + 1}")
    df['period'] = period

    return df