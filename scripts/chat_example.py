"""
A scripted run of the chat about data/comments.txt, so the example conversation in examples/chat comes from the
real model and can be repeated.
"""

from moderator.chat import ChatSession
from moderator.config import ROOT
from moderator.service import Moderator

OUTPUT = ROOT / "examples" / "chat"
QUESTIONS = [
    "Które komentarze są groźbami i dlaczego?",
    "A który z nich jest najpoważniejszy?",
    "Which comments look like spam, and which rules do they break?",
    "Ile komentarzy trzeba usunąć i jaka kategoria pojawia się najczęściej?",
]


def main() -> None:
    session = ChatSession(Moderator(), ROOT / "data" / "comments.txt")
    session.load()
    for question in QUESTIONS:
        print(f"\nYOU: {question}\nMODEL: ", end="", flush=True)
        for piece in session.ask(question):
            print(piece, end="", flush=True)
        print()
    for path in (
        session.report(OUTPUT / "report.txt"),
        session.chart(OUTPUT / "chart.svg"),
        session.save_log(OUTPUT / "chat_log.txt"),
    ):
        print(f"saved {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
