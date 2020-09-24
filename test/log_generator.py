# DO NOT USE IN TESTS!
# see existing tests on how to use Test-Fakes instead

# This program is more of a util than can come in handy
# writes fake logs to stdout every second
# eg use: pipe it to an active log file

from time import sleep
from random import randint
from glancemetrics.utils.datetime import current_time
from test.factories import fake_log_str

min_hit_rate = 6000
max_hit_rate = 9000

try:
    while True:
        now = current_time()
        for i in range(randint(min_hit_rate, max_hit_rate)):
            print(fake_log_str(time=now))
        sleep(1)
except KeyboardInterrupt:
    pass
