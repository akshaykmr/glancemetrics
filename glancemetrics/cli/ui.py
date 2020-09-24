from typing import List
from rich.console import Console
from rich.table import Table
from datetime import timedelta, datetime, timezone
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
    incident_limit: int,
):
    clear_terminal()
    console.print("GlanceMetrics", style="bold cyan")
    console.print(
        f"app has been running for {humanize.naturaldelta(program_runtime)}. [yellow]ctrl-c[/yellow] to quit\n"
    )
    console.print(
        f"[bold]Insights[/bold] for {humanize.precisedelta(insights_window)}\n"
    )
    console.print(insights_table(insights))
    console.print("\n[bold] Top sections 📈[/bold]")
    console.print(sections_table(top_sections))
    console.print(
        f"\n\n[bold] Alerts [/bold] (upto {incident_limit} latest incidents)\n"
    )

    for alert in alerts:
        print_alert_incidents(alert, limit=incident_limit)


def insights_table(i: Insights) -> Table:
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Total Hits")
    table.add_column("Data Sent")
    table.add_column("Known Users")
    table.add_column("Errors", header_style="bright_red")
    table.add_column("Client Errors", header_style="bright_red")
    table.add_column("Server Errors", header_style="bright_red")

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


def sections_table(top_sections: List[SectionLogs]) -> Table:
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Section")
    table.add_column("Hits")

    for section in top_sections:
        row = [
            section.name,
            section.hits,
        ]
        table.add_row(*[str(cell) for cell in row])
    return table


def humanize_time(d: datetime) -> str:
    """whatever format for time is preferable in UI"""
    return d.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")


def print_alert_incidents(alert: Alert, limit: int) -> Table:
    "only high traffic alert supported for now"

    alert_window = humanize.precisedelta(alert.window)
    console.print(
        f"[bold]config:[/bold] triggered if req/s > {alert.threshold} for {alert_window} on avg.\n"
    )
    if not alert.incidents:
        console.print("[green] All good, no incidents! [/green]")
        return

    # show upto 3 latest incidents in most recent order
    for incident in list(reversed(alert.incidents))[:limit]:
        duration = humanize.precisedelta(incident.duration)
        breach_rate = humanize.intcomma(incident.breach_hitrate)
        max_rate = humanize.intcomma(incident.max_hitrate)

        if incident.active:
            console.print(
                f"[bold bright_red] 🚨 Ongoing (since {duration}):[/bold bright_red]",
                end=" ",
            )
        else:
            console.print(f"[bold]Recovered (duration {duration}):[/bold]", end=" ")
        console.print(
            f"High traffic generated an alert - hits = {breach_rate}, triggered at {humanize_time(incident.triggered_at)}, max hitrate = {max_rate}",
            end="",
        )
        if not incident.active:
            console.print(
                f", recovered at {humanize_time(incident.recovered_at)}", end=""
            )
        console.print("\n")
