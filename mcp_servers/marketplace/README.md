# Development Marketplace MCP server

This server exposes **synthetic jobs only**. It is not the instructor's GigSim, and its in-memory draft registry is not durable across server processes. The adapter returns a deterministic draft ID for a given idempotency key, but that is not proof of exactly-once external writes.

```bash
python -m mcp_servers.marketplace.server
```

Tools: `list_jobs`, `get_job`, and `create_proposal_draft`. Resource template: `marketplace://jobs/{job_id}`. The draft tool supports `dry_run`; it never submits a bid or sends a message. The Docker API selects the MCP-backed port with `GIGBID_MARKETPLACE=demo_mcp`, while ordinary local tests default to the direct synthetic adapter. The graph's human approval interrupt guards the draft write.
