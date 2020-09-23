from typing import List

# metrics app outline


class GlanceMetrics:
    def __init__(self, alerts=None, insights_interval=None):

        # any alerts or recovery messages for the session
        # append to this log during session
        self.alert_messages: List[str] = []
        pass

    def refresh(self):
        """update self with latest metrics from logs"""
        # read log-buckets till None or till time at refresh (logs may keep on coming)
        # pass bucket to any observer - insights, alerts
        raise NotImplementedError

    @property
    def insights(self):
        # stats from last n seconds of logs
        # - total hits, popular sections
        # - bytes transferred
        # - known, anon users
        # - percenatge errors - distribution for client errors, server-errors
        # - current avg. request/sec
        raise NotImplementedError
