from random import choice, randint
from datetime import timedelta, datetime
from typing import List

from glancemetrics.domain.models import LogRecord
from glancemetrics.utils.datetime import current_time


def random_ip():
    ips = [
        "60.147.141.19",
        "60.147.141.19",
        "43.2.214.24",
        "26.88.193.28",
        "200.255.24.100",
        "5.76.99.64",
        "225.254.122.42",
        "229.137.91.145",
        "130.206.72.64",
        "82.65.216.216",
        "216.219.66.127",
        "22.156.169.65",
        "141.71.138.218",
        "200.137.223.25",
    ]
    return choice(ips)


def random_method():
    methods = ["GET", "PUT", "POST", "DELETE", "HEAD"]
    return choice(methods)


def random_path():
    paths = ["/", "/doggo" "/pupper", "/api/hello", "/api/blah", "/doge", "/wow"]
    return choice(paths)


def random_time():
    return current_time() - timedelta(seconds=randint(0, 100))


def random_status():
    status = [
        200,
        201,
        202,
        400,
        404,
        500,
        501,
        503,
        301,
        303,
        300,
        100,
        101,
        406,
        418,  # teapot is very important
    ]
    return choice(status)


def log_record_dm(
    ip=None,
    time=None,
    method=None,
    path=None,
    status_code=None,
    content_size=None,
    identity=None,
    user_id=None,
) -> LogRecord:
    return LogRecord(
        ip=ip or random_ip(),
        time=time or random_time(),
        method=method or random_method(),
        path=path or random_path(),
        status_code=status_code or random_status(),
        content_size=randint(500, 1500) if content_size is None else content_size,
        identity=identity,
        user_id=user_id,
    )


def random_user_id():
    ids = [
        "-",  # none
        "mojo",
        "john",
        "akshay",
        "datadoggo",
    ]
    return choice(ids)


def fake_log_str(
    ip=None,
    time=None,
    method=None,
    path=None,
    status_code=None,
    content_size=None,
    identity=None,
    user_id=None,
):
    time_tag = datetime.strftime(time or random_time(), "[%d/%b/%Y:%H:%M:%S %z]")
    content_size = randint(500, 1500) if content_size is None else content_size
    user_id = random_user_id() if user_id is None else "-"
    return f"""{ip or random_ip()} {identity or '-'} {user_id} {time_tag} "{method or random_method()} {path or random_path()} HTTP/1.1" {status_code or random_status()} {content_size}"""


class FakeFile:
    """fake file interface that implements basic readline and append"""

    def __init__(self, lines: List[str]):
        self.lines = lines or []
        self.read_lines = 0

    def readline(self):
        if self.read_lines == len(self.lines):
            return None
        line = self.lines[self.read_lines]
        self.read_lines += 1
        return line

    # only for test purposes
    def append(self, log: str):
        self.lines.append(log)

    # only for test purposes
    def append_logs(self, logs: List[str]):
        self.lines += logs
