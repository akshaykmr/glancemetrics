from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class LogRecord:
    ip: str
    time: datetime
    method: str  # there can be custom HTTP methods as well
    path: str
    status_code: int
    content_size: int  # in bytes
    identity: Optional[str]
    user_id: Optional[str]

    @classmethod
    def from_common_log_format(cls, log: str) -> "LogRecord":
        raise NotImplementedError
