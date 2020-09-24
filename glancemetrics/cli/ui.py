from typing import List
from rich import print

from glancemetrics.domain.alerts import Alert
from glancemetrics.domain.insights import Insights, SectionLogs

from .utils import clear_terminal


def render(insights: Insights, top_sections: List[SectionLogs], alerts: List[Alert]):
    clear_terminal()

    print([s.name for s in top_sections])
    print(insights, flush=True)
