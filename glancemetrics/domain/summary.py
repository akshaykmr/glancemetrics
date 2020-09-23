from datetime import timedelta, datetime
from typing import Tuple, List
from glancemetrics.domain.models import LogBucket, LogSeries
from glancemetrics.domain.insights import Insights, top_sections, SectionLogs
from glancemetrics.utils.datetime import current_time


class InsightsSummary:
    """
    ingests stream of logbuckets and provides insights for a a time interval
    say, past 10 seconds if window = 10 seconds
    """

    def __init__(self, window: timedelta):
        if window < timedelta(seconds=1):
            raise ValueError("interval must be atleast 1 second")
        self._window = window
        self._series: LogSeries = LogSeries()

    @property
    def _limit(self) -> datetime:
        return current_time() - self._window

    def ingest(self, bucket: LogBucket):
        if bucket.time < self._limit:
            return
        self._trim_series()
        self.series.append(bucket)

    @property
    def insights(
        self, top_section_limit: int = 10
    ) -> Tuple[Insights, List[SectionLogs]]:
        self._trim_series()
        return (
            Insights.from_log_series(self._series),
            top_sections(self._series, limit=top_section_limit),
        )

    def _trim_series(self):
        self._series.trim(from_time=self._limit)
