import asyncio

from mcp_servers.workspace.client import DemoWorkspace


def test_workspace_mcp_hold_is_idempotent(monkeypatch, tmp_path):
    monkeypatch.setenv("GIGBID_WORKSPACE_DB", str(tmp_path / "workspace.sqlite3"))

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

    asyncio.run(verify())
