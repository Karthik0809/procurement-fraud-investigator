from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

HypothesisStatus = Literal["proposed", "supported", "weakened", "rejected"]


class Evidence(BaseModel):
    """A single verifiable fact, always tied to the source it came from."""

    id: str
    source: str  # e.g. "bids", "companies_registry", "sanctions"
    claim: str  # human-readable fact
    data: dict = Field(default_factory=dict)


class Hypothesis(BaseModel):
    """A red flag the system believes may indicate fraud, plus its audit trail."""

    id: str
    kind: str  # bid_rotation | cover_bidding | shared_officer | shared_address | sanctions_match | single_bidder
    entities: list[str]  # company ids (or SANCTION:<name>)
    statement: str
    score: float  # detector's raw strength, 0..1
    evidence_ids: list[str] = Field(default_factory=list)
    status: HypothesisStatus = "proposed"
    confidence: float = 0.0
    open_questions: list[str] = Field(default_factory=list)  # checks the Skeptic wants answered
    checks: dict[str, dict] = Field(default_factory=dict)  # check name -> result from Investigator
    skeptic_notes: list[str] = Field(default_factory=list)
    data: dict = Field(default_factory=dict)


class TraceEvent(BaseModel):
    step: int
    iteration: int
    agent: str
    action: str
    detail: str
    data: dict = Field(default_factory=dict)


class InvestigationRequest(BaseModel):
    scope: str = "all"  # agency name, or "all"
    question: str | None = None
    max_iterations: int = Field(default=3, ge=1, le=6)


class InvestigationResult(BaseModel):
    id: str
    request: InvestigationRequest
    hypotheses: list[Hypothesis]
    evidence: dict[str, Evidence]
    trace: list[TraceEvent]
    report: dict
    graph: dict
