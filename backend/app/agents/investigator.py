"""Investigator: answers the Skeptic's open questions by gathering new evidence."""

from ..models import Evidence
from ..tools.checks import CHECKS
from ..tools.data_sources import DataContext
from .state import InvestigationState, log


def make_investigator_node(ctx: DataContext):
    def investigator_node(state: InvestigationState) -> dict:
        hypotheses = [h.model_copy(deep=True) for h in state["hypotheses"]]
        evidence = dict(state["evidence"])
        trace_state = dict(state)
        answered = 0

        for h in hypotheses:
            for question in h.open_questions:
                result, source, claim = CHECKS[question](h, ctx, hypotheses)
                eid = f"E{len(evidence) + 1:03d}"
                evidence[eid] = Evidence(id=eid, source=source, claim=claim, data={"check": question, **result})
                h.evidence_ids.append(eid)
                h.checks[question] = result
                answered += 1
                trace_state["trace"] = log(trace_state, "Investigator", question,
                                           f"{h.id}: {claim}", {"hypothesis": h.id, "evidence": eid})
            h.open_questions = []

        if answered == 0:
            trace_state["trace"] = log(trace_state, "Investigator", "idle", "No open questions to investigate")
        return {"hypotheses": hypotheses, "evidence": evidence, "trace": trace_state["trace"]}

    return investigator_node
