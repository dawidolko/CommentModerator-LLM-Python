"""
The forum rules split into paragraphs (### §X.Y headings). Each paragraph is one document for retrieval and the
list of ids against which a cited rule is checked.
"""

import re
from dataclasses import dataclass
from pathlib import Path

HEADING = re.compile(r"^###\s+(§\d+\.\d+)\s+(.+)$")


@dataclass(frozen=True)
class Rule:
    id: str
    title: str
    text: str

    def render(self) -> str:
        return f"{self.id} {self.title}: {self.text}"


class RuleBook:
    def __init__(self, rules: list[Rule]):
        self.rules = rules
        self.by_id = {rule.id: rule for rule in rules}

    @classmethod
    def load(cls, path: Path) -> "RuleBook":
        return cls(parse(path.read_text(encoding="utf-8")))

    def __len__(self) -> int:
        return len(self.rules)

    def __contains__(self, rule_id: str | None) -> bool:
        return rule_id in self.by_id

    def get(self, rule_id: str) -> Rule:
        return self.by_id[rule_id]


def parse(markdown: str) -> list[Rule]:
    rules: list[Rule] = []
    current: tuple[str, str] | None = None
    body: list[str] = []
    for line in markdown.splitlines():
        match = HEADING.match(line.strip())
        if match or line.startswith("## "):
            if current:
                rules.append(Rule(current[0], current[1], " ".join(body).strip()))
            current = (match.group(1), match.group(2).strip()) if match else None
            body = []
        elif current and line.strip():
            body.append(line.strip())
    if current:
        rules.append(Rule(current[0], current[1], " ".join(body).strip()))
    return rules
