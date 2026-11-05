# Submission status — 6 November 2026

**Deadline:** 12 November 2026, 11:59 PM PKT. Submit all required items together on the correct Google Classroom assignment. Commit final code before the deadline.

| Deliverable | Status |
| --- | --- |
| GigSim starter and dev set | Awaiting instructor kit from student |
| Required full-stack application | In progress; local demo slice only |
| Public deployment and reviewer login | Pending |
| Public GitHub repository and on-time final commit | Pending |
| Measured R&D report PDF | Pending real experiments and results |
| Three-minute demo video | Pending working end-to-end app |
| Published Portfolio MCP server | Pending packaging and release |
| Published technical write-up | Pending real findings |
| Optional source ZIP | Prepare only if requested by Classroom |
| Google Classroom submission and private reviewer comment | Pending correct course access and completed artifacts |

## Rubric audit

| Area | Verified now | Major work still required |
| --- | --- | --- |
| MCP tool layer (20) | Read-only Portfolio MCP on synthetic evidence | GigSim and Workspace servers, third-party integrations, auth, tool annotations, schema snapshots, Inspector evidence, agent access through MCP |
| Advanced RAG (20) | A keyword-based demo retriever and conservative citation check | CV/repo ingestion, V0 plus four measured variants, judge calibration, human panel, ablation, per-persona and job-type results |
| Multi-agent graphs (25) | Parallel bid analysis and real approval interrupt; three local tests pass | Conversation graph, LLM roles, critic loop, Postgres checkpoint, memory, baselines, crash/restart proof, tracing |
| Web interface (15) | React inbox and bid review screen; production build passes | Auth/onboarding, full proposal studio, pipeline, messages, analytics, settings, live streaming, five Playwright tests |
| Production engineering (10) | Local development API and synthetic adapter | Complete Docker Compose, worker, CI/eval gates, budgets, OAuth encryption, tenant isolation, deployment and live monitoring |
| Portfolio and report (10) | Initial README and architecture notes | Measured report PDF, demo GIF/video, three public traces, published MCP package, published write-up, résumé bullet |

**Current verification:** `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python3 -m pytest -q` passed 3 tests on 6 November 2026; `npm run build` passed. These checks cover only the development slice. They do not predict a grade.

Do not fill missing results or URLs with invented values. The Assignment 1 Meeting Sentinel project is unrelated and remains untouched.
