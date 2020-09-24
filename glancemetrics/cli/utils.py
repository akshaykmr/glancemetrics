import sys


def clear_terminal():
    sys.stdout.write("\033[2J\033[1;1H")
