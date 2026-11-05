"""Typed handoffs. These contracts remain stable across marketplace adapters."""

from enum import StrEnum
from pydantic import BaseModel, Field


class Evidence(BaseModel):
    id: str
    title: str
    text: str
    source: str
    skills: list[str] = Field(default_factory=list)


class JobSpec(BaseModel):
    id: str
    title: str
    description: str
    skills: list[str]
    budget_min: float = Field(ge=0)
    budget_max: float = Field(ge=0)
    connects_cost: int = Field(ge=0)
    client_rating: float = Field(ge=0, le=5)
    screening_questions: list[str] = Field(default_factory=list)


class RiskReport(BaseModel):
    score: float = Field(ge=0, le=1)
    flags: list[str] = Field(default_factory=list)
    injected_instruction: bool = False


class FitReport(BaseModel):
    score: float = Field(ge=0, le=1)
    evidence: list[Evidence] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)


class Decision(StrEnum):
    BID = "bid"
    SKIP = "skip"
    WATCH = "watch"


class BidDecision(BaseModel):
    action: Decision
    reason: str


class PriceQuote(BaseModel):
    amount: float = Field(ge=0)
    currency: str = "USD"
    rationale: str


class Claim(BaseModel):
    text: str
    evidence_ids: list[str]
    supported: bool = False


class ProposalDraft(BaseModel):
    text: str
    claims: list[Claim]


class ComplianceVerdict(BaseModel):
    allowed: bool
    reasons: list[str] = Field(default_factory=list)
