from pathlib import Path
from time import sleep
from glancemetrics.utils.datetime import current_time, seconds_interval
from glancemetrics.domain.models import LogRecord, LogBucket


def _needs_new_bucket(log: LogRecord, current_bucket: LogBucket) -> bool:
    return seconds_interval(log.time) != current_bucket.time


def logwatcher(filepath: str):
    """yields bucket of logs (groups of 1-second interval)"""
    path = Path(filepath).resolve()
    assert path.exists()
    current_bucket = None
    with open(str(path), "r") as log_file:
        while True:
            line = log_file.readline()
            if not line:
                # no new logs
                yield None
                sleep(0.2)
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
    watcher = logwatcher(file_path)
    limit = 10
    count = 0
    for bucket in watcher:
        if count > limit:
            break
        print(bucket)
        print("\n\n")
        count += 1
