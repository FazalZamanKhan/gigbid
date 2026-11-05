"""Conservative citation check for the deterministic demo proposal."""

from agent.handoffs import Evidence, ProposalDraft


def verify_claims(draft: ProposalDraft, evidence: list[Evidence]) -> ProposalDraft:
    by_id = {item.id: item for item in evidence}
    checked = []
    for claim in draft.claims:
        support = bool(claim.evidence_ids) and all(
            evidence_id in by_id and by_id[evidence_id].title in claim.text
            for evidence_id in claim.evidence_ids
        )
        checked.append(claim.model_copy(update={"supported": support}))
    return draft.model_copy(update={"claims": checked})
