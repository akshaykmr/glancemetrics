from typing import List
from dataclasses import dataclass
from glancemetrics.domain.models import LogSeries, LogRecord
from glancemetrics.utils import group_by
from itertools import chain


@dataclass
class SectionLogs:
    name: str
    logs: List[LogRecord]

    @property
    def hits(self) -> int:
        return len(self.logs)


def group_by_section(series: LogSeries) -> List[SectionLogs]:
    all_logs: List[LogRecord] = list(
        chain.from_iterable([bucket.logs for bucket in series.buckets])
    )
    return [
        SectionLogs(
            name=section,
            logs=logs
        )
        for section, logs in group_by(all_logs, key=lambda log: log.section).items()
    ]


def sorted_sections(section_logs: List[SectionLogs]) -> List[SectionLogs]:
    return sorted(section_logs, key=lambda section_insights: section_insights.hits, reverse=True)


def top_sections(series: LogSeries, limit: int = 10) -> List[SectionLogs]:
    section_logs = group_by_section(series)
    return sorted_sections(section_logs)[:limit]
