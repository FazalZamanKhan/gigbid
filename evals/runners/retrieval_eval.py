"""Run retrieval-only experiments on an explicitly supplied labeled dev set.

This command does not ship, infer, or invent the instructor's evaluation data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics
import time

from rag.variants.pipeline import CachedEmbedder, Chunk, FastCrossEncoderReranker, FastEmbedder, fixed_chunks, retrieve
from rag.variants.corrective_graph import build_corrective_graph


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    for number, line in enumerate(path.read_text().splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(f"{path}:{number}: invalid JSON") from error
    return rows


def fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ranked_sources(result) -> list[str]:
    seen: set[str] = set()
    sources = []
    for hit in result.hits:
        if hit.chunk.source_id not in seen:
            sources.append(hit.chunk.source_id)
            seen.add(hit.chunk.source_id)
    return sources


def retrieval_metrics(ranked: list[str], gold: set[str]) -> dict[str, float] | None:
    if not gold:
        return None
    recall = len(set(ranked[:5]) & gold) / len(gold)
    first = next((position for position, item in enumerate(ranked, 1) if item in gold), None)
    mrr = 1 / first if first else 0.0
    dcg = sum(1 / math.log2(position + 1) for position, item in enumerate(ranked[:10], 1) if item in gold)
    ideal = sum(1 / math.log2(position + 1) for position in range(1, min(len(gold), 10) + 1))
    return {"recall_at_5": recall, "mrr": mrr, "ndcg_at_10": dcg / ideal}


def summarize(rows: list[dict]) -> dict:
    labeled = [row["metrics"] for row in rows if row["metrics"] is not None]
    latencies = sorted(row["latency_ms"] for row in rows)
    aggregate = {key: round(statistics.mean(item[key] for item in labeled), 4) if labeled else None
                 for key in ("recall_at_5", "mrr", "ndcg_at_10")}
    aggregate["p95_latency_ms"] = latencies[math.ceil(0.95 * len(latencies)) - 1] if latencies else None
    aggregate["abstention_rate"] = round(sum(row["abstained"] for row in rows) / len(rows), 4) if rows else None
    aggregate["labeled_cases"] = len(labeled)
    aggregate["cases"] = len(rows)
    return aggregate


def evaluate(chunks: list[Chunk], cases: list[dict], variants: list[str], embedder, reranker=None) -> dict:
    indexed = CachedEmbedder(embedder)
    index_started = time.perf_counter()
    indexed.encode([chunk.text for chunk in chunks])
    index_build_ms = round((time.perf_counter() - index_started) * 1000, 2)
    output: dict = {"cases": len(cases), "chunks": len(chunks), "index_build_ms": index_build_ms, "variants": {}}
    for variant in variants:
        cached = CachedEmbedder(embedder)
        cached.cache.update(indexed.cache)
        corrective = build_corrective_graph(chunks, cached) if variant == "v8" else None
        rows = []
        for case in cases:
            started = time.perf_counter()
            if corrective:
                state = corrective.invoke({"query": case["query"], "requirements": case.get("requirements", [])})
                seen = set()
                ranked = []
                for hit in state["hits"]:
                    if hit["source_id"] not in seen:
                        ranked.append(hit["source_id"])
                        seen.add(hit["source_id"])
                queries = state["queries"]
                abstained = state["abstained"]
            else:
                result = retrieve(variant, case["query"], chunks, cached,
                                  requirements=case.get("requirements"), reranker=reranker, k=10)
                ranked = _ranked_sources(result)
                queries = result.queries
                abstained = result.abstained
            elapsed_ms = (time.perf_counter() - started) * 1000
            metrics = retrieval_metrics(ranked, set(case["gold_evidence_ids"]))
            rows.append({"id": case["id"], "persona": case.get("persona"), "job_type": case.get("job_type"),
                         "ranked_source_ids": ranked, "queries": queries, "abstained": abstained,
                         "latency_ms": round(elapsed_ms, 2), "metrics": metrics})
        by_persona = {str(value): summarize([row for row in rows if row["persona"] == value])
                      for value in sorted({row["persona"] for row in rows}, key=str)}
        by_job_type = {str(value): summarize([row for row in rows if row["job_type"] == value])
                       for value in sorted({row["job_type"] for row in rows}, key=str)}
        output["variants"][variant] = {"aggregate": summarize(rows), "by_persona": by_persona,
                                       "by_job_type": by_job_type, "rows": rows}
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, required=True, help="JSONL with id, text, optional outcome_score (training-derived only)")
    parser.add_argument("--cases", type=Path, required=True, help="JSONL with id, query, gold_evidence_ids, optional requirements/persona/job_type")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--variants", nargs="+", default=["v0", "v1", "v2", "v3", "v4", "v8"])
    parser.add_argument("--embedding-model", default="BAAI/bge-small-en-v1.5")
    parser.add_argument("--reranker-model", default="Xenova/ms-marco-MiniLM-L-6-v2")
    parser.add_argument("--dataset-label", required=True, help="Explicit provenance, e.g. synthetic-smoke or official-dev")
    args = parser.parse_args()
    corpus = read_jsonl(args.corpus)
    cases = read_jsonl(args.cases)
    chunks = []
    for row in corpus:
        outcome_score = float(row.get("outcome_score", 0))
        if not 0 <= outcome_score <= 1:
            raise ValueError("outcome_score must be in [0, 1]")
        if "source_id" in row:
            chunks.append(Chunk(id=row["id"], text=row["text"], source_id=row["source_id"], outcome_score=outcome_score))
        else:
            chunks.extend(Chunk(id=chunk.id, text=chunk.text, source_id=chunk.source_id, outcome_score=outcome_score)
                          for chunk in fixed_chunks(row["id"], row["text"]))
    embedder = FastEmbedder(args.embedding_model)
    reranker = FastCrossEncoderReranker(args.reranker_model) if any(name in {"v3", "v4"} for name in args.variants) else None
    results = evaluate(chunks, cases, args.variants, embedder, reranker)
    results["provenance"] = {"dataset_label": args.dataset_label, "corpus_sha256": fingerprint(args.corpus),
                             "cases_sha256": fingerprint(args.cases), "embedding_model": args.embedding_model,
                             "reranker_model": args.reranker_model if reranker else None,
                             "note": "Retrieval metrics only; proposal quality and GigSim outcomes are not measured here."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2) + "\n")
    print(args.output)


if __name__ == "__main__":
    main()
