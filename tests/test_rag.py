"""
Splitting the rules, retrieval and the checks of a cited paragraph.
"""

from moderator.rag import moderate_with_rules
from moderator.retrieval import Retriever, rrf, tokens
from moderator.rules import parse
from tests.conftest import verdict


def test_rulebook_has_every_paragraph(rulebook):
    assert len(rulebook) == 14
    assert "§2.1" in rulebook and "§5.3" in rulebook
    assert rulebook.get("§3.1").title == "Zakaz gróźb"


def test_parse_ignores_section_text_outside_paragraphs():
    rules = parse("# Title\nintro\n## §1 Part\nnot a rule\n### §1.1 First\nline one\nline two\n## §2 Next\n")
    assert [(rule.id, rule.text) for rule in rules] == [("§1.1", "line one line two")]


def test_tokens_strip_polish_letters_and_cut_to_a_stem():
    assert tokens("Zabronione są GROŹBY") == ["zabro", "sa", "grozb"]


def test_rrf_rewards_documents_found_by_both_rankings():
    assert rrf([[0, 1, 2], [2, 0, 1]])[0] == 0


def test_bm25_finds_the_advertising_paragraph(rulebook):
    found = Retriever(rulebook.rules).search("kod rabatowy, promocja, kup teraz", method="bm25")
    assert found[0].id == "§5.1"


def test_rag_keeps_a_cited_rule_that_exists(fake_llm, rulebook):
    llm = fake_llm(verdict(rule="§2.1"))
    result = moderate_with_rules(llm, rulebook, Retriever(rulebook.rules), "jesteś idiotą", method="bm25")
    assert result.verdict.rule == "§2.1"
    assert result.retrieved[0] == "§2.1"
    assert "§2.1 Zakaz obrażania" in llm.calls[0]["messages"][0]["content"]


def test_rag_sends_a_made_up_rule_to_review(fake_llm, rulebook):
    result = moderate_with_rules(
        fake_llm(verdict(rule="§9.9")), rulebook, Retriever(rulebook.rules), "x", method="bm25"
    )
    assert result.verdict.decision == "review"
    assert result.verdict.rule is None
    assert "§9.9" in result.error


def test_rag_sends_a_removal_without_a_rule_to_review(fake_llm, rulebook):
    result = moderate_with_rules(fake_llm(verdict(rule=None)), rulebook, Retriever(rulebook.rules), "x", method="bm25")
    assert result.verdict.decision == "review"
    assert "without a paragraph" in result.error


def test_rag_sends_the_retrieved_paragraphs_as_the_allowed_rules(fake_llm, rulebook):
    llm = fake_llm(verdict(rule="§2.1"))
    result = moderate_with_rules(llm, rulebook, Retriever(rulebook.rules), "idiota", method="bm25", always=["§2.3"])
    assert llm.calls[0]["format"]["properties"]["rule"]["enum"] == result.retrieved
    assert "§2.3" in result.retrieved
