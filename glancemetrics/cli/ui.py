from typing import List
from rich.console import Console
from rich.table import Table
from datetime import timedelta
import humanize

from glancemetrics.domain.alerts import Alert
from glancemetrics.domain.insights import Insights, SectionLogs

from .utils import clear_terminal

console = Console()


def render(
    insights: Insights,
    top_sections: List[SectionLogs],
    alerts: List[Alert],
    insights_window: timedelta,
    program_runtime: timedelta,
):
    clear_terminal()
    console.print("GlanceMetrics\n", style="bold cyan")
    console.print(
        f"app has been running for {humanize.naturaldelta(program_runtime)}. [yellow]ctrl-c[/yellow] to quit\n\n"
    )
    console.print(
        f"[bold]Insights[/bold] - past {humanize.naturaldelta(insights_window)}"
    )
    console.print(insights_table(insights))


def insights_table(i: Insights):
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Total Hits")
    table.add_column("Data Sent")
    table.add_column("Known Users")
    table.add_column("Errors", header_style="red")
    table.add_column("Client Errors", header_style="red")
    table.add_column("Server Errors", header_style="red")

    row = [
        humanize.intcomma(i.hits),
        humanize.naturalsize(i.bytes_transferred),
        humanize.intcomma(i.known_users),
        humanize.intcomma(i.error_count),
        humanize.intcomma(i.client_errors),
        humanize.intcomma(i.server_errors),
    ]
    table.add_row(*[str(cell) for cell in row])
    return table
