"""MarketplacePort implementation that calls the synthetic MCP server."""

import sys
import json

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from agent.handoffs import JobSpec


class DemoMCPMarketplace:
    async def _call(self, name: str, arguments: dict) -> object:
        server = StdioServerParameters(
            command=sys.executable,
            args=["-m", "mcp_servers.marketplace.server"],
        )
        async with stdio_client(server) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(name, arguments)
        if result.isError:
            raise RuntimeError(f"Marketplace MCP {name} failed")
        if result.structuredContent:
            return result.structuredContent.get("result", result.structuredContent)
        if result.content and result.content[0].type == "text":
            return json.loads(result.content[0].text)
        raise RuntimeError(f"Marketplace MCP {name} returned no JSON")

    async def list_jobs(self) -> list[JobSpec]:
        return [JobSpec.model_validate(item) for item in await self._call("list_jobs", {})]

    async def get_job(self, job_id: str) -> JobSpec:
        item = await self._call("get_job", {"job_id": job_id})
        if item.get("error") == "not_found":
            raise KeyError(job_id)
        return JobSpec.model_validate(item)

    async def create_proposal_draft(
        self, job_id: str, text: str, idempotency_key: str, dry_run: bool = False
    ) -> dict:
        result = await self._call("create_proposal_draft", {
            "job_id": job_id,
            "text": text,
            "idempotency_key": idempotency_key,
            "dry_run": dry_run,
        })
        if result.get("error") == "not_found":
            raise KeyError(job_id)
        return result

    async def send_message(
        self, job_id: str, text: str, idempotency_key: str, dry_run: bool = False
    ) -> dict:
        result = await self._call("send_message", {
            "job_id": job_id,
            "text": text,
            "idempotency_key": idempotency_key,
            "dry_run": dry_run,
        })
        if result.get("error") == "not_found":
            raise KeyError(job_id)
        return result
