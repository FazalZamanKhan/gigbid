# MCP tool inventory (development)

| Tool | Server | Mode | Auth | Status |
| --- | --- | --- | --- | --- |
| `search_evidence(requirement, k)` | Portfolio | Read | Local stdio | Implemented on synthetic evidence |
| `get_case_study(id)` | Portfolio | Read | Local stdio | Implemented on synthetic evidence |
| `list_skills()` | Portfolio | Read | Local stdio | Implemented on synthetic evidence |
| `list_jobs()` | Development Marketplace | Read | Local stdio | Implemented on synthetic jobs |
| `get_job(job_id)` | Development Marketplace | Read | Local stdio | Implemented on synthetic jobs |
| `create_proposal_draft(job_id, text, idempotency_key, dry_run)` | Development Marketplace | Draft write | Local stdio and graph approval | Synthetic draft only; never submits a bid |

The development Marketplace MCP server has read-only and idempotent tool annotations. It is not the instructor's GigSim. The Workspace MCP server, production HTTP bearer auth, schema snapshots, and third-party server trust rationales are pending. The sole synthetic draft write is behind the graph's human approval interrupt and marketplace port.
