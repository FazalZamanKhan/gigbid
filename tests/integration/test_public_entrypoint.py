import asyncio
import base64

from httpx import ASGITransport, AsyncClient

from apps.api.public import app, web_dist


def test_single_origin_serves_web_and_api():
    async def exercise():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            assert (await client.get("/api/health")).json()["status"] == "ok"
            if web_dist.is_dir():
                assert "GigBid" in (await client.get("/")).text
            assert len((await client.get("/api/jobs")).json()) == 2
    asyncio.run(exercise())


def test_reviewer_login_protects_page_and_api(monkeypatch):
    monkeypatch.setenv("GIGBID_REVIEWER_USERNAME", "reviewer")
    monkeypatch.setenv("GIGBID_REVIEWER_PASSWORD", "test-secret")

    async def exercise():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            assert (await client.get("/")).status_code == 401
            assert (await client.get("/api/jobs")).status_code == 401
            assert (await client.get("/api/health")).status_code == 200
            token = base64.b64encode(b"reviewer:test-secret").decode()
            if web_dist.is_dir():
                assert (await client.get("/", headers={"Authorization": f"Basic {token}"})).status_code == 200
            assert (await client.get("/api/jobs", headers={"Authorization": f"Basic {token}"})).status_code == 200
    asyncio.run(exercise())
