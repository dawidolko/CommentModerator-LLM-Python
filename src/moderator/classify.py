"""
Zero-shot and few-shot moderation of one comment. An answer that is not valid JSON for the schema is retried once;
a second failure becomes a `review` verdict, so a broken answer never lets a comment through.
"""

import json
import time

from pydantic import ValidationError

from moderator.llm import LLM
from moderator.prompts import moderation_messages
from moderator.schema import Moderation, Verdict, fallback, verdict_schema

MODES = ("zero-shot", "few-shot")


def ask_for_verdict(
    llm: LLM, messages: list[dict], with_rule: bool, rule_ids: list[str] | None = None
) -> tuple[Verdict, str | None]:
    schema = verdict_schema(with_rule, rule_ids)
    error = None
    for attempt in range(2):
        raw = llm.chat(messages, format=schema)
        try:
            return Verdict.model_validate(json.loads(raw)), None
        except (json.JSONDecodeError, ValidationError) as problem:
            error = f"invalid JSON after {attempt + 1} attempts: {str(problem).splitlines()[0]}"
    return fallback("The model did not return a valid answer, a human should check this comment."), error


def classify(llm: LLM, text: str, mode: str = "few-shot") -> Moderation:
    started = time.perf_counter()
    verdict, error = ask_for_verdict(llm, moderation_messages(text, mode), with_rule=False)
    return Moderation(
        text=text,
        verdict=verdict,
        mode=mode,
        model=llm.settings.text_model,
        latency_s=time.perf_counter() - started,
        error=error,
    )
