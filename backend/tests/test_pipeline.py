"""End-to-end checks against the synthetic sample data (planted ring + decoys)."""

from app.agents.workflow import run_investigation
from app.models import InvestigationRequest
from app.tools.data_sources import DataContext
from app.tools.red_flags import detect_cover_bidding, detect_sanctions_matches, find_rings

RING = ["C001", "C002", "C003"]


def ctx():
    return DataContext.load()


def test_ring_detected():
    rings = [r["members"] for r in find_rings(ctx())]
    assert RING in rings


def test_cover_bidding_only_on_colluding_groups():
    groups = [s["entities"] for s in detect_cover_bidding(ctx())]
    assert RING in groups
    assert ["C009", "C010", "C011"] not in groups  # genuinely competitive bids


def test_sanctions_fuzzy_match():
    assert any("C008" in s["entities"] for s in detect_sanctions_matches(ctx()))


def test_full_investigation():
    result = run_investigation(InvestigationRequest())
    by_kind = {}
    for h in result.hypotheses:
        by_kind.setdefault(h.kind, []).append(h)

    # the planted ring survives the Skeptic
    ring_network = result.report["networks"][0]
    assert set(RING) <= set(ring_network["companies"])

    # decoys are explained away, not reported
    dover_address = next(h for h in by_kind["shared_address"] if "C004" in h.entities)
    assert dover_address.status == "weakened"
    nominee = next(h for h in by_kind["shared_officer"] if "C005" in h.entities)
    assert nominee.status == "weakened"

    # sanctions hit needed a follow-up loop (identity check -> corroboration)
    sanction = by_kind["sanctions_match"][0]
    assert sanction.status == "supported" and "corroboration" in sanction.checks

    # every reported hypothesis cites evidence
    for h in result.hypotheses:
        assert h.evidence_ids and all(e in result.evidence for e in h.evidence_ids)
    assert result.report["summary"]["iterations"] >= 3
