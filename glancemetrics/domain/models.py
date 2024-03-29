from dataclasses import dataclass, field
from itertools import dropwhile
from typing import Optional, List
from datetime import datetime, timedelta
from glancemetrics.utils.datetime import parse_tz_offset, seconds_interval
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
            method=method.upper(),
            path=path.lower(),
            status_code=int(log_dict["s"]),
            content_size=int(log_dict["b"]),
            identity=None if identity == "-" else identity,
            user_id=None if user_id == "-" else user_id,
        )

    @property
    def section(self) -> str:
        bread_crumbs = [c for c in self.path.split("/") if c]
        return f"/{bread_crumbs[0]}" if bread_crumbs else "/"

    @property
    def is_error(self) -> bool:
        return self.is_client_error or self.is_server_error

    @property
    def is_client_error(self) -> bool:
        return 400 <= self.status_code < 500

    @property
    def is_server_error(self) -> bool:
        return 500 <= self.status_code < 600


@dataclass
class LogBucket:
    """logs captured in a 1-second interval."""

    time: datetime  # time + 1 second interval
    logs: List[LogRecord] = field(default_factory=list)

    def __post_init__(self):
        # the grouping is per second
        assert self.time.microsecond == 0

    def add(self, log: LogRecord):
        # floors microsecond, note: replace returns new datetime, doesn't modify original
        log_interval = seconds_interval(log.time)
        if log_interval != self.time:
            raise AssertionError("adding log in inappropriate bucket")
        self.logs.append(log)

    @classmethod
    def from_initial_log(cls, log: LogRecord) -> "LogBucket":
        bucket = cls(time=seconds_interval(log.time))
        bucket.add(log)
        return bucket


@dataclass
class LogSeries:
    """histogram like grouping of logs with time, using 1-second intervals
    eg.
        if start-time was 1:00:00
        buckets[0] would be the logs captured in 1:00:00 - 1:00:01 interval
        buckets[1] would be the logs captured in 1:00:01 - 1:00:02 interval
    """

    buckets: List[LogBucket] = field(default_factory=list)

    @property
    def start_time(self) -> Optional[datetime]:
        if self.buckets:
            return self.buckets[0].time

    @property
    def end_time(self) -> Optional[datetime]:
        if self.buckets:
            return self.buckets[-1].time

    def append(self, log_bucket: LogBucket) -> "LogBucket":
        if not self.start_time:
            self.buckets.append(log_bucket)
            return

        previous_bucket = self.buckets[-1]
        time_diff = log_bucket.time - previous_bucket.time
        if time_diff <= timedelta(seconds=0):
            raise Exception("invalid continuation log-bucket for series")

        # pad empty buckets till time diff = 1 second
        self.buckets += [
            LogBucket(time=previous_bucket.time + timedelta(seconds=s + 1))
            for s in range(int(time_diff.total_seconds()) - 1)
        ]

        previous_bucket = self.buckets[-1]
        assert log_bucket.time - previous_bucket.time == timedelta(seconds=1)
        self.buckets.append(log_bucket)

    def trim(self, from_time: datetime):
        """
        trims series buckets where time > from time
        a consumer may use trim to let old logs that are not needed to get garbage collected
        """
        # series is already sorted
        self.buckets = list(dropwhile(lambda b: b.time < from_time, self.buckets))
