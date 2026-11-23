"""
The Gradio web app. Each tab lives in its own module in web/tabs and gets the shared Moderator; the header shows the
models in use and whether Ollama answers, so a missing model is visible before the first click.
"""

from pathlib import Path

import gradio as gr

from moderator.service import Moderator
from moderator.web.components import header
from moderator.web.tabs import batch, chat, evaluation, rules, single

STYLE = Path(__file__).with_name("style.css")


def ollama_status(moderator: Moderator) -> list[str] | None:
    try:
        return moderator.llm.missing_models()
    except Exception:
        return None


def build(moderator: Moderator | None = None) -> gr.Blocks:
    moderator = moderator or Moderator()
    settings = moderator.settings
    models = [("text", settings.text_model), ("vision", settings.vision_model), ("search", settings.embed_model)]
    with gr.Blocks(title="Comment Moderator") as app:
        gr.HTML(header(models, ollama_status(moderator), len(moderator.rulebook)))
        with gr.Tabs():
            for tab in (single, batch, chat, rules, evaluation):
                tab.build(moderator)
    return app


def launch_options() -> dict:
    theme = gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="violet",
        neutral_hue="slate",
        font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"],
        radius_size="lg",
    )
    return {"theme": theme, "css": STYLE.read_text(encoding="utf-8"), "footer_links": []}
