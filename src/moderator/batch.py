"""
Moderation of a whole file: a CSV with a `text` column or a TXT with one comment per line in, a table with one
verdict per comment out.
"""

from collections.abc import Callable, Iterable
from pathlib import Path

import pandas as pd

from moderator.schema import Moderation
from moderator.service import Moderator

COLUMNS = ["id", "text", "toxic", "categories", "severity", "decision", "reason", "rule", "latency_s"]


def read_comments(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        frame = pd.read_csv(path)
        if "text" not in frame.columns:
            raise ValueError(f"{path.name} needs a 'text' column")
    else:
        lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
        frame = pd.DataFrame({"text": [line for line in lines if line]})
    if "id" not in frame.columns:
        frame.insert(0, "id", range(1, len(frame) + 1))
    return frame


def moderate_frame(
    moderator: Moderator, frame: pd.DataFrame, mode: str = "few-shot", progress: Callable[[Iterable], Iterable] = iter
) -> tuple[pd.DataFrame, list[Moderation]]:
    results = [moderator.text(str(text), mode) for text in progress(frame["text"].tolist())]
    rows = [{"id": comment_id, **result.row()} for comment_id, result in zip(frame["id"], results, strict=True)]
    return pd.DataFrame(rows, columns=COLUMNS), results


def save(table: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(path, index=False)
    return path
