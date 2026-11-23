"""
The unitary/toxic-bert baseline from Lab 2: multi-label, so a sigmoid per label and a threshold on the highest
score. It only knows English and gives no reason, which is the point of comparing it with the LLM.
"""

import os
from functools import lru_cache

LABEL_TO_CATEGORY = {
    "toxic": "insult",
    "severe_toxic": "insult",
    "insult": "insult",
    "obscene": "obscene",
    "threat": "threat",
    "identity_hate": "identity_hate",
}


@lru_cache
def toxic_bert(model_name: str):
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
    from transformers import pipeline

    return pipeline("text-classification", model=model_name, top_k=None, function_to_apply="sigmoid", device="cpu")


def scores(texts: list[str], model_name: str) -> list[dict[str, float]]:
    outputs = toxic_bert(model_name)(texts, truncation=True, batch_size=8)
    return [{item["label"]: float(item["score"]) for item in output} for output in outputs]


def verdict(label_scores: dict[str, float], threshold: float) -> dict:
    top = max(label_scores.values())
    named = {label: score for label, score in label_scores.items() if label not in {"toxic", "severe_toxic"}}
    categories = sorted({LABEL_TO_CATEGORY[label] for label, score in named.items() if score >= threshold})
    toxic = top >= threshold
    return {
        "toxic": toxic,
        "score": round(top, 4),
        "categories": categories or (["insult"] if toxic else ["none"]),
    }
