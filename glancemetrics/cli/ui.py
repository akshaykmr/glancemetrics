from typing import List
from glancemetrics.domain.alerts import Alert
from glancemetrics.domain.insights import Insights, SectionLogs
from .utils import clear_terminal


def render(insights: Insights, top_sections: List[SectionLogs], alerts: List[Alert]):
    clear_terminal()
    print(insights, flush=True)
