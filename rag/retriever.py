"""Local, transparent evidence retrieval for the pre-starter demo.

This is not the evaluated RAG pipeline required by the assignment.
"""

from agent.handoffs import Evidence, JobSpec

DEMO_EVIDENCE = [
    Evidence(id="demo-e1", title="Python CSV analysis dashboard", text="Synthetic example: cleaned CSV data in Python and created a dashboard.", source="synthetic-demo", skills=["Python", "Data analysis", "Dashboard"]),
    Evidence(id="demo-e2", title="Accessible interface review", text="Synthetic example: reviewed keyboard access and responsive layouts.", source="synthetic-demo", skills=["Accessibility", "Frontend"]),
]


def search_evidence(job: JobSpec, corpus: list[Evidence] | None = None) -> list[Evidence]:
    items = corpus if corpus is not None else DEMO_EVIDENCE
    wanted = {skill.casefold() for skill in job.skills}
    scored = [(len(wanted & {s.casefold() for s in item.skills}), item) for item in items]
    return [item for score, item in sorted(scored, key=lambda x: x[0], reverse=True) if score > 0]
