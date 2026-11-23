"""
Commands for files: batch moderation and the chat about a file with /report, /chart, /save and /exit.
"""

from pathlib import Path

import typer
from rich.markdown import Markdown
from rich.prompt import Prompt

from moderator.batch import moderate_frame, read_comments, save
from moderator.chat import COMMANDS, ChatSession
from moderator.cli.views import console, progress_bar, results_table
from moderator.report import save_chart, save_report
from moderator.service import Moderator

HELP = {
    "batch": "Moderate a whole file of comments and write the results to CSV.",
    "chat": "Talk with the model about a file of comments. Commands: /report /chart /save /exit.",
}


def batch(
    source: Path = typer.Argument(..., exists=True, dir_okay=False, help="A .csv with a 'text' column or a .txt file."),
    output: Path = typer.Option(Path("out/moderated.csv"), "--output", "-o", help="Where to write the CSV."),
    mode: str = typer.Option("few-shot", "--mode", "-m", help="zero-shot, few-shot or rag."),
    report: bool = typer.Option(True, help="Also write report.txt and chart.svg next to the CSV."),
) -> None:
    moderator = Moderator()
    frame = read_comments(source)
    table, _ = moderate_frame(moderator, frame, mode, progress_bar(f"moderating ({mode})"))
    save(table, output)
    console.print(results_table(table, limit=12))
    console.print(f"[green]saved[/] {output} ({len(table)} comments, {table['latency_s'].mean():.2f} s per comment)")
    if report:
        model = moderator.settings.text_model
        console.print(f"[green]saved[/] {save_report(table, output.with_name('report.txt'), source.name, model)}")
        console.print(
            f"[green]saved[/] {save_chart(table, output.with_name('chart.svg'), f'Moderation of {source.name}')}"
        )


def chat(
    source: Path = typer.Argument(..., exists=True, dir_okay=False, help="A .txt file with one comment per line."),
    mode: str = typer.Option("rag", "--mode", "-m", help="How the comments are moderated before the chat."),
) -> None:
    session = ChatSession(Moderator(), source, mode)
    session.load(progress_bar("reading the file"))
    console.print(
        f"[bold]{len(session.table)}[/] comments from {source.name} moderated, ask about them. "
        f"Commands: {', '.join(COMMANDS)}"
    )
    while True:
        question = Prompt.ask("[bold cyan]you[/]").strip()
        if not question:
            continue
        if question in ("/exit", "/quit"):
            console.print(f"[green]saved[/] {session.save_log()}")
            break
        if question == "/help":
            for name, about in COMMANDS.items():
                console.print(f"  [cyan]{name}[/] {about}")
        elif question == "/report":
            console.print(f"[green]saved[/] {session.report()}")
        elif question == "/chart":
            console.print(f"[green]saved[/] {session.chart()}")
        elif question == "/save":
            console.print(f"[green]saved[/] {session.save_log()}")
        else:
            answer = "".join(session.ask(question))
            console.print("[bold magenta]model[/]")
            console.print(Markdown(answer))


def register(app: typer.Typer) -> None:
    for command in (batch, chat):
        app.command(help=HELP[command.__name__])(command)
