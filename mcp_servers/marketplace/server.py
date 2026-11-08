"""Synthetic Marketplace MCP server for development, not a GigSim substitute."""

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from mcp_servers.marketplace.adapters.demo import DemoMarketplace


mcp = FastMCP("GigBid Development Marketplace")
marketplace = DemoMarketplace()


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
async def list_jobs() -> list[dict]:
    """List synthetic development jobs. Read only."""
    return [job.model_dump() for job in await marketplace.list_jobs()]


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
async def get_job(job_id: str) -> dict:
    """Get one synthetic development job by identifier. Read only."""
    try:
        return (await marketplace.get_job(job_id)).model_dump()
    except KeyError:
        return {"error": "not_found", "job_id": job_id}


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True))
async def create_proposal_draft(job_id: str, text: str, idempotency_key: str, dry_run: bool = False) -> dict:
    """Preview or create a synthetic draft. Never submits a bid or message."""
    try:
        return await marketplace.create_proposal_draft(job_id, text, idempotency_key, dry_run)
    except KeyError:
        return {"error": "not_found", "job_id": job_id}


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True))
async def send_message(job_id: str, text: str, idempotency_key: str, dry_run: bool = False) -> dict:
    """Preview or record one synthetic client message. No external message is sent."""
    try:
        return await marketplace.send_message(job_id, text, idempotency_key, dry_run)
    except KeyError:
        return {"error": "not_found", "job_id": job_id}


@mcp.resource("marketplace://jobs/{job_id}")
async def job_resource(job_id: str) -> str:
    """Return a synthetic job as JSON."""
    try:
        return (await marketplace.get_job(job_id)).model_dump_json()
    except KeyError:
        return '{"error":"not_found"}'


if __name__ == "__main__":
    mcp.run()
