"""
Moderator: the one entry point used by the CLI, the web app and the scripts, so every interface gives the same
answer for the same comment. The rules and the retriever are built on first use.
"""

from functools import cached_property
from pathlib import Path

from moderator.classify import classify
from moderator.config import Settings, settings
from moderator.llm import LLM
from moderator.rag import moderate_with_rules
from moderator.retrieval import Retriever
from moderator.rules import RuleBook
from moderator.schema import Moderation
from moderator.vision import moderate_image

MODES = ("zero-shot", "few-shot", "rag")


class Moderator:
    def __init__(self, config: Settings | None = None):
        self.settings = config or settings()
        self.llm = LLM(self.settings)

    @cached_property
    def rulebook(self) -> RuleBook:
        return RuleBook.load(self.settings.path("rules"))

    @cached_property
    def retriever(self) -> Retriever:
        dense = self.llm if self.settings.retrieval.get("use_embeddings", True) else None
        skip = tuple(f"{section}." for section in self.settings.retrieval.get("skip_sections", []))
        rules = [rule for rule in self.rulebook.rules if not rule.id.startswith(skip)]
        return Retriever(rules, dense, self.settings.retrieval.get("rrf_k", 60))

    def text(self, text: str, mode: str = "few-shot") -> Moderation:
        if mode == "rag":
            options = self.settings.retrieval
            return moderate_with_rules(
                self.llm,
                self.rulebook,
                self.retriever,
                text,
                top_k=options.get("top_k", 3),
                method=options.get("method", "dense"),
                always=options.get("always_include", []),
            )
        return classify(self.llm, text, mode)

    def image(self, image: Path | bytes, mode: str = "rag") -> Moderation:
        return moderate_image(self.llm, image, lambda text: self.text(text, mode))
