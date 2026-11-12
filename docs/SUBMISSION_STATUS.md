# Submission status — 12 November 2026

The [Google Classroom assignment](https://classroom.google.com/c/ODE5OTY5MDAxMDQx/a/ODk1NzY1NTUyMTUw/details) was edited on 11 November and currently displays **Due Nov 15**. The older attached PDF says 12 November at 11:59 PM PKT. Commit a safe code revision before the older date as well, and verify the Classroom time before final submission. Submit all deliverables together. The work is still marked **Assigned**; no submission is claimed.

| Deliverable | Verified status |
| --- | --- |
| Instructor starter example | Received 12 November. It is a 20 KB scaffold with tiny synthetic examples and placeholders; no working GigSim, personas, or evaluation set. |
| Public source | [Repository](https://github.com/FazalZamanKhan/gigbid) and commit `5e876b0` pushed 12 November; GitHub CI passed. Further code may follow before final submission. |
| Local app | Synthetic bid and conversation approval paths; React build, 16 Python tests and 7 Playwright tests passed locally on 12 November. Docker currently stopped. |
| Data | [Attributed 2024 Kaggle source](DATA_CARD.md) yielded 14,620 fixed-price posts after filtering, used for descriptive budget aggregates only. Synthetic development data is separately labeled. |
| Deployed app and private reviewer login | Pending Render sign-in, deployment, and live verification. Credentials must go in a private Classroom comment only. |
| Published Portfolio MCP | [Public `portfolio-v0.1.0` tag](https://github.com/FazalZamanKhan/gigbid/tree/portfolio-v0.1.0/mcp_servers/portfolio); installation and an MCP call were verified. |
| Technical write-up | [Published GitHub Pages article](https://fazalzamankhan.github.io/gigbid/TECHNICAL_WRITEUP.html), verified HTTP 200. |
| R&D report PDF | [Four-page evidence-limited report](../output/pdf/GigBid_RD_Report.pdf) prepared and visually checked; update it if further experiments are completed. It openly reports missing GigSim results. |
| Three-minute video | [Public viewing page](https://fazalzamankhan.github.io/gigbid/DEMO.html) verified HTTP 200 and its 3:02 MP4 returned a byte-range response. Captioned and silent; synthetic workflow only. |
| ZIP | Regenerate from final committed source if Classroom requests one. |

## Rubric risks

The prototype has no official GigSim integration or simulator outcome measurements. It also lacks a real model-backed Writer and Critic, larger labeled retrieval and agent comparisons, persistent long-term memory, a scheduled worker, full tracing and cost accounting, multi-user authentication, complete required screens, and a fully verified container stack. These missing elements are material for the 100-mark rubric. The example scaffold and Kaggle dataset do not supply the missing GigSim contract or gold outcome labels. No report or README should invent them.

The four-query synthetic retrieval smoke test tied V0/V1/V2/V3/V4/V8 at Recall@5=1.0; this fixture cannot select a production RAG variant, and V4 had no outcome scores to use. Four public JSON files in `docs/traces/` are synthetic LangGraph state snapshots, not production spans. The last verified Postgres restart test covered a bid, not an external-write crash. A live Render URL may use free Postgres, which expires after 30 days and needs maintenance or migration until grades are released.
