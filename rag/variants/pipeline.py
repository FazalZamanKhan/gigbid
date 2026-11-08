"""Reproducible retrieval variants. Official metrics require instructor data.

Corpus documents are fixed chunks with stable IDs. Outcome scores must be
derived from training history only, never from the evaluation split.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import math
import re
from typing import Protocol


TOKEN = re.compile(r"[a-z0-9][a-z0-9+#.-]*", re.I)


def tokens(text: str) -> list[str]:
    return TOKEN.findall(text.casefold())


@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    source_id: str
    outcome_score: float = 0.0


@dataclass(frozen=True)
class Hit:
    chunk: Chunk
    score: float


@dataclass(frozen=True)
class RetrievalResult:
    variant: str
    hits: list[Hit]
    queries: list[str]
    abstained: bool = False


class Embedder(Protocol):
    def encode(self, texts: list[str]) -> list[list[float]]: ...


class Reranker(Protocol):
    def score(self, pairs: list[tuple[str, str]]) -> list[float]: ...


class CachedEmbedder:
    """Cache document embeddings so per-query timings exclude re-indexing."""

    def __init__(self, inner: Embedder):
        self.inner = inner
        self.cache: dict[str, list[float]] = {}

    def encode(self, texts: list[str]) -> list[list[float]]:
        missing = list(dict.fromkeys(text for text in texts if text not in self.cache))
        if missing:
            vectors = self.inner.encode(missing)
            if len(vectors) != len(missing):
                raise ValueError("Embedder returned the wrong number of vectors")
            self.cache.update(zip(missing, vectors))
        return [self.cache[text] for text in texts]


class FastEmbedder:
    """Optional ONNX embedding backend; install the ``rag`` extra first."""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        from fastembed import TextEmbedding

        self.model = TextEmbedding(model_name=model_name)
        self.model_name = model_name

    def encode(self, texts: list[str]) -> list[list[float]]:
        return [vector.tolist() for vector in self.model.embed(texts)]


class FastCrossEncoderReranker:
    """Optional ONNX cross encoder backend for V3/V4."""

    def __init__(self, model_name: str = "Xenova/ms-marco-MiniLM-L-6-v2"):
        from fastembed.rerank.cross_encoder import TextCrossEncoder

        self.model = TextCrossEncoder(model_name=model_name)
        self.model_name = model_name

    def score(self, pairs: list[tuple[str, str]]) -> list[float]:
        if not pairs:
            return []
        if len({query for query, _ in pairs}) != 1:
            raise ValueError("Cross encoder batch must share one query")
        return [float(value) for value in self.model.rerank(pairs[0][0], [document for _, document in pairs])]


def fixed_chunks(source_id: str, text: str, size: int = 120, overlap: int = 20) -> list[Chunk]:
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("Require size > overlap >= 0")
    words = text.split()
    return [Chunk(id=f"{source_id}:{index}", source_id=source_id, text=" ".join(words[start:start + size]))
            for index, start in enumerate(range(0, len(words), size - overlap)) if words[start:start + size]]


def _cosine(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("Embedding dimensions differ")
    norm_left = math.sqrt(sum(value * value for value in left))
    norm_right = math.sqrt(sum(value * value for value in right))
    if not norm_left or not norm_right:
        return 0.0
    return sum(a * b for a, b in zip(left, right)) / (norm_left * norm_right)


def _rank(scores: dict[str, float], chunks: list[Chunk]) -> list[Hit]:
    return sorted((Hit(chunk, scores[chunk.id]) for chunk in chunks if chunk.id in scores),
                  key=lambda hit: (-hit.score, hit.chunk.id))


def _dense(query: str, chunks: list[Chunk], embedder: Embedder) -> list[Hit]:
    vectors = embedder.encode([query, *[chunk.text for chunk in chunks]])
    if len(vectors) != len(chunks) + 1:
        raise ValueError("Embedder returned the wrong number of vectors")
    return _rank({chunk.id: _cosine(vectors[0], vector) for chunk, vector in zip(chunks, vectors[1:])}, chunks)


def _bm25(query: str, chunks: list[Chunk], k1: float = 1.5, b: float = 0.75) -> list[Hit]:
    docs = [Counter(tokens(chunk.text)) for chunk in chunks]
    lengths = [sum(doc.values()) for doc in docs]
    average = sum(lengths) / len(lengths) if lengths else 1
    scores: dict[str, float] = {}
    for chunk, doc, length in zip(chunks, docs, lengths):
        score = 0.0
        for term in set(tokens(query)):
            frequency = doc[term]
            if not frequency:
                continue
            document_frequency = sum(term in candidate for candidate in docs)
            inverse_frequency = math.log(1 + (len(docs) - document_frequency + 0.5) / (document_frequency + 0.5))
            score += inverse_frequency * (frequency * (k1 + 1)) / (frequency + k1 * (1 - b + b * length / average))
        scores[chunk.id] = score
    return _rank(scores, chunks)


def _rrf(rankings: list[list[Hit]], chunks: list[Chunk], offset: int = 60) -> list[Hit]:
    scores: Counter[str] = Counter()
    for ranking in rankings:
        for position, hit in enumerate(ranking, 1):
            scores[hit.chunk.id] += 1 / (offset + position)
    return _rank(dict(scores), chunks)


def _coverage(query: str, text: str) -> float:
    terms = set(tokens(query))
    return len(terms & set(tokens(text))) / len(terms) if terms else 0.0


def retrieve(
    variant: str,
    query: str,
    chunks: list[Chunk],
    embedder: Embedder,
    *,
    requirements: list[str] | None = None,
    reranker: Reranker | None = None,
    k: int = 5,
    candidate_count: int = 20,
    min_coverage: float = 0.2,
) -> RetrievalResult:
    if variant not in {"v0", "v1", "v2", "v3", "v4", "v8"}:
        raise ValueError(f"Unknown variant: {variant}")
    if k < 1 or candidate_count < k:
        raise ValueError("Require candidate_count >= k >= 1")
    if len({chunk.id for chunk in chunks}) != len(chunks):
        raise ValueError("Chunk IDs must be unique")
    if not chunks:
        return RetrievalResult(variant, [], [query], abstained=variant == "v8")

    dense = _dense(query, chunks, embedder)
    if variant == "v0":
        return RetrievalResult(variant, dense[:k], [query])
    if variant == "v1":
        queries = [item for item in (requirements or []) if item.strip()] or [query]
        return RetrievalResult(variant, _rrf([_dense(item, chunks, embedder) for item in queries], chunks)[:k], queries)

    hybrid = _rrf([dense, _bm25(query, chunks)], chunks)
    if variant == "v2":
        return RetrievalResult(variant, hybrid[:k], [query])
    if variant == "v8":
        if max(_coverage(query, hit.chunk.text) for hit in hybrid[:k]) >= min_coverage:
            return RetrievalResult(variant, hybrid[:k], [query])
        queries = [item for item in (requirements or []) if item.strip()]
        if not queries:
            return RetrievalResult(variant, [], [query], abstained=True)
        revised = _rrf([_dense(item, chunks, embedder) for item in queries] + [_bm25(item, chunks) for item in queries], chunks)
        if max(_coverage(item, hit.chunk.text) for item in queries for hit in revised[:k]) < min_coverage:
            return RetrievalResult(variant, [], [query, *queries], abstained=True)
        return RetrievalResult(variant, revised[:k], [query, *queries])

    if reranker is None:
        raise ValueError("V3 and V4 require a cross encoder reranker")
    candidates = hybrid[:candidate_count]
    scores = reranker.score([(query, hit.chunk.text) for hit in candidates])
    if len(scores) != len(candidates):
        raise ValueError("Reranker returned the wrong number of scores")
    reranked = sorted((Hit(hit.chunk, float(score) + (0.15 * hit.chunk.outcome_score if variant == "v4" else 0.0))
                       for hit, score in zip(candidates, scores)), key=lambda hit: (-hit.score, hit.chunk.id))
    return RetrievalResult(variant, reranked[:k], [query])
