"""
The verdict schema and the retry and fallback of plain classification.
"""

import pytest
from pydantic import ValidationError

from moderator.classify import classify
from moderator.schema import Verdict, verdict_schema
from tests.conftest import verdict


def test_categories_drop_none_when_a_real_category_is_present():
    result = Verdict(toxic=True, categories=["none", "insult", "insult"], severity=2, decision="remove", reason="x")
    assert result.categories == ["insult"]


def test_empty_categories_become_none():
    assert Verdict(toxic=False, categories=[], severity=0, decision="allow", reason="ok").categories == ["none"]


def test_rule_gets_a_paragraph_sign_and_empty_values_become_none():
    assert (
        Verdict(toxic=True, categories=["spam"], severity=2, decision="remove", reason="x", rule="5.1").rule == "§5.1"
    )
    assert Verdict(toxic=False, categories=["none"], severity=0, decision="allow", reason="x", rule="null").rule is None


def test_unknown_category_and_severity_out_of_range_are_rejected():
    with pytest.raises(ValidationError):
        Verdict(toxic=True, categories=["rude"], severity=2, decision="remove", reason="x")
    with pytest.raises(ValidationError):
        Verdict(toxic=True, categories=["insult"], severity=5, decision="remove", reason="x")


def test_schema_without_rule_for_plain_classification():
    assert "rule" not in verdict_schema(False)["properties"]
    assert "rule" in verdict_schema(True)["required"]


def test_classify_retries_once_after_invalid_json(fake_llm):
    llm = fake_llm("not json", verdict(rule=None))
    result = classify(llm, "you clown", "few-shot")
    assert result.verdict.decision == "remove"
    assert len(llm.calls) == 2
    assert result.error is None


def test_classify_falls_back_to_review_after_two_failures(fake_llm):
    result = classify(fake_llm("{", "{}"), "text", "zero-shot")
    assert result.verdict.decision == "review"
    assert "invalid JSON" in result.error


def test_zero_shot_sends_no_examples(fake_llm):
    llm = fake_llm(verdict(), verdict())
    classify(llm, "a", "zero-shot")
    classify(llm, "a", "few-shot")
    assert len(llm.calls[0]["messages"]) == 2
    assert len(llm.calls[1]["messages"]) > 2


def test_schema_limits_the_rule_to_the_retrieved_paragraphs():
    schema = verdict_schema(True, ["§2.1", "§2.3"])
    assert schema["properties"]["rule"] == {"type": "string", "enum": ["§2.1", "§2.3"]}
