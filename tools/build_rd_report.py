"""Build the assignment report from committed measurements and explicit gaps."""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output/pdf/GigBid_RD_Report.pdf"
MARKET = json.loads((ROOT / "data/derived/kaggle_market_priors.json").read_text())
RETRIEVAL = json.loads((ROOT / "evals/results/synthetic_retrieval.json").read_text())

navy = colors.HexColor("#15263c")
blue = colors.HexColor("#1d526c")
gold = colors.HexColor("#ba8b3b")
muted = colors.HexColor("#526276")
pale = colors.HexColor("#eef3f6")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleX", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=25, leading=29, textColor=navy, spaceAfter=12))
styles.add(ParagraphStyle(name="SubtitleX", parent=styles["Normal"], fontSize=12, leading=17, textColor=blue, spaceAfter=13))
styles.add(ParagraphStyle(name="HeadingX", parent=styles["Heading1"], fontSize=15, leading=18, textColor=navy, spaceBefore=10, spaceAfter=7))
styles.add(ParagraphStyle(name="SubheadX", parent=styles["Heading2"], fontSize=10.5, leading=13, textColor=blue, spaceBefore=8, spaceAfter=5))
styles.add(ParagraphStyle(name="BodyX", parent=styles["BodyText"], fontSize=9.1, leading=12.7, textColor=navy, spaceAfter=7))
styles.add(ParagraphStyle(name="SmallX", parent=styles["BodyText"], fontSize=7.6, leading=10, textColor=navy, spaceAfter=4))
styles.add(ParagraphStyle(name="HeaderX", parent=styles["SmallX"], fontName="Helvetica-Bold", textColor=colors.white))
styles.add(ParagraphStyle(name="CenterX", parent=styles["Normal"], alignment=TA_CENTER, fontSize=8, textColor=muted))


def p(value: str, style: str = "BodyX") -> Paragraph:
    return Paragraph(value, styles[style])


def tbl(rows: list[list[str]], widths: list[float]) -> Table:
    table = Table([[p(str(cell), "HeaderX" if index == 0 else "SmallX") for cell in row] for index, row in enumerate(rows)],
                  colWidths=widths, hAlign="LEFT", repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), navy),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, pale]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, 0), 1, gold),
    ]))
    return table


def page(canvas, doc):
    canvas.saveState()
    width, height = doc.pagesize
    canvas.setStrokeColor(gold)
    canvas.setLineWidth(1.4)
    canvas.line(.65 * inch, height - .55 * inch, width - .65 * inch, height - .55 * inch)
    canvas.setFillColor(navy)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(.65 * inch, height - .42 * inch, "GIGBID  /  AI-4016 R&D REPORT")
    canvas.setFillColor(muted)
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(width - .65 * inch, .42 * inch, f"12 Nov 2026  |  Page {doc.page}")
    canvas.restoreState()


story: list = []
story += [Spacer(1, .5 * inch), p("GigBid", "TitleX"), p("Research and Development Report", "SubtitleX")]
story += [p("Fazal Zaman Khan | Individual AI-4016 Assignment II | Evidence available 12 November 2026")]
story += [p("<b>Research question.</b> Can an evidence-grounded, human-reviewed agent workflow prepare freelance proposals while preserving a traceable decision and blocking unapproved writes? This report evaluates an implemented synthetic development slice. It does not claim simulator reply or hire outcomes.")]
story += [p("<b>Hypothesis.</b> Parallel requirement, risk, and fit analysis behind MCP tools can produce a reviewable proposal decision while an interrupt prevents external writes until approval. Retrieval variants should be selected only when a labeled development set distinguishes them.")]
story += [p("1. Scope and data", "HeadingX")]
story += [tbl([
    ["Source", "Use and boundary"],
    ["Course example starter ZIP", "Inspected 12 Nov. Contains directory suggestions, templates, and tiny synthetic samples; no working GigSim, personas, or official evaluation labels. Its placeholder code and sample records were not copied."],
    ["Own synthetic development set", "Three demo jobs, two portfolio records, six evidence chunks and four labeled retrieval queries. The UI and tests mark these synthetic; they are not freelancer experience or marketplace performance."],
    ["Asaniczka 2024 Upwork jobs", "Instructor-permitted public Kaggle source, ODC Attribution. Used only for aggregate fixed-price budget references. No raw post text or live-job claims enter the repository."],
], [1.55 * inch, 5.2 * inch])]
story += [p("The original brief dated 27 October states a 12 November deadline; the Classroom assignment was edited on 11 November and displays <b>Due Nov 15</b>. The current Classroom deadline should be checked at submission. This discrepancy does not affect the measured results.", "SmallX")]
story += [PageBreak()]

story += [p("2. Design and safety", "HeadingX")]
story += [p("React calls a FastAPI API. The bid LangGraph loads a synthetic job through one typed marketplace port. Job analysis, risk scoring, and portfolio matching fan out in parallel. The fit branch calls the Portfolio MCP server over an actual stdio MCP session; the container path also uses a synthetic Marketplace MCP service. A decision node chooses bid, watch, or skip. Bid paths calculate a price and write a deterministic cited draft. A rule-based Critic rejects its generic opening, sends it back to the Writer once, and accepts the revised draft; configuration caps revisions at two. Claim and phrase checks then precede a human approval interrupt. Only approval resumes to create a synthetic marketplace draft. The conversation graph drafts a reply using Workspace MCP slots and interrupts before recording a synthetic message.")]
story += [tbl([
    ["Boundary", "Implemented", "Limit"],
    ["Marketplace", "Typed port; synthetic direct/MCP adapters; dry-run and idempotent draft/message methods", "No actual GigSim API was supplied; no live Upwork account or OAuth"],
    ["Portfolio", "Read-only MCP search, case-study lookup, skills, resource template and prompt", "Two invented examples only; no CV or repository ingestion"],
    ["State", "LangGraph human interrupts; in-memory local checkpoints; optional Postgres checkpoints in Docker", "No durable outbox or arbitrary external-write crash proof"],
    ["Safety", "Configurable risk phrases, injection skip, bounded deterministic Critic loop, claim check and approval gate", "Rule-based checks can miss novel attacks or unsupported paraphrases"],
], [1.12 * inch, 3.15 * inch, 2.48 * inch])]
story += [p("A scam example asking for free work and off-platform contact is skipped before approval. A planted instruction to claim false experience is also skipped. Rejection does not create a draft. Editing the proposal blocks the write pending another check; it does not silently send changed text. The approved synthetic message path also requires an interrupt. These invariants have automated tests, but their measured attack success rate on a realistic attack distribution remains unknown.")]
story += [p("The previous Postgres container check paused one bid at approval, restarted the API, resumed it, and produced one synthetic draft. This shows recovery for that case. It does not establish exactly-once delivery if a process fails after a remote write but before checkpoint persistence.")]
story += [PageBreak()]

story += [p("3. Measured results and interpretation", "HeadingX")]
story += [p("<b>Engineering tests.</b> On 12 November, 16 Python tests and seven Playwright end-to-end tests passed locally; TypeScript/Vite production build passed. GitHub CI passed for commit bba9749, including Python, web, browser, and hosted-image jobs. Browser tests cover local demo setup persistence, approve, reject with reason, edited-draft hold, marketplace outage banner, scam/injection skip, and approved synthetic client reply. These are workflow checks, not a statistical quality estimate.")]
story += [p("<b>Retrieval smoke.</b> A BGE small English embedding model ran on four hand-written queries over six synthetic chunks. All four variants below returned every relevant item. The fixture is too easy to select a deployed design; V3/V4 reranker measurements are absent from this result. Query timings exclude initial index build but include Python overhead and vary with local CPU conditions.")]
rows = [["Variant", "Recall@5", "MRR", "nDCG@10", "p95 query ms"]]
for key, label in (("v0", "V0 dense"), ("v1", "V1 decomposition"), ("v2", "V2 hybrid"), ("v8", "V8 corrective")):
    result = RETRIEVAL["variants"][key]["aggregate"]
    rows.append([label, f"{result['recall_at_5']:.2f}", f"{result['mrr']:.2f}", f"{result['ndcg_at_10']:.2f}", f"{result['p95_latency_ms']:.0f}"])
story += [tbl(rows, [1.85 * inch, 1.05 * inch, .8 * inch, 1.15 * inch, 1.9 * inch])]
story += [p("The perfect tie rejects a tempting but unsupported conclusion that advanced retrieval improved relevance. The application still uses a transparent keyword search over its two demo portfolio records. The V0/V1/V2/V3/V4/V8 harness is implemented, but a larger independently labeled set and full reranker run are needed before choosing a production variant.")]
story += [p("<b>Tool design and agent comparisons.</b> The prescribed 40-task MCP tool-granularity study and 50-job single-agent/supervisor/hand-built graph comparison were not run. No selection accuracy, argument accuracy, token cost, judge calibration, GigSim reply/hire rate, official bid F1, or per-proposal p95/cost is reported. The example kit and Kaggle data do not contain the required outcome labels.")]
story += [PageBreak()]

story += [p("4. Historical market data and limits", "HeadingX")]
count = MARKET["rows"]
story += [p(f"The Kaggle ZIP held {count['total']:,} rows. The reproducible script removed {count['duplicates']:,} exact title/description duplicates, {count['hourly_excluded']:,} hourly rows, {count['missing_budget']:,} rows without a fixed budget, and {count['invalid_or_outlier_budget']:,} invalid or out-of-range budgets. It retained {count['included']:,} fixed-price posts in USD 50-100,000. A deterministic title-keyword rule assigned mutually exclusive categories. The table is descriptive and is not a fair-price label or evidence of winning bids.")]
market_rows = [["Title category", "Posts", "Median USD", "P25 USD", "P75 USD"]]
for key in ("analytics", "web_development", "ai_ml", "design", "marketing", "writing", "other"):
    item = MARKET["categories"][key]
    market_rows.append([key.replace("_", " ").title(), f"{item['count']:,}", f"{item['median_usd']:,.0f}",
                        f"{item['p25_usd']:,.0f}", f"{item['p75_usd']:,.0f}"])
story += [tbl(market_rows, [2 * inch, 1 * inch, 1.25 * inch, 1.25 * inch, 1.25 * inch])]
story += [p("The source dates to 2024. Titles can be ambiguous; missing budgets and the USD range filter can bias medians. Fixed projects differ greatly in scope, and historical posted budgets do not tell us what freelancers charged or whether clients replied. The script publishes no raw descriptions, URLs, names, or private data. The data card records the source URL, ODC-By license, exact SHA-256 of the downloaded ZIP, filters, and derived JSON.")]
story += [p("5. Research decision and remaining work", "HeadingX")]
story += [p("The evidence supports a narrow engineering conclusion: the synthetic approval path prevents the demonstrated unapproved writes, and the MCP/graph interfaces execute end to end. It does <b>not</b> establish improved proposal quality or marketplace outcomes. The next required study needs an actual GigSim contract and labeled personas, a harder retrieval set, model-backed Writer/Critic and calibrated judging, a controlled agent baseline, production traces with latency/cost, and a forced external-write crash test. The final deployed preview also needs public URL, reviewer login, video, and long-lived hosting verification.")]
story += [p("<b>Reproduce.</b> Run <font face='Courier'>PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q</font>, <font face='Courier'>cd apps/web &amp;&amp; npm run test:e2e</font>, and <font face='Courier'>python tools/build_market_priors.py PATH_TO_KAGGLE_ZIP</font>. Exact retrieval input hashes and model ID are in <font face='Courier'>evals/results/synthetic_retrieval.json</font>. Source and methods: <link href='https://github.com/FazalZamanKhan/gigbid'>github.com/FazalZamanKhan/gigbid</link>; Kaggle source: <link href='https://www.kaggle.com/datasets/asaniczka/upwork-job-postings-dataset-2024-50k-records'>asaniczka, Upwork Job Postings Dataset 2024</link>; assignment brief: AI-4016 Assignment II PDF and later Classroom update.", "SmallX")]

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
doc = SimpleDocTemplate(str(OUTPUT), pagesize=(8.5 * inch, 11 * inch), leftMargin=.7 * inch,
                        rightMargin=.7 * inch, topMargin=.8 * inch, bottomMargin=.7 * inch,
                        title="GigBid Research and Development Report", author="Fazal Zaman Khan")
doc.build(story, onFirstPage=page, onLaterPages=page)
print(OUTPUT)
