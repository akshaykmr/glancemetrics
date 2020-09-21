from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from glancemetrics.utils.datetime import parse_tz_offset
from clfparser import CLFParser


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
        log_dict = CLFParser.logDict(log)
        # convert this parsers dict to our interface
        method, path, *misc = log_dict["r"].strip('"').split(" ")
        identity = log_dict["l"]
        user_id = log_dict["u"]
        time: datetime = log_dict["time"]
        tz = parse_tz_offset(log_dict["timezone"])
        return cls(
            ip=log_dict["h"],
            time=time.replace(tzinfo=tz),
            method=method,
            path=path,
            status_code=int(log_dict["s"]),
            content_size=int(log_dict["b"]),
            identity=None if identity == "-" else identity,
            user_id=None if user_id == "-" else user_id,
        )

    @property
    def section(self) -> str:
        bread_crumbs = [c for c in self.path.split("/") if c]
        return bread_crumbs[0] if bread_crumbs else "/"
