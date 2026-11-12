import asyncio

from mcp_servers.marketplace.adapters.demo import DemoMarketplace


def test_write_requires_explicit_non_dry_run_and_is_idempotent():
    async def exercise():
        marketplace = DemoMarketplace()
        preview = await marketplace.create_proposal_draft("demo-1", "Cited draft", "key-1", dry_run=True)
        assert preview["dry_run"] is True
        assert marketplace.drafts == {}
        first = await marketplace.create_proposal_draft("demo-1", "Cited draft", "key-1")
        second = await marketplace.create_proposal_draft("demo-1", "Cited draft", "key-1")
        assert first == second
        assert len(marketplace.drafts) == 1
        conflict = await marketplace.create_proposal_draft("demo-1", "Changed text", "key-1")
        assert conflict["error"] == "idempotency_conflict"
        assert marketplace.drafts["key-1"] == first
    asyncio.run(exercise())
