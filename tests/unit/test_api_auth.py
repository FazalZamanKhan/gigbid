import base64
import asyncio

import httpx

from apps.api.main import app


def test_reviewer_credentials_guard_api(monkeypatch):
    monkeypatch.setenv("GIGBID_REVIEWER_USERNAME", "reviewer")
    monkeypatch.setenv("GIGBID_REVIEWER_PASSWORD", "private-test-password")
    async def verify():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            assert (await client.get("/health")).status_code == 200
            assert (await client.get("/jobs")).status_code == 401
            assert (await client.get("/jobs", headers={"Authorization": "Basic !!!"})).status_code == 401
            token = base64.b64encode(b"reviewer:private-test-password").decode()
            assert (await client.get("/jobs", headers={"Authorization": f"Basic {token}"})).status_code == 200

    asyncio.run(verify())

    monkeypatch.delenv("GIGBID_REVIEWER_PASSWORD")

    async def verify_misconfigured():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            assert (await client.get("/jobs")).status_code == 503

    asyncio.run(verify_misconfigured())
