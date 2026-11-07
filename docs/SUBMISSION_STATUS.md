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
| MCP tool layer (20) | Read-only Portfolio MCP on synthetic evidence; fit node invokes `search_evidence` over MCP | GigSim and Workspace servers, third-party integrations, auth, tool annotations, schema snapshots, Inspector evidence, MCP-only access for all capabilities |
| Advanced RAG (20) | A keyword-based demo retriever and conservative citation check | CV/repo ingestion, V0 plus four measured variants, judge calibration, human panel, ablation, per-persona and job-type results |
| Multi-agent graphs (25) | Parallel bid analysis and approval interrupt; Postgres checkpoint recovered a pending approval after API restart | Conversation graph, LLM roles, critic loop, memory, baselines, external-write crash proof, tracing |
| Web interface (15) | React inbox and bid review screen; production build passes | Auth/onboarding, full proposal studio, pipeline, messages, analytics, settings, live streaming, five Playwright tests |
| Production engineering (10) | Partial Docker Compose starts; web/API/Postgres/Redis respond; reviewer API authentication tests pass | Complete Docker Compose, worker, CI/eval gates, budgets, OAuth encryption, tenant isolation, deployment and live monitoring |
| Portfolio and report (10) | README, architecture notes, a four-page interim PDF, and unpublished write-up/demo outlines | Final measured report PDF, demo video, three public traces, published MCP package and write-up, résumé bullet |

**Current verification:** `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python3 -m pytest -q` passed 4 tests on 7 November 2026; `npm run build` passed; `docker compose -f infra/docker-compose.yml up -d --build` started successfully. A `demo-1` run paused for approval, survived `docker compose restart api`, and created a draft after approval. A `demo-2` run skipped with no draft. These checks cover only the synthetic development slice. They do not predict a grade.

Do not fill missing results or URLs with invented values. The Assignment 1 Meeting Sentinel project is unrelated and remains untouched.
