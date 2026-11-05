"""Read-only Portfolio MCP server, currently using synthetic demonstration items.

Replace the corpus loader with provided persona data before any evaluation.
"""

from mcp.server.fastmcp import FastMCP
from rag.retriever import DEMO_EVIDENCE

mcp = FastMCP("GigBid Portfolio")


@mcp.tool()
def search_evidence(requirement: str, k: int = 5) -> list[dict]:
    """Find portfolio evidence for one job requirement. Read only."""
    words = set(requirement.casefold().split())
    scored = []
    for item in DEMO_EVIDENCE:
        haystack = f"{item.title} {item.text} {' '.join(item.skills)}".casefold()
        score = sum(word in haystack for word in words)
        if score:
            scored.append((score, item))
    return [item.model_dump() for _, item in sorted(scored, key=lambda x: x[0], reverse=True)[: max(0, min(k, 20))]]


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


if __name__ == "__main__":
    mcp.run()
