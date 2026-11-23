"""
Comparison on the labelled comments: toxic-bert at 0.5 and at the precision = recall point of the PR curve (as in
Lab 2.3), the LLM in zero-shot, few-shot and RAG mode, and recall of the three retrievers.
"""

from collections.abc import Callable, Iterable
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import precision_recall_curve, precision_recall_fscore_support

from moderator import baseline
from moderator.batch import moderate_frame
from moderator.service import Moderator

LLM_VARIANTS = ("zero-shot", "few-shot", "rag")
RETRIEVERS = ("bm25", "dense", "hybrid")


def toxic_scores(gold: pd.Series, predicted: pd.Series) -> dict:
    precision, recall, f1, _ = precision_recall_fscore_support(
        gold.astype(int), predicted.astype(int), average="binary", zero_division=0
    )
    return {"precision": precision, "recall": recall, "f1": f1}


def category_accuracy(gold: pd.Series, predicted: pd.Series) -> float:
    hits = [want in str(got).split(";") for want, got in zip(gold, predicted, strict=True)]
    return float(np.mean(hits))


def pr_threshold(gold: pd.Series, scores: list[float]) -> float:
    precision, recall, thresholds = precision_recall_curve(gold.astype(int), scores)
    gap = np.abs(precision[:-1] - recall[:-1])
    return float(thresholds[int(np.argmin(gap))])


def evaluate_baseline(settings, data: pd.DataFrame) -> tuple[list[dict], pd.DataFrame]:
    model = settings.baseline["model"]
    label_scores = baseline.scores(data["text"].tolist(), model)
    top = [max(scores.values()) for scores in label_scores]
    rows, table = [], data[["id", "lang", "toxic", "category"]].copy()
    table["bert_score"] = [round(value, 4) for value in top]
    for name, threshold in (("toxic-bert @0.50", 0.5), ("toxic-bert @PR", pr_threshold(data["toxic"], top))):
        verdicts = [baseline.verdict(scores, threshold) for scores in label_scores]
        predicted = pd.Series([item["toxic"] for item in verdicts])
        categories = pd.Series([";".join(item["categories"]) for item in verdicts])
        for subset, mask in (("all", data["lang"].notna()), ("en", data["lang"] == "en"), ("pl", data["lang"] == "pl")):
            rows.append(
                {
                    "variant": name,
                    "subset": subset,
                    "threshold": round(threshold, 3),
                    **toxic_scores(data["toxic"][mask], predicted[mask.values]),
                    "category_acc": category_accuracy(data["category"][mask], categories[mask.values]),
                    "rule_acc": np.nan,
                    "latency_s": np.nan,
                }
            )
    return rows, table


def evaluate_llm(
    moderator: Moderator, data: pd.DataFrame, progress: Callable[[Iterable], Iterable] = iter
) -> tuple[list[dict], dict[str, pd.DataFrame]]:
    rows, tables = [], {}
    for mode in LLM_VARIANTS:
        table, _ = moderate_frame(moderator, data, mode, progress)
        tables[mode] = table
        for subset, mask in (("all", data["lang"].notna()), ("en", data["lang"] == "en"), ("pl", data["lang"] == "pl")):
            part = table[mask.values]
            rows.append(
                {
                    "variant": f"LLM {mode}",
                    "subset": subset,
                    "threshold": np.nan,
                    **toxic_scores(data["toxic"][mask], part["toxic"]),
                    "category_acc": category_accuracy(data["category"][mask], part["categories"]),
                    "rule_acc": float((part["rule"].values == data["rule"][mask].values).mean())
                    if mode == "rag"
                    else np.nan,
                    "latency_s": part["latency_s"].mean(),
                }
            )
    return rows, tables


def evaluate_retrieval(moderator: Moderator, data: pd.DataFrame) -> list[dict]:
    rows = []
    for method in RETRIEVERS:
        ranks = []
        for text, gold in zip(data["text"], data["rule"], strict=True):
            order = [moderator.retriever.rules[index].id for index in moderator.retriever.ranking(text, method)]
            ranks.append(order.index(gold) + 1)
        ranks = np.array(ranks)
        rows.append(
            {
                "retriever": method,
                "recall@1": float((ranks <= 1).mean()),
                "recall@3": float((ranks <= 3).mean()),
                "mrr": float((1 / ranks).mean()),
            }
        )
    return rows


def save_chart(results: pd.DataFrame, path: Path) -> Path:
    data = results[results["subset"] == "all"].set_index("variant")
    metrics = ["precision", "recall", "f1", "category_acc"]
    figure, axis = plt.subplots(figsize=(10, 4.2))
    width = 0.8 / len(metrics)
    positions = np.arange(len(data))
    for offset, metric in enumerate(metrics):
        axis.bar(positions + offset * width, data[metric], width, label=metric)
    axis.set_xticks(positions + width * (len(metrics) - 1) / 2, data.index, rotation=12)
    axis.set_ylim(0, 1.05)
    axis.set_title("Toxic class on 40 labelled comments")
    axis.legend(ncols=4, loc="lower right", fontsize=9)
    axis.spines[["top", "right"]].set_visible(False)
    figure.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path)
    plt.close(figure)
    return path


def markdown_table(frame: pd.DataFrame) -> str:
    header = "| " + " | ".join(frame.columns) + " |"
    divider = "| " + " | ".join("---" for _ in frame.columns) + " |"
    lines = [header, divider]
    for row in frame.itertuples(index=False):
        cells = [
            f"{value:.3f}"
            if isinstance(value, float) and not np.isnan(value)
            else ("–" if isinstance(value, float) else str(value))
            for value in row
        ]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)
