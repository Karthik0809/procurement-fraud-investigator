"""Fuzzy matching for names and addresses across sources that spell things differently."""

import re
from difflib import SequenceMatcher

_COMPANY_SUFFIXES = r"\b(ltd|limited|llc|inc|incorporated|co|corp|corporation|plc|gmbh)\b"
_ADDRESS_ABBREV = {
    "street": "st", "avenue": "ave", "road": "rd", "lane": "ln", "suite": "ste",
    "drive": "dr", "boulevard": "blvd", "way": "way",
}
_MIDDLE_INITIAL = re.compile(r"\b[a-z]\b")


def normalize_company(name: str) -> str:
    s = re.sub(r"[^\w\s]", " ", name.lower())
    s = re.sub(_COMPANY_SUFFIXES, " ", s)
    return " ".join(s.split())


def normalize_person(name: str) -> str:
    s = re.sub(r"[^\w\s]", " ", name.lower())
    s = _MIDDLE_INITIAL.sub(" ", s)  # "James A. Morrow" -> "james morrow"
    return " ".join(s.split())


def normalize_address(address: str) -> str:
    s = re.sub(r"[^\w\s]", " ", address.lower())
    return " ".join(_ADDRESS_ABBREV.get(tok, tok) for tok in s.split())


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def person_match(a: str, b: str) -> float:
    return similarity(normalize_person(a), normalize_person(b))
