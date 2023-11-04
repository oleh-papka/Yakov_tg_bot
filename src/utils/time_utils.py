from datetime import datetime, timezone, timedelta, time


class UserTime(datetime):
    def __new__(cls, *args, **kwargs):
        if offset := kwargs.get('offset'):
            dt = datetime.now(timezone.utc) + timedelta(seconds=offset)
        elif type(args[0]) is datetime:
            dt = args[0]
        else:
            dt = datetime(*args, **kwargs)

        self = super().__new__(
            cls,
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=dt.hour,
            minute=dt.minute,
            second=dt.second,
            microsecond=dt.microsecond,
            tzinfo=dt.tzinfo,
            fold=dt.fold
        )
        self.dt = dt

        return self

    def __init__(self, *args, **kwargs):
        super().__init__()

    def time_repr(self) -> str:
        """Returns time in 'HH:MM' format"""
        return self.dt.strftime('%H:%M')

    def date_repr(self, style_flag: None | bool = None, custom_separator: str = None) -> str:
        """Returns date in 'YYYY-MM-DD' format"""

        if custom_separator:
            resp = self.dt.strftime(f'%d{custom_separator}%m{custom_separator}%Y')
        else:
            if style_flag:
                resp = self.dt.strftime('%d.%m.%Y')
            else:
                resp = self.dt.strftime('%Y-%m-%d')
        return resp

    def time_date_repr(self) -> str:
        """Returns time and date in 'HH:MM YYYY/MM/DD' format"""
        return self.dt.strftime('%H:%M %d/%m/%Y')

    @property
    def tomorrow(self):
        """Returns UserTime object for the next day"""
        return UserTime(self.dt + timedelta(days=1))

    @property
    def yesterday(self):
        """Returns UserTime object for the previous day"""
        return UserTime(self.dt - timedelta(days=1))

    @property
    def next_day_flag(self) -> bool:
        """Check if evening and soon will be new day"""
        return True if self.dt.hour in range(20, 24) else False

    @classmethod
    def from_epoch(cls, epoch: int, offset: int | None = None):
        """Converts epoch time repr to UserTime obj with offset"""
        offset = 0 if not offset else offset
        return cls(datetime.utcfromtimestamp(epoch + offset))

    @staticmethod
    def get_time_from_offset(offset: int) -> dict:
        """Return basic datetime objects from offset."""
        dt = datetime.now(timezone.utc) + timedelta(seconds=offset)
        time = dt.strftime('%H:%M')
        date = dt.strftime('%Y-%m-%d')
        date_time = dt.strftime('%H:%M %d-%m-%Y')
        tomorrow_dt = dt + timedelta(days=1)
        tomorrow = tomorrow_dt.strftime('%Y-%m-%d')
        yesterday = UserTime(dt)

        return {
            'time': time,
            'date': date,
            'date_time': date_time,
            'dt': dt,
            'tomorrow': tomorrow,
            'yesterday': yesterday
        }

    @staticmethod
    def format_unix_time(time_unix: int, time_offset: int) -> str:
        """Format unix time to human-readable (HH:MM) format"""
        dt = datetime.utcfromtimestamp(time_unix + time_offset)
        return dt.strftime('%H:%M')

    @staticmethod
    def offset_repr(timezone_offset: int | str) -> str:
        """Format timezone offset to sign-digit('+/d') format"""
        timezone_offset = int(int(timezone_offset) / 3600)
        return f'{timezone_offset:+d}'


def parse_action_time(time_str: str) -> time | None:
    time_formats = ['%H:%M', '%H %M', '%I:%M', '%I %M']

    for time_format in time_formats:
        try:
            return datetime.strptime(time_str, time_format).time()
        except ValueError:
            pass

    return
