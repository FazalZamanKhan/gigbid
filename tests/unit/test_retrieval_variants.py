from evals.runners.retrieval_eval import evaluate, retrieval_metrics
from rag.variants.pipeline import Chunk, fixed_chunks, retrieve, tokens
from rag.variants.corrective_graph import build_corrective_graph


class CountEmbedder:
    """Small deterministic vectors for control-flow tests, not real embeddings."""

    def encode(self, texts):
        return [[float(text.casefold().count("python")), float(text.casefold().count("dashboard") + text.casefold().count("celery")), 1.0]
                for text in texts]


class TokenReranker:
    def score(self, pairs):
        return [float(len(set(tokens(query)) & set(tokens(document)))) for query, document in pairs]


CORPUS = [
    Chunk("a:0", "Python dashboard for business analytics", "a", 0.1),
    Chunk("b:0", "Celery worker and Python task queue", "b", 0.8),
    Chunk("c:0", "Accessible design and keyboard review", "c", 0.0),
]


def test_chunks_are_stable_and_overlap():
    chunks = fixed_chunks("case", "one two three four five", size=3, overlap=1)
    assert [chunk.id for chunk in chunks] == ["case:0", "case:1", "case:2"]
    assert chunks[1].text == "three four five"


def test_variants_are_ranked_and_corrective_retrieval_can_abstain():
    for variant in ("v0", "v1", "v2", "v3", "v4", "v8"):
        result = retrieve(variant, "Python Celery", CORPUS, CountEmbedder(),
                          requirements=["Python", "Celery"], reranker=TokenReranker(), k=2)
        assert len(result.hits) == 2
        assert result.hits[0].chunk.source_id in {"a", "b"}
    missing = retrieve("v8", "Kubernetes Terraform", CORPUS, CountEmbedder(),
                       requirements=["Kubernetes", "Terraform"], k=2)
    assert missing.abstained and not missing.hits


def test_retrieval_metrics_and_provenance_fields():
    metrics = retrieval_metrics(["x", "a", "b"], {"a", "b"})
    assert metrics["recall_at_5"] == 1
    assert metrics["mrr"] == 0.5
    assert 0 < metrics["ndcg_at_10"] < 1
    results = evaluate(CORPUS, [{"id": "synthetic-1", "query": "Python Celery",
                                "gold_evidence_ids": ["b"], "persona": "synthetic"}],
                       ["v0", "v2"], CountEmbedder())
    assert results["cases"] == 1
    assert results["variants"]["v0"]["aggregate"]["labeled_cases"] == 1


def test_corrective_graph_requeries_and_refuses_unsupported_claims():
    graph = build_corrective_graph(CORPUS, CountEmbedder(), k=2)
    refused = graph.invoke({"query": "Kubernetes Terraform", "requirements": ["Kubernetes", "Terraform"]})
    assert refused["abstained"] and not refused["hits"]
    assert refused["initial_grade"] == refused["final_grade"] == 0
    supported = graph.invoke({"query": "Python Celery", "requirements": ["Celery"]})
    assert not supported["abstained"]
    assert supported["hits"]
