import asyncio

from mcp_servers.marketplace.client import DemoMCPMarketplace


def test_marketplace_mcp_protocol_and_dry_run():
    async def verify():
        market = DemoMCPMarketplace()
        jobs = await market.list_jobs()
        assert {job.id for job in jobs} == {"demo-1", "demo-2"}
        job = await market.get_job("demo-1")
        preview = await market.create_proposal_draft(job.id, "Cited synthetic draft", "test-preview", True)
        assert preview["dry_run"] is True
        assert "draft_id" not in preview

    asyncio.run(verify())
