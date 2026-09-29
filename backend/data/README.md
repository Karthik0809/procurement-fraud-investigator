# Data

## `sample/`: synthetic demo dataset
| Item | Detail |
|---|---|
| Source | Hand-built by the team; **entirely fictional** (companies, people, sanctions entries) |
| Licence | Ours (MIT) |
| Records | 11 companies, 12 officers, 15 tenders, 38 bids, 2 sanctions entries |
| Purpose | Reproducible offline demo, a planted fraud ring plus 4 innocent decoys, and tests |
| Regenerate | Edit the CSVs directly; `pytest` checks the expected outcomes |
| Limitations | Small; the thresholds were chosen to be realistic but aren't calibrated on real data |

### Schema (the same contract every `DataSource` must return)
- `companies(company_id, name, address, city, registered_date)`
- `officers(officer_id, name, company_id, role, nationality)`
- `tenders(tender_id, agency, category, title, award_date, estimated_value)`
- `bids(tender_id, company_id, amount, won)`
- `sanctions(name, list, country, reason)`

## Real data (planned, build window)
Document each source here: URL, licence, subset used, record count, how to regenerate, limitations.
Rules: open and legally usable; **no real personal data** (pseudonymise officers, keep sanctions synthetic);
commit only small samples; large raw files go in `data/raw/` (gitignored) via a download script.
