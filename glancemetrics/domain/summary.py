from datetime import timedelta
from typing import Tuple, List
from glancemetrics.domain.models import LogBucket, LogSeries
from glancemetrics.domain.insights import Insights, top_sections, SectionLogs
from glancemetrics.utils.datetime import current_time


class InsightsSummary:
    """
    ingests stream of logs and provides insights for a a time interval
    say, past 10 seconds if window = 10 seconds
    """

    def __init__(self, window: timedelta):
        if window < timedelta(seconds=1):
            raise ValueError("interval must be atleast 1 second")
        self._window = timedelta
        self._series: LogSeries = LogSeries()

    def ingest(self, log: LogBucket):
        # todo: trim the series for window
        if log.time < current_time() + self._window:
            return
        self.series.append(log)

    @property
    def insights(
        self, top_section_limit: int = 10
    ) -> Tuple[Insights, List[SectionLogs]]:
        # todo: trim the series for window
        return (
            Insights.from_log_series(self._series),
            top_sections(self._series, limit=top_section_limit),
        )
