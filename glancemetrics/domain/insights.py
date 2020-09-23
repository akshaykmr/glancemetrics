from typing import List
from dataclasses import dataclass
from datetime import timedelta
from glancemetrics.domain.models import LogSeries, LogRecord
from glancemetrics.utils import group_by
from itertools import chain


def hit_rate(hits: int, window: timedelta) -> float:
    """avg. hit rate in reqs/s"""
    seconds = int(window.total_seconds())
    if seconds < 1:
        raise ValueError("invalid window size")
    return round(hits / seconds, 1)


def total_hits(series: LogSeries) -> int:
    return sum([len(bucket.logs) for bucket in series.buckets])


@dataclass
class Insights:
    """ metrics report for a time-window """

    hits: int
    bytes_transferred: int
    known_users: int
    error_count: int
    client_errors: int
    server_errors: int

    @property
    def error_percentage(self):
        if not self.hits:
            return 0
        return (self.error_count / self.hits) * 100

    @classmethod
    def from_log_series(cls, series: LogSeries) -> "Insights":
        all_logs: List[LogRecord] = list(
            chain.from_iterable([bucket.logs for bucket in series.buckets])
        )
        error_logs = [log for log in all_logs if log.is_error]
        client_errors = [log for log in error_logs if log.is_client_error]
        server_errors = [log for log in error_logs if log.is_server_error]
        total_bytes = sum([log.content_size for log in all_logs])
        return cls(
            hits=len(all_logs),
            bytes_transferred=total_bytes,
            known_users=len({log.user_id for log in all_logs if log.user_id}),
            error_count=len(error_logs),
            client_errors=len(client_errors),
            server_errors=len(server_errors),
        )


@dataclass
class SectionLogs:
    """ logs pertaining to a section """

    name: str
    logs: List[LogRecord]

    @property
    def hits(self) -> int:
        return len(self.logs)


def _group_by_section(series: LogSeries) -> List[SectionLogs]:
    all_logs: List[LogRecord] = list(
        chain.from_iterable([bucket.logs for bucket in series.buckets])
    )
    return [
        SectionLogs(name=section, logs=logs)
        for section, logs in group_by(all_logs, key=lambda log: log.section).items()
    ]


def _sorted_sections(section_logs: List[SectionLogs]) -> List[SectionLogs]:
    """sort by number of hits"""
    return sorted(
        section_logs, key=lambda section_insights: section_insights.hits, reverse=True
    )


def top_sections(series: LogSeries, limit: int = 10) -> List[SectionLogs]:
    """top hits sections"""
    section_logs = _group_by_section(series)
    return _sorted_sections(section_logs)[:limit]
