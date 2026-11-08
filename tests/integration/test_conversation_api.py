import asyncio

from httpx import ASGITransport, AsyncClient

from apps.api.main import app


def test_conversation_api_requires_approval_and_exposes_trace():
    async def exercise():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/jobs/demo-1/conversations", json={
                "incoming": "Can we schedule an interview?", "day": "2026-11-10",
            })
            assert response.status_code == 200
            pending = response.json()
            assert pending["status"] == "awaiting_approval"
            run_id = pending["run_id"]
            assert pending["state"]["intent"] == "interview"
            assert "marketplace_result" not in pending["state"]
            reread = await client.get(f"/conversations/{run_id}")
            assert reread.json()["status"] == "awaiting_approval"
            approved = await client.post(f"/conversations/{run_id}/approval", json={"approved": True})
            assert approved.status_code == 200
            assert approved.json()["state"]["marketplace_result"]["synthetic"] is True
            duplicate = await client.post(f"/conversations/{run_id}/approval", json={"approved": True})
            assert duplicate.status_code == 409
    asyncio.run(exercise())
