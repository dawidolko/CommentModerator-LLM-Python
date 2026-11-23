"""
Comments posted as images. The vision model writes out the text of the meme or screenshot, the answer is cleaned of
labels and repeated lines (small models repeat them), and the text is moderated like any other comment.
"""

import re
import time
from pathlib import Path

from moderator.llm import LLM
from moderator.prompts import VISION_READ
from moderator.schema import Moderation

TEXT_PART = re.compile(r"TEXT:\s*(.*?)\s*(?:PICTURE:|$)", re.S)
LABEL = re.compile(r"^\s*(TEXT|PICTURE)\s*:\s*", re.I)


def clean_text(answer: str) -> str:
    match = TEXT_PART.search(answer)
    lines = []
    for line in (match.group(1) if match else answer).splitlines():
        line = LABEL.sub("", line).strip().strip('"')
        if line and (not lines or lines[-1].lower() != line.lower()):
            lines.append(line)
    return " ".join(dict.fromkeys(lines))


def read_image(llm: LLM, image: Path | bytes) -> str:
    return clean_text(llm.look(image, VISION_READ))


def moderate_image(llm: LLM, image: Path | bytes, moderate) -> Moderation:
    started = time.perf_counter()
    text = read_image(llm, image)
    result = moderate(text)
    return result.model_copy(
        update={
            "mode": f"image+{result.mode}",
            "read_text": text,
            "latency_s": time.perf_counter() - started,
            "model": f"{llm.settings.vision_model} + {result.model}",
        }
    )
