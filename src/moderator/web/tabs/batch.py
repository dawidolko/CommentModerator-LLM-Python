"""
Batch tab: upload a file, get statistics tiles, the chart, the table and the three output files.
"""

from pathlib import Path

import gradio as gr

from moderator.batch import moderate_frame, read_comments, save
from moderator.config import ROOT
from moderator.report import save_chart, save_report
from moderator.service import MODES, Moderator
from moderator.web.components import private_folder, stats_tiles
from moderator.web.i18n import Translator, both_plain, hint, text

COLUMNS = ["id", "decision", "categories", "severity", "rule", "reason", "text"]


def build(moderator: Moderator, t: Translator) -> None:
    def run(path: str | None, mode: str, progress=gr.Progress()):
        if not path:
            raise gr.Error(both_plain("error.file"))
        source = Path(path)
        table, _ = moderate_frame(moderator, read_comments(source), mode, progress.tqdm)
        folder = private_folder(moderator.settings.output_dir)
        csv = save(table, folder / f"{source.stem}_moderated.csv")
        report = save_report(table, folder / f"{source.stem}_report.txt", source.name, moderator.settings.text_model)
        chart = save_chart(table, folder / f"{source.stem}_chart.svg", f"Moderation of {source.name}")
        return (
            stats_tiles(table),
            gr.update(value=str(chart), visible=True),
            gr.update(value=table[COLUMNS], visible=True),
            gr.update(value=[str(csv), str(report), str(chart)], visible=True),
        )

    with t.bind(gr.Tab(text("en", "tab.batch")), "tab.batch"):
        with gr.Row(equal_height=False):
            with gr.Column(scale=1, min_width=300):
                upload = t.bind(
                    gr.File(
                        label=text("en", "batch.file"),
                        file_types=[".csv", ".txt"],
                        value=str(ROOT / "data" / "comments.csv"),
                    ),
                    "batch.file",
                )
                mode = t.bind(gr.Radio(list(MODES), value="few-shot", label=text("en", "mode")), "mode")
                button = t.bind(
                    gr.Button(text("en", "batch.button"), variant="primary", size="lg"), "batch.button", "value"
                )
                files = t.bind(
                    gr.File(label=text("en", "batch.files"), file_count="multiple", visible=False), "batch.files"
                )
            with gr.Column(scale=2):
                tiles = gr.HTML(hint("batch.hint"), elem_id="batch-tiles")
                chart = gr.Image(label="Chart", type="filepath", show_label=False, visible=False)
        table = t.bind(
            gr.Dataframe(
                label=text("en", "batch.table"),
                wrap=True,
                max_height=520,
                column_widths=["5%", "9%", "13%", "8%", "7%", "29%", "29%"],
                elem_id="batch-table",
                visible=False,
            ),
            "batch.table",
        )
        button.click(run, [upload, mode], [tiles, chart, table, files])
