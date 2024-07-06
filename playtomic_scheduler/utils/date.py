# Native imports
from zoneinfo import ZoneInfo
from datetime import datetime

# 3rd party imports
import pytz
import tzlocal


def get_local_timezone():
    """
    Get system's local timezone.
    """
    return tzlocal.get_localzone_name()


def set_start_of_day(date: datetime):
    """
    Set the start of the day for the provided date.
    """
    return date.replace(hour=0, minute=0, second=0, microsecond=0)


def set_end_of_day(date: datetime):
    """
    Set the end of the day for the provided date.
    """
    return date.replace(hour=23, minute=59, second=59, microsecond=999999)


def parse_datetime(hour: str, baseline: datetime):
    """
    Parse the provided hours to a datetime object in UTC.
    """
    time_parts = hour.split(":")
    if len(time_parts) < 2:
        raise ValueError(
            "Invalid time format. Please provide time in HH:MM | HH:MM:SS format."
        )

    hour, minutes = time_parts[0], time_parts[1]

    seconds = 0
    if len(time_parts) > 2:
        seconds = time_parts[2]

    return baseline.replace(
        hour=int(hour), minute=int(minutes), second=int(seconds), microsecond=0
    )


def parse_utc_to_local(utc_date: datetime):
    """
    Parse the provided UTC date string to local timezone.
    """
    utc_date = utc_date.replace(tzinfo=pytz.UTC)
    local_timezone = get_local_timezone()
    return utc_date.astimezone(pytz.timezone(local_timezone))
