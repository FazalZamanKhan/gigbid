"""Export reproducible synthetic LangGraph state snapshots for public review.

These are development traces, not the assignment's required production spans.
"""

import asyncio
import json
import os
from pathlib import Path
import tempfile

from langgraph.types import Command

from agent.graphs.bid_graph import build_bid_graph
from agent.graphs.conversation_graph import build_conversation_graph
from mcp_servers.marketplace.client import DemoMCPMarketplace
from mcp_servers.workspace.client import DemoWorkspace

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "docs" / "traces"
DEST.mkdir(parents=True, exist_ok=True)


def save(name: str, payload: dict) -> None:
    path = DEST / f"{name}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(path.relative_to(ROOT))


def state_view(snapshot) -> dict:
    fields = ("events", "analysis", "risk", "fit", "decision", "price", "draft", "compliance", "intent", "risk_flags", "slots", "approval", "marketplace_result")
    return {"next_nodes": list(snapshot.next), "state": {key: snapshot.values[key] for key in fields if key in snapshot.values}}


async def bid(name: str, job_id: str, approve: bool = False) -> None:
    graph = build_bid_graph(DemoMCPMarketplace())
    config = {"configurable": {"thread_id": f"trace-{name}"}}
    await graph.ainvoke({"job_id": job_id, "events": []}, config)
    before = state_view(await graph.aget_state(config))
    result = {"scope": "synthetic-development", "path": "LangGraph with Portfolio and Marketplace MCP stdio", "job_id": job_id, "before_human_action": before}
    if approve:
        assert before["next_nodes"] == ["approval"]
        await graph.ainvoke(Command(resume={"approved": True}), config)
        result["after_human_action"] = state_view(await graph.aget_state(config))
    else:
        assert before["state"]["decision"]["action"] == "skip"
        assert not before["next_nodes"]
    save(name, result)


async def conversation() -> None:
    graph = build_conversation_graph(DemoMCPMarketplace(), DemoWorkspace())
    config = {"configurable": {"thread_id": "trace-interview-reply"}}
    await graph.ainvoke({"run_id": "trace-interview-reply", "job_id": "demo-1", "incoming": "Could we schedule an interview?", "day": "2026-11-10", "events": []}, config)
    before = state_view(await graph.aget_state(config))
    assert before["next_nodes"] == ["approval"]
    await graph.ainvoke(Command(resume={"approved": True}), config)
    after = state_view(await graph.aget_state(config))
    save("interview-reply-approved", {"scope": "synthetic-development", "path": "LangGraph with Marketplace and Workspace MCP stdio", "job_id": "demo-1", "before_human_action": before, "after_human_action": after})


async def main() -> None:
    with tempfile.TemporaryDirectory(prefix="gigbid-traces-") as directory:
        os.environ["GIGBID_WORKSPACE_DB"] = str(Path(directory) / "workspace.sqlite3")
        await bid("proposal-approved", "demo-1", approve=True)
        await bid("scam-skipped", "demo-2")
        await bid("injection-skipped", "demo-3")
        await conversation()


if __name__ == "__main__":
    asyncio.run(main())
