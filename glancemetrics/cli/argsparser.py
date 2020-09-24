import argparse
from glancemetrics import defaults

parser = argparse.ArgumentParser(
    prog="GlanceMetrics",
    description="monitor log file (CLF) for insights and alerts",
    epilog="Enjoy the program! :)",
)

parser.add_argument(
    "-f",
    "--file",
    type=str,
    help=f"path to log file. eg. log.txt or /tmp/log.txt (defaults to {defaults.FILE})",
    default=defaults.FILE,
)

parser.add_argument(
    "--timewindow",
    type=int,
    help=f"time window for insights in seconds (defaults to {defaults.INSIGHTS_TIME_WINDOW} seconds)",
    default=defaults.INSIGHTS_TIME_WINDOW,
)

parser.add_argument(
    "--alertwindow",
    type=int,
    help=f"time window for insights in minutes (defaults to {defaults.ALERT_WINDOW})",
    default=defaults.ALERT_WINDOW,
)

parser.add_argument(
    "--alert_threshold",
    type=int,
    help=f"hit rate threshold in req/s (defaults to {defaults.ALERT_THRESHOLD})",
    default=defaults.ALERT_THRESHOLD,
)

parser.add_argument(
    "-r",
    "--refresh",
    type=int,
    help=f"refresh rate of the UI in seconds (defaults to {defaults.UI_REFRESH})",
    default=defaults.UI_REFRESH,
)
