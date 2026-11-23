"""
Reading comment files, the text report and the SVG chart.
"""

import pandas as pd

from moderator.batch import read_comments
from moderator.report import build_report, category_counts, save_chart

TABLE = pd.DataFrame(
    [
        {
            "id": 1,
            "text": "hi",
            "toxic": False,
            "categories": "none",
            "severity": 0,
            "decision": "allow",
            "reason": "ok",
            "rule": "",
            "latency_s": 1.0,
        },
        {
            "id": 2,
            "text": "you clown",
            "toxic": True,
            "categories": "insult",
            "severity": 2,
            "decision": "remove",
            "reason": "insult",
            "rule": "§2.1",
            "latency_s": 2.0,
        },
        {
            "id": 3,
            "text": "buy now",
            "toxic": True,
            "categories": "spam;insult",
            "severity": 1,
            "decision": "review",
            "reason": "ad",
            "rule": "§5.1",
            "latency_s": 3.0,
        },
    ]
)


def test_category_counts_split_multiple_categories():
    assert category_counts(TABLE) == {"none": 1, "insult": 2, "spam": 1}


def test_report_lists_flagged_comments_by_severity():
    report = build_report(TABLE, "comments.txt", "qwen2.5:7b")
    assert "Comments:      3" in report
    assert report.index("#2 [remove") < report.index("#3 [review")
    assert "#1 [" not in report
    assert "Average time per comment: 2.00 s" in report


def test_chart_is_an_svg(tmp_path):
    path = save_chart(TABLE, tmp_path / "chart.svg")
    content = path.read_text()
    assert content.lstrip().startswith("<?xml") and "<svg" in content


def test_read_comments_from_txt_numbers_the_lines(tmp_path):
    source = tmp_path / "c.txt"
    source.write_text("first\n\nsecond\n", encoding="utf-8")
    frame = read_comments(source)
    assert frame["id"].tolist() == [1, 2]
    assert frame["text"].tolist() == ["first", "second"]


def test_every_web_request_gets_its_own_folder(tmp_path):
    from moderator.web.components import private_folder

    first, second = private_folder(tmp_path), private_folder(tmp_path)
    assert first != second
    assert first.parent == second.parent == tmp_path / "web"
