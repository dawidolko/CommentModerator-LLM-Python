"""
Evaluation tab: shows the results written by `moderator evaluate`.
"""

import gradio as gr

from moderator.config import ROOT
from moderator.service import Moderator
from moderator.web.i18n import Translator, hint, text

FOLDER = ROOT / "examples" / "evaluation"


def build(moderator: Moderator, t: Translator) -> None:
    with t.bind(gr.Tab(text("en", "tab.evaluation")), "tab.evaluation"):
        summary = FOLDER / "evaluation.md"
        if not summary.exists():
            gr.HTML(hint("evaluation.empty"))
            return
        chart = FOLDER / "classification.svg"
        if chart.exists():
            gr.Image(str(chart), label="Toxic class", show_label=False, height=380)
        gr.Markdown(summary.read_text(encoding="utf-8"))
