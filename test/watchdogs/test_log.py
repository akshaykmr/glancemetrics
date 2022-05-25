from datetime import datetime, timezone, timedelta
from glancemetrics.watchdogs.log import logwatcher
from glancemetrics.domain.models import LogBucket, LogRecord
from glancemetrics.utils.datetime import current_time

from test.factories import FakeFile, fake_log_str


def test_it_yields_log_buckets_correctly():
    logs = [
        '10.223.157.186 - - [15/Jul/2020:14:58:59 +0000] "GET /favicon.ico HTTP/1.1" 404 209',
        '11.22.157.186 - - [15/Jul/2020:14:58:59 +0000] "GET /api/pup HTTP/1.1" 200 154',
        '10.223.157.186 - - [15/Jul/2020:14:59:59 +0000] "GET /blah/central HTTP/1.1" 200 92',
        '10.223.157.186 - - [15/Jul/2020:15:23:11 +0000] "GET /doge HTTP/1.1" 200 1123',
        '11.22.157.186 - - [15/Jul/2020:15:23:11 +0000] "GET /power HTTP/1.1" 200 154',
    ]

    fake_file = FakeFile(logs)
    watcher = logwatcher(fake_file)
    buckets = [next(watcher) for i in range(5)]
    assert buckets[0] == LogBucket(
        time=datetime(
            2020,
            7,
            15,
            14,
            58,
            59,
            tzinfo=timezone.utc,
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
                    tzinfo=timezone.utc,
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
                    tzinfo=timezone.utc,
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
            2020,
            7,
            15,
            14,
            59,
            59,
            tzinfo=timezone.utc,
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
                    tzinfo=timezone.utc,
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
            2020,
            7,
            15,
            15,
            23,
            11,
            tzinfo=timezone.utc,
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
                    tzinfo=timezone.utc,
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
                    tzinfo=timezone.utc,
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

    # if we write to file, new buckets can be generated
    fake_file.append(
        '11.22.157.186 - - [15/Jul/2020:15:23:12 +0000] "GET /tailing_swiftly HTTP/1.1" 200 154'
    )
    assert next(watcher) == LogBucket(
        time=datetime(
            2020,
            7,
            15,
            15,
            23,
            12,
            tzinfo=timezone.utc,
        ),
        logs=[
            LogRecord(
                ip="11.22.157.186",
                time=datetime(
                    2020,
                    7,
                    15,
                    15,
                    23,
                    12,
                    tzinfo=timezone.utc,
                ),
                method="GET",
                path="/tailing_swiftly",
                status_code=200,
                content_size=154,
                identity=None,
                user_id=None,
            )
        ],
    )
    assert next(watcher) is None

    # append a log to greater than current time
    # to test it waits for the bucket to complete before yielding it
    log = fake_log_str(time=current_time() + timedelta(seconds=1))
    fake_file.append(log)
    assert next(watcher) is None
