# Submission status — 8 November 2026

**Deadline:** 12 November 2026, 11:59 PM PKT. Submit all required items together on the correct Google Classroom assignment. Commit final code before the deadline.

| Deliverable | Status |
| --- | --- |
| GigSim starter and dev set | Not attached in the AI-4016 Classroom Assignment II item as of 8 November; classmates have also requested it in comments |
| Required full-stack application | In progress; local synthetic bid and conversation slices work |
| Public deployment and reviewer login | Pending |
| Public GitHub repository and on-time final commit | [Public repository](https://github.com/FazalZamanKhan/gigbid) exists; interim commits on time, final commit still pending |
| Measured R&D report PDF | Pending real experiments and results |
| Three-minute demo video | Pending working end-to-end app |
| Published Portfolio MCP server | [Synthetic development release](https://github.com/FazalZamanKhan/gigbid/tree/portfolio-v0.1.0/mcp_servers/portfolio) and documented `uvx` command live; Git-tag installation and MCP call verified |
| Published technical write-up | [1,500-word article](https://fazalzamankhan.github.io/gigbid/TECHNICAL_WRITEUP.html) live; explicitly discloses synthetic development scope |
| Optional source ZIP | Interim source archive prepared locally; regenerate from the final commit only if requested |
| Google Classroom submission and private reviewer comment | Correct assignment page found; submission pending completed artifacts |

## Rubric audit

| Area | Verified now | Major work still required |
| --- | --- | --- |
| MCP tool layer (20) | Portfolio, synthetic Marketplace, and local mock Workspace MCP servers; Docker graphs invoke them through MCP | GigSim, third-party integrations, production auth, schema snapshots, Inspector evidence, MCP-only access for remaining capabilities |
| Advanced RAG (20) | Keyword demo retriever and conservative citation check; V0/V1/V2/V3/V4/V8 experiment harness; BGE embedding smoke run on four synthetic cases | Official corpus/results, cross-encoder model download, chosen deployed variant, judge calibration, human panel, ablation, per-persona and job-type evidence |
| Multi-agent graphs (25) | Parallel bid analysis; bid and conversation approval interrupts; Postgres checkpoint recovered a pending bid approval after API restart; synthetic state traces exported | LLM roles, critic loop, memory, baselines, external-write crash proof, production tracing |
| Web interface (15) | React inbox, bid review, and synthetic message review screens; production build passes | Auth/onboarding, full proposal studio, pipeline, analytics, settings, live streaming, five Playwright tests |
| Production engineering (10) | Partial Docker Compose previously started; web/API/Postgres/Redis responded; reviewer API auth and CI pass, including the hosted image build; single-origin preview entry point tested locally | Complete Docker Compose, worker, official eval gates, budgets, OAuth encryption, tenant isolation, deployment and live monitoring |
| Portfolio and report (10) | README, architecture notes, four synthetic public state traces, a four-page interim PDF, a published synthetic Portfolio MCP release, a published technical write-up, and an honest résumé bullet | Final measured report PDF, demo video, production traces with cost |

**Current verification:** `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q` passed 16 tests on 8 November 2026; `npm run build` passed; [GitHub CI](https://github.com/FazalZamanKhan/gigbid/actions) passed the prior push. The local browser completed a synthetic bid review and approved a synthetic client reply. The retrieval harness ran V0/V1/V2/V8 with a real BGE embedding model on four trivial synthetic queries; all retrieved the relevant item, so this is a smoke check rather than comparative evidence. The cross-encoder model download failed on a network error. In the previous Docker build, a bid run survived an API restart and created one synthetic draft. Docker is currently stopped, so the newer conversation and hosted entry point have not had a container check. These checks do not predict a grade.

Do not fill missing results or URLs with invented values. The Assignment 1 Meeting Sentinel project is unrelated and remains untouched.
