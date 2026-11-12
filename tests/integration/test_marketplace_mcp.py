import asyncio
from uuid import uuid4

from mcp_servers.marketplace.client import DemoMCPMarketplace


def test_marketplace_mcp_protocol_and_dry_run():
    async def verify():
        market = DemoMCPMarketplace()
        jobs = await market.list_jobs()
        assert {job.id for job in jobs} == {"demo-1", "demo-2", "demo-3"}
        job = await market.get_job("demo-1")
        preview = await market.create_proposal_draft(job.id, "Cited synthetic draft", "test-preview", True)
        assert preview["dry_run"] is True
        assert "draft_id" not in preview

    asyncio.run(verify())


def test_mcp_write_receipt_persists_across_server_processes():
    async def verify():
        market = DemoMCPMarketplace()
        key = f"test-{uuid4()}"
        first = await market.create_proposal_draft("demo-1", "Cited synthetic draft", key)
        assert first["draft_id"] == f"draft-{key}"
        again = await market.create_proposal_draft("demo-1", "Cited synthetic draft", key)
        assert again == first
        conflict = await market.create_proposal_draft("demo-1", "Changed synthetic draft", key)
        assert conflict == {"error": "idempotency_conflict", "draft_id": first["draft_id"]}
        message = await market.send_message("demo-1", "Interview reply", key)
        assert message["message_id"] == f"message-{key}"
        assert await market.send_message("demo-1", "Interview reply", key) == message
        message_conflict = await market.send_message("demo-1", "Changed reply", key)
        assert message_conflict == {"error": "idempotency_conflict", "message_id": message["message_id"]}

    asyncio.run(verify())
