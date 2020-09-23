from datetime import datetime, timezone, timedelta
import pytest

from glancemetrics.domain.models import LogRecord, LogBucket, LogSeries

from test.factories import log_record_dm


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


def test_log_bucket_throws_error_if_adding_log_from_another_interval():
    bucket = LogBucket(time=datetime(2018, 5, 9, 16, 0, 39, tzinfo=timezone.utc))
    bucket.add(log_record_dm(time=datetime(2018, 5, 9, 16, 0, 39, tzinfo=timezone.utc)))

    with pytest.raises(AssertionError):
        # next second
        bucket.add(
            log_record_dm(time=datetime(2018, 5, 9, 16, 0, 40, tzinfo=timezone.utc))
        )


class TestLogSeries:
    def test_log_series_append_bucket_works_for_future_intervals_by_padding(self):
        series = LogSeries()

        bucket_1 = LogBucket(time=datetime(2018, 5, 9, 16, 0, 39, tzinfo=timezone.utc))
        bucket_1.add(
            log_record_dm(time=datetime(2018, 5, 9, 16, 0, 39, tzinfo=timezone.utc))
        )
        bucket_1.add(
            log_record_dm(time=datetime(2018, 5, 9, 16, 0, 39, tzinfo=timezone.utc))
        )

        bucket_2 = LogBucket(time=datetime(2018, 5, 9, 16, 0, 40, tzinfo=timezone.utc))
        bucket_3 = LogBucket(time=datetime(2018, 5, 9, 16, 0, 43, tzinfo=timezone.utc))

        series.append(bucket_1)
        series.append(bucket_2)
        series.append(bucket_3)

        assert series.buckets == [
            bucket_1,
            bucket_2,
            LogBucket(time=datetime(2018, 5, 9, 16, 0, 41, tzinfo=timezone.utc)),
            LogBucket(time=datetime(2018, 5, 9, 16, 0, 42, tzinfo=timezone.utc)),
            bucket_3,
        ]

    def test_appending_past_bucket_to_series_raises_exception(self):
        series = LogSeries()

        bucket_1 = LogBucket(time=datetime(2018, 5, 9, 16, 0, 39, tzinfo=timezone.utc))
        bucket_1.add(
            log_record_dm(time=datetime(2018, 5, 9, 16, 0, 39, tzinfo=timezone.utc))
        )

        bucket_2 = LogBucket(time=datetime(2018, 5, 9, 16, 0, 38, tzinfo=timezone.utc))

        series.append(bucket_1)
        with pytest.raises(Exception):
            series.append(bucket_2)

    def test_trimming_series(self):
        series = LogSeries()

        bucket_1 = LogBucket(time=datetime(2018, 5, 9, 16, 0, 39, tzinfo=timezone.utc))
        bucket_1.add(
            log_record_dm(time=datetime(2018, 5, 9, 16, 0, 39, tzinfo=timezone.utc))
        )
        bucket_1.add(
            log_record_dm(time=datetime(2018, 5, 9, 16, 0, 39, tzinfo=timezone.utc))
        )

        bucket_2 = LogBucket(time=datetime(2018, 5, 9, 16, 0, 40, tzinfo=timezone.utc))
        bucket_3 = LogBucket(time=datetime(2018, 5, 9, 16, 0, 43, tzinfo=timezone.utc))

        series.append(bucket_1)
        series.append(bucket_2)
        series.append(bucket_3)

        series.trim(from_time=datetime(2018, 5, 9, 16, 0, 41, tzinfo=timezone.utc))

        assert series.buckets == [
            LogBucket(time=datetime(2018, 5, 9, 16, 0, 41, tzinfo=timezone.utc)),
            LogBucket(time=datetime(2018, 5, 9, 16, 0, 42, tzinfo=timezone.utc)),
            bucket_3,
        ]

        series.trim(from_time=datetime(2018, 5, 9, 16, 0, 45, tzinfo=timezone.utc))
        assert series.buckets == []
