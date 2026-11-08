import asyncio

from mcp_servers.workspace.client import DemoWorkspace


def test_workspace_mcp_hold_is_idempotent(monkeypatch, tmp_path):
    database = tmp_path / "workspace.sqlite3"
    database.unlink(missing_ok=True)
    monkeypatch.setenv("GIGBID_WORKSPACE_DB", str(database))

    async def verify():
        workspace = DemoWorkspace()
        slot = (await workspace.get_free_slots("2026-11-10"))[0]
        preview = await workspace.create_tentative_hold(slot, "hold-key", True)
        assert preview["dry_run"] is True
        first = await workspace.create_tentative_hold(slot, "hold-key")
        second = await workspace.create_tentative_hold(slot, "hold-key")
        assert first["hold_id"] == second["hold_id"]
        assert slot not in await workspace.get_free_slots("2026-11-10")
        conflict = await workspace.create_tentative_hold(slot, "different-key")
        assert conflict["error"] == "slot_unavailable"
        different_slot = (await workspace.get_free_slots("2026-11-10"))[0]
        reused_key = await workspace.create_tentative_hold(different_slot, "hold-key")
        assert reused_key["error"] == "idempotency_conflict"

    asyncio.run(verify())
