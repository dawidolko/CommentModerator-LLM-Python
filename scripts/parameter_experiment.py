"""
Sends the same requests with different Ollama options to the text model and writes what changed to
examples/parameters/parameters.json (temperature, seed, top_p, top_k, num_predict, format, num_ctx, stop).
"""

import json
import time
from collections import Counter

from pydantic import ValidationError

from moderator.config import ROOT
from moderator.prompts import moderation_messages
from moderator.schema import Verdict, verdict_schema
from moderator.service import Moderator

OUTPUT = ROOT / "examples" / "parameters"
COMMENT = "This is the worst API design I have ever seen, nothing is consistent."
BORDERLINE = "Kurde, znowu zapomniałem średnika. Klasyka."
EXPLAIN = [
    {
        "role": "user",
        "content": f'In one sentence, explain to a new forum user why this comment could upset someone: "{COMMENT}"',
    }
]
RUNS = 5


SAMPLES = [
    "Jesteś totalnym idiotą, nawet pętli nie umiesz napisać.",
    "Earn $500 a day working from home, click bit.ly/xx-cash now!!!",
    "Dzięki za odpowiedź, po dodaniu await wszystko działa.",
    "If you post that again I will find you and break your fingers.",
    "Moim zdaniem Vue jest prostszy od Angulara, ale to kwestia gustu.",
]


def is_verdict(answer: str) -> bool:
    try:
        Verdict.model_validate(json.loads(answer))
        return True
    except (json.JSONDecodeError, ValidationError):
        return False


def decisions(moderator: Moderator, options: dict) -> list[str]:
    schema = verdict_schema(False)
    answers = []
    for _ in range(RUNS):
        raw = moderator.llm.chat(moderation_messages(BORDERLINE, "zero-shot"), options=options, format=schema)
        verdict = json.loads(raw)
        answers.append(f"{verdict['decision']}/{verdict['severity']}")
    return answers


def texts(moderator: Moderator, options: dict, runs: int = RUNS) -> list[str]:
    return [moderator.llm.chat(EXPLAIN, options=options).strip() for _ in range(runs)]


def main() -> None:
    moderator = Moderator()
    base = {key: value for key, value in moderator.settings.generation.items() if key != "seed"}
    results: dict = {"model": moderator.settings.text_model, "comment": COMMENT, "borderline": BORDERLINE, "runs": RUNS}

    results["temperature"] = {}
    for temperature in (0.0, 0.7, 1.5):
        answers = decisions(moderator, {**base, "temperature": temperature})
        results["temperature"][str(temperature)] = dict(Counter(answers))

    seeded = texts(moderator, {**base, "temperature": 0.9, "seed": 42}, runs=3)
    unseeded = texts(moderator, {**base, "temperature": 0.9}, runs=3)
    results["seed"] = {"with seed 42": len(set(seeded)), "without seed": len(set(unseeded)), "example": seeded[0]}

    results["top_p"] = {}
    for top_p in (0.1, 1.0):
        answers = texts(moderator, {**base, "temperature": 1.0, "top_p": top_p, "top_k": 100})
        results["top_p"][str(top_p)] = {"distinct": len(set(answers)), "first": answers[0]}

    results["top_k"] = {}
    for top_k in (1, 100):
        answers = texts(moderator, {**base, "temperature": 1.0, "top_p": 1.0, "top_k": top_k})
        results["top_k"][str(top_k)] = {"distinct": len(set(answers))}

    short = moderator.llm.chat(
        moderation_messages(COMMENT, "zero-shot"), options={**base, "num_predict": 15}, format=verdict_schema(False)
    )
    results["num_predict"] = {"15 tokens": short}

    results["format"] = {}
    for name, schema in (("none", None), ("json", "json"), ("schema", verdict_schema(False))):
        answers = [
            moderator.llm.chat(moderation_messages(text, "zero-shot"), options={**base, "seed": 42}, format=schema)
            for text in SAMPLES
        ]
        results["format"][name] = {
            "valid": sum(is_verdict(answer) for answer in answers),
            "of": len(SAMPLES),
            "first": answers[0][:200],
        }

    results["num_ctx"] = {}
    for size in (2048, 16384):
        options = {**base, "num_ctx": size, "num_predict": 60, "seed": 42}
        moderator.llm.chat(EXPLAIN, options=options)
        started = time.perf_counter()
        moderator.llm.chat(EXPLAIN, options=options)
        results["num_ctx"][str(size)] = round(time.perf_counter() - started, 2)

    stop = moderator.llm.chat(EXPLAIN, options={**base, "stop": [","]})
    results["stop"] = {"stop at comma": stop}

    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "parameters.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
