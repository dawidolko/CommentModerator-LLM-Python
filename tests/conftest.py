"""
Shared fixtures: the settings, the rules and a fake LLM that returns prepared answers and records the calls.
"""

import json

import pytest

from moderator.config import ROOT, load_settings
from moderator.rules import RuleBook


class FakeLLM:
    def __init__(self, answers: list[str], settings):
        self.answers = list(answers)
        self.settings = settings
        self.calls: list[dict] = []

    def chat(self, messages, options=None, format=None, model=None):
        self.calls.append({"messages": messages, "format": format})
        return self.answers.pop(0)

    def stream(self, messages, options=None):
        yield from self.answers.pop(0).split(" ")

    def embed(self, texts):
        return [[float(len(text) % 7 + 1), float(text.count("§") + 1), 1.0] for text in texts]


def verdict(**overrides) -> str:
    base = {
        "toxic": True,
        "categories": ["insult"],
        "severity": 2,
        "decision": "remove",
        "reason": "Insult.",
        "rule": "§2.1",
    }
    return json.dumps({**base, **overrides})


@pytest.fixture
def settings():
    return load_settings(ROOT / "config.yaml")


@pytest.fixture
def rulebook():
    return RuleBook.load(ROOT / "data" / "rules" / "forum_rules.md")


@pytest.fixture
def fake_llm(settings):
    return lambda *answers: FakeLLM(list(answers), settings)
