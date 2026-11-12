# Three-minute demo outline (recording pending)

This is a recording plan for the synthetic preview. The example starter ZIP does not include a working GigSim. If a simulator is supplied, record a verified GigSim-backed flow instead. Do not describe the synthetic examples as evaluation results.

| Time | Show | Narration |
| --- | --- | --- |
| 0:00-0:25 | GigBid inbox and synthetic data badge | Explain that the supplied kit is an example scaffold and the current flow uses synthetic data. |
| 0:25-1:05 | Open the dashboard job | Show the parallel analysis timeline, fit evidence, risk score, and bid decision. Identify the Portfolio MCP evidence source. |
| 1:05-1:40 | Proposal studio | Show the cited portfolio claim, price rationale, dry-run preview, and approval pause. Reload the page to show run recovery. |
| 1:40-2:10 | Reject one run, then approve a new run | Point out that rejection creates no draft. Approval creates only a draft after the explicit human action. |
| 2:10-2:40 | Open the suspicious job | Show risk flags and the skip decision. No approval step appears. |
| 2:40-3:00 | Source and limitations | Show tests/README briefly and state that official GigSim, measured RAG results, and deployment are pending. |

Before publishing any replacement, verify audio or captions, page legibility, a viewable link, duration near three minutes, and that no credentials or private data appear on screen.

The current [captioned recording](DEMO.html) is 3:02 and silent. It was generated from the local synthetic app using `apps/web/scripts/record-demo.mjs` at `http://127.0.0.1:8020/`; the script records UI interactions with Playwright and never opens a live marketplace. To reproduce it, build the web app, start `python -m uvicorn apps.api.public:app --host 127.0.0.1 --port 8020`, then run `node scripts/record-demo.mjs` from `apps/web`. The source WebM is written to `tmp/demo-video/`; the public MP4 and GIF were compressed from it with FFmpeg.
