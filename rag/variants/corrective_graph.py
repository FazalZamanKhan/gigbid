"""V8 corrective retrieval as an explicit LangGraph subgraph."""

from __future__ import annotations

from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from rag.variants.pipeline import Chunk, Embedder, retrieve, tokens


class CorrectiveState(TypedDict, total=False):
    query: str
    requirements: list[str]
    hits: list[dict]
    queries: list[str]
    initial_grade: float
    final_grade: float
    abstained: bool


def _coverage(query: str, text: str) -> float:
    wanted = set(tokens(query))
    return len(wanted & set(tokens(text))) / len(wanted) if wanted else 0.0


def _serialize(result) -> list[dict]:
    return [{"id": hit.chunk.id, "source_id": hit.chunk.source_id, "text": hit.chunk.text, "score": hit.score}
            for hit in result.hits]


def build_corrective_graph(chunks: list[Chunk], embedder: Embedder, *, k: int = 10, min_coverage: float = 0.2):
    def initial(state: CorrectiveState) -> CorrectiveState:
        result = retrieve("v2", state["query"], chunks, embedder, k=k)
        return {"hits": _serialize(result), "queries": [state["query"]]}

    def grade_initial(state: CorrectiveState) -> CorrectiveState:
        grade = max((_coverage(state["query"], hit["text"]) for hit in state["hits"]), default=0.0)
        return {"initial_grade": grade, "abstained": False}

    def route(state: CorrectiveState) -> str:
        return END if state["initial_grade"] >= min_coverage else "requery"

    def requery(state: CorrectiveState) -> CorrectiveState:
        queries = [item for item in state.get("requirements", []) if item.strip()]
        if not queries:
            return {"hits": [], "queries": [state["query"]], "abstained": True}
        result = retrieve("v1", state["query"], chunks, embedder, requirements=queries, k=k)
        return {"hits": _serialize(result), "queries": [state["query"], *queries]}

    def grade_final(state: CorrectiveState) -> CorrectiveState:
        queries = state.get("requirements", [])
        grade = max((_coverage(query, hit["text"]) for query in queries for hit in state["hits"]), default=0.0)
        if grade < min_coverage:
            return {"hits": [], "final_grade": grade, "abstained": True}
        return {"final_grade": grade, "abstained": False}

    graph = StateGraph(CorrectiveState)
    graph.add_node("initial", initial)
    graph.add_node("grade_initial", grade_initial)
    graph.add_node("requery", requery)
    graph.add_node("grade_final", grade_final)
    graph.add_edge(START, "initial")
    graph.add_edge("initial", "grade_initial")
    graph.add_conditional_edges("grade_initial", route)
    graph.add_edge("requery", "grade_final")
    graph.add_edge("grade_final", END)
    return graph.compile()
