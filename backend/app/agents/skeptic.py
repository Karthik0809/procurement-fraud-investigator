"""Skeptic: tries to explain every red flag away before it can reach the report.

For each proposed hypothesis the Skeptic either
  * asks the Investigator for the evidence it needs to rule out an innocent explanation, or
  * judges the hypothesis (supported / weakened / rejected) once that evidence is in,
    possibly raising a follow-up question — which sends the loop round again.
"""

from ..models import Hypothesis
from .state import InvestigationState, log

# evidence the Skeptic insists on before judging each kind of red flag
REQUIRED_CHECKS = {
    "bid_rotation": ["market_depth", "sample_size"],
    "cover_bidding": ["market_depth"],
    "shared_officer": ["officer_role"],
    "shared_address": ["address_density"],
    "sanctions_match": ["identity_verification"],
    "single_bidder": ["corroboration"],
}


def judge(h: Hypothesis) -> tuple[str, float, str, list[str]]:
    """Return (status, confidence, note, follow_up_checks)."""
    c = h.checks
    if h.kind in ("bid_rotation", "cover_bidding"):
        depth, size = c["market_depth"]["distinct_bidders"], c["market_depth"]["group_size"]
        if h.kind == "bid_rotation" and c["sample_size"]["tenders"] < 4:
            return ("weakened", h.score * 0.4,
                    f"Only {c['sample_size']['tenders']} tenders — rotation could be coincidence.", [])
        if depth <= size + 1:
            return ("weakened", h.score * 0.4,
                    f"Thin market: only {depth} companies bid in this category, so the same firms "
                    "winning in turn may be natural.", [])
        return ("supported", h.score * 0.9,
                f"{depth} companies compete in this market, yet this group of {size} dominates — "
                "no innocent explanation found.", [])

    if h.kind == "shared_officer":
        if c["officer_role"]["nominee"]:
            return ("weakened", 0.2, "Shared officer is a nominee-director service that serves many "
                                     "unrelated firms — weak link on its own.", [])
        return ("supported", h.score * 0.85, "Same real person controls two 'competing' bidders.", [])

    if h.kind == "shared_address":
        n = c["address_density"]["companies_at_address"]
        if n >= 4:
            return ("weakened", 0.15, f"{n} companies use this address — likely a registered-agent or "
                                      "virtual office, not a real link.", [])
        return ("supported", 0.7, f"Only {n} companies at this address and they compete — "
                                  "strongly suggests common control.", [])

    if h.kind == "sanctions_match":
        if not c["identity_verification"]["consistent"]:
            return ("rejected", 0.05, "Name is similar but nationality does not match — different person.", [])
        if "corroboration" not in c:
            return ("proposed", h.score, "Identity is consistent. Before escalating, check whether this "
                                         "company shows other red flags.", ["corroboration"])
        others = c["corroboration"]["corroborating"]
        return ("supported", h.score * (1.0 if others else 0.8),
                "Identity consistent" + (f" and corroborated by {', '.join(others)}." if others else "."), [])

    if h.kind == "single_bidder":
        others = c["corroboration"]["corroborating"]
        if others:
            return ("supported", 0.7, f"Sole-bidder wins corroborated by {', '.join(others)}.", [])
        return ("weakened", 0.3, "Single-bid tenders are common in niche categories; no other red flags.", [])

    return ("weakened", 0.1, "No rule to evaluate this red flag.", [])


def skeptic_node(state: InvestigationState) -> dict:
    hypotheses = [h.model_copy(deep=True) for h in state["hypotheses"]]
    iteration = state.get("iteration", 0) + 1
    max_iter = state["request"].get("max_iterations", 3)
    trace_state = {**state, "iteration": iteration}

    for h in hypotheses:
        if h.status != "proposed":
            continue
        missing = [q for q in REQUIRED_CHECKS.get(h.kind, []) if q not in h.checks]
        if missing:
            h.open_questions = missing
            trace_state["trace"] = log(trace_state, "Skeptic", "challenge",
                                       f"{h.id} ({h.kind}): need {', '.join(missing)} before I accept this",
                                       {"hypothesis": h.id, "questions": missing})
            continue

        status, conf, note, follow_ups = judge(h)
        h.skeptic_notes.append(note)
        h.confidence = round(conf, 2)
        if follow_ups:
            h.open_questions = follow_ups
            trace_state["trace"] = log(trace_state, "Skeptic", "follow_up", f"{h.id}: {note}",
                                       {"hypothesis": h.id, "questions": follow_ups})
            continue
        h.status = status
        trace_state["trace"] = log(trace_state, "Skeptic", status, f"{h.id}: {note}",
                                   {"hypothesis": h.id, "confidence": h.confidence})

    # out of budget: anything still open is escalated to a human instead of guessed
    if iteration >= max_iter:
        for h in hypotheses:
            if h.open_questions:
                h.open_questions, h.status = [], "weakened"
                h.skeptic_notes.append("Unresolved within the iteration budget — escalate to a human auditor.")
                trace_state["trace"] = log(trace_state, "Skeptic", "escalate", f"{h.id}: out of iterations")

    return {"hypotheses": hypotheses, "iteration": iteration, "trace": trace_state["trace"]}


def route_after_skeptic(state: InvestigationState) -> str:
    return "investigator" if any(h.open_questions for h in state["hypotheses"]) else "reporter"
