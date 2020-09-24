from datetime import timedelta
from typing import List, Iterator, Optional, Tuple

from glancemetrics.domain.models import LogBucket
from glancemetrics.domain.insights import Insights, SectionLogs
from glancemetrics.domain.summary import InsightsSummary
from glancemetrics.domain.alerts import Alert

from glancemetrics.utils.datetime import current_time


class GlanceMetrics:
    def __init__(
        self,
        log_stream: Iterator[Optional[LogBucket]],
        insights_window: timedelta = timedelta(seconds=10),
        alerts=None,
    ):
        self.alerts: List[Alert] = alerts or []

        self._log_stream = log_stream
        self._insights_view = InsightsSummary(window=insights_window)

        # holds any callables interested in stream of logs. eg: insights, alerts!
        self._log_ingestors = [
            self._insights_view.ingest,
            *[alert.ingest for alert in self.alerts],
        ]

    def refresh(self):
        """update self with latest metrics from logs"""
        # ingest log stream till None
        # or log time exceeds refresh-tick (logs may keep on coming)
        refresh_tick = current_time()
        while True:
            bucket = next(self._log_stream)
            if bucket is None:
                for alert in self.alerts:
                    # can't ingore alerts update if no new logs
                    alert.refresh()
                return
            for ingestor in self._log_ingestors:
                ingestor(bucket)
            if bucket.time > refresh_tick:
                return

    def insights(
        self, top_sections_limit: int = 10
    ) -> Tuple[Insights, List[SectionLogs]]:
        return self._insights_view.get_insights(top_sections_limit=top_sections_limit)
