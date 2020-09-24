from typing import Iterator, Optional
from datetime import timedelta

from glancemetrics.utils.datetime import current_time, seconds_interval
from glancemetrics.domain.models import LogRecord, LogBucket


def _needs_new_bucket(log: LogRecord, current_bucket: LogBucket) -> bool:
    return seconds_interval(log.time) != current_bucket.time


def _bucket_complete(bucket: LogBucket) -> bool:
    return current_time() - bucket.time > timedelta(seconds=1)


def logwatcher(log_file) -> Iterator[Optional[LogBucket]]:
    """
    yields bucket of logs (groups of 1-second interval)
    """
    current_bucket = None
    while True:
        line = log_file.readline()
        if not line:
            # no new logs
            if current_bucket and _bucket_complete(current_bucket):
                yield current_bucket
                current_bucket = None
            else:
                yield None
            continue

        log = LogRecord.from_common_log_format(line)

        if current_bucket and _needs_new_bucket(log, current_bucket):
            yield current_bucket
            current_bucket = None

        if current_bucket is None:
            current_bucket = LogBucket(time=seconds_interval(log.time))

        current_bucket.add(log)
