# GigBid: a human-reviewed bid workflow

GigBid is a development prototype for a freelance bidding assistant. The current build uses two synthetic jobs and synthetic portfolio evidence because the GigSim starter kit and evaluation set were not attached to the Classroom assignment when this work began. The prototype demonstrates the workflow; it does not establish marketplace performance.

## Architecture

The React inbox calls a FastAPI service. A LangGraph workflow loads a job through a typed marketplace port, then runs requirement analysis, risk assessment, and portfolio fit matching in parallel. The decision node chooses bid, watch, or skip from configurable thresholds. A bid path produces a price and a cited draft, checks claims and prohibited language, and pauses at a LangGraph human interrupt. Approval creates a draft through the marketplace port with an idempotency key. Rejection ends the run without a write. An edited draft is held because a changed claim requires another evidence and compliance pass.

The default local run uses an in-memory checkpointer. The Docker development stack uses a Postgres checkpointer, so the pending approval can survive an API restart. Redis is provisioned for the planned worker but is not used by the current graph. The Portfolio MCP server exposes read-only evidence tools, a case-study resource, and a screening-answer prompt. The fit node invokes its evidence search over a real MCP stdio session. The Docker stack uses a Marketplace MCP adapter for synthetic job reads and draft creation; local tests may use the direct adapter. Workspace MCP and real GigSim integration remain pending.

## Safety boundary

The marketplace port is the only place that can create a draft. The approval node first requests a dry-run preview. A real draft is created only after an explicit `approved: true` response for an unchanged draft. The demo adapter never contacts a live marketplace. The graph cannot submit a bid or send a client message.

## What the demo proves

The integration tests exercise a bid that pauses for approval, an approval that creates one draft, and a rejected draft that causes no write. The React production build and API smoke test cover the current UI/API shape. The Docker stack is tested separately for container startup and checkpoint recovery. These checks are engineering checks, not R&D evaluation results.

## Next integration steps

After the instructor publishes the GigSim kit, implement the adapter against its documented API and preserve its fixtures unchanged. Replace synthetic evidence with consented CV, project, and repository records. Add Marketplace and Workspace MCP servers, enforce MCP access from the graph, build the conversation workflow, and run the prescribed RAG and graph evaluations on the official split. The report must state exact denominators, per-persona and job-type results, failures, and limitations. Only those measured results should appear in the public technical write-up.
