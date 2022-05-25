**GlanceMetrics**

HTTP log monitoring console program. Tail live logs for basic insights and setup simple alerts. Supports [Common log format](https://en.wikipedia.org/wiki/Common_Log_Format) for now.

> screenshot

<img src="./screenshot.png" width="750">

## Run with docker

To monitor a log file with path `/data/access.log`:

`docker run akshaykmr/glancemetrics -f /data/access.log`

You'll need to mount the directory of log file, else docker won't be able to see it. For eg. if log file is `/tmp/access.log` then mount `/tmp` dir in docker run command. Here's how  `docker run -it -v /tmp:/data akshaykmr/glancemetrics -f /data/access.log` . Your app should be running! 



> Note: UI updates every 2 seconds by default, it'll show the insights for past 10 seconds. Everything is configurable for your needs though.

To get full list of configurable options and help pass `-h` flag: `docker run -it -v /tmp:/data akshaykmr/glancemetrics -h`.
  - You can configure file-path, insights-window, alerts-threshold, alert-window, ui-refresh-rate, top-section-limit and more!
  - eg. with file in `/home/logs.txt`, insights-window of 30s, alert triggering at 20req/s avg for 5mins: `docker run -it -v /home:/data akshaykmr/glancemetrics -f /data/logs.txt --timewindow=30  --alert_threshold=30 --alertwindow=5`


## Run from source with docker / Local Development

0. `cd` to this directory (dir with readme.md)
1. Build the image `docker build -t glancemetrics .`
2. `docker run -it -v /tmp:/data glancemetrics -f /data/access.log`

Misc: create fake logs and run the app against them --
- create fake log stream: `make generate_logs > /tmp/fake_access.log`
- In another terminal: `docker run -it -v /tmp:/data akshaykmr/glancemetrics -f /data/fake_access.log`

## Running tests

  - `make test`

## Code overview
Here's the breakdown in brief:
- **domain/models**: `LogRecord`, `LogBucket`, `LogSeries` - capture the core-primitives that I felt made it easier to work with the problem i.e Thinking in terms of buckets, series, time-windows, and simple functions operating on them.
- **`watchdogs/log.py`**: streaming log reader that yields buckets of logs
- **domain** - `summary`, `insights`, `alerts`: calculate interesting insights, trigger/recover alerts etc.
- **`glance.py`** - main app library that uses the above constructs and tails the log file.
- **`app.py`** - boots the app with desired configuration options, and keeps it ticking.
- **`ui.py`** - user interface and presentation.
- **tests**: recommend checking out the tests for more insights.


## Other thoughts, improvements

- Speaking of performance, I tested it by generating fake logs with `make generate_logs` - req/s averaging `7000/s`. The UI was still fast enough to refresh every 2 seconds.
- When starting afresh with large log files (109 MB) though it could take ~11 seconds for the first render (a lot of wasteful processing for logs we're not interested in). To combat this I seek to end of file at the start of the program, since we're only interested in the recent logs. Now it starts instantly. An improvement could be to seek till the first log which falls within the insights-window and then init the log-stream.
- Improve test-coverage for `glance.py` - enforce-wiring with alerts/insights view eg. `assert alert.ingest.called_with(fake_log_buckted) on glance.refresh()`.
- Writing the alert triggered/recovered to a file would be useful I think.
- Lookout for log-rotation and stream the new log file (maybe monitor metadata?)
- Misc: Evaluate introducing a MetricSeries data-structure (series of reduced-metrics of log-buckets). I thought of this when implementing hit-rate alert. This would increase efficiency. Though it was good enough to reuse log-series where I have all the information.


## License

Copyright Akshay Kumar <akshay.kmr4321@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
