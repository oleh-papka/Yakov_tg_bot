from datetime import datetime, timezone


def get_time_from_offset(offset: int) -> dict:
    timestamp = datetime.now(timezone.utc).timestamp() + offset
    dt = datetime.fromtimestamp(timestamp)
    time = dt.strftime('%H:%M')
    date = dt.strftime('%Y-%m-%d')

    return {
        'time': time,
        'date': date,
        'dt': dt
    }


def timezone_offset_repr(timezone_offset: int | str) -> str:
    timezone_offset = int(timezone_offset/3600)
    return f'{timezone_offset:+d}'
