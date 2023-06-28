from django.utils import timezone


class DateTimeFormatter:
    @staticmethod
    def future_date(years=10) -> timezone.datetime:
        return timezone.datetime(timezone.now().year + years, 1, 1, 0, 0)

    @staticmethod
    def past_date(years=10) -> timezone.datetime:
        return timezone.datetime(timezone.now().year - years, 1, 1, 0, 0)

    @staticmethod
    def datetime_timezone_str(datetime: timezone.datetime) -> str:
        datetime = datetime.astimezone(
            timezone.get_current_timezone()
        ).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
        return f'{datetime[:-2]}:{datetime[-2:]}'
