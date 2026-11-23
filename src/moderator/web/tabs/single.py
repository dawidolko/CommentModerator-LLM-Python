"""
Tabs for one comment and for one image, with examples to click.
"""

from pathlib import Path

import gradio as gr

from moderator.config import ROOT
from moderator.service import MODES, Moderator
from moderator.web.components import verdict_card

EXAMPLES = [
    "Jesteś totalnym idiotą, nawet pętli nie umiesz napisać.",
    "I could kill for a coffee right now, this debugging session is endless.",
    "Earn $500 a day working from home, click bit.ly/xx-cash now!!!",
    "Ten kod jest napisany fatalnie, nie ma żadnej obsługi błędów i testów.",
]

PLACEHOLDER = (
    '<p class="hint">The verdict appears here: decision, severity, categories, the reason and, '
    "in the RAG mode, the cited rule.</p>"
)


def build(moderator: Moderator) -> None:
    def check_text(text: str, mode: str) -> str:
        if not text.strip():
            raise gr.Error("Write a comment first.")
        return verdict_card(moderator.text(text, mode), moderator.rulebook)

    def check_image(path: str | None, mode: str) -> str:
        if not path:
            raise gr.Error("Upload an image first.")
        return verdict_card(moderator.image(Path(path), mode), moderator.rulebook)

    images = sorted(str(path) for path in (ROOT / "data" / "images").glob("*.png"))

    with gr.Tab("Single comment"):
        with gr.Row():
            with gr.Column():
                text = gr.Textbox(label="Comment", lines=4, placeholder="Paste a comment in Polish or English")
                mode = gr.Radio(list(MODES), value="rag", label="Mode")
                button = gr.Button("Moderate", variant="primary", size="lg")
                gr.Examples(EXAMPLES, inputs=text, label="Try one")
            result = gr.HTML(PLACEHOLDER)
        button.click(check_text, [text, mode], result)
        text.submit(check_text, [text, mode], result)

    with gr.Tab("Image"):
        with gr.Row():
            with gr.Column():
                image = gr.Image(type="filepath", label="Meme or screenshot", height=320)
                image_mode = gr.Radio(list(MODES), value="rag", label="Mode for the text read from the image")
                image_button = gr.Button("Read and moderate", variant="primary", size="lg")
                if images:
                    gr.Examples(images, inputs=image, label="Sample memes and screenshots", examples_per_page=6)
            image_result = gr.HTML(PLACEHOLDER)
        image_button.click(check_image, [image, image_mode], image_result)
