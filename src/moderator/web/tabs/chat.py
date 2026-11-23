"""
Chat tab: load a TXT file, ask about it with streamed answers, save the report, the chart and the chat log.
"""

from pathlib import Path

import gradio as gr

from moderator.chat import ChatSession
from moderator.config import ROOT
from moderator.service import Moderator

QUESTIONS = [
    "Które komentarze są groźbami i dlaczego?",
    "Which comments look like spam?",
    "Ile komentarzy trzeba usunąć i za co najczęściej?",
]


def build(moderator: Moderator) -> None:
    def load(path: str | None, progress=gr.Progress()):
        if not path:
            raise gr.Error("Upload a .txt file first.")
        session = ChatSession(moderator, Path(path))
        session.load(progress.tqdm)
        removed = int((session.table["decision"] == "remove").sum())
        status = f"{len(session.table)} comments moderated, {removed} to remove. Ask about them."
        return session, [], status

    def answer(question: str, history: list, session: ChatSession | None):
        if session is None:
            raise gr.Error("Load a file first.")
        history = history + [{"role": "user", "content": question}, {"role": "assistant", "content": ""}]
        for piece in session.ask(question):
            history[-1]["content"] += piece
            yield "", history

    def export(session: ChatSession | None):
        if session is None:
            raise gr.Error("Load a file first.")
        return [str(session.report()), str(session.chart()), str(session.save_log())]

    with gr.Tab("Chat about a file"):
        session = gr.State(None)
        with gr.Row():
            with gr.Column(scale=1):
                upload = gr.File(
                    label="Comments (.txt, one per line)",
                    file_types=[".txt"],
                    value=str(ROOT / "data" / "comments.txt"),
                )
                load_button = gr.Button("Load and moderate", variant="primary", size="lg")
                status = gr.Markdown(
                    '<p class="hint">Load the file first; every comment is moderated once and cached.</p>'
                )
                export_button = gr.Button("Save report.txt, chart.svg and the chat log")
                files = gr.File(label="Saved files", file_count="multiple")
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(label="Conversation", height=460)
                question = gr.Textbox(label="Question", placeholder="Ask about the comments")
                gr.Examples(QUESTIONS, inputs=question, label="Try asking")
        load_button.click(load, upload, [session, chatbot, status])
        question.submit(answer, [question, chatbot, session], [question, chatbot])
        export_button.click(export, session, files)
