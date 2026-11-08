"""Build the transparent, pre-evaluation GigBid R&D report draft."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "GigBid_RD_Report_INTERIM.pdf"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

navy = colors.HexColor("#14243b")
gold = colors.HexColor("#bd8b3c")
gray = colors.HexColor("#526277")
pale = colors.HexColor("#f3f6fa")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=25, leading=31, textColor=navy, spaceAfter=16))
styles.add(ParagraphStyle(name="Sub", parent=styles["Normal"], fontSize=12, leading=18, textColor=gray, spaceAfter=14))
styles.add(ParagraphStyle(name="H1x", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=16, leading=20, textColor=navy, spaceBefore=14, spaceAfter=8))
styles.add(ParagraphStyle(name="H2x", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11, leading=15, textColor=navy, spaceBefore=11, spaceAfter=5))
styles.add(ParagraphStyle(name="Bodyx", parent=styles["BodyText"], fontSize=9.5, leading=14, textColor=navy, spaceAfter=7))
styles.add(ParagraphStyle(name="Smallx", parent=styles["BodyText"], fontSize=8, leading=11, textColor=gray, spaceAfter=5))
styles.add(ParagraphStyle(name="TableHeader", parent=styles["Smallx"], textColor=colors.white, fontName="Helvetica-Bold"))
styles.add(ParagraphStyle(name="Centerx", parent=styles["Normal"], alignment=TA_CENTER, fontSize=9, textColor=gray))


def p(text, style="Bodyx"):
    return Paragraph(text, styles[style])


def heading(text):
    return p(text, "H1x")


def subheading(text):
    return p(text, "H2x")


def table(rows, widths):
    data = [[p(str(cell), "TableHeader" if index == 0 else "Smallx") for cell in row] for index, row in enumerate(rows)]
    result = Table(data, colWidths=widths, hAlign="LEFT", repeatRows=1)
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), navy),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, pale]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LINEBELOW", (0, 0), (-1, 0), 1, gold),
    ]))
    return result


def page(canvas, doc):
    canvas.saveState()
    width, height = doc.pagesize
    canvas.setStrokeColor(gold)
    canvas.setLineWidth(1.5)
    canvas.line(0.65 * inch, height - 0.55 * inch, width - 0.65 * inch, height - 0.55 * inch)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(navy)
    canvas.drawString(0.65 * inch, height - 0.42 * inch, "GIGBID  /  INTERIM R&D REPORT")
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(gray)
    canvas.drawRightString(width - 0.65 * inch, 0.42 * inch, f"8 Nov 2026  |  Page {doc.page}")
    canvas.restoreState()


story = []
story += [Spacer(1, 0.75 * inch), p("GigBid", "CoverTitle"), p("Research & Development Report - Interim Draft", "Sub")]
story += [p("Individual AI-4016 Assignment II | Development checkpoint: 8 November 2026", "Bodyx")]
story += [Spacer(1, 0.2 * inch)]
story += [table([
    ["Status", "Evidence at this checkpoint"],
    ["Prototype", "A local React/FastAPI application, bid and conversation LangGraph workflows, and three development MCP servers exist."],
    ["Verified", "Sixteen automated tests, the React production build, and GitHub CI pass. An earlier Docker bid run survived an API restart; the newer conversation path awaits a container check."],
    ["Unavailable", "The instructor's GigSim starter kit and official evaluation data were not attached to the Classroom assignment at the time of this report."],
    ["Submission", "This is an interim draft. It must not be treated as the final measured R&D submission."],
], [1.2 * inch, 5.55 * inch])]
story += [Spacer(1, 0.25 * inch), p("Research question", "H1x")]
story += [p("Can an evidence-grounded, human-reviewed agent workflow prepare safer freelance proposals while preserving a traceable decision and preventing unapproved marketplace writes? The current prototype tests the engineering path. It cannot answer marketplace quality or performance questions until the official simulator, personas, and evaluation split are available.")]
story += [PageBreak()]

story += [heading("1. System design")]
story += [p("The web inbox sends a job identifier to FastAPI. A typed marketplace port loads the job through the synthetic Marketplace MCP server in the Docker stack. A LangGraph fan-out runs an analyst, risk assessor, and fit matcher in parallel. The fit matcher calls the Portfolio MCP server's <b>search_evidence</b> tool through a real MCP stdio session. A decision node selects bid, watch, or skip from configuration thresholds. The bid branch prepares a price and a cited proposal draft, checks claim support and prohibited phrases, and pauses at a human approval interrupt. A synthetic draft is created only after approval. A separate conversation graph classifies a synthetic client message, reads mock interview slots through Workspace MCP, drafts a reply, and pauses before recording a synthetic message.")]
story += [table([
    ["Boundary", "Current implementation", "Remaining integration"],
    ["Marketplace", "Typed port with synthetic MCP-backed draft and message tools", "Instructor GigSim adapter and durable write idempotency"],
    ["Evidence", "Portfolio MCP over synthetic records; six retrieval variants in an experiment harness", "Consented portfolio, official labels, chosen measured retrieval design"],
    ["State", "Memory locally; optional Postgres checkpointer in Docker", "Restart test, outbox, scheduling, multi-tenant isolation"],
    ["Human control", "Dry-run previews and bid/message approval interrupts", "Full reviewer studio and conversation escalation"],
], [1.05 * inch, 2.65 * inch, 3.05 * inch])]
story += [subheading("Safety invariants")]
story += [p("The demo adapter performs no live marketplace action. Rejection creates no draft or message. A job post with an instruction aimed at the assistant is hard-skipped, even if its numeric risk score is below the general threshold. An edited proposal is held for renewed claim and compliance review; an edited reply is checked against forbidden phrases. Approval paths use separate idempotency keys. The Workspace server stores only local mock holds and email drafts. The API can require reviewer HTTP Basic authentication when both environment variables are configured; public deployment must use HTTPS and stronger tenant controls.")]
story += [subheading("Traceability")]
story += [p("Each graph run stores state and event labels, including extracted requirements, risk check, portfolio fit, decision, price, draft, compliance, and human action. Four exported synthetic state snapshots under <b>docs/traces</b> show approval, scam skip, injection skip, and client reply paths; they are not production spans with model cost. A containerized run paused at approval, survived an API restart through Postgres, and finished after approval. This demonstrates checkpoint recovery for one synthetic run, not exactly-once marketplace writes under arbitrary failure.")]
story += [PageBreak()]

story += [heading("2. Verification and R&D method")]
story += [p("The present checks establish only that the local development slice behaves as designed. They are not measurements on the assignment's hidden or official data.")]
story += [table([
    ["Check", "Observed result", "Interpretation"],
    ["Automated Python tests", "16 passed on 8 Nov 2026", "Bid and conversation approvals, MCP mock behavior, retrieval control flow, API routing, and reviewer authentication work locally."],
    ["React production build", "Passed on 8 Nov 2026", "TypeScript and Vite compile the current UI, including message review."],
    ["MCP protocol call", "search_evidence returned typed synthetic records", "The portfolio server can be called over MCP, and the fit node uses that path."],
    ["Retrieval smoke", "4 tiny synthetic queries; V0/V1/V2/V8 returned all gold items", "Real BGE embeddings ran; this trivial fixture is not comparative evidence or an official result. Cross-encoder model fetch is pending."],
    ["Docker Compose", "Earlier bid check passed; new check pending", "An MCP-backed bid approval survived API restart and created one synthetic draft. Docker stopped after a host restart before the conversation path could be checked."],
], [1.5 * inch, 1.8 * inch, 3.45 * inch])]
story += [subheading("Planned evaluation after the official kit arrives")]
story += [p("Preserve the instructor's provided fixtures and train/dev/test split. Register the exact corpus and parser versions. Compare a transparent keyword baseline against at least four retrieval variants, including sparse, dense, hybrid, and reranked retrieval where feasible. Measure retrieval recall at k, citation support, unsupported claim rate, proposal quality with calibrated human judging, latency, and cost. Report confidence intervals and results by persona and job type. Include an ablation for evidence retrieval and a baseline graph comparison. Use the prescribed GigSim outcomes and release no hidden labels into the model prompt.")]
story += [subheading("Release gates")]
story += [p("The final report should include the exact dataset count, exclusions, label rubric, annotator agreement, seeds, model and prompt versions, per-variant tables, failure examples, trace links, and reproducible commands. None of those values is estimated in this interim draft.")]
story += [PageBreak()]

story += [heading("3. Limitations and next steps")]
story += [p("The synthetic jobs and evidence are small and hand-written. The deterministic writer does not demonstrate LLM reasoning or response quality. The retrieval smoke fixture has only four straightforward queries; perfect retrieval there cannot justify a production variant. The project still lacks the official GigSim adapter, real model service, scheduled worker, full RAG study, browser end-to-end suite, and public application deployment. The synthetic Portfolio MCP development release and technical write-up are public. The only verified system outcome is prototype behavior on the included examples.")]
story += [table([
    ["Priority", "Required work", "Acceptance evidence"],
    ["1", "Obtain and inspect the official GigSim kit and evaluation data", "Adapter contract, unchanged fixtures, data card"],
    ["2", "Complete GigSim integration, durable external writes, and conversation verification", "Inspector snapshots, restart and isolation tests"],
    ["3", "Run measured RAG and graph evaluations", "Reproducible scripts, labeled results, human panel, ablations"],
    ["4", "Deploy, publish, record, and submit", "Live URLs, final commit, three-minute video, final PDF, private reviewer comment"],
], [0.8 * inch, 3.4 * inch, 2.55 * inch])]
story += [Spacer(1, 0.3 * inch), p("Integrity note", "H1x")]
story += [p("No result in this document is described as an instructor evaluation. The report should be revised after the complete system and official data are available. A final submission must provide working public links and one coherent Classroom submission before the deadline.")]
story += [Spacer(1, 0.25 * inch), p("Source and reproducibility", "H1x")]
story += [p("Implementation source: github.com/FazalZamanKhan/gigbid, main branch, development checkpoint. Assignment requirements: AI-4016 Assignment II brief in the course Classroom item, checked 8 November 2026. Commands: <b>PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q</b>, <b>npm run build</b>, and <b>python -m evals.runners.retrieval_eval</b> with the synthetic fixture and provenance label.")]

doc = SimpleDocTemplate(str(OUTPUT), pagesize=(8.5 * inch, 11 * inch), leftMargin=0.7 * inch, rightMargin=0.7 * inch, topMargin=0.8 * inch, bottomMargin=0.7 * inch, title="GigBid Interim R&D Report", author="Fazal Zaman Khan")
doc.build(story, onFirstPage=page, onLaterPages=page)
print(OUTPUT)
