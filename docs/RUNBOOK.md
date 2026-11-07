# Runbook (development)

The default FastAPI process uses an in-memory LangGraph checkpointer. Restarting the API loses pending approvals and synthetic drafts. Set `GIGBID_CHECKPOINT_BACKEND=postgres` and `DATABASE_URL` to use `AsyncPostgresSaver`; startup creates its checkpoint tables. Set `LANGGRAPH_STRICT_MSGPACK=true` before startup. On 7 November, the Docker stack recovered a pending synthetic approval after an API restart, then created the approved draft. This does not establish exactly-once behavior under a crash during the external write; a durable marketplace write outbox is still needed.

Set both `GIGBID_REVIEWER_USERNAME` and `GIGBID_REVIEWER_PASSWORD` to require HTTP Basic authentication for API data and actions. Leave them unset only for local development. Serve a public deployment through HTTPS. Generate a unique password outside Git and share it only in the private Google Classroom comment.

Before public deployment: use the Postgres checkpointer in production and verify crash/restart behavior, add Redis-backed scheduling, connect the provided GigSim adapter if released, wire the remaining MCP servers and token storage, verify idempotent writes after a forced restart, add tenant-scoped authentication, and run the required evaluations. Configure all secrets through environment variables and keep `.env` out of Git.
