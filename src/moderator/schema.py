"""
The verdict every mode returns. The same Pydantic model is turned into the JSON schema passed to Ollama's
`format`, so the model cannot answer with a category, decision or severity outside the lists below.
"""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

CATEGORIES = ("insult", "obscene", "threat", "identity_hate", "spam", "none")
DECISIONS = ("allow", "review", "remove")

Category = Literal["insult", "obscene", "threat", "identity_hate", "spam", "none"]
Decision = Literal["allow", "review", "remove"]


class Verdict(BaseModel):
    toxic: bool
    categories: list[Category]
    severity: int = Field(ge=0, le=3)
    decision: Decision
    reason: str
    rule: str | None = None

    @field_validator("categories")
    @classmethod
    def tidy_categories(cls, value: list[str]) -> list[str]:
        unique = list(dict.fromkeys(value))
        real = [item for item in unique if item != "none"]
        return real or ["none"]

    @field_validator("rule")
    @classmethod
    def tidy_rule(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value or value.lower() in {"none", "null", "-"}:
            return None
        return value if value.startswith("§") else f"§{value}"


class Moderation(BaseModel):
    text: str
    verdict: Verdict
    mode: str
    model: str
    latency_s: float
    error: str | None = None
    retrieved: list[str] = Field(default_factory=list)
    read_text: str | None = None

    def row(self) -> dict:
        return {
            "text": self.text,
            "toxic": self.verdict.toxic,
            "categories": ";".join(self.verdict.categories),
            "severity": self.verdict.severity,
            "decision": self.verdict.decision,
            "reason": self.verdict.reason,
            "rule": self.verdict.rule or "",
            "latency_s": round(self.latency_s, 2),
        }


def verdict_schema(with_rule: bool, rule_ids: list[str] | None = None) -> dict:
    schema = Verdict.model_json_schema()
    if not with_rule:
        schema["properties"].pop("rule", None)
    elif rule_ids:
        schema["properties"]["rule"] = {"type": "string", "enum": rule_ids}
    schema["required"] = ["toxic", "categories", "severity", "decision", "reason"] + (["rule"] if with_rule else [])
    return schema


def fallback(reason: str) -> Verdict:
    return Verdict(toxic=False, categories=["none"], severity=0, decision="review", reason=reason)
