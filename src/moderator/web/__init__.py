"""
The Gradio web app. Each tab lives in its own module in web/tabs and gets the shared Moderator; the header shows the
models in use and whether Ollama answers, so a missing model is visible before the first click. The toolbar switches
the interface language (PL / EN) and the light or dark theme; both choices are kept in the browser's localStorage,
and the page still works when storage is blocked.
"""

from functools import partial
from pathlib import Path

import gradio as gr

from moderator.service import Moderator
from moderator.web.components import header
from moderator.web.i18n import Translator, text
from moderator.web.tabs import batch, chat, evaluation, rules, single

STYLE = Path(__file__).with_name("style.css")

SET_LANGUAGE = """(lang) => {
  document.body.classList.toggle('lang-pl', lang === 'pl');
  document.querySelectorAll('#toolbar .lang').forEach((b) => b.classList.toggle('active', b.id === 'lang-' + lang));
  try { localStorage.setItem('cm-lang', lang); } catch (e) {}
  return lang;
}"""

TOGGLE_THEME = """() => {
  const dark = document.body.classList.toggle('dark');
  try { localStorage.setItem('cm-theme', dark ? 'dark' : 'light'); } catch (e) {}
}"""

RESTORE = (
    "() => {\n"
    "  let lang = 'en', theme = null;\n"
    "  try { lang = localStorage.getItem('cm-lang') || 'en'; theme = localStorage.getItem('cm-theme'); } catch (e) {}\n"
    "  if (theme) document.body.classList.toggle('dark', theme === 'dark');\n"
    f"  return ({SET_LANGUAGE})(lang);\n"
    "}"
)


def ollama_status(moderator: Moderator) -> list[str] | None:
    try:
        return moderator.llm.missing_models()
    except Exception:
        return None


def build(moderator: Moderator | None = None) -> gr.Blocks:
    moderator = moderator or Moderator()
    settings = moderator.settings
    models = [("text", settings.text_model), ("vision", settings.vision_model), ("search", settings.embed_model)]
    t = Translator()
    with gr.Blocks(title="Comment Moderator") as app:
        language = gr.Textbox(value="en", visible=False)
        with gr.Row(elem_id="toolbar"):
            polish = gr.Button("PL", size="sm", elem_id="lang-pl", elem_classes=["lang"])
            english = gr.Button("EN", size="sm", elem_id="lang-en", elem_classes=["lang", "active"])
            theme = t.bind(gr.Button(text("en", "theme"), size="sm", elem_id="theme"), "theme", "value")
        gr.HTML(header(models, ollama_status(moderator), len(moderator.rulebook)))
        with gr.Tabs():
            for tab in (single, batch, chat, rules, evaluation):
                tab.build(moderator, t)
        for button, lang in ((polish, "pl"), (english, "en")):
            button.click(
                partial(t.updates, lang),
                None,
                t.components,
                js=f"() => {{ ({SET_LANGUAGE})('{lang}'); }}",
                show_progress="hidden",
            )
        theme.click(None, js=TOGGLE_THEME)
        app.load(t.restore, language, t.components, js=RESTORE, show_progress="hidden")
    return app


def launch_options() -> dict:
    theme = gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="violet",
        neutral_hue="slate",
        font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"],
        radius_size="lg",
    ).set(
        body_background_fill="#eef1f6",
        background_fill_primary="#eef1f6",
        block_background_fill="#ffffff",
        block_border_width="1px",
        block_border_color="#dbe1ea",
        block_shadow="0 1px 2px rgba(15, 23, 42, 0.05), 0 8px 20px -12px rgba(15, 23, 42, 0.18)",
        block_label_background_fill="#e0e7ff",
        panel_background_fill="#ffffff",
        input_background_fill="#f8fafc",
        input_border_width="1px",
        input_border_color="#cfd8e3",
        input_shadow="none",
        checkbox_label_background_fill="#f8fafc",
        checkbox_label_border_width="1px",
        checkbox_label_border_color="#cfd8e3",
        checkbox_label_text_color="#1e293b",
        button_secondary_background_fill="#ffffff",
        button_secondary_border_color="#cfd8e3",
        button_primary_shadow="0 6px 16px -8px rgba(79, 70, 229, 0.7)",
        body_background_fill_dark="#0b1020",
        background_fill_primary_dark="#0b1020",
        block_border_color_dark="#273246",
        block_shadow_dark="0 8px 20px -14px rgba(0, 0, 0, 0.8)",
        input_border_color_dark="#334155",
        checkbox_label_border_color_dark="#334155",
    )
    return {"theme": theme, "css": STYLE.read_text(encoding="utf-8"), "footer_links": []}
