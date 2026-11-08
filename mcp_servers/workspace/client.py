"""Typed client for the local mock Workspace MCP server."""

import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class DemoWorkspace:
    async def _call(self, name: str, arguments: dict):
        server = StdioServerParameters(command=sys.executable, args=["-m", "mcp_servers.workspace.server"])
        async with stdio_client(server) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(name, arguments)
        if result.isError:
            raise RuntimeError(f"Workspace MCP {name} failed")
        if result.structuredContent:
            return result.structuredContent.get("result", result.structuredContent)
        if result.content and result.content[0].type == "text":
            return json.loads(result.content[0].text)
        raise RuntimeError(f"Workspace MCP {name} returned no JSON")

    async def get_free_slots(self, day: str) -> list[str]:
        return await self._call("get_free_slots", {"day": day})

    async def create_tentative_hold(self, slot: str, key: str, dry_run: bool = False) -> dict:
        return await self._call("create_tentative_hold", {"slot": slot, "idempotency_key": key, "dry_run": dry_run})

    async def create_email_draft(self, recipient: str, subject: str, body: str, key: str, dry_run: bool = False) -> dict:
        return await self._call("create_email_draft", {"recipient": recipient, "subject": subject, "body": body, "idempotency_key": key, "dry_run": dry_run})
