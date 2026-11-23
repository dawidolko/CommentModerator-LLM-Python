"""
Rules tab: the paragraphs of the forum rules and a search box for the three retrievers.
"""

import gradio as gr

from moderator.service import Moderator
from moderator.web.components import rules_html
from moderator.web.i18n import Translator, both_plain, text


def build(moderator: Moderator, t: Translator) -> None:
    def search(query: str, method: str, top_k: int) -> str:
        if not query.strip():
            raise gr.Error(both_plain("error.query"))
        return rules_html(moderator.retriever.search(query, top_k=int(top_k), method=method))

    with t.bind(gr.Tab(text("en", "tab.rules")), "tab.rules"):
        with gr.Row():
            with gr.Column():
                query = t.bind(
                    gr.Textbox(
                        label=text("en", "comment"), lines=3, value="Kup tanie konto premium, kod RABAT50 daje -50%!"
                    ),
                    "comment",
                )
                method = t.bind(
                    gr.Radio(
                        ["bm25", "dense", "hybrid"],
                        value=moderator.settings.retrieval.get("method", "dense"),
                        label=text("en", "rules.retriever"),
                    ),
                    "rules.retriever",
                )
                top_k = t.bind(gr.Slider(1, 6, value=3, step=1, label=text("en", "rules.count")), "rules.count")
                button = t.bind(gr.Button(text("en", "rules.button"), variant="primary"), "rules.button", "value")
                found = gr.HTML()
            with gr.Column():
                t.bind(gr.Markdown(text("en", "rules.title")), "rules.title", "value")
                gr.HTML(rules_html(moderator.rulebook.rules))
        button.click(search, [query, method, top_k], found)
