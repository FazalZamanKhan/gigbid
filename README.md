# GigBid

GigBid is an **in-progress** AI-4016 Assignment II project. This repository is being built while the instructor's GigSim starter kit and evaluation data are obtained. The current demo uses synthetic local jobs and a deterministic draft; it is **not** a completed submission, deployed application, or measured R&D result.

## Current development slice

- A typed marketplace port has a local demo adapter. The GigSim adapter will be wired to the provided simulator's actual API after the starter kit arrives.
- The bid graph analyses a job, checks a draft against portfolio evidence, and pauses for human approval before any marketplace write. It currently calls a local demo retriever rather than the Portfolio MCP server.
- A FastAPI API exposes jobs, runs, approvals, and health. The React UI displays the inbox and approval panel.
- Portfolio MCP provides read-only evidence tools and resource templates. Marketplace and Workspace servers are being added.

## Run locally

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
make demo
```

For the web UI, run `cd apps/web && npm install && npm run dev`. The API is at `http://localhost:8000`; the Vite UI is at `http://localhost:5173`.

## Assignment status

See [docs/SUBMISSION_STATUS.md](docs/SUBMISSION_STATUS.md) for the rubric audit. No public URL, evaluation number, trace, demo video, or report is claimed until verified. Reviewer credentials must be supplied in a private Google Classroom comment, never in the public repository.
