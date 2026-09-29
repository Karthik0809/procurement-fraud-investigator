"""The agent graph:

    Planner -> Hypothesis -> Skeptic <-> Investigator -> Reporter
                                 (loops until every question is answered
                                  or the iteration budget runs out)
"""

import uuid

from langgraph.graph import END, StateGraph

from ..models import InvestigationRequest, InvestigationResult
from ..tools.data_sources import DataContext
from .hypothesis import make_hypothesis_node
from .investigator import make_investigator_node
from .planner import planner_node
from .reporter import make_reporter_node
from .skeptic import route_after_skeptic, skeptic_node
from .state import InvestigationState


def build_graph(ctx: DataContext):
    g = StateGraph(InvestigationState)
    g.add_node("planner", planner_node)
    g.add_node("hypothesis", make_hypothesis_node(ctx))
    g.add_node("skeptic", skeptic_node)
    g.add_node("investigator", make_investigator_node(ctx))
    g.add_node("reporter", make_reporter_node(ctx))

    g.set_entry_point("planner")
    g.add_edge("planner", "hypothesis")
    g.add_edge("hypothesis", "skeptic")
    g.add_conditional_edges("skeptic", route_after_skeptic, {"investigator": "investigator", "reporter": "reporter"})
    g.add_edge("investigator", "skeptic")
    g.add_edge("reporter", END)
    return g.compile()


def build_ui_graph(result_state: InvestigationState, ctx: DataContext) -> dict:
    """Nodes/links for the investigation graph in the frontend."""
    nodes, links = {}, []
    for h in result_state["hypotheses"]:
        for e in h.entities:
            if e not in nodes:
                is_sanction = e.startswith("SANCTION:")
                nodes[e] = {"id": e, "label": e.split(":", 1)[1] if is_sanction else ctx.company_name(e),
                            "type": "sanction" if is_sanction else "company"}
        ents = h.entities
        for i in range(len(ents)):
            for j in range(i + 1, len(ents)):
                links.append({"source": ents[i], "target": ents[j], "kind": h.kind,
                              "status": h.status, "hypothesis": h.id})
    return {"nodes": list(nodes.values()), "links": links}


def run_investigation(req: InvestigationRequest, ctx: DataContext | None = None) -> InvestigationResult:
    ctx = (ctx or DataContext.load()).scoped(req.scope)
    final = build_graph(ctx).invoke(
        {"request": req.model_dump(), "trace": [], "evidence": {}},
        {"recursion_limit": 50},
    )
    return InvestigationResult(
        id=uuid.uuid4().hex[:8], request=req, hypotheses=final["hypotheses"], evidence=final["evidence"],
        trace=final["trace"], report=final["report"], graph=build_ui_graph(final, ctx),
    )
