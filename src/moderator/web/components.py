"""
HTML pieces shared by the tabs: the header, the verdict card, the statistics tiles and the list of rules. All text
that comes from a model or a user is escaped before it is put into the page. Files a visitor downloads go to a fresh
random folder per request, so two people using the app at once never see or overwrite each other's results.
"""

from html import escape
from pathlib import Path
from uuid import uuid4

import pandas as pd

from moderator.rules import Rule, RuleBook
from moderator.schema import Moderation


def private_folder(output_dir: Path) -> Path:
    folder = output_dir / "web" / uuid4().hex
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def header(models: list[tuple[str, str]], missing: list[str] | None, rules: int) -> str:
    chips = "".join(f'<span class="chip model"><small>{role}</small>{escape(name)}</span>' for role, name in models)
    if missing is None:
        status = '<span class="status down">Ollama unreachable</span>'
    elif missing:
        status = f'<span class="status warn">missing: {escape(", ".join(missing))}</span>'
    else:
        status = '<span class="status up">Ollama connected</span>'
    return (
        '<div class="hero"><div class="hero-text"><h1>Comment Moderator</h1>'
        "<p>Forum comment moderation with a local LLM: verdicts, memes, whole files, a chat about them "
        f"and decisions that cite the forum rules ({rules} paragraphs).</p></div>"
        f'<div class="hero-side">{status}<div class="chips">{chips}</div></div></div>'
    )


def severity_meter(level: int) -> str:
    dots = "".join(f'<i class="{"on" if index < level else ""}"></i>' for index in range(3))
    return f'<span class="severity" title="severity {level} of 3">{dots}<small>{level}/3</small></span>'


def verdict_card(result: Moderation, rulebook: RuleBook | None = None) -> str:
    verdict = result.verdict
    parts = [
        f'<div class="verdict {verdict.decision}"><div class="verdict-head">'
        f'<span class="badge">{verdict.decision.upper()}</span>{severity_meter(verdict.severity)}'
        f'<span class="meta">{escape(result.model)} · {escape(result.mode)} · {result.latency_s:.1f} s</span></div>'
    ]
    if result.read_text is not None:
        parts.append(
            f'<div class="read"><span class="label">Read from the image</span><p>{escape(result.read_text)}</p></div>'
        )
    parts.append(f'<p class="reason">{escape(verdict.reason)}</p>')
    chips = "".join(f'<span class="chip cat {escape(name)}">{escape(name)}</span>' for name in verdict.categories)
    parts.append(f'<div class="chips">{chips}</div>')
    if result.mode.endswith("rag"):
        if rulebook is not None and verdict.rule in rulebook:
            rule = rulebook.get(verdict.rule)
            parts.append(
                f'<div class="cited"><span class="label">Cited rule</span>'
                f"<b>{escape(rule.id)} {escape(rule.title)}</b><p>{escape(rule.text)}</p></div>"
            )
        found = "".join(f'<span class="chip ghost">{escape(rule_id)}</span>' for rule_id in result.retrieved)
        parts.append(f'<div class="retrieved"><span class="label">Retrieved</span>{found}</div>')
    if result.error:
        parts.append(f'<p class="note">{escape(result.error)}</p>')
    parts.append("</div>")
    return "".join(parts)


def stats_tiles(table: pd.DataFrame) -> str:
    decisions = table["decision"].value_counts()
    tiles = [
        ("comments", len(table), ""),
        ("allow", int(decisions.get("allow", 0)), "allow"),
        ("review", int(decisions.get("review", 0)), "review"),
        ("remove", int(decisions.get("remove", 0)), "remove"),
        ("s per comment", f"{table['latency_s'].mean():.1f}", ""),
    ]
    body = "".join(f'<div class="tile {kind}"><b>{value}</b><span>{name}</span></div>' for name, value, kind in tiles)
    return f'<div class="tiles">{body}</div>'


def rules_html(rules: list[Rule]) -> str:
    return "".join(
        f'<div class="rule"><b>{escape(rule.id)} {escape(rule.title)}</b><p>{escape(rule.text)}</p></div>'
        for rule in rules
    )
