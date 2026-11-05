# AI usage record

Codex created the initial architecture, Python contracts, LangGraph development bid graph, FastAPI API, React UI, and local tests on 3 November 2026. The student must review and be able to explain every line.

One caught error: Codex initially pinned MCP Python SDK 2.3.0, but `langchain-mcp-adapters==0.3.2` requires `mcp<2`. Dependency resolution failed. The project now pins MCP 1.30.0 and uses that SDK's `FastMCP` import. This must be revisited when the adapter supports SDK 2.x.
