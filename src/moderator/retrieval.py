"""
Search over the paragraphs of the rules: BM25 on normalised five-letter stems, dense search with
nomic-embed-text (which expects the search_document / search_query prefixes) and Reciprocal Rank Fusion of both.
"""

import re
import unicodedata

import numpy as np
from rank_bm25 import BM25Okapi

from moderator.llm import LLM
from moderator.rules import Rule

WORD = re.compile(r"[a-z0-9$*]+")
STEM = 5


def normalise(text: str) -> str:
    text = text.lower().replace("ł", "l")
    return "".join(char for char in unicodedata.normalize("NFKD", text) if not unicodedata.combining(char))


def tokens(text: str) -> list[str]:
    return [word[:STEM] for word in WORD.findall(normalise(text)) if len(word) > 1]


def rrf(rankings: list[list[int]], k: int = 60) -> list[int]:
    scores: dict[int, float] = {}
    for ranking in rankings:
        for position, index in enumerate(ranking):
            scores[index] = scores.get(index, 0.0) + 1.0 / (k + position + 1)
    return sorted(scores, key=scores.get, reverse=True)


class Retriever:
    def __init__(self, rules: list[Rule], llm: LLM | None = None, rrf_k: int = 60):
        self.rules = rules
        self.llm = llm
        self.rrf_k = rrf_k
        self.bm25 = BM25Okapi([tokens(rule.render()) for rule in rules])
        self._vectors: np.ndarray | None = None

    def vectors(self) -> np.ndarray:
        if self._vectors is None:
            texts = [f"search_document: {rule.render()}" for rule in self.rules]
            self._vectors = unit(np.array(self.llm.embed(texts)))
        return self._vectors

    def bm25_ranking(self, query: str) -> list[int]:
        scores = self.bm25.get_scores(tokens(query))
        return list(np.argsort(-scores, kind="stable"))

    def dense_ranking(self, query: str) -> list[int]:
        query_vector = unit(np.array(self.llm.embed([f"search_query: {query}"])))[0]
        return list(np.argsort(-(self.vectors() @ query_vector), kind="stable"))

    def ranking(self, query: str, method: str = "hybrid") -> list[int]:
        if method == "bm25" or self.llm is None:
            return self.bm25_ranking(query)
        if method == "dense":
            return self.dense_ranking(query)
        return rrf([self.bm25_ranking(query), self.dense_ranking(query)], self.rrf_k)

    def search(self, query: str, top_k: int = 3, method: str = "hybrid") -> list[Rule]:
        return [self.rules[index] for index in self.ranking(query, method)[:top_k]]


def unit(matrix: np.ndarray) -> np.ndarray:
    return matrix / np.linalg.norm(matrix, axis=1, keepdims=True)
