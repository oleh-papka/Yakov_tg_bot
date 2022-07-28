from datetime import datetime

import pytz


def get_user_time(timezone='Europe/Kiev') -> dict:
    user_timezone = pytz.timezone(timezone)

    user_timestamp = datetime.now(user_timezone)
    user_time = user_timestamp.strftime('%H:%M')
    user_date = user_timestamp.strftime('%Y-%m-%d')

    return {
        'time': user_time,
        'date': user_date,
        'timestamp': user_timestamp
    }
