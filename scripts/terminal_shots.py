"""
Screenshots for the report: runs CLI commands and renders their real output, and the key functions of the code, as
SVG terminal windows with Rich. The SVG files are then converted to PNG for LaTeX.
"""

import inspect
import io
import os
import re
import subprocess
import sys
from importlib import import_module
from pathlib import Path

from rich.console import Console
from rich.syntax import Syntax
from rich.text import Text

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "report" / "svg"
WIDTH = 104
CODE_WIDTH = 122
CURSOR = re.compile(r"\x1b\[\d*[AKG]|\r|\x1b\[\?25[lh]")
PROGRESS = re.compile(r"moderating \(|reading the file|evaluating")

COMMANDS = {
    "check": ["check"],
    "classify_insult": ["classify", "Jesteś totalnym idiotą, nawet pętli nie umiesz napisać.", "--mode", "zero-shot"],
    "classify_idiom": ["classify", "I could kill for a coffee right now, this debugging session is endless."],
    "bert_idiom": ["bert", "I could kill for a coffee right now, this debugging session is endless."],
    "image_meme": ["image", "data/images/meme_03.png"],
    "image_screenshot": ["image", "data/images/screenshot_01.png"],
    "rag_spam": ["rag", "Kup tanie konto premium na www.super-promo.example, kod RABAT50 daje -50%!"],
    "rag_threat": ["rag", "Daj mi swój adres, przyjadę i pogadamy inaczej niż na forum."],
    "batch": ["batch", "data/comments.csv", "-o", "examples/batch/moderated.csv"],
}

CODE = {
    "code_settings": ("moderator.config", "load_settings"),
    "code_llm": ("moderator.llm", "LLM"),
    "code_schema": ("moderator.schema", "Verdict"),
    "code_prompt": ("moderator.prompts", "moderation_messages"),
    "code_classify": ("moderator.classify", "ask_for_verdict"),
    "code_vision": ("moderator.vision", "moderate_image"),
    "code_batch": ("moderator.batch", "moderate_frame"),
    "code_chat": ("moderator.chat", "ChatSession"),
    "code_retrieval": ("moderator.retrieval", "Retriever"),
    "code_rag": ("moderator.rag", "moderate_with_rules"),
    "code_report": ("moderator.report", "save_chart"),
}


def without_progress(output: str) -> str:
    output = CURSOR.sub("", output)
    return "\n".join(line for line in output.splitlines() if not PROGRESS.search(line))


def terminal(name: str, args: list[str]) -> None:
    env = {**os.environ, "COLUMNS": str(WIDTH), "FORCE_COLOR": "1", "TERM": "xterm-256color"}
    command = [str(Path(sys.executable).with_name("moderator")), *args]
    result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, check=True)
    console = Console(record=True, width=WIDTH, force_terminal=True, file=io.StringIO())
    console.print(Text("$ moderator " + " ".join(f'"{a}"' if " " in a else a for a in args), style="bold green"))
    console.print(Text.from_ansi(without_progress(result.stdout).rstrip()))
    console.save_svg(str(OUTPUT / f"{name}.svg"), title="terminal")


def code(name: str, module: str, attribute: str) -> None:
    source = inspect.getsource(getattr(import_module(module), attribute))
    console = Console(record=True, width=CODE_WIDTH, file=io.StringIO())
    console.print(Syntax(source, "python", theme="github-dark", line_numbers=False, word_wrap=True))
    console.save_svg(str(OUTPUT / f"{name}.svg"), title=f"src/{module.replace('.', '/')}.py")


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    wanted = set(sys.argv[1:])
    for name, (module, attribute) in CODE.items():
        if not wanted or name in wanted:
            code(name, module, attribute)
    for name, args in COMMANDS.items():
        if not wanted or name in wanted:
            print(f"running {name}", flush=True)
            terminal(name, args)


if __name__ == "__main__":
    main()
