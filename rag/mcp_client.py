"""Portfolio retrieval through the MCP protocol for the development graph."""

import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from agent.handoffs import Evidence, JobSpec


async def search_evidence_mcp(job: JobSpec) -> list[Evidence]:
    server = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_servers.portfolio.server"],
    )
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "search_evidence",
                {"requirement": " ".join(job.skills), "k": 20},
            )
    if result.isError or not result.structuredContent:
        raise RuntimeError("Portfolio MCP search_evidence failed")
    return [Evidence.model_validate(item) for item in result.structuredContent["result"]]
