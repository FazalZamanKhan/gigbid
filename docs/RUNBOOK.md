# Runbook (development)

The current FastAPI process and LangGraph checkpointer are memory-backed. Restarting the API loses pending approvals and synthetic drafts. This is a development limitation and **does not satisfy** the assignment's crash-and-resume requirement.

Before public deployment: replace the checkpointer with Postgres, add Redis-backed scheduling, connect the provided GigSim adapter, wire the remaining MCP servers and token storage, verify idempotent writes after a forced restart, add tenant-scoped authentication, and run the required evaluations. Configure all secrets through environment variables and keep `.env` out of Git.
