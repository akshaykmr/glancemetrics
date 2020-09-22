from typing import List
from datetime import datetime, timedelta, timezone
from glancemetrics.watchdogs.log import logwatcher
from glancemetrics.domain.models import LogBucket, LogRecord


class FakeFile:
    """fake file interface that implements basic readline"""

    def __init__(self, lines: List[str]):
        self.lines = lines
        self.read_lines = 0

    def readline(self):
        if self.read_lines == len(self.lines):
            return None
        line = self.lines[self.read_lines]
        self.read_lines += 1
        return line


def test_it_yields_log_buckets_correctly():
    logs = [
        '10.223.157.186 - - [15/Jul/2020:14:58:59 -0700] "GET /favicon.ico HTTP/1.1" 404 209',
        '11.22.157.186 - - [15/Jul/2020:14:58:59 -0700] "GET /api/pup HTTP/1.1" 200 154',
        '10.223.157.186 - - [15/Jul/2020:14:59:59 -0700] "GET /blah/central HTTP/1.1" 200 92',
        '10.223.157.186 - - [15/Jul/2020:15:23:11 -0700] "GET /doge HTTP/1.1" 200 1123',
        '11.22.157.186 - - [15/Jul/2020:15:23:11 -0700] "GET /power HTTP/1.1" 200 154',
    ]

    fake_file = FakeFile(logs)
    watcher = logwatcher(fake_file)
    buckets = [next(watcher) for i in range(5)]
    assert buckets[0] == LogBucket(
        time=datetime(
            2020, 7, 15, 14, 58, 59, tzinfo=timezone(timedelta(days=-1, seconds=61200)),
        ),
        logs=[
            LogRecord(
                ip="10.223.157.186",
                time=datetime(
                    2020,
                    7,
                    15,
                    14,
                    58,
                    59,
                    tzinfo=timezone(timedelta(days=-1, seconds=61200)),
                ),
                method="GET",
                path="/favicon.ico",
                status_code=404,
                content_size=209,
                identity=None,
                user_id=None,
            ),
            LogRecord(
                ip="11.22.157.186",
                time=datetime(
                    2020,
                    7,
                    15,
                    14,
                    58,
                    59,
                    tzinfo=timezone(timedelta(days=-1, seconds=61200)),
                ),
                method="GET",
                path="/api/pup",
                status_code=200,
                content_size=154,
                identity=None,
                user_id=None,
            ),
        ],
    )
    assert buckets[1] == LogBucket(
        time=datetime(
            2020, 7, 15, 14, 59, 59, tzinfo=timezone(timedelta(days=-1, seconds=61200)),
        ),
        logs=[
            LogRecord(
                ip="10.223.157.186",
                time=datetime(
                    2020,
                    7,
                    15,
                    14,
                    59,
                    59,
                    tzinfo=timezone(timedelta(days=-1, seconds=61200)),
                ),
                method="GET",
                path="/blah/central",
                status_code=200,
                content_size=92,
                identity=None,
                user_id=None,
            )
        ],
    )

    assert buckets[2] == LogBucket(
        time=datetime(
            2020, 7, 15, 15, 23, 11, tzinfo=timezone(timedelta(days=-1, seconds=61200)),
        ),
        logs=[
            LogRecord(
                ip="10.223.157.186",
                time=datetime(
                    2020,
                    7,
                    15,
                    15,
                    23,
                    11,
                    tzinfo=timezone(timedelta(days=-1, seconds=61200)),
                ),
                method="GET",
                path="/doge",
                status_code=200,
                content_size=1123,
                identity=None,
                user_id=None,
            ),
            LogRecord(
                ip="11.22.157.186",
                time=datetime(
                    2020,
                    7,
                    15,
                    15,
                    23,
                    11,
                    tzinfo=timezone(timedelta(days=-1, seconds=61200)),
                ),
                method="GET",
                path="/power",
                status_code=200,
                content_size=154,
                identity=None,
                user_id=None,
            ),
        ],
    )

    assert buckets[3] is None
    assert buckets[4] is None
