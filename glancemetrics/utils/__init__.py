# misc utils
import sys

import itertools as it
from typing import List, Callable, Any, Dict


def group_by(lizt: List[Any], key: Callable[[Any], Any]) -> Dict[Any, List[Any]]:
    sorted_list = sorted(lizt, key=key)
    return {k: list(v) for k, v in it.groupby(sorted_list, key)}


def clear_terminal():
    sys.stdout.write("\033[2J\033[1;1H")
