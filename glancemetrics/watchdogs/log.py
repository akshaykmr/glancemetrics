from pathlib import Path
from typing import Generator, Optional
from time import sleep
from datetime import timedelta

from glancemetrics.utils.datetime import current_time, seconds_interval
from glancemetrics.domain.models import LogRecord, LogBucket


def _needs_new_bucket(log: LogRecord, current_bucket: LogBucket) -> bool:
    return seconds_interval(log.time) != current_bucket.time


def _bucket_complete(bucket: LogBucket) -> bool:
    return current_time() - bucket.time > timedelta(seconds=1)


def _validate_file_path(filepath: str) -> Path:
    path = Path(filepath).resolve()
    assert path.exists()
    return path


def logwatcher(log_file) -> Generator[Optional[LogBucket], None, None]:
    """yields bucket of logs (groups of 1-second interval)"""
    current_bucket = None
    while True:
        line = log_file.readline()
        if not line:
            # no new logs
            if current_bucket and _bucket_complete(current_bucket):
                yield current_bucket
                current_bucket = None
                continue
            else:
                yield None
                sleep(0.2)
                continue

        log = LogRecord.from_common_log_format(line)
        assert log.time <= current_time()

        if current_bucket and _needs_new_bucket(log, current_bucket):
            yield current_bucket
            current_bucket = None

        if current_bucket is None:
            current_bucket = LogBucket(time=seconds_interval(log.time))

        current_bucket.add(log)


if __name__ == "__main__":
    # experiment zone
    file_path = "logs.txt"
    path = _validate_file_path(file_path)
    with open(str(path), "r") as log_file:
        watcher = logwatcher(log_file)
        limit = 5
        count = 0
        for bucket in watcher:
            if count > limit:
                break
            print(bucket)
            print("\n\n")
            count += 1
