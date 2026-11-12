# Data card

## Sources and use

| Source | Status | Use |
| --- | --- | --- |
| [Upwork Job Postings Dataset 2024 (50K Records)](https://www.kaggle.com/datasets/asaniczka/upwork-job-postings-dataset-2024-50k-records), asaniczka | Real, historical, public Kaggle data; ODC Attribution License (ODC-By) | Aggregate fixed-price budget reference only. We do not commit raw posts or treat them as current jobs, client histories, outcomes, or ground truth. |
| `mcp_servers/marketplace/adapters/demo.py` | Three locally authored **synthetic** jobs | UI and workflow tests, including a scam and a prompt-injection example. IDs start `demo-`. |
| `mcp_servers/portfolio/server.py` | Two locally authored **synthetic** evidence items | Portfolio MCP protocol and claim-path demonstrations. They do not describe the student's real work. |
| `evals/datasets/synthetic_*.jsonl` | Six hand-written **synthetic** evidence chunks and four labeled questions | Retrieval smoke test only; no statistically useful comparison. |
| `GigBid_Student_Starter_Kit_v0.1.zip` (Classroom example) | Instructor's example scaffold, inspected 12 November 2026 | Interface and checklist reference only. Its tiny sample records and placeholder code were not copied into this project. It contains no GigSim service, persona corpus, or evaluation set. |

The Classroom update explicitly permits the listed Kaggle datasets and realistic synthetic data if they are distinguished and documented. No instructor GigSim implementation, three-persona corpus, gold development labels, or hidden evaluation set was supplied in the example ZIP. Thus GigSim reply/hire rates, official bid/skip F1, and price-band accuracy **cannot be measured** from these sources. Historical Kaggle posts do not include those labels.

## Kaggle preprocessing and reproducibility

`tools/build_market_priors.py` consumes the Kaggle download ZIP without creating or publishing a raw CSV copy. Run `python tools/build_market_priors.py /path/to/download.zip` from the repository root. The output is [`data/derived/kaggle_market_priors.json`](../data/derived/kaggle_market_priors.json). It records the source URL, ODC-By attribution, ZIP SHA-256, row counts, and category summaries. The source ZIP observed on 12 November 2026 has SHA-256 `3f40f06c267f6429e6c9fdd9a81c0c9eb85edadb1d6638394e9ce5b35`.

The script reads 53,058 rows, removes 23 exact title-and-description duplicates, excludes 22,945 hourly posts and 8,227 fixed-price posts without a budget, and excludes 7,243 budgets outside USD 50–100,000 or nonnumeric. This leaves 14,620 fixed-price postings. A deterministic, mutually exclusive title-keyword rule assigns one of analytics, web development, AI/ML, design, marketing, writing, or other. For each category it reports count, median, and 25th/75th percentiles. These figures describe the supplied 2024 sample only. They are **not** fair-price labels or causal evidence of winning bids; the data is old, heterogeneous, and affected by missing budgets and keyword errors. Category assignment and the USD range filter may bias the medians. Client histories, reviews, proposals, and conversations remain synthetic only.

## Evaluation boundaries

The retrieval smoke fixture uses synthetic evidence and hand-written gold identifiers, with no train/test separation because it is not used for model selection. Any outcome-aware rank feature must come from training history only. No real user portfolio or private client record enters the public repository. Instructor hidden data must never be committed. All public UI labels identify the active workflow as a synthetic preview; its approved writes create local synthetic drafts or messages only.
