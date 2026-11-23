"""
The `moderator` command. Commands are split by area into single, files and tools; views holds the Rich output.
"""

import typer

from moderator.cli import files, single, tools

app = typer.Typer(help="Comment moderation with a local LLM (Ollama).", no_args_is_help=True, add_completion=False)

single.register(app)
files.register(app)
tools.register(app)


def main() -> None:
    app()
