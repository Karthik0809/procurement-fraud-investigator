"""Data access layer.

Every agent reads data through a `DataSource`, so swapping the local CSV demo
data for Zetaris-federated sources is a one-line config change
(DATA_BACKEND=zetaris) rather than a rewrite.

Logical tables the agents expect:
  companies(company_id, name, address, city, registered_date)
  officers(officer_id, name, company_id, role, nationality)
  tenders(tender_id, agency, category, title, award_date, estimated_value)
  bids(tender_id, company_id, amount, won)
  sanctions(name, list, country, reason)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import pandas as pd

from ..config import settings

TABLES = ("companies", "officers", "tenders", "bids", "sanctions")


class DataSource(Protocol):
    name: str

    def table(self, name: str) -> pd.DataFrame: ...


class LocalCSVSource:
    name = "local-csv"

    def __init__(self, directory: Path):
        self.directory = directory

    def table(self, name: str) -> pd.DataFrame:
        return pd.read_csv(self.directory / f"{name}.csv", dtype=str, keep_default_na=False)


class ZetarisSource:
    """Federated access to the source systems through Zetaris.

    TODO(day 1): implement using the connection method from the Zetaris
    resources on HackOS (workshop 7 Oct). The idea: each logical table below
    maps to a federated query over the *original* systems (contract registry,
    company registry, sanctions list) — no copying data into one database.
    Keep the returned column names identical to LocalCSVSource.
    """

    name = "zetaris"

    # logical table -> federated SQL (fill in once the sources are registered in Zetaris)
    QUERIES: dict[str, str] = {
        "companies": "SELECT ... FROM <company_registry>",
        "officers": "SELECT ... FROM <officer_registry>",
        "tenders": "SELECT ... FROM <contract_awards>",
        "bids": "SELECT ... FROM <bid_records>",
        "sanctions": "SELECT ... FROM <sanctions_list>",
    }

    def __init__(self, url: str, user: str, password: str):
        self.url, self.user, self.password = url, user, password

    def table(self, name: str) -> pd.DataFrame:
        raise NotImplementedError("Wire up Zetaris here — see docstring and ROADMAP.md")


def get_source() -> DataSource:
    if settings.data_backend == "zetaris" and not settings.sample_mode:
        return ZetarisSource(settings.zetaris_url, settings.zetaris_user, settings.zetaris_password)
    return LocalCSVSource(settings.data_path)


@dataclass
class DataContext:
    """All tables loaded once per investigation, with numeric columns typed."""

    source_name: str
    companies: pd.DataFrame
    officers: pd.DataFrame
    tenders: pd.DataFrame
    bids: pd.DataFrame
    sanctions: pd.DataFrame

    @classmethod
    def load(cls, source: DataSource | None = None) -> "DataContext":
        source = source or get_source()
        t = {name: source.table(name) for name in TABLES}
        t["bids"]["amount"] = t["bids"]["amount"].astype(float)
        t["bids"]["won"] = t["bids"]["won"].astype(int)
        return cls(source_name=source.name, **t)

    def company_name(self, company_id: str) -> str:
        row = self.companies[self.companies.company_id == company_id]
        return row.name.iloc[0] if not row.empty else company_id

    def scoped(self, agency: str) -> "DataContext":
        """Restrict tenders/bids to one agency (companies, officers, sanctions stay global)."""
        if agency == "all":
            return self
        tenders = self.tenders[self.tenders.agency.str.lower() == agency.lower()]
        bids = self.bids[self.bids.tender_id.isin(tenders.tender_id)]
        return DataContext(self.source_name, self.companies, self.officers, tenders, bids, self.sanctions)
