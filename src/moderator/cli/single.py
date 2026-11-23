"""
Commands for one comment: classify, rag, image and the toxic-bert baseline.
"""

from pathlib import Path

import typer
from rich.table import Table

from moderator import baseline
from moderator.cli.views import console, verdict_panel
from moderator.service import Moderator

HELP = {
    "classify": "Classify one comment with the text model.",
    "rag": "Classify one comment and cite the paragraph of the forum rules (RAG).",
    "image": "Read the text of an image with the vision model, then classify it.",
    "bert": "Score one comment with the unitary/toxic-bert baseline (English only).",
}


def classify(
    text: str = typer.Argument(..., help="The comment to check."),
    mode: str = typer.Option("few-shot", "--mode", "-m", help="zero-shot, few-shot or rag."),
) -> None:
    moderator = Moderator()
    console.print(verdict_panel(moderator.text(text, mode), moderator.rulebook))


def rag(text: str = typer.Argument(..., help="The comment to check.")) -> None:
    moderator = Moderator()
    result = moderator.text(text, "rag")
    console.print(verdict_panel(result, moderator.rulebook))
    for rule_id in result.retrieved:
        rule = moderator.rulebook.get(rule_id)
        console.print(f"[cyan]{rule.id}[/] [bold]{rule.title}[/]: [dim]{rule.text}[/]")


def image(
    path: Path = typer.Argument(..., exists=True, dir_okay=False, help="A meme or a screenshot."),
    mode: str = typer.Option("rag", "--mode", "-m", help="How the text read from the image is classified."),
) -> None:
    moderator = Moderator()
    console.print(verdict_panel(moderator.image(path, mode), moderator.rulebook))


def bert(text: str = typer.Argument(..., help="The comment to check.")) -> None:
    moderator = Moderator()
    model, threshold = moderator.settings.baseline["model"], moderator.settings.baseline["threshold"]
    scores = baseline.scores([text], model)[0]
    view = Table(title=f"{model}, threshold {threshold}")
    view.add_column("label")
    view.add_column("score", justify="right")
    for label, score in sorted(scores.items(), key=lambda item: -item[1]):
        view.add_row(label, f"[{'red' if score >= threshold else 'dim'}]{score:.3f}[/]")
    console.print(view)
    console.print(baseline.verdict(scores, threshold))


def register(app: typer.Typer) -> None:
    for command in (classify, rag, image, bert):
        app.command(help=HELP[command.__name__])(command)
