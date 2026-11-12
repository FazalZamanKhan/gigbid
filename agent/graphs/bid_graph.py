"""Development bid graph with a real LangGraph human interrupt.

The deterministic analysis is a replaceable development slice. No GigSim
results, production durability, or AI quality are implied by this module.
"""

from __future__ import annotations

from typing import Annotated, TypedDict
import operator

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send, interrupt

from agent.handoffs import (
    BidDecision, Claim, ComplianceVerdict, Critique, Decision, Evidence, FitReport,
    JobSpec, PriceQuote, ProposalDraft, RiskReport,
)
from agent.marketplace_port import MarketplacePort
from agent.settings import load_config
from rag.mcp_client import search_evidence_mcp
from rag.verify import verify_claims


class BidState(TypedDict, total=False):
    job_id: str
    job: dict
    analysis: dict
    risk: dict
    fit: dict
    decision: dict
    price: dict
    draft: dict
    critique: dict
    compliance: dict
    approval: dict
    marketplace_result: dict
    events: Annotated[list[str], operator.add]


def build_bid_graph(marketplace: MarketplacePort, checkpointer=None):
    config = load_config()
    policy = config["decision"]
    max_revisions = config["budgets"]["max_critic_revisions"]

    async def scout(state: BidState) -> BidState:
        job = await marketplace.get_job(state["job_id"])
        return {"job": job.model_dump(), "events": ["Scout loaded job"]}

    def dispatch(state: BidState):
        return [Send("analyst", state), Send("risk_assessor", state), Send("fit_matcher", state)]

    def analyst(state: BidState) -> BidState:
        job = JobSpec.model_validate(state["job"])
        return {"analysis": {"requirements": job.skills, "title": job.title}, "events": ["Analyst extracted requirements"]}

    def risk_assessor(state: BidState) -> BidState:
        job = JobSpec.model_validate(state["job"])
        text = f"{job.title} {job.description}".casefold()
        flags = [phrase for phrase in policy["risk_phrases"] if phrase in text]
        score = min(1.0, policy["risk_weight_per_flag"] * len(flags) + (policy["low_rating_risk_weight"] if job.client_rating < policy["minimum_client_rating"] else 0))
        risk = RiskReport(score=score, flags=flags, injected_instruction=any(phrase in text for phrase in policy["injection_phrases"]))
        return {"risk": risk.model_dump(), "events": ["Risk assessor checked post"]}

    async def fit_matcher(state: BidState) -> BidState:
        job = JobSpec.model_validate(state["job"])
        evidence = await search_evidence_mcp(job)
        covered = {s.casefold() for item in evidence for s in item.skills}
        missing = [skill for skill in job.skills if skill.casefold() not in covered]
        score = len(job.skills) and (len(job.skills) - len(missing)) / len(job.skills) or 0.0
        fit = FitReport(score=score, evidence=evidence, missing_skills=missing)
        return {"fit": fit.model_dump(), "events": ["Fit matcher found cited evidence"]}

    def decide(state: BidState) -> BidState:
        risk = RiskReport.model_validate(state["risk"])
        fit = FitReport.model_validate(state["fit"])
        job = JobSpec.model_validate(state["job"])
        if risk.injected_instruction:
            decision = BidDecision(action=Decision.SKIP, reason="Job post contains an instruction aimed at the assistant")
        elif risk.score > policy["maximum_risk_score"]:
            decision = BidDecision(action=Decision.SKIP, reason="Risk flags: " + ", ".join(risk.flags))
        elif fit.score < policy["minimum_fit_score"]:
            decision = BidDecision(action=Decision.SKIP, reason="Portfolio evidence does not cover enough requirements")
        elif job.budget_max == 0:
            decision = BidDecision(action=Decision.WATCH, reason="No stated budget")
        else:
            decision = BidDecision(action=Decision.BID, reason="Evidence covers requirements and no high-risk flag was found")
        return {"decision": decision.model_dump(mode="json"), "events": [f"Decision: {decision.action}"]}

    def after_decide(state: BidState):
        return "price" if state["decision"]["action"] == "bid" else END

    def price(state: BidState) -> BidState:
        job = JobSpec.model_validate(state["job"])
        amount = round((job.budget_min + job.budget_max) / 2, 2)
        return {"price": PriceQuote(amount=amount, rationale="Midpoint of the stated budget; no market pricing data yet").model_dump(), "events": ["Price quote prepared"]}

    def writer(state: BidState) -> BidState:
        job = JobSpec.model_validate(state["job"])
        fit = FitReport.model_validate(state["fit"])
        cited = fit.evidence[0]
        claim_text = f"My portfolio includes {cited.title}."
        if state.get("critique", {}).get("revision", 0):
            text = f"For your {job.title} project, I can apply the work shown in {cited.title}. {claim_text} I would confirm the scope with you before starting."
        else:
            text = f"Hello, I read your request for {job.title}. {claim_text} I would confirm the scope with you before starting."
        draft = ProposalDraft(text=text, claims=[Claim(text=claim_text, evidence_ids=[cited.id])])
        revision = state.get("critique", {}).get("revision", 0)
        return {"draft": verify_claims(draft, fit.evidence).model_dump(), "events": [f"Writer prepared cited demo draft, revision {revision}"]}

    def critic(state: BidState) -> BidState:
        draft = ProposalDraft.model_validate(state["draft"])
        issues = []
        if draft.text.startswith("Hello, I read your request"):
            issues.append("Opening repeats the job title without a specific plan")
        if any(not claim.supported for claim in draft.claims):
            issues.append("A proposal claim lacks evidence")
        revision = state.get("critique", {}).get("revision", 0)
        critique = Critique(accepted=not issues, issues=issues, revision=revision + (1 if issues else 0))
        return {"critique": critique.model_dump(), "events": ["Critic accepted draft" if not issues else f"Critic requested revision {critique.revision}: {'; '.join(issues)}"]}

    def after_critic(state: BidState):
        critique = Critique.model_validate(state["critique"])
        if critique.accepted:
            return "compliance"
        return "writer" if critique.revision <= max_revisions else END

    def compliance(state: BidState) -> BidState:
        draft = ProposalDraft.model_validate(state["draft"])
        reasons = []
        if any(not claim.supported for claim in draft.claims):
            reasons.append("Unsupported claim")
        if any(phrase in draft.text.casefold() for phrase in policy["forbidden_draft_phrases"]):
            reasons.append("Off-platform contact or guarantee")
        return {"compliance": ComplianceVerdict(allowed=not reasons, reasons=reasons).model_dump(), "events": ["Compliance checked draft"]}

    def after_compliance(state: BidState):
        return "approval" if state["compliance"]["allowed"] else END

    async def approval(state: BidState) -> BidState:
        preview = await marketplace.create_proposal_draft(
            state["job_id"], state["draft"]["text"],
            f"{state['job_id']}:preview", dry_run=True,
        )
        response = interrupt({
            "job": state["job"], "risk": state["risk"], "fit": state["fit"],
            "price": state["price"], "draft": state["draft"], "dry_run": preview,
        })
        if not isinstance(response, dict) or not response.get("approved"):
            return {"approval": {"approved": False, "reason": response.get("reason", "Rejected") if isinstance(response, dict) else "Rejected"}, "events": ["Human rejected draft"]}
        edited = response.get("text", state["draft"]["text"])
        if edited != state["draft"]["text"]:
            return {"approval": {"approved": False, "reason": "Edited draft needs claim and compliance recheck before it can be sent"}, "events": ["Edited draft held for review"]}
        return {"approval": {"approved": True}, "events": ["Human approved draft"]}

    def after_approval(state: BidState):
        return "create_draft" if state["approval"]["approved"] else END

    async def create_draft(state: BidState) -> BidState:
        result = await marketplace.create_proposal_draft(
            state["job_id"], state["draft"]["text"],
            f"{state['job_id']}:approved-draft", dry_run=False,
        )
        return {"marketplace_result": result, "events": ["Approved marketplace draft created"]}

    graph = StateGraph(BidState)
    for name, node in (
        ("scout", scout), ("analyst", analyst), ("risk_assessor", risk_assessor),
        ("fit_matcher", fit_matcher), ("decide", decide), ("price", price),
        ("writer", writer), ("critic", critic), ("compliance", compliance), ("approval", approval),
        ("create_draft", create_draft),
    ):
        graph.add_node(name, node)
    graph.add_edge(START, "scout")
    graph.add_conditional_edges("scout", dispatch)
    graph.add_edge(["analyst", "risk_assessor", "fit_matcher"], "decide")
    graph.add_conditional_edges("decide", after_decide)
    graph.add_edge("price", "writer")
    graph.add_edge("writer", "critic")
    graph.add_conditional_edges("critic", after_critic)
    graph.add_conditional_edges("compliance", after_compliance)
    graph.add_conditional_edges("approval", after_approval)
    graph.add_edge("create_draft", END)
    return graph.compile(checkpointer=checkpointer or MemorySaver())
