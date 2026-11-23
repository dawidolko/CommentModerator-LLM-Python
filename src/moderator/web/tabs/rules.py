"""
Rules tab: the paragraphs of the forum rules and a search box for the three retrievers.
"""

import gradio as gr

from moderator.service import Moderator
from moderator.web.components import rules_html


def build(moderator: Moderator) -> None:
    def search(query: str, method: str, top_k: int) -> str:
        if not query.strip():
            raise gr.Error("Write a comment to search with.")
        return rules_html(moderator.retriever.search(query, top_k=int(top_k), method=method))

    with gr.Tab("Rules (RAG)"):
        with gr.Row():
            with gr.Column():
                query = gr.Textbox(label="Comment", lines=3, value="Kup tanie konto premium, kod RABAT50 daje -50%!")
                method = gr.Radio(
                    ["bm25", "dense", "hybrid"],
                    value=moderator.settings.retrieval.get("method", "dense"),
                    label="Retriever",
                )
                top_k = gr.Slider(1, 6, value=3, step=1, label="Paragraphs")
                button = gr.Button("Find paragraphs", variant="primary")
                found = gr.HTML()
            with gr.Column():
                gr.Markdown("### Forum rules")
                gr.HTML(rules_html(moderator.rulebook.rules))
        button.click(search, [query, method, top_k], found)
