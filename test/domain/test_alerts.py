from datetime import timedelta
from unittest.mock import patch

from glancemetrics.domain.alerts import Alert
from glancemetrics.watchdogs.log import logwatcher
from glancemetrics.utils.datetime import current_time

from test.factories import FakeFile, fake_log_str


def _ingest_all_logs(stream, alert):
    for bucket in stream:
        if bucket is None:
            break
        alert.ingest(bucket)
    alert.refresh()


@patch("glancemetrics.domain.alerts.current_time")
def test_high_traffic_alerting(time_now_fn):
    # this test goes through the flow of a
    # normal scenario -> high traffic alert
    # then a recovered alert once traffic subsides

    now = current_time()
    time_now_fn.return_value = now
    alert = Alert(threshold=3, window=timedelta(seconds=5))
    log_file = FakeFile([])
    stream = logwatcher(log_file)

    # hit rate exceeded but out of window
    log_file.append_logs(
        [
            *[
                fake_log_str(time=now - timedelta(seconds=8)) for _ in range(6)
            ],  # hit rate of 6
            *[
                fake_log_str(time=now - timedelta(seconds=7)) for _ in range(8)
            ],  # hit rate of 8
        ]
    )
    _ingest_all_logs(stream, alert)
    assert not alert.is_blaring
    assert alert.incidents == []

    # hit rate in bounds - avg of 3 not exceeded in past five seconds
    log_file.append_logs(
        [
            *[fake_log_str(time=now - timedelta(seconds=6)) for _ in range(8)],
            *[fake_log_str(time=now - timedelta(seconds=3)) for _ in range(12)],
        ]
    )
    _ingest_all_logs(stream, alert)
    assert not alert.is_blaring
    assert alert.incidents == []

    # hit rate exceeded
    log_file.append_logs(
        [*[fake_log_str(time=now - timedelta(seconds=2)) for _ in range(9)]]
    )
    _ingest_all_logs(stream, alert)
    assert alert.is_blaring

    incident = alert.active_incident
    assert incident.breach_hitrate == round(
        (12 + 9) / 5, 1
    )  # 9 + 12 hits divided by time window size
    assert incident.triggered_at == now

    # lets advance the time by 2 seconds, with no new logs
    now += timedelta(seconds=2)
    time_now_fn.return_value = now
    _ingest_all_logs(stream, alert)
    assert not alert.is_blaring
    assert incident.recovered_at == now
