#!/usr/bin/env/python
from time import sleep
import io
from datetime import timedelta

from glancemetrics.glance import GlanceMetrics
from glancemetrics.domain.alerts import Alert

from glancemetrics.cli.argsparser import parser
from glancemetrics.cli.ui import render

from glancemetrics.watchdogs.log import logwatcher
from glancemetrics.utils import ensure_file_exists
from glancemetrics.utils.datetime import current_time


args = parser.parse_args()
program_start_time = current_time()
ui_refresh_rate = args.refresh

file_path = ensure_file_exists(args.file)

with open(str(file_path), "r") as log_file:
    # seek to end of file for faster app startup in case of large log files
    # since we're only interested in current metrics
    # TODO: could also implement smartly seeking to first log where timestamp > (now - app_window)
    log_file.seek(0, io.SEEK_END)
    insights_window = timedelta(seconds=args.timewindow)
    alert = Alert(
        threshold=args.alert_threshold, window=timedelta(minutes=args.alertwindow)
    )
    glance_app = GlanceMetrics(
        log_stream=logwatcher(log_file),
        insights_window=insights_window,
        alerts=[alert],
    )
    try:
        while True:
            glance_app.refresh()
            insights, top_sections = glance_app.insights(
                top_sections_limit=args.section_limit
            )
            render(
                insights,
                top_sections,
                alerts=glance_app.alerts,
                insights_window=insights_window,
                program_runtime=current_time() - program_start_time,
                incident_limit=args.incident_limit,
            )
            sleep(ui_refresh_rate)
    except KeyboardInterrupt:
        # could use sys.signal handler instead
        pass
    print("exiting program, bye 👋")
