from typing import List
from glancemetrics.domain.models import LogSeries
from glancemetrics.watchdogs.log import logwatcher

from .factories import FakeFile


def logs_to_series(logs: List[str]) -> LogSeries:
    series = LogSeries()
    if not logs:
        return series
    fake_file = FakeFile(logs)
    for bucket in logwatcher(fake_file):
        if bucket is None:
            return series
        series.append(bucket)
