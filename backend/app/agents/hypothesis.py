"""Hypothesis agent: runs the planned detectors and turns raw signals into hypotheses."""

from ..models import Evidence, Hypothesis
from ..tools.data_sources import DataContext
from ..tools.red_flags import DETECTORS
from .state import InvestigationState, log


def make_hypothesis_node(ctx: DataContext):
    def hypothesis_node(state: InvestigationState) -> dict:
        evidence = dict(state.get("evidence", {}))
        hypotheses: list[Hypothesis] = []
        trace_state = dict(state)

        for name in state["plan"]["detectors"]:
            signals = DETECTORS[name](ctx)
            for sig in signals:
                ev_ids = []
                for ev in sig["evidence"]:
                    eid = f"E{len(evidence) + 1:03d}"
                    evidence[eid] = Evidence(id=eid, **ev)
                    ev_ids.append(eid)
                hypotheses.append(Hypothesis(
                    id=f"H{len(hypotheses) + 1:02d}", kind=sig["kind"], entities=sig["entities"],
                    statement=sig["statement"], score=sig["score"], evidence_ids=ev_ids, data=sig["data"],
                ))
            trace_state["trace"] = log(trace_state, "Hypothesis", "detect",
                                       f"{name}: {len(signals)} signal(s)")

        trace_state["trace"] = log(trace_state, "Hypothesis", "propose",
                                   f"Proposed {len(hypotheses)} hypotheses for scrutiny",
                                   {"ids": [h.id for h in hypotheses]})
        return {"hypotheses": hypotheses, "evidence": evidence, "trace": trace_state["trace"]}

    return hypothesis_node
