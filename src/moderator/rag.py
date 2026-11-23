"""
Moderation grounded in the forum rules. The retrieved paragraphs go into the prompt and also become the only allowed
values of `rule` in the schema; a removal without a paragraph is downgraded to `review`.
"""

import time

from moderator.classify import ask_for_verdict
from moderator.llm import LLM
from moderator.prompts import moderation_messages
from moderator.retrieval import Retriever
from moderator.rules import RuleBook
from moderator.schema import Moderation


def moderate_with_rules(
    llm: LLM,
    rulebook: RuleBook,
    retriever: Retriever,
    text: str,
    top_k: int = 3,
    method: str = "dense",
    always: list[str] | None = None,
) -> Moderation:
    started = time.perf_counter()
    found = retriever.search(text, top_k=top_k, method=method)
    for rule_id in always or []:
        if rule_id in rulebook and rulebook.get(rule_id) not in found:
            found.append(rulebook.get(rule_id))
    context = "\n".join(rule.render() for rule in found)
    verdict, error = ask_for_verdict(
        llm, moderation_messages(text, "few-shot", rules=context), with_rule=True, rule_ids=[rule.id for rule in found]
    )
    if verdict.rule is not None and verdict.rule not in rulebook:
        error = f"the model cited {verdict.rule}, which is not in the rules"
        verdict = verdict.model_copy(update={"decision": "review", "rule": None})
    elif verdict.decision == "remove" and verdict.rule is None:
        error = "removal without a paragraph of the rules, sent to review"
        verdict = verdict.model_copy(update={"decision": "review"})
    return Moderation(
        text=text,
        verdict=verdict,
        mode="rag",
        model=llm.settings.text_model,
        latency_s=time.perf_counter() - started,
        error=error,
        retrieved=[rule.id for rule in found],
    )
