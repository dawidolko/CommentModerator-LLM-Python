"""
Evaluation tab: shows the results written by `moderator evaluate`.
"""

import gradio as gr

from moderator.config import ROOT
from moderator.service import Moderator

FOLDER = ROOT / "examples" / "evaluation"


def build(moderator: Moderator) -> None:
    with gr.Tab("Evaluation"):
        summary = FOLDER / "evaluation.md"
        if not summary.exists():
            gr.Markdown("No results yet. Run `moderator evaluate` to create them.")
            return
        chart = FOLDER / "classification.svg"
        if chart.exists():
            gr.Image(str(chart), label="Toxic class", show_label=False, height=380)
        gr.Markdown(summary.read_text(encoding="utf-8"))
