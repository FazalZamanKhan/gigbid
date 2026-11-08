"""Synthetic client conversation graph with a human approval interrupt."""

from __future__ import annotations

from typing import Annotated, TypedDict
import operator

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt

from agent.handoffs import ConversationIntent, JobSpec, MessageDraft
from agent.marketplace_port import MarketplacePort
from agent.settings import load_config


class WorkspacePort:
    async def get_free_slots(self, day: str) -> list[str]: ...


class ConversationState(TypedDict, total=False):
    run_id: str
    job_id: str
    day: str
    incoming: str
    job: dict
    intent: str
    risk_flags: list[str]
    slots: list[str]
    draft: dict
    compliance: dict
    approval: dict
    marketplace_result: dict
    events: Annotated[list[str], operator.add]


def _check_reply(text: str, forbidden: list[str]) -> list[str]:
    folded = text.casefold()
    return [phrase for phrase in forbidden if phrase in folded]


def build_conversation_graph(marketplace: MarketplacePort, workspace: WorkspacePort, checkpointer=None):
    policy = load_config()["decision"]

    async def load_job(state: ConversationState) -> ConversationState:
        job = await marketplace.get_job(state["job_id"])
        return {"job": job.model_dump(), "events": ["Client Liaison loaded job context"]}

    def classify(state: ConversationState) -> ConversationState:
        text = state["incoming"].casefold()
        flags = [phrase for phrase in policy["risk_phrases"] + policy["injection_phrases"] if phrase in text]
        if flags:
            intent = ConversationIntent.SCAM
        elif any(term in text for term in ("interview", "meet", "call", "schedule")):
            intent = ConversationIntent.INTERVIEW
        elif any(term in text for term in ("rate", "price", "budget", "discount")):
            intent = ConversationIntent.NEGOTIATION
        else:
            intent = ConversationIntent.QUESTION
        return {"intent": intent.value, "risk_flags": flags, "events": [f"Client Liaison classified {intent.value}"]}

    def after_classify(state: ConversationState):
        if state["intent"] == ConversationIntent.SCAM:
            return END
        return "slots" if state["intent"] == ConversationIntent.INTERVIEW else "draft"

    async def slots(state: ConversationState) -> ConversationState:
        available = await workspace.get_free_slots(state["day"])
        return {"slots": available[:2], "events": ["Workspace MCP returned interview slots"]}

    def draft(state: ConversationState) -> ConversationState:
        job = JobSpec.model_validate(state["job"])
        intent = ConversationIntent(state["intent"])
        if intent == ConversationIntent.INTERVIEW and state.get("slots"):
            offered = " or ".join(state["slots"])
            text = f"Thanks for your interest in {job.title}. I can meet at {offered}. Please confirm which works for you."
        elif intent == ConversationIntent.INTERVIEW:
            text = f"Thanks for your interest in {job.title}. I will confirm a suitable interview time shortly."
        elif intent == ConversationIntent.NEGOTIATION:
            text = f"Thanks for discussing {job.title}. I can review the scope and rate with you before confirming terms."
        else:
            text = f"Thanks for your message about {job.title}. Could you share the specific deliverable or question you want me to address?"
        message = MessageDraft(text=text, intent=intent, slot_ids=state.get("slots", []))
        return {"draft": message.model_dump(mode="json"), "events": ["Client Liaison prepared synthetic reply"]}

    def compliance(state: ConversationState) -> ConversationState:
        violations = _check_reply(state["draft"]["text"], policy["forbidden_draft_phrases"])
        return {"compliance": {"allowed": not violations, "reasons": violations}, "events": ["Compliance checked reply"]}

    def after_compliance(state: ConversationState):
        return "approval" if state["compliance"]["allowed"] else END

    async def approval(state: ConversationState) -> ConversationState:
        preview = await marketplace.send_message(
            state["job_id"], state["draft"]["text"], f"{state['run_id']}:preview", dry_run=True,
        )
        response = interrupt({
            "incoming": state["incoming"], "intent": state["intent"],
            "risk_flags": state["risk_flags"], "slots": state.get("slots", []),
            "draft": state["draft"], "dry_run": preview,
        })
        if not isinstance(response, dict) or not response.get("approved"):
            reason = response.get("reason", "Rejected") if isinstance(response, dict) else "Rejected"
            return {"approval": {"approved": False, "reason": reason}, "events": ["Human rejected reply"]}
        edited = response.get("text") or state["draft"]["text"]
        violations = _check_reply(edited, policy["forbidden_draft_phrases"])
        if violations:
            return {"approval": {"approved": False, "reason": "Edited reply failed compliance: " + ", ".join(violations)}, "events": ["Edited reply blocked"]}
        return {"approval": {"approved": True, "text": edited}, "events": ["Human approved reply"]}

    def after_approval(state: ConversationState):
        return "record_message" if state["approval"]["approved"] else END

    async def record_message(state: ConversationState) -> ConversationState:
        result = await marketplace.send_message(
            state["job_id"], state["approval"]["text"], f"{state['run_id']}:approved-message", dry_run=False,
        )
        return {"marketplace_result": result, "events": ["Approved synthetic message recorded"]}

    graph = StateGraph(ConversationState)
    for name, node in (
        ("load_job", load_job), ("classify", classify), ("slots", slots),
        ("draft", draft), ("compliance", compliance), ("approval", approval),
        ("record_message", record_message),
    ):
        graph.add_node(name, node)
    graph.add_edge(START, "load_job")
    graph.add_edge("load_job", "classify")
    graph.add_conditional_edges("classify", after_classify)
    graph.add_edge("slots", "draft")
    graph.add_edge("draft", "compliance")
    graph.add_conditional_edges("compliance", after_compliance)
    graph.add_conditional_edges("approval", after_approval)
    graph.add_edge("record_message", END)
    return graph.compile(checkpointer=checkpointer or MemorySaver())
