"""Planner: decides which red-flag detectors to run for this investigation."""

from ..llm import chat, llm_enabled
from ..tools.red_flags import DETECTORS
from .state import InvestigationState, log

SYSTEM = (
    "You plan public-procurement fraud investigations. Given an investigator's question, "
    "choose which detectors to run. Reply with ONLY a comma-separated list chosen from: "
    + ", ".join(DETECTORS)
)


def planner_node(state: InvestigationState) -> dict:
    req = state["request"]
    question = req.get("question")
    detectors = list(DETECTORS)
    rationale = "No specific question — running the full detector suite."

    if question and llm_enabled():
        reply = chat(SYSTEM, question, fallback=",".join(DETECTORS), max_tokens=100)
        chosen = [d for d in DETECTORS if d in reply]
        if chosen:
            detectors, rationale = chosen, f"LLM planner selected detectors for: '{question}'"

    plan = {"scope": req.get("scope", "all"), "detectors": detectors}
    return {
        "plan": plan,
        "iteration": 0,
        "trace": log(state, "Planner", "plan", rationale, plan),
    }
