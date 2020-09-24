#!/usr/bin/env/python

from pathlib import Path
from time import sleep
from datetime import timedelta

from glancemetrics.argsparser import parser
from glancemetrics.watchdogs.log import logwatcher
from glancemetrics.domain.alerts import Alert
from glancemetrics.glance import GlanceMetrics


def _validate_file_path(filepath: str) -> Path:
    path = Path(filepath).resolve()
    if not path.exists():
        print(
            f"""ERROR: file "{filepath}" not found. Please check the file path. \n
If using with Docker, you need to mount the volume
else docker would not be able to see the file.

DOCKER-TIP: if your file lies in /tmp/access.log then
easiest way is to mount the folder to /data of container like so:
docker run -v /tmp:/data glancemetrics -f /data/access.log
"""
        )
        exit(-1)
    return path


args = parser.parse_args()
ui_refresh_rate = args.refresh
file_path = _validate_file_path(args.file)

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
            print(glance_app.insights(), flush=True)
            sleep(ui_refresh_rate)
    except KeyboardInterrupt:
        # could use sys.signal handler instead
        pass
    print("exiting program")
