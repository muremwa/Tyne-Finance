from typing import Any
from datetime import date, datetime

from django.utils import timezone


class DateTimeFormatter:
    @staticmethod
    def future_date(years=10) -> datetime:
        return timezone.datetime(timezone.now().year + years, 1, 1, 0, 0)

    @staticmethod
    def past_date(years=10) -> datetime:
        return timezone.datetime(timezone.now().year - years, 1, 1, 0, 0)

    @staticmethod
    def datetime_timezone_str(dt: datetime) -> str:
        dt = dt.astimezone(
            timezone.get_current_timezone()
        ).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
        return f'{dt[:-2]}:{dt[-2:]}'

    @staticmethod
    def make_date(value: Any) -> date:
        if type(value) == datetime:
            return value.date()

        elif type(value) == date:
            return value

        elif type(value) == str:
            return datetime.strptime(value, "%Y-%m-%d").date()

        else:
            raise TypeError('Enter a valid type')
