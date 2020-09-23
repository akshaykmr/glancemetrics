from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta

from glancemetrics.domain.models import LogSeries, LogBucket
from glancemetrics.utils.datetime import current_time


@dataclass
class Incident:
    hits: int
    triggered_at: datetime
    recovered_at: Optional[datetime] = None

    @property
    def active(self) -> bool:
        return self.recovered_at is None

    @property
    def duration(self) -> timedelta:
        till = self.recovered_at if self.active else current_time()
        return till - self.recovered_at


class Alert:
    """
    monitors high traffic scenario for a a time interval
    say, past 2 minutes

    # TODO: this class can be abstracted for different types of alerts
    # i.e. not just high-traffic alerts
    """

    def __init__(self, window: timedelta):
        if window < timedelta(seconds=1):
            raise ValueError("interval must be atleast 1 second")

        self._window = window
        self._series: LogSeries = LogSeries()

        self.incidents: List[Incident] = []

    def ingest(self, bucket: LogBucket):
        if bucket.time < self._limit:
            return
        self._trim_series()
        self._series.append(bucket)
        # TODO: trigger / recover alert

    @property
    def is_blaring(self) -> bool:
        return self.active_incident is not None

    @property
    def latest_incident(self) -> Optional[Incident]:
        return self.incidents[-1] if self.incidents else None

    @property
    def active_incident(self) -> Optional[Incident]:
        if self.latest_incident is None:
            return None
        return self.latest_incident if self.latest_incident.active else None

    @property
    def _limit(self) -> datetime:
        return current_time() - self._window

    def _trim_series(self):
        self._series.trim(from_time=self._limit)
