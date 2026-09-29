# Roadmap: from skeleton to winning submission

Scoring: **Impact 30 · Technical 20 · Innovation 15 · Demo 15 · Product & UX 10 · Sponsor Tech 10**

> ⚠️ **Rules check first.** Before 15 Oct, read the Official Rules on HackOS to see what may exist
> before the build window opens (15 Oct 00:00 UTC). If pre-written code isn't allowed for your track,
> treat this repo as a **design reference**: rebuild it during the build window and keep the commit
> history honest. (The Tinkerer Track explicitly judges only work done during the hackathon.)

---

## ✅ Already working (skeleton)

- [x] LangGraph loop: Planner → Hypothesis → Skeptic ⇄ Investigator → Reporter
- [x] 6 deterministic red-flag detectors (rotation, cover bidding, shared officer, shared address, sanctions fuzzy match, single bidder)
- [x] Skeptic with innocent-explanation checks, follow-up questions, and human escalation when the budget runs out
- [x] Evidence store: every claim has an ID that points back to source rows
- [x] Full reasoning trace
- [x] FastAPI + React UI (graph, risk networks, evidence, trace)
- [x] Synthetic dataset with planted fraud + 4 decoys, end-to-end tests
- [x] NVIDIA NIM wrapper with offline fallback

---

## Before 15 Oct: prep (no build-window code)

- [ ] Attend or watch the **Zetaris (7 Oct)**, **NVIDIA (8 Oct)** and **Meterless (12 Oct)** workshops. Note exact APIs and SDKs.
- [ ] Decide where **Meterless** fits (check whether it helps with metering/billing of agent runs; if not, skip it; sponsor points come mainly from meaningful use)
- [ ] Get an NVIDIA API key; pick the model (a strong instruct model for the Skeptic/Reporter, a smaller one for the Planner)
- [ ] Shortlist real datasets (below) and check licences and rate limits
- [ ] Find 2–3 **real prosecuted bid-rigging cases** (DOJ Antitrust Division press releases, UK CMA cases) for validation
- [ ] Assign owners: agents / data+Zetaris / detectors+validation / UI+demo

## Day 1 (15 Oct): real data and sponsor integration
- [ ] **Zetaris**: register sources (contracts, company registry, sanctions) as separate federated sources and implement `ZetarisSource` in `backend/app/tools/data_sources.py`. Keep column names identical to the CSVs.
- [ ] Ingest one real market end to end (choose ONE country; recommended options below)
- [ ] Switch `DATA_BACKEND=zetaris` and confirm the sample scenario still passes the tests
- [ ] Set `NVIDIA_API_KEY` and confirm the Planner and Reporter use NIM

### Data sources

| Need | Source | Note |
|---|---|---|
| Contract awards | USAspending.gov API (US), Contracts Finder (UK), TED (EU) | Awards only, not losing bids |
| **Bid-level data** | OCDS publishers such as Ukraine's Prozorro | Losing bids are rare in public data; check coverage before committing |
| Company officers/owners | OpenCorporates, UK Companies House API (free, excellent officer data) | UK is the easiest market for officer links |
| Sanctions | OpenSanctions | Has good entity-matching docs |

**Recommendation:** UK (Contracts Finder + Companies House + OpenSanctions) for officer and address
links, plus the synthetic scenario for cover bidding, since public data rarely has losing bids. Be upfront about this in the demo.

## Days 2–3: make the agents truly agentic
- [ ] **LLM Skeptic**: after the rule checks, ask the LLM for *additional* innocent explanations, then have it *request a tool call* to test each one. This is the biggest innovation lever.
- [ ] **Tool-calling Investigator**: let the LLM choose which check to run (function calling over `CHECKS`) instead of a fixed mapping
- [ ] **Dynamic replanning**: if the Skeptic rejects most hypotheses, the Planner widens the scope (more agencies or years) and re-runs
- [ ] New detectors: **split purchasing** (contracts just under approval thresholds), **new-company wins** (registered shortly before a large award), **price outliers** vs. the category median, **bidder address = official's address** (conflict of interest)
- [ ] Better entity resolution: transliteration, token-sort matching, date of birth where available
- [ ] **Shared memory** across investigations: known registered-agent addresses and nominee services the Skeptic has already learned about

## Day 4: graph and data depth
- [ ] Move relationships into **Neo4j** (companies, people, addresses, tenders) and add multi-hop queries such as "director of X is a shareholder of Y which subcontracts to Z"
- [ ] Persist investigations in **PostgreSQL** (replace the in-memory dict in `main.py`)
- [ ] Failure handling: data source down → partial results + a note in the trace; LLM timeout → fallback (already built in)

## Day 5: validation and UX (this is where you win)
- [ ] **Validation run**: point the system at a real prosecuted case → show "flagged before the indictment". This becomes your headline demo moment.
- [ ] **Metrics**: precision on the planted and real cases; time vs. manual review (e.g. "3 weeks → 4 minutes")
- [ ] UI: **stream the trace live** (SSE or WebSocket) so judges watch the agents argue in real time
- [ ] UI: click a graph edge → show its evidence and the Skeptic's verdict; animate rejected edges fading out
- [ ] UI: export the auditor briefing as PDF
- [ ] Clean setup test: fresh clone → `docker compose up` → working demo

## Day 6: submission (deadline 20 Oct, 23:45 UTC)
- [ ] 3-minute demo video (script below)
- [ ] README: problem, architecture diagram, sponsor tech usage, how to run, limitations
- [ ] Check for committed secrets: `git log -p | grep -i "api_key\|password"`
- [ ] Submit on HackOS with the repo link, video, track (Track 3) and team

---

## 🎬 Demo video script (3 min)

1. **0:00–0:20 Hook.** "Procurement fraud costs governments billions each year. Auditors spend weeks
   cross-referencing registries by hand. Watch our agents do it in minutes, and argue with themselves."
2. **0:20–1:30 Live run.** Click Run. The trace streams. Point at the Skeptic challenging, the Investigator
   fetching, and a decoy being **explained away** ("registered-agent address, 4 companies"). This
   shows judges you are not flagging everything.
3. **1:30–2:15 The why.** Open the top network: rotation + cover bids + shared director + shared
   address, each with an evidence ID. Show the sanctions hit that needed an extra loop.
4. **2:15–2:40 Real-world validation.** Show a real case the system flagged.
5. **2:40–3:00 Architecture and sponsor tech.** Zetaris federation (data stays at the source), NVIDIA NIM
   reasoning, human-in-the-loop escalation.

## 🏆 What makes this outstanding (checklist for judges)

| Judges look for | Where we show it |
|---|---|
| Not a pipeline | Skeptic ⇄ Investigator loop with follow-ups and escalation |
| Critique/validation | The Skeptic dismisses 5 of 12 hypotheses, with reasons |
| Shared memory/context | Evidence store + (Day 3) learned registered-agent list |
| Branching/retries/recovery | Follow-up questions, iteration budget, LLM fallback, partial results |
| Logs/traces | Full reasoning trace, streamed live |
| Real problem | Auditor persona, real case validation, time saved |
| Sponsor tech meaningfully | Zetaris federation is essential (the data really is fragmented); NVIDIA powers reasoning |
