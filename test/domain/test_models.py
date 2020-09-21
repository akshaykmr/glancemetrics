from glancemetrics.domain.models import LogRecord
from datetime import datetime, timezone, timedelta


class TestLogRecordFromCLF:
    def test_simple_log(self):
        log = '127.0.0.1 - james [09/May/2018:16:00:39 +0000] "GET /report HTTP/1.0" 200 123'
        record = LogRecord.from_common_log_format(log)
        assert record == LogRecord(
            ip="127.0.0.1",
            time=datetime(2018, 5, 9, 16, 0, 39, tzinfo=timezone.utc),
            method="GET",
            path="/report",
            status_code=200,
            content_size=123,
            identity=None,
            user_id="james",
        )

    def test_log_with_tz_offset(self):
        log = '10.223.157.186 - - [15/Jul/2009:14:58:59 -0700] "GET /favicon.ico HTTP/1.1" 404 209'
        record = LogRecord.from_common_log_format(log)
        assert record == LogRecord(
            ip="10.223.157.186",
            time=datetime(
                2009,
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
        )


def test_log_record_section():
    log = '10.223.157.186 - - [15/Jul/2009:14:58:59 -0700] "GET /pages/foo HTTP/1.1" 404 209'
    record = LogRecord.from_common_log_format(log)
    assert record.section == "pages"