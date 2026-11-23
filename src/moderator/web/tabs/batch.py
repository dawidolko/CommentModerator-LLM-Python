"""
Batch tab: upload a file, get statistics tiles, the chart, the table and the three output files.
"""

from pathlib import Path

import gradio as gr

from moderator.batch import moderate_frame, read_comments, save
from moderator.config import ROOT
from moderator.report import save_chart, save_report
from moderator.service import MODES, Moderator
from moderator.web.components import stats_tiles

COLUMNS = ["id", "decision", "categories", "severity", "rule", "reason", "text"]


def build(moderator: Moderator) -> None:
    def run(path: str | None, mode: str, progress=gr.Progress()):
        if not path:
            raise gr.Error("Upload a .csv or .txt file first.")
        source = Path(path)
        table, _ = moderate_frame(moderator, read_comments(source), mode, progress.tqdm)
        folder = moderator.settings.output_dir / "web"
        csv = save(table, folder / f"{source.stem}_moderated.csv")
        report = save_report(table, folder / f"{source.stem}_report.txt", source.name, moderator.settings.text_model)
        chart = save_chart(table, folder / f"{source.stem}_chart.svg", f"Moderation of {source.name}")
        return stats_tiles(table), str(chart), table[COLUMNS], [str(csv), str(report), str(chart)]

    with gr.Tab("Batch"):
        with gr.Row(equal_height=False):
            with gr.Column(scale=1, min_width=300):
                upload = gr.File(
                    label="Comments (.csv with a text column or .txt)",
                    file_types=[".csv", ".txt"],
                    value=str(ROOT / "data" / "comments.csv"),
                )
                mode = gr.Radio(list(MODES), value="few-shot", label="Mode")
                button = gr.Button("Moderate the file", variant="primary", size="lg")
                files = gr.File(label="Results: CSV, report.txt, chart.svg", file_count="multiple")
            with gr.Column(scale=2):
                tiles = gr.HTML('<p class="hint">Results appear here after the run.</p>', elem_id="batch-tiles")
                chart = gr.Image(label="Chart", type="filepath", show_label=False)
        table = gr.Dataframe(
            label="Moderated comments",
            wrap=True,
            max_height=520,
            column_widths=["5%", "9%", "13%", "8%", "7%", "29%", "29%"],
            elem_id="batch-table",
        )
        button.click(run, [upload, mode], [tiles, chart, table, files])
