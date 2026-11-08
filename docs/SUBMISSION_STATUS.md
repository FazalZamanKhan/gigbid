# Submission status — 7 November 2026

**Deadline:** 12 November 2026, 11:59 PM PKT. Submit all required items together on the correct Google Classroom assignment. Commit final code before the deadline.

| Deliverable | Status |
| --- | --- |
| GigSim starter and dev set | Not attached in the AI4015 Classroom Assignment 2 item as of 7 November; classmates have also requested it in comments |
| Required full-stack application | In progress; local demo slice only |
| Public deployment and reviewer login | Pending |
| Public GitHub repository and on-time final commit | Pending |
| Measured R&D report PDF | Pending real experiments and results |
| Three-minute demo video | Pending working end-to-end app |
| Published Portfolio MCP server | Pending packaging and release |
| Published technical write-up | Pending real findings |
| Optional source ZIP | Interim source archive prepared locally; regenerate from the final commit only if requested |
| Google Classroom submission and private reviewer comment | Correct AI4015 course and Assignment 2 page found; submission pending completed artifacts |

## Rubric audit

| Area | Verified now | Major work still required |
| --- | --- | --- |
| MCP tool layer (20) | Portfolio, synthetic Marketplace, and local mock Workspace MCP servers; Docker graphs invoke them through MCP | GigSim, third-party integrations, production auth, schema snapshots, Inspector evidence, MCP-only access for remaining capabilities |
| Advanced RAG (20) | A keyword-based demo retriever and conservative citation check | CV/repo ingestion, V0 plus four measured variants, judge calibration, human panel, ablation, per-persona and job-type results |
| Multi-agent graphs (25) | Parallel bid analysis; bid and conversation approval interrupts; Postgres checkpoint recovered a pending bid approval after API restart | LLM roles, critic loop, memory, baselines, external-write crash proof, tracing |
| Web interface (15) | React inbox, bid review, and synthetic message review screens; production build passes | Auth/onboarding, full proposal studio, pipeline, analytics, settings, live streaming, five Playwright tests |
| Production engineering (10) | Partial Docker Compose starts; web/API/Postgres/Redis respond; reviewer API authentication tests pass | Complete Docker Compose, worker, CI/eval gates, budgets, OAuth encryption, tenant isolation, deployment and live monitoring |
| Portfolio and report (10) | README, architecture notes, a four-page interim PDF, and unpublished write-up/demo outlines | Final measured report PDF, demo video, three public traces, published MCP package and write-up, résumé bullet |

**Current verification:** `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python3 -m pytest -q` passed 8 tests on 7 November 2026; `npm run build` passed. In the previous Docker build, a `demo-1` bid run paused for approval, survived `docker compose restart api`, and created a synthetic draft after approval; `demo-2` skipped with no draft. The new conversation path has passed local automated tests; its container and restart checks are in progress. These checks cover only the synthetic development slice. They do not predict a grade.

Do not fill missing results or URLs with invented values. The Assignment 1 Meeting Sentinel project is unrelated and remains untouched.
