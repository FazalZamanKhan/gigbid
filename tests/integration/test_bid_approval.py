import asyncio

from langgraph.types import Command
from agent.graphs.bid_graph import build_bid_graph
from mcp_servers.marketplace.adapters.demo import DemoMarketplace


def test_bid_waits_for_human_and_rejection_does_not_write():
    async def exercise():
        marketplace = DemoMarketplace()
        graph = build_bid_graph(marketplace)
        config = {"configurable": {"thread_id": "review-1"}}
        await graph.ainvoke({"job_id": "demo-1", "events": []}, config)
        snapshot = await graph.aget_state(config)
        assert "approval" in snapshot.next
        assert marketplace.drafts == {}
        await graph.ainvoke(Command(resume={"approved": False, "reason": "No bid"}), config)
        assert marketplace.drafts == {}
    asyncio.run(exercise())


def test_approved_bid_creates_one_draft_and_scam_skips():
    async def exercise():
        marketplace = DemoMarketplace()
        graph = build_bid_graph(marketplace)
        approved_config = {"configurable": {"thread_id": "review-2"}}
        await graph.ainvoke({"job_id": "demo-1", "events": []}, approved_config)
        assert marketplace.drafts == {}
        await graph.ainvoke(Command(resume={"approved": True}), approved_config)
        snapshot = await graph.aget_state(approved_config)
        assert snapshot.values["marketplace_result"]["draft_id"]
        assert len(marketplace.drafts) == 1
        scam_config = {"configurable": {"thread_id": "review-3"}}
        await graph.ainvoke({"job_id": "demo-2", "events": []}, scam_config)
        scam = await graph.aget_state(scam_config)
        assert scam.values["decision"]["action"] == "skip"
        assert "approval" not in scam.next
        assert len(marketplace.drafts) == 1
    asyncio.run(exercise())


def test_injected_job_instruction_is_ignored_and_skipped():
    async def exercise():
        marketplace = DemoMarketplace()
        graph = build_bid_graph(marketplace)
        config = {"configurable": {"thread_id": "injection-review"}}
        await graph.ainvoke({"job_id": "demo-3", "events": []}, config)
        snapshot = await graph.aget_state(config)
        assert snapshot.values["risk"]["injected_instruction"] is True
        assert snapshot.values["decision"]["action"] == "skip"
        assert "approval" not in snapshot.next
        assert marketplace.drafts == {}
    asyncio.run(exercise())
