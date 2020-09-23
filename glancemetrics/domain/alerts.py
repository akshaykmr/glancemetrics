from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta

from glancemetrics.domain.models import LogSeries, LogBucket
from glancemetrics.domain.insights import hit_rate, total_hits
from glancemetrics.utils.datetime import current_time


# TODO: can use interfaces/ABC for different types of alerts
# i.e. not just high-traffic alerts


@dataclass
class Incident:
    # hit-rate when breach occurred
    breach_hitrate: int

    # max-rate during incident interval
    max_hitrate: int
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
    monitors high traffic scenario for a time interval
    say, past 2 minutes
    """

    def __init__(self, threshold: int, window: timedelta):
        self.threshold = threshold  # in req/s

        if window < timedelta(seconds=1):
            raise ValueError("interval must be atleast 1 second")
        self._window = window

        # TODO: can use a metric-series, to just keep series of hit-rate instead
        # this can improve memory usage for very high log throughput.
        self._series: LogSeries = LogSeries()

        self.incidents: List[Incident] = []

    def ingest(self, bucket: LogBucket):
        if bucket.time < self._limit:
            return
        self._trim_series()
        self._series.append(bucket)
        self.refresh()

    def refresh(self):
        self._trim_series()
        hits = hit_rate(total_hits(self._series), self._window)
        active_incident = self.active_incident
        if hits < self.threshold:
            if active_incident:
                active_incident.recovered_at = current_time()
            return

        # ongoing incident
        if active_incident is not None:
            active_incident.max_hitrate = max(active_incident.max_hitrate, hits)
            return

        # new incident
        incident = Incident(
            breach_hitrate=hits, max_hitrate=hits, triggered_at=current_time(),
        )
        self.incidents.append(incident)

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
