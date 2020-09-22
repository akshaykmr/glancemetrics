from datetime import datetime, tzinfo, timedelta, timezone
import re


def parse_tz_offset(offset: str) -> tzinfo:
    """convert str offsets like 0530 and -0700 to tzinfo"""
    sign, hours, minutes = re.match("([+\-]?)(\d{2})(\d{2})", offset).groups()
    sign = -1 if sign == "-" else 1
    hours, minutes = int(hours), int(minutes)
    return timezone(sign * timedelta(hours=hours, minutes=minutes))


def current_time() -> datetime:
    """tz aware current time"""
    return datetime.now(timezone.utc)


def seconds_interval(d: datetime) -> datetime:
    """new dto with seconds floored, used to identify interval"""
    return d.replace(microsecond=0)
