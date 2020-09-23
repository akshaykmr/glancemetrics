from datetime import timedelta
from glancemetrics.glance import GlanceMetrics
from glancemetrics.utils.datetime import current_time
from glancemetrics.watchdogs.log import logwatcher
from test.factories import FakeFile, fake_log_str


def test_refreshing_ingests_all_logs_till_none():
    logs = [
        '10.223.157.186 - - [15/Jul/2020:14:58:59 +0000] "GET /favicon.ico HTTP/1.1" 404 209',
        '11.22.157.186 - - [15/Jul/2020:14:58:59 +0000] "GET /api/pup HTTP/1.1" 200 154',
        '10.223.157.186 - - [15/Jul/2020:14:59:59 +0000] "GET /blah/central HTTP/1.1" 200 92',
        '10.223.157.186 - - [15/Jul/2020:15:23:11 +0000] "GET /doge HTTP/1.1" 200 1123',
        '11.22.157.186 - - [15/Jul/2020:15:23:11 +0000] "GET /power HTTP/1.1" 200 154',
        fake_log_str(
            time=current_time() - timedelta(seconds=2), content_size=22, path="/doggo"
        ),
        fake_log_str(
            time=current_time() - timedelta(seconds=1), content_size=300, path="/yolo"
        ),
        fake_log_str(
            time=current_time() - timedelta(seconds=1), content_size=40, path="/doggo"
        ),
    ]
    log_file = FakeFile(logs)
    stream = logwatcher(log_file)

    glance = GlanceMetrics(stream, insights_window=timedelta(seconds=5))
    glance.refresh()
    assert next(stream) is None
    insights, top_sections = glance.insights(top_sections_limit=1)
    assert insights.bytes_transferred == 362
    top_section = top_sections[0]
    assert top_section.name == "doggo"
    assert top_section.hits == 2
