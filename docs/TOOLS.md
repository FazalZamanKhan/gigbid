# MCP tool inventory (development)

| Tool | Server | Mode | Auth | Status |
| --- | --- | --- | --- | --- |
| `search_evidence(requirement, k)` | Portfolio | Read | Local stdio | Implemented on synthetic evidence |
| `get_case_study(id)` | Portfolio | Read | Local stdio | Implemented on synthetic evidence |
| `list_skills()` | Portfolio | Read | Local stdio | Implemented on synthetic evidence |

The Marketplace and Workspace MCP servers, HTTP bearer auth, annotations, schema snapshots, and third-party server trust rationales are pending. No agent has a marketplace write tool in the current development build. The sole demo write is behind the graph's human approval interrupt and marketplace port.
