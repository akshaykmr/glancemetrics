import datetime
import re


def parse_tz_offset(offset: str) -> datetime.tzinfo:
    """convert str offsets like 0530 and -0700 to tzinfo"""
    sign, hours, minutes = re.match("([+\-]?)(\d{2})(\d{2})", offset).groups()
    sign = -1 if sign == "-" else 1
    hours, minutes = int(hours), int(minutes)
    return datetime.timezone(sign * datetime.timedelta(hours=hours, minutes=minutes))
