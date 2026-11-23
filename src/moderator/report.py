"""
Output files of a moderated table: a plain-text report with the removed and reviewed comments first, and an SVG
chart of the categories and decisions.
"""

from collections import Counter
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from moderator.schema import CATEGORIES, DECISIONS

DECISION_COLORS = {"allow": "#3a8f5c", "review": "#d9a21b", "remove": "#c2453d"}


def category_counts(table: pd.DataFrame) -> Counter:
    counts = Counter()
    for value in table["categories"].fillna("none"):
        counts.update(str(value).split(";"))
    return counts


def build_report(table: pd.DataFrame, source: str, model: str) -> str:
    total = len(table)
    decisions = table["decision"].value_counts()
    counts = category_counts(table)
    lines = [
        "COMMENT MODERATION REPORT",
        "=" * 60,
        f"Source file:   {source}",
        f"Model:         {model}",
        f"Created:       {datetime.now():%Y-%m-%d %H:%M}",
        f"Comments:      {total}",
        f"Toxic:         {int(table['toxic'].astype(bool).sum())} ({table['toxic'].astype(bool).mean():.0%})",
        "",
        "Decisions",
        "-" * 60,
    ]
    lines += [f"  {name:<10}{int(decisions.get(name, 0)):>4}" for name in DECISIONS]
    lines += ["", "Categories", "-" * 60]
    lines += [f"  {name:<14}{counts.get(name, 0):>4}" for name in CATEGORIES]
    flagged = table[table["decision"] != "allow"].sort_values("severity", ascending=False)
    lines += ["", f"Removed or sent to review ({len(flagged)})", "-" * 60]
    for row in flagged.itertuples():
        rule = f" {row.rule}" if isinstance(row.rule, str) and row.rule else ""
        lines.append(f"#{row.id} [{row.decision}, severity {row.severity}, {row.categories}{rule}]")
        lines.append(f"    {row.text}")
        lines.append(f"    -> {row.reason}")
    if "latency_s" in table:
        lines += ["", f"Average time per comment: {table['latency_s'].mean():.2f} s"]
    return "\n".join(lines) + "\n"


def save_report(table: pd.DataFrame, path: Path, source: str, model: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_report(table, source, model), encoding="utf-8")
    return path


def save_chart(table: pd.DataFrame, path: Path, title: str = "Moderation results") -> Path:
    counts = category_counts(table)
    categories = [name for name in CATEGORIES if name != "none"]
    decisions = table["decision"].value_counts()
    figure, (left, right) = plt.subplots(1, 2, figsize=(10, 4), gridspec_kw={"width_ratios": [3, 2]})
    left.bar(categories, [counts.get(name, 0) for name in categories], color="#4c6ef5")
    left.set_title("Comments per category")
    left.set_ylabel("comments")
    left.tick_params(axis="x", rotation=20)
    right.bar(
        DECISIONS,
        [int(decisions.get(name, 0)) for name in DECISIONS],
        color=[DECISION_COLORS[name] for name in DECISIONS],
    )
    right.set_title("Decisions")
    for axis in (left, right):
        axis.spines[["top", "right"]].set_visible(False)
        axis.yaxis.get_major_locator().set_params(integer=True)
        for bar in axis.patches:
            axis.annotate(
                f"{int(bar.get_height())}",
                (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                ha="center",
                va="bottom",
                fontsize=9,
            )
    figure.suptitle(title)
    figure.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, format=path.suffix.lstrip(".") or "svg")
    plt.close(figure)
    return path
