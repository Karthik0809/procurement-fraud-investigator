"""Evidence-gathering checks the Investigator runs when the Skeptic asks a question.

Each check answers one specific "is there an innocent explanation?" question and
returns (result, claim) — result goes into hypothesis.checks, claim becomes Evidence.
"""

from __future__ import annotations

from typing import Callable

from ..models import Hypothesis
from .data_sources import DataContext
from .entity_resolution import normalize_address

CheckFn = Callable[[Hypothesis, DataContext, list[Hypothesis]], tuple[dict, str, str]]


def address_density(h: Hypothesis, ctx: DataContext, _all) -> tuple[dict, str, str]:
    addr = h.data["address"]
    n = int((ctx.companies.address.map(normalize_address) == addr).sum())
    return ({"companies_at_address": n},
            "companies_registry",
            f"{n} registered companies use the address '{addr}'")


def officer_role(h: Hypothesis, ctx: DataContext, _all) -> tuple[dict, str, str]:
    rows = ctx.officers[ctx.officers.officer_id.isin(h.data["officer_ids"])]
    roles = rows.role.tolist()
    nominee = any("nominee" in r.lower() for r in roles)
    return ({"roles": roles, "nominee": nominee},
            "officer_registry",
            f"Officer roles: {', '.join(roles)}" + (" (nominee service)" if nominee else ""))


def market_depth(h: Hypothesis, ctx: DataContext, _all) -> tuple[dict, str, str]:
    categories = ctx.tenders[ctx.tenders.tender_id.isin(h.data["tenders"])].category.unique().tolist()
    cat_tenders = ctx.tenders[ctx.tenders.category.isin(categories)].tender_id
    bidders = ctx.bids[ctx.bids.tender_id.isin(cat_tenders)].company_id.nunique()
    return ({"categories": categories, "distinct_bidders": int(bidders), "group_size": len(h.entities)},
            "bids",
            f"{bidders} distinct companies bid in {', '.join(categories)} (group size {len(h.entities)})")


def sample_size(h: Hypothesis, ctx: DataContext, _all) -> tuple[dict, str, str]:
    n = len(h.data["tenders"])
    return {"tenders": n}, "bids", f"Pattern observed across {n} tenders"


def identity_verification(h: Hypothesis, ctx: DataContext, _all) -> tuple[dict, str, str]:
    officer = ctx.officers[ctx.officers.officer_id == h.data["officer_id"]].iloc[0]
    sanction = ctx.sanctions[ctx.sanctions.name == h.data["sanction_name"]].iloc[0]
    consistent = officer["nationality"] == sanction["country"]
    return ({"officer_nationality": officer["nationality"], "sanction_country": sanction["country"],
             "consistent": bool(consistent)},
            "sanctions",
            f"Officer nationality {officer['nationality']} vs sanctions entry country {sanction['country']}: "
            + ("consistent" if consistent else "MISMATCH"))


def corroboration(h: Hypothesis, ctx: DataContext, all_h: list[Hypothesis]) -> tuple[dict, str, str]:
    companies = {e for e in h.entities if not e.startswith("SANCTION:")}
    others = [o.id for o in all_h
              if o.id != h.id and o.status != "rejected" and companies & set(o.entities)]
    return ({"corroborating": others},
            "cross-hypothesis",
            f"{len(others)} other open red flag(s) involve the same companies: {', '.join(others) or 'none'}")


CHECKS: dict[str, CheckFn] = {
    "address_density": address_density,
    "officer_role": officer_role,
    "market_depth": market_depth,
    "sample_size": sample_size,
    "identity_verification": identity_verification,
    "corroboration": corroboration,
}
