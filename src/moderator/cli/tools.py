"""
Commands around the app: check the models, run the evaluation, start the web app.
"""

from pathlib import Path

import pandas as pd
import typer
from rich.table import Table

from moderator import evaluate as evaluation
from moderator.cli.views import console, progress_bar
from moderator.service import Moderator

HELP = {
    "check": "Check the connection to Ollama and that the models are pulled.",
    "evaluate": "Compare toxic-bert, LLM zero-shot, few-shot and RAG on data/comments.csv.",
    "web": "Start the web app (Gradio).",
}


def check() -> None:
    moderator = Moderator()
    settings = moderator.settings
    console.print(f"Ollama: [bold]{settings.ollama_host}[/]")
    try:
        available = moderator.llm.models()
    except Exception as problem:
        console.print(f"[red]cannot reach Ollama:[/] {problem}")
        raise typer.Exit(1) from problem
    view = Table()
    view.add_column("role")
    view.add_column("model")
    view.add_column("status")
    missing = moderator.llm.missing_models()
    for role, name in (
        ("text", settings.text_model),
        ("vision", settings.vision_model),
        ("embeddings", settings.embed_model),
    ):
        view.add_row(role, name, "[red]missing: ollama pull " + name + "[/]" if name in missing else "[green]ready[/]")
    console.print(view)
    console.print(f"{len(available)} models available, rules: {len(moderator.rulebook)} paragraphs")
    if missing:
        raise typer.Exit(1)


def evaluate(
    output: Path = typer.Option(Path("examples/evaluation"), "--output", "-o", help="Folder for the results."),
    skip_llm: bool = typer.Option(False, help="Only the baseline and retrieval, no LLM calls."),
) -> None:
    moderator = Moderator()
    data = pd.read_csv(moderator.settings.path("comments_csv"))
    output.mkdir(parents=True, exist_ok=True)
    rows, bert_table = evaluation.evaluate_baseline(moderator.settings, data)
    bert_table.to_csv(output / "baseline_scores.csv", index=False)
    if not skip_llm:
        llm_rows, tables = evaluation.evaluate_llm(moderator, data, progress_bar("evaluating"))
        rows += llm_rows
        for mode, table in tables.items():
            table.to_csv(output / f"predictions_{mode}.csv", index=False)
    results = pd.DataFrame(rows)
    retrieval = pd.DataFrame(evaluation.evaluate_retrieval(moderator, data))
    results.to_csv(output / "classification.csv", index=False)
    retrieval.to_csv(output / "retrieval.csv", index=False)
    evaluation.save_chart(results, output / "classification.svg")
    summary = results[results["subset"] == "all"].drop(columns="subset")
    by_language = results[results["subset"] != "all"][["variant", "subset", "precision", "recall", "f1"]]
    text = "\n\n".join(
        [
            f"# Evaluation\n\n{len(data)} labelled comments ({int(data['toxic'].sum())} toxic), "
            f"text model `{moderator.settings.text_model}`, embeddings `{moderator.settings.embed_model}`.",
            "## Toxic class, all comments\n\n" + evaluation.markdown_table(summary),
            "## By language\n\n" + evaluation.markdown_table(by_language),
            "## Finding the right paragraph of the rules\n\n" + evaluation.markdown_table(retrieval),
        ]
    )
    (output / "evaluation.md").write_text(text + "\n", encoding="utf-8")
    console.print(text)


def web(
    host: str = typer.Option("127.0.0.1", help="Address to listen on (0.0.0.0 in Docker)."),
    port: int = typer.Option(7860, help="Port of the web app."),
) -> None:
    from moderator.web import build, launch_options

    build().launch(server_name=host, server_port=port, **launch_options())


def register(app: typer.Typer) -> None:
    for command in (check, evaluate, web):
        app.command(help=HELP[command.__name__])(command)
