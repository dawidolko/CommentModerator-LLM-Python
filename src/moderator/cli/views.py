"""
Rich output of the CLI: the verdict panel, the results table and a progress bar that any loop over comments can use.
The console records its output, which is how the screenshots in the report are made.
"""

from rich.console import Console, Group
from rich.panel import Panel
from rich.progress import BarColumn, MofNCompleteColumn, Progress, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text

from moderator.schema import Moderation

console = Console(record=True, width=100)

DECISION_STYLE = {"allow": "bold green", "review": "bold yellow", "remove": "bold red"}


def verdict_panel(result: Moderation, rules=None) -> Panel:
    verdict = result.verdict
    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="dim", justify="right")
    grid.add_column()
    if result.read_text is not None:
        grid.add_row("read from image", Text(result.read_text, style="italic"))
    else:
        grid.add_row("comment", Text(result.text, style="italic"))
    grid.add_row("decision", Text(verdict.decision.upper(), style=DECISION_STYLE[verdict.decision]))
    grid.add_row("toxic", "yes" if verdict.toxic else "no")
    grid.add_row("categories", ", ".join(verdict.categories))
    grid.add_row("severity", f"{verdict.severity} / 3")
    grid.add_row("reason", verdict.reason)
    if result.mode.endswith("rag"):
        grid.add_row("retrieved", ", ".join(result.retrieved))
        rule = verdict.rule or "-"
        if rules is not None and verdict.rule in rules:
            rule = f"{verdict.rule} {rules.get(verdict.rule).title}"
        grid.add_row("rule", Text(rule, style="bold cyan"))
    if result.error:
        grid.add_row("note", Text(result.error, style="yellow"))
    footer = Text(f"{result.model} · {result.mode} · {result.latency_s:.2f} s", style="dim")
    return Panel(
        Group(grid, Text(), footer),
        title="Moderation",
        border_style=DECISION_STYLE[verdict.decision].split()[-1],
        expand=False,
    )


def results_table(table, limit: int | None = None) -> Table:
    view = Table(show_lines=False, header_style="bold")
    for column, width in (("id", 4), ("decision", 8), ("categories", 14), ("sev", 3), ("rule", 6), ("text", 52)):
        view.add_column(column, max_width=width, overflow="ellipsis", no_wrap=column != "text")
    rows = table if limit is None else table.head(limit)
    for row in rows.itertuples():
        view.add_row(
            str(row.id),
            Text(row.decision, style=DECISION_STYLE[row.decision]),
            str(row.categories),
            str(row.severity),
            str(row.rule or ""),
            str(row.text),
        )
    return view


def progress_bar(description: str):
    def track(items):
        items = list(items)
        with Progress(
            TextColumn(description),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task(description, total=len(items))
            for item in items:
                yield item
                progress.advance(task)

    return track
