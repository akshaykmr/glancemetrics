#!/usr/bin/env/python
from time import sleep
from datetime import timedelta

from glancemetrics.glance import GlanceMetrics
from glancemetrics.domain.alerts import Alert

from glancemetrics.cli.argsparser import parser
from glancemetrics.cli.ui import render

from glancemetrics.watchdogs.log import logwatcher
from glancemetrics.utils import ensure_file_exists


args = parser.parse_args()
ui_refresh_rate = args.refresh
file_path = ensure_file_exists(args.file)

with open(str(file_path), "r") as log_file:
    alert = Alert(threshold=args.alert_threshold, window=timedelta(minutes=2),)
    glance_app = GlanceMetrics(
        log_stream=logwatcher(log_file),
        insights_window=timedelta(seconds=args.timewindow),
        alerts=[alert],
    )
    try:
        while True:
            glance_app.refresh()
            insights, top_sections = glance_app.insights()
            render(insights, top_sections, alerts=glance_app.alerts)
            sleep(ui_refresh_rate)
    except KeyboardInterrupt:
        # could use sys.signal handler instead
        pass
    print("exiting program")
