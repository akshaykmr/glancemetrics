from glancemetrics.domain.models import LogSeries
from glancemetrics.domain.insights import top_sections, Insights
from test.utils import logs_to_series


class TestInsights:
    def test_empty_series(self):
        series = LogSeries()
        assert Insights.from_log_series(series) == Insights(
            hits=0,
            bytes_transferred=0,
            transfer_rate=0,
            known_users=0,
            hit_rate=0,
            error_count=0,
            client_errors=0,
            server_errors=0,
        )

    def test_stats(self):
        logs = [
            '10.223.157.186 - - [15/Jul/2020:14:58:59 +0000] "GET /doge HTTP/1.1" 404 209',
            '11.22.157.186 - fred [15/Jul/2020:14:58:59 +0000] "GET /api/pup HTTP/1.1" 200 154',
            '10.223.157.186 - - [15/Jul/2020:14:59:00 +0000] "GET /api/meme HTTP/1.1" 200 92',
            '10.223.157.186 - - [15/Jul/2020:14:59:00 +0000] "GET /doge HTTP/1.1" 200 1123',
            '11.22.157.186 - fred [15/Jul/2020:15:00:00 +0000] "GET /power HTTP/1.1" 200 154',
            '11.22.157.186 - fred [15/Jul/2020:15:00:00 +0000] "GET /doge HTTP/1.1" 200 11',
            '180.22.157.186 - luna [15/Jul/2020:15:00:02 +0000] "GET /api HTTP/1.1" 200 90',
            '180.22.157.186 - luna [15/Jul/2020:15:00:02 +0000] "GET /api HTTP/1.1" 500 90',
            '180.22.157.186 - luna [15/Jul/2020:15:00:02 +0000] "GET /api HTTP/1.1" 500 90',
            '180.22.157.186 - luna [15/Jul/2020:15:00:02 +0000] "GET /api HTTP/1.1" 500 90',
        ]
        series = logs_to_series(logs)
        assert Insights.from_log_series(series) == Insights(
            hits=10,
            bytes_transferred=2103,
            known_users=2,
            transfer_rate=32.9,
            hit_rate=0.2,
            error_count=4,
            client_errors=1,
            server_errors=3,
        )

    def test_popular_sections(self):
        logs = [
            '10.223.157.186 - - [15/Jul/2020:14:58:59 +0000] "GET /doge HTTP/1.1" 404 209',
            '11.22.157.186 - fred [15/Jul/2020:14:58:59 +0000] "GET /api/pup HTTP/1.1" 200 154',
            '10.223.157.186 - - [15/Jul/2020:14:59:00 +0000] "GET /api/meme HTTP/1.1" 200 92',
            '10.223.157.186 - - [15/Jul/2020:14:59:00 +0000] "GET /doge HTTP/1.1" 200 1123',
            '11.22.157.186 - fred [15/Jul/2020:15:00:00 +0000] "GET /power HTTP/1.1" 200 154',
            '11.22.157.186 - fred [15/Jul/2020:15:00:00 +0000] "GET /doge HTTP/1.1" 200 11',
            '180.22.157.186 - luna [15/Jul/2020:15:00:02 +0000] "GET /api HTTP/1.1" 200 90',
            '180.22.157.186 - luna [15/Jul/2020:15:00:02 +0000] "GET /api HTTP/1.1" 500 90',
            '180.22.157.186 - luna [15/Jul/2020:15:00:02 +0000] "GET /api HTTP/1.1" 500 90',
            '180.22.157.186 - luna [15/Jul/2020:15:00:02 +0000] "GET /api HTTP/1.1" 500 90',
        ]
        series = logs_to_series(logs)
        first, second = top_sections(series, limit=2)
        assert first.name == "api"
        assert first.hits == 6
        assert second.name == "doge"
        assert second.hits == 3
