# Architecture (development state)

```mermaid
flowchart LR
    Web[React UI] --> API[FastAPI]
    API --> Bid[LangGraph bid graph]
    Bid --> Port[Marketplace port]
    Port --> Demo[Local synthetic adapter]
    Port --> MarketplaceMCP[Development Marketplace MCP adapter]
    Port -. after kit arrives .-> GigSim[Provided GigSim adapter]
    Bid --> Portfolio[Portfolio MCP]
    Portfolio --> Retrieval[Synthetic evidence corpus]
    Bid --> Gate[Human approval interrupt]
    Gate --> Port
    API --> Conversation[LangGraph conversation graph]
    Conversation --> Workspace[Workspace MCP mock]
    Conversation --> MessageGate[Human message approval]
    MessageGate --> Port
```

The marketplace port is the sole write boundary. The graph analyses a job through parallel Analyst, Risk Assessor, and Fit Matcher branches, then prepares a draft and pauses for approval. Local runs default to an in-memory checkpointer; the Docker development stack selects Postgres checkpoints. The local adapter and evidence corpus are synthetic, so they cannot support assignment results.

The fit node consumes the Portfolio MCP `search_evidence` tool over a stdio session. The Docker stack selects an MCP-backed implementation of the typed marketplace port; local tests can use the direct adapter. The conversation graph classifies synthetic incoming messages, reads mock free slots from the Workspace MCP server, drafts a reply, and requires a separate human approval interrupt before the Marketplace MCP message tool records it. The Workspace mock can also save idempotent tentative holds and email drafts; neither action contacts an external service. The real GigSim adapter, scheduled worker, tracing, and measured RAG variants remain to be implemented. Postgres checkpoints are available in the partial Docker development stack; other state is process-local or in a local mock SQLite store.
