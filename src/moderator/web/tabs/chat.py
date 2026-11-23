"""
Chat tab: load a TXT file, ask about it with streamed answers, save the report, the chart and the chat log.
"""

from pathlib import Path

import gradio as gr

from moderator.chat import ChatSession
from moderator.config import ROOT
from moderator.service import Moderator
from moderator.web.components import private_folder
from moderator.web.i18n import Translator, both, both_plain, hint, text

QUESTIONS = [
    "Które komentarze są groźbami i dlaczego?",
    "Which comments look like spam?",
    "Ile komentarzy trzeba usunąć i za co najczęściej?",
]


def build(moderator: Moderator, t: Translator) -> None:
    def load(path: str | None, progress=gr.Progress()):
        if not path:
            raise gr.Error(both_plain("error.txt"))
        session = ChatSession(moderator, Path(path))
        session.load(progress.tqdm)
        removed = int((session.table["decision"] == "remove").sum())
        status = both("chat.status", total=len(session.table), removed=removed)
        return session, [], f'<p class="status-line">{status}</p>'

    def answer(question: str, history: list, session: ChatSession | None):
        if session is None:
            raise gr.Error(both_plain("error.load"))
        history = history + [{"role": "user", "content": question}, {"role": "assistant", "content": ""}]
        for piece in session.ask(question):
            history[-1]["content"] += piece
            yield "", history

    def export(session: ChatSession | None):
        if session is None:
            raise gr.Error(both_plain("error.load"))
        folder = private_folder(moderator.settings.output_dir)
        paths = (
            session.report(folder / "report.txt"),
            session.chart(folder / "chart.svg"),
            session.save_log(folder / "chat_log.txt"),
        )
        return [str(path) for path in paths]

    with t.bind(gr.Tab(text("en", "tab.chat")), "tab.chat"):
        session = gr.State(None)
        with gr.Row():
            with gr.Column(scale=1):
                upload = t.bind(
                    gr.File(
                        label=text("en", "chat.file"), file_types=[".txt"], value=str(ROOT / "data" / "comments.txt")
                    ),
                    "chat.file",
                )
                load_button = t.bind(
                    gr.Button(text("en", "chat.load"), variant="primary", size="lg"), "chat.load", "value"
                )
                status = gr.HTML(hint("chat.hint"))
                export_button = t.bind(gr.Button(text("en", "chat.export")), "chat.export", "value")
                files = t.bind(gr.File(label=text("en", "chat.files"), file_count="multiple"), "chat.files")
            with gr.Column(scale=2):
                chatbot = t.bind(gr.Chatbot(label=text("en", "chat.conversation"), height=460), "chat.conversation")
                question = t.bind_with(
                    gr.Textbox(label=text("en", "chat.question"), placeholder=text("en", "chat.placeholder")),
                    lambda lang: {"label": text(lang, "chat.question"), "placeholder": text(lang, "chat.placeholder")},
                )
                gr.Examples(QUESTIONS, inputs=question, label="Examples · Przykłady")
        load_button.click(load, upload, [session, chatbot, status])
        question.submit(answer, [question, chatbot, session], [question, chatbot])
        export_button.click(export, session, files)
