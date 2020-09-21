import datetime
import re


def parse_tz_offset(offset_str) -> datetime.tzinfo:
    sign, hours, minutes = re.match("([+\-]?)(\d{2})(\d{2})", offset_str).groups()
    sign = -1 if sign == "-" else 1
    hours, minutes = int(hours), int(minutes)
    return datetime.timezone(sign * datetime.timedelta(hours=hours, minutes=minutes))
