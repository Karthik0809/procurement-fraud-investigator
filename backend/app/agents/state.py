from __future__ import annotations

from typing import TypedDict

from ..models import Evidence, Hypothesis, TraceEvent


class InvestigationState(TypedDict, total=False):
    request: dict
    plan: dict
    hypotheses: list[Hypothesis]
    evidence: dict[str, Evidence]
    trace: list[TraceEvent]
    iteration: int
    report: dict


def log(state: InvestigationState, agent: str, action: str, detail: str, data: dict | None = None) -> list[TraceEvent]:
    """Append a trace event and return the new trace list (nodes return it as a state update)."""
    trace = list(state.get("trace", []))
    trace.append(TraceEvent(step=len(trace) + 1, iteration=state.get("iteration", 0),
                            agent=agent, action=action, detail=detail, data=data or {}))
    return trace
