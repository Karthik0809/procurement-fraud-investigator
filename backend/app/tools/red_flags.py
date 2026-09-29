"""Deterministic red-flag detectors.

Each detector returns a list of *signals*: raw suspicions with the evidence
that triggered them. The Hypothesis agent turns signals into hypotheses; the
Skeptic then tries to explain them away. Detectors stay deterministic on
purpose so every claim in the final report can be traced to real rows.
"""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations
from statistics import median

from .data_sources import DataContext
from .entity_resolution import normalize_address, person_match

Signal = dict  # {kind, entities, statement, score, evidence: [{source, claim, data}], data}


def _bidders_by_tender(ctx: DataContext) -> dict[str, set[str]]:
    return ctx.bids.groupby("tender_id").company_id.apply(set).to_dict()


def _winner_by_tender(ctx: DataContext) -> dict[str, str]:
    w = ctx.bids[ctx.bids.won == 1]
    return dict(zip(w.tender_id, w.company_id))


def _co_bidding_pairs(ctx: DataContext) -> dict[tuple[str, str], list[str]]:
    pairs: dict[tuple[str, str], list[str]] = defaultdict(list)
    for tender, bidders in _bidders_by_tender(ctx).items():
        for a, b in combinations(sorted(bidders), 2):
            pairs[(a, b)].append(tender)
    return pairs


def find_rings(ctx: DataContext, min_co_bids: int = 3) -> list[dict]:
    """Groups of companies that repeatedly bid against each other and take turns winning."""
    winners = _winner_by_tender(ctx)
    bidders = _bidders_by_tender(ctx)

    # link two companies if they co-bid often and each has won at least once against the other
    parent: dict[str, str] = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for (a, b), tenders in _co_bidding_pairs(ctx).items():
        if len(tenders) < min_co_bids:
            continue
        if any(winners.get(t) == a for t in tenders) and any(winners.get(t) == b for t in tenders):
            parent[find(a)] = find(b)

    groups: dict[str, set[str]] = defaultdict(set)
    for c in list(parent):
        groups[find(c)].add(c)

    rings = []
    for members in groups.values():
        if len(members) < 2:
            continue
        tenders = sorted(t for t, bs in bidders.items() if len(bs & members) >= 2)
        wins = {m: sum(winners.get(t) == m for t in tenders) for m in members}
        ring_win_share = sum(wins.values()) / len(tenders)
        rings.append({"members": sorted(members), "tenders": tenders, "wins": wins, "win_share": ring_win_share})
    return rings


def detect_bid_rotation(ctx: DataContext) -> list[Signal]:
    signals = []
    for ring in find_rings(ctx):
        if ring["win_share"] < 0.8:
            continue
        n = len(ring["tenders"])
        spread = max(ring["wins"].values()) - min(ring["wins"].values())
        evenness = 1 - spread / n
        names = ", ".join(ctx.company_name(m) for m in ring["members"])
        signals.append({
            "kind": "bid_rotation",
            "entities": ring["members"],
            "statement": f"{names} bid against each other on {n} tenders and took turns winning "
                         f"({ring['win_share']:.0%} won by the group).",
            "score": round(0.5 * ring["win_share"] + 0.5 * evenness, 2),
            "evidence": [{
                "source": "bids",
                "claim": f"Win counts within the group: "
                         + ", ".join(f"{ctx.company_name(m)}={w}" for m, w in ring["wins"].items()),
                "data": ring,
            }],
            "data": {"tenders": ring["tenders"]},
        })
    return signals


def detect_cover_bidding(ctx: DataContext, max_median_gap: float = 0.05, max_gap: float = 0.08) -> list[Signal]:
    """Losing bids from the same group sit suspiciously close above the winner — every time."""
    signals = []
    bids = ctx.bids
    for ring in find_rings(ctx):
        members = set(ring["members"])
        gaps = []
        for t in ring["tenders"]:
            tb = bids[(bids.tender_id == t) & bids.company_id.isin(members)]
            win = tb[tb.won == 1]
            if win.empty:
                continue
            win_amt = win.amount.iloc[0]
            gaps += [(amt - win_amt) / win_amt for amt in tb[tb.won == 0].amount]
        if not gaps:
            continue
        med, mx = median(gaps), max(gaps)
        if med <= max_median_gap and mx <= max_gap:
            signals.append({
                "kind": "cover_bidding",
                "entities": ring["members"],
                "statement": f"Losing bids from this group are consistently just {med:.1%} above the winner "
                             f"(max {mx:.1%}) — a classic cover-bid pattern.",
                "score": round(1 - 0.5 * med / max_median_gap, 2),
                "evidence": [{
                    "source": "bids",
                    "claim": f"{len(gaps)} losing bids, median gap {med:.1%}, max gap {mx:.1%}",
                    "data": {"gaps": [round(g, 4) for g in gaps], "tenders": ring["tenders"]},
                }],
                "data": {"tenders": ring["tenders"], "median_gap": med},
            })
    return signals


def detect_shared_officers(ctx: DataContext, threshold: float = 0.9) -> list[Signal]:
    signals = []
    officers = ctx.officers
    for (a, b), tenders in _co_bidding_pairs(ctx).items():
        oa, ob = officers[officers.company_id == a], officers[officers.company_id == b]
        for _, ra in oa.iterrows():
            for _, rb in ob.iterrows():
                m = person_match(ra["name"], rb["name"])
                if m < threshold:
                    continue
                signals.append({
                    "kind": "shared_officer",
                    "entities": [a, b],
                    "statement": f"{ctx.company_name(a)} and {ctx.company_name(b)} competed on {len(tenders)} "
                                 f"tender(s) but share an officer: {ra['name']} / {rb['name']}.",
                    "score": round(0.6 + 0.4 * m, 2),
                    "evidence": [{
                        "source": "officer_registry",
                        "claim": f"{ra['name']} ({ra['role']}) at {ctx.company_name(a)}; "
                                 f"{rb['name']} ({rb['role']}) at {ctx.company_name(b)} — name match {m:.2f}",
                        "data": {"officers": [ra.to_dict(), rb.to_dict()], "co_bid_tenders": tenders},
                    }],
                    "data": {"officer_ids": [ra["officer_id"], rb["officer_id"]], "co_bid_tenders": tenders},
                })
    return signals


def detect_shared_address(ctx: DataContext) -> list[Signal]:
    co_bidders: set[str] = set()
    pairs = _co_bidding_pairs(ctx)
    for a, b in pairs:
        co_bidders |= {a, b}
    by_addr: dict[str, list[str]] = defaultdict(list)
    for _, r in ctx.companies[ctx.companies.company_id.isin(co_bidders)].iterrows():
        by_addr[normalize_address(r["address"])].append(r["company_id"])

    signals = []
    for addr, companies in by_addr.items():
        # only flag companies at the same address that actually bid against each other
        linked = sorted({c for a, b in pairs for c in (a, b) if a in companies and b in companies})
        if len(linked) < 2:
            continue
        signals.append({
            "kind": "shared_address",
            "entities": linked,
            "statement": f"{', '.join(ctx.company_name(c) for c in linked)} bid against each other "
                         f"but are registered at the same address.",
            "score": 0.6,
            "evidence": [{
                "source": "companies_registry",
                "claim": f"Normalized address '{addr}' shared by {len(linked)} competing bidders",
                "data": {"address": addr, "companies": linked},
            }],
            "data": {"address": addr},
        })
    return signals


def detect_sanctions_matches(ctx: DataContext, threshold: float = 0.85) -> list[Signal]:
    signals = []
    for _, o in ctx.officers.iterrows():
        for _, s in ctx.sanctions.iterrows():
            m = person_match(o["name"], s["name"])
            if m < threshold:
                continue
            signals.append({
                "kind": "sanctions_match",
                "entities": [o["company_id"], f"SANCTION:{s['name']}"],
                "statement": f"Officer {o['name']} of {ctx.company_name(o['company_id'])} closely matches "
                             f"sanctioned person {s['name']} ({s['list']}).",
                "score": round(m, 2),
                "evidence": [{
                    "source": "sanctions",
                    "claim": f"'{o['name']}' vs '{s['name']}' name similarity {m:.2f}",
                    "data": {"officer": o.to_dict(), "sanction": s.to_dict(), "match": m},
                }],
                "data": {"officer_id": o["officer_id"], "sanction_name": s["name"], "match": m},
            })
    return signals


def detect_single_bidder(ctx: DataContext, min_tenders: int = 2) -> list[Signal]:
    counts = ctx.bids.groupby("tender_id").company_id.count()
    single = counts[counts == 1].index
    wins = ctx.bids[ctx.bids.tender_id.isin(single)].groupby("company_id").tender_id.apply(list)
    signals = []
    for company, tenders in wins.items():
        if len(tenders) < min_tenders:
            continue
        signals.append({
            "kind": "single_bidder",
            "entities": [company],
            "statement": f"{ctx.company_name(company)} won {len(tenders)} tenders where it was the only bidder.",
            "score": min(1.0, 0.3 + 0.15 * len(tenders)),
            "evidence": [{
                "source": "bids",
                "claim": f"Sole bidder on {', '.join(tenders)}",
                "data": {"tenders": tenders},
            }],
            "data": {"tenders": tenders},
        })
    return signals


DETECTORS = {
    "bid_rotation": detect_bid_rotation,
    "cover_bidding": detect_cover_bidding,
    "shared_officer": detect_shared_officers,
    "shared_address": detect_shared_address,
    "sanctions_match": detect_sanctions_matches,
    "single_bidder": detect_single_bidder,
}
