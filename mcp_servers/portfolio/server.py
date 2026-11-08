"""Read-only Portfolio MCP server, currently using synthetic demonstration items.

Replace the corpus loader with provided persona data before any evaluation.
"""

from mcp.server.fastmcp import FastMCP
from rag.retriever import DEMO_EVIDENCE
from rag.variants.pipeline import Chunk, FastCrossEncoderReranker, FastEmbedder, retrieve
from rag.variants.corrective_graph import build_corrective_graph

mcp = FastMCP("GigBid Portfolio")


@mcp.tool()
def search_evidence(requirement: str, k: int = 5, variant: str = "keyword", requirements: list[str] | None = None) -> list[dict]:
    """Find portfolio evidence for one job requirement. Read only."""
    limit = max(0, min(k, 20))
    if not limit:
        return []
    if variant != "keyword":
        chunks = [Chunk(id=f"{item.id}:0", source_id=item.id,
                        text=f"{item.title}. {item.text} Skills: {', '.join(item.skills)}") for item in DEMO_EVIDENCE]
        embedder = FastEmbedder()
        if variant == "v8":
            state = build_corrective_graph(chunks, embedder, k=limit).invoke(
                {"query": requirement, "requirements": requirements or []})
            ids = [hit["source_id"] for hit in state["hits"]]
        else:
            reranker = FastCrossEncoderReranker() if variant in {"v3", "v4"} else None
            result = retrieve(variant, requirement, chunks, embedder,
                              requirements=requirements, reranker=reranker, k=limit)
            ids = [hit.chunk.source_id for hit in result.hits]
        by_id = {item.id: item for item in DEMO_EVIDENCE}
        return [by_id[item_id].model_dump() for item_id in ids]
    words = set(requirement.casefold().split())
    scored = []
    for item in DEMO_EVIDENCE:
        haystack = f"{item.title} {item.text} {' '.join(item.skills)}".casefold()
        score = sum(word in haystack for word in words)
        if score:
            scored.append((score, item))
    return [item.model_dump() for _, item in sorted(scored, key=lambda x: x[0], reverse=True)[:limit]]


@mcp.tool()
def get_case_study(id: str) -> dict:
    """Return one portfolio item by its identifier. Read only."""
    for item in DEMO_EVIDENCE:
        if item.id == id:
            return item.model_dump()
    return {"error": "not_found", "id": id}


@mcp.tool()
def list_skills() -> list[str]:
    """List portfolio skills. Read only."""
    return sorted({skill for item in DEMO_EVIDENCE for skill in item.skills})


@mcp.resource("portfolio://case/{id}")
def case_resource(id: str) -> str:
    """Load a portfolio case study as text."""
    for item in DEMO_EVIDENCE:
        if item.id == id:
            return item.model_dump_json()
    return '{"error":"not_found"}'


@mcp.prompt()
def answer_screening_question(question: str) -> str:
    """Draft a screening answer using only cited portfolio evidence."""
    return f"Answer this screening question only with evidence returned by search_evidence. Cite each factual claim. If evidence is absent, say so. Question: {question}"


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
