# GlanceMetrics

![image info](./screenshot.png)

Hello/Bonjour!, thank you for taking out the time to carefully evaluate this project. If you have any questions/concerns please let me know.

## How to run the app on your machine

We're going to use **docker** so that you do not have to install
anything on your system. Follow these steps:

0. `cd` to this directory (dir with readme.md)
1. Build the image `docker build -t glancemetrics .`
2. To run the app, you'll need to mount the directory of log file, else docker won't be able to see it. For eg. if log file is `/tmp/access.log` then mount `/tmp` dir in docker run command. Here's how  `docker run -it -v /tmp:/data glancemetrics -f /data/access.log` . Your app should be running! 

> Note: UI updates every 2 seconds by default, it'll show the insights for past 10 seconds. I just didn't feel like waiting 10 seconds. Everything is configurable for your needs though.

To get full list of configurable options and help pass `-h` flag: `docker run -it -v /tmp:/data glancemetrics -h`.
  - You can configure file-path, insights-window, alerts-threshold, alert-window, ui-refresh-rate, top-section-limit and more!
  - eg. with file in `/home/akshay/logs.txt`, insights-window of 30s, alert triggering at 20req/s avg for 5mins: `docker run -it -v /home/akshay:/data glancemetrics -f /data/logs.txt --timewindow=30  --alert_threshold=30 --alertwindow=5`


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


## Bonus: Live demo!

What?? Yep, I'm going to use another project on mine to demo this project!
It's like deploying to production -- satisfying.
I've set-up 2 streaming terminals -- one of this application, and the other with `tail -f` of a log file. 

check it out (no sign-in needed): https://teletype.oorja.io/rooms?id=bc41ea1c-bcca-482a-8c1c-14576460e429#MVcLBWDmMqZSmiWcqYyuYQ==

^^ looks better on large screens, keep scrolled to bottom.
I'll keep this running for a week, hopefully my cheap VPS holds up well during this time.


## Other thoughts, improvements


<!-- 109 MB file -> 11 seconds to load if not seeking -->