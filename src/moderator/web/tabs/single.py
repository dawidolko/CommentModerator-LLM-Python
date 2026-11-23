"""
Tabs for one comment and for one image, with examples to click.
"""

from pathlib import Path

import gradio as gr

from moderator.config import ROOT
from moderator.service import MODES, Moderator
from moderator.web.components import verdict_card
from moderator.web.i18n import Translator, both_plain, hint, text

EXAMPLES = [
    "Jesteś totalnym idiotą, nawet pętli nie umiesz napisać.",
    "I could kill for a coffee right now, this debugging session is endless.",
    "Earn $500 a day working from home, click bit.ly/xx-cash now!!!",
    "Ten kod jest napisany fatalnie, nie ma żadnej obsługi błędów i testów.",
]
EXAMPLES_LABEL = "Examples · Przykłady"


def build(moderator: Moderator, t: Translator) -> None:
    def check_text(comment: str, mode: str) -> str:
        if not comment.strip():
            raise gr.Error(both_plain("error.comment"))
        return verdict_card(moderator.text(comment, mode), moderator.rulebook)

    def check_image(path: str | None, mode: str) -> str:
        if not path:
            raise gr.Error(both_plain("error.image"))
        return verdict_card(moderator.image(Path(path), mode), moderator.rulebook)

    images = sorted(str(path) for path in (ROOT / "data" / "images").glob("*.png"))

    with t.bind(gr.Tab(text("en", "tab.single")), "tab.single"):
        with gr.Row():
            with gr.Column():
                comment = t.bind_with(
                    gr.Textbox(label=text("en", "comment"), lines=4, placeholder=text("en", "comment.placeholder")),
                    lambda lang: {"label": text(lang, "comment"), "placeholder": text(lang, "comment.placeholder")},
                )
                mode = t.bind(gr.Radio(list(MODES), value="rag", label=text("en", "mode")), "mode")
                button = t.bind(gr.Button(text("en", "moderate"), variant="primary", size="lg"), "moderate", "value")
                gr.Examples(EXAMPLES, inputs=comment, label=EXAMPLES_LABEL)
            result = gr.HTML(hint("verdict.hint"))
        button.click(check_text, [comment, mode], result)
        comment.submit(check_text, [comment, mode], result)

    with t.bind(gr.Tab(text("en", "tab.image")), "tab.image"):
        with gr.Row():
            with gr.Column():
                image = t.bind(gr.Image(type="filepath", label=text("en", "image"), height=320), "image")
                image_mode = t.bind(gr.Radio(list(MODES), value="rag", label=text("en", "image.mode")), "image.mode")
                image_button = t.bind(
                    gr.Button(text("en", "image.button"), variant="primary", size="lg"), "image.button", "value"
                )
                if images:
                    gr.Examples(images, inputs=image, label=EXAMPLES_LABEL, examples_per_page=6)
            image_result = gr.HTML(hint("verdict.hint"))
        image_button.click(check_image, [image, image_mode], image_result)
