"""Reporter: groups supported red flags into networks and writes the explainable report."""

from collections import defaultdict

from ..llm import chat
from ..tools.data_sources import DataContext
from .state import InvestigationState, log

SYSTEM = (
    "You write concise briefings for public-procurement auditors. Use ONLY the facts given. "
    "Cite evidence ids in brackets like [E003]. Describe risk indicators, never accuse anyone of a crime. "
    "End with 1-2 concrete next steps for a human investigator."
)


def _networks(hypotheses) -> list[set[str]]:
    parent: dict[str, str] = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            x = parent[x]
        return x

    for h in hypotheses:
        companies = [e for e in h.entities if not e.startswith("SANCTION:")]
        for c in companies:
            find(c)
        for a, b in zip(companies, companies[1:]):
            parent[find(a)] = find(b)
    groups = defaultdict(set)
    for c in parent:
        groups[find(c)].add(c)
    return list(groups.values())


def make_reporter_node(ctx: DataContext):
    def reporter_node(state: InvestigationState) -> dict:
        hyps = state["hypotheses"]
        evidence = state["evidence"]
        supported = [h for h in hyps if h.status == "supported"]

        networks = []
        for members in _networks(supported):
            related = [h for h in supported if members & set(h.entities)]
            risk = 1.0
            for h in related:
                risk *= 1 - h.confidence
            risk = min(round(1 - risk, 2), 0.99)  # never claim certainty

            facts = "\n".join(
                f"- {h.id} [{h.kind}, confidence {h.confidence}]: {h.statement} "
                f"Evidence: " + "; ".join(f"[{e}] {evidence[e].claim}" for e in h.evidence_ids)
                for h in related
            )
            fallback = (f"Risk network of {len(members)} companies with {len(related)} corroborating red flags:\n"
                        + facts + "\nNext step: request bid documents and ownership filings for these companies.")
            narrative = chat(SYSTEM, f"Companies: {', '.join(ctx.company_name(m) for m in members)}\n{facts}",
                             fallback=fallback)
            networks.append({
                "companies": sorted(members),
                "company_names": [ctx.company_name(m) for m in sorted(members)],
                "risk_score": risk,
                "hypotheses": [h.id for h in related],
                "narrative": narrative,
            })
        networks.sort(key=lambda n: n["risk_score"], reverse=True)

        dismissed = [{"id": h.id, "kind": h.kind, "statement": h.statement, "status": h.status,
                      "why": h.skeptic_notes[-1] if h.skeptic_notes else ""}
                     for h in hyps if h.status in ("weakened", "rejected")]

        report = {
            "summary": {
                "hypotheses": len(hyps), "supported": len(supported), "dismissed": len(dismissed),
                "networks": len(networks), "iterations": state.get("iteration", 0),
                "data_source": ctx.source_name,
            },
            "networks": networks,
            "dismissed": dismissed,
            "disclaimer": "Risk indicators for human review — not findings of wrongdoing.",
        }
        return {"report": report,
                "trace": log(state, "Reporter", "report",
                             f"{len(networks)} risk network(s), {len(dismissed)} red flag(s) explained away")}

    return reporter_node
