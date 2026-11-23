"""
Conversation about a file of comments. The file is moderated once (cached by its hash), the results go into the
system prompt as a table, and every question and answer is kept in the history so follow-up questions work.
"""

import hashlib
from collections.abc import Callable, Iterable, Iterator
from datetime import datetime
from pathlib import Path

import pandas as pd

from moderator.batch import moderate_frame, read_comments
from moderator.prompts import CHAT_SYSTEM
from moderator.report import save_chart, save_report
from moderator.service import Moderator

COMMANDS = {
    "/report": "save a .txt report",
    "/chart": "save an .svg chart",
    "/save": "save this conversation as .txt",
    "/help": "list the commands",
    "/exit": "leave the chat",
}


class ChatSession:
    def __init__(self, moderator: Moderator, source: Path, mode: str = "rag"):
        self.moderator = moderator
        self.source = source
        self.mode = mode
        self.table: pd.DataFrame | None = None
        self.history: list[dict] = []
        self.log: list[tuple[str, str]] = []

    @property
    def cache_file(self) -> Path:
        digest = hashlib.sha1(self.source.read_bytes()).hexdigest()[:10]
        return self.moderator.settings.output_dir / "cache" / f"{self.source.stem}-{self.mode}-{digest}.csv"

    def load(self, progress: Callable[[Iterable], Iterable] = iter) -> pd.DataFrame:
        if self.cache_file.exists():
            self.table = pd.read_csv(self.cache_file, keep_default_na=False)
        else:
            self.table, _ = moderate_frame(self.moderator, read_comments(self.source), self.mode, progress)
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            self.table.to_csv(self.cache_file, index=False)
        return self.table

    def context(self) -> str:
        lines = ["id | decision | categories | severity | rule | reason | text"]
        for row in self.table.itertuples():
            lines.append(
                f"#{row.id} | {row.decision} | {row.categories} | {row.severity} | {row.rule or '-'} | "
                f"{row.reason} | {row.text}"
            )
        return "\n".join(lines)

    def messages(self, question: str) -> list[dict]:
        system = {"role": "system", "content": CHAT_SYSTEM.format(table=self.context())}
        return [system, *self.history, {"role": "user", "content": question}]

    def ask(self, question: str) -> Iterator[str]:
        answer = ""
        for piece in self.moderator.llm.stream(self.messages(question)):
            answer += piece
            yield piece
        self.history += [{"role": "user", "content": question}, {"role": "assistant", "content": answer}]
        self.log += [("you", question), ("model", answer)]

    def report(self, path: Path | None = None) -> Path:
        path = path or self.moderator.settings.output_dir / "report.txt"
        return save_report(self.table, path, self.source.name, self.moderator.settings.text_model)

    def chart(self, path: Path | None = None) -> Path:
        path = path or self.moderator.settings.output_dir / "chart.svg"
        return save_chart(self.table, path, f"Moderation of {self.source.name}")

    def save_log(self, path: Path | None = None) -> Path:
        path = path or self.moderator.settings.output_dir / "chat_log.txt"
        header = [
            f"Chat about {self.source.name}",
            f"Model: {self.moderator.settings.text_model}",
            f"Date: {datetime.now():%Y-%m-%d %H:%M}",
            "",
        ]
        body = [f"{speaker.upper()}: {text}\n" for speaker, text in self.log]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(header + body), encoding="utf-8")
        return path
