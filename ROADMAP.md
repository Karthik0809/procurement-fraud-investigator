# Roadmap

Built from the official Welcome Guide, Overview, Participant Journey Map, Event Calendar and FAQ.
All times are UTC. **Official Rules on the event page override everything here.**

Scoring: **Impact 30 · Technical 20 · Innovation 15 · Demo 15 · Product & UX 10 · Sponsor Tech 10**

---

## 🚨 Rule that shapes everything: pre-hackathon code

> FAQ: *"Can I use code I wrote before the hackathon? **No.** Projects in the four main tracks must be
> built during the build window. The Tinkerer Track is the only exception."*

The code in this repo was written **before** 15 Oct. There are two legitimate paths:

| | **Path A: Track 3, fresh build** | **Path B: Tinkerer Track** |
|---|---|---|
| What happens to this code | Not submitted. Keep it as a private prototype. On 15 Oct, start a **new repo** and write the code again during the window. | This repo *is* the "existing prototype". It's tagged `pre-hackathon-prototype`. |
| What's judged | Everything you build 15–20 Oct | **Only** the new work after the tag |
| Sponsor tech | Optional (10 pts) | **Required** (NVIDIA / Zetaris) |
| Best for | Competing in the main tracks | Keeping the head start legitimately |

**What you *can* carry over in both paths:** the idea, the research, the architecture plan, dataset
choices and the demo script. Concepts are fine; code is not. Don't copy code files into a Path A repo.

**Confirm at onboarding (14 Oct Q&A):** "Can planning docs and architecture notes written before the window be reused?" Also: how Tinkerer prizes compare with main-track prizes.
Track changes are allowed **until the end of 15 Oct**; after that the track is locked.

---

## 📊 Data rules (FAQ)
- Use **open, legally usable** data. **Avoid real personal data.**
  - Contract awards (organisations) are OK.
  - Company registries are OK at company level. **Director and officer names are personal data, so use synthetic or pseudonymised people** (e.g. hashed IDs), or leave people out.
  - Sanctions lists name real people, so keep the sanctions scenario **synthetic**.
- Keep the repo light: **samples only**, not full datasets.
- **Fallback mode is required** if an external API is down. (Already designed: `DATA_BACKEND=local` sample data plus the LLM fallback.)

---

## 🗓️ Calendar

### Pre-event
| Date | Action | Done |
|---|---|---|
| Now | Register on hackathon.genai.works, complete HackOS profile (skills, track, team preference) | [ ] |
| Now | Recruit teammates on HackOS (Backend, Data Scientist, Full Stack, ML/AI) | [ ] |
| Now | Research datasets and **real public cases** (company-level) for validation | [ ] |
| **7 Oct 16:00** | **Zetaris workshop**: how to register sources and run federated queries | [ ] |
| **8 Oct 16:00** | **NVIDIA workshop**: NIM models, tool calling, API key | [ ] |
| **12 Oct 12:00** | ⏰ Registration reminder (closes 13 Oct 00:00, hard deadline) | [ ] |
| **12 Oct 16:00** | **Meterless workshop**: decide whether it has a real role | [ ] |
| By 14 Oct | Complete sponsor access/setup (keys, accounts) | [ ] |
| **14 Oct 16:00** | **Onboarding**: confirm track and team, join the track room, ask the rules questions above | [ ] |

### Build window: 15 Oct 00:00 → 20 Oct 23:45 (144 h)

**15–16 Oct: lock and build the minimal loop**
- [ ] Final track decision (locks at the end of 15 Oct)
- [ ] Set up the repo (fresh repo for Path A), `.env.example`, `.gitignore`
- [ ] Data layer through **Zetaris** (contracts / company registry / synthetic officers and sanctions as separate sources)
- [ ] Agent loop working end to end: Planner → Hypothesis → Skeptic ⇄ Investigator → Reporter
- [ ] **NVIDIA NIM** connected; logging and trace from the first run

**17 Oct 16:00: ⏰ mid-build check.** Ask: *"If the deadline were tomorrow, what would fail?"*
- [ ] Minimal end-to-end version works
- [ ] Sponsor tech connected and tested
- [ ] Agent activity logged
- [ ] Initial input/output examples exist
- [ ] Blockers raised with mentors

**17–18 Oct: deepen agent behaviour** (what judges reward)
- [ ] **LLM Skeptic**: proposes innocent explanations and chooses which checks to run (tool calling). This avoids the "rule functions labelled as agents" critique.
- [ ] **Skeptic → Planner re-planning**: if evidence is insufficient, the Planner revises the scope or detectors (the official "strong pattern")
- [ ] **Dynamic delegation**: the Investigator picks tools based on context
- [ ] **Shared memory across runs**: learned registered-agent addresses and nominee services
- [ ] Retries and fallbacks: data source down → partial result + trace note
- [ ] **More than one case** (required: "sample inputs and outputs… more than one case"):
  1. Colluding ring (should flag)
  2. **Clean market (should flag nothing)**, which proves it isn't a hardcoded demo path
  3. Real company-level data from one country
- [ ] More detectors: split purchasing, new-company wins, price outliers

**19 Oct: freeze features, harden, package**
- [ ] ⛔ Feature freeze
- [ ] Clean setup test: fresh clone → `docker compose up` → works with **no manual steps**
- [ ] Credentials only from env vars; `git log -p | grep -iE "api_key|password|token"` is clean
- [ ] README: setup, run, env vars, agent description
- [ ] `docs/ARCHITECTURE.md` and `docs/SPONSOR_TECH.md` finalised
- [ ] Sample inputs and outputs saved in `samples/`
- [ ] **Deploy the live demo** (required link), e.g. Render/Railway/Fly for the backend and Vercel for the frontend, in offline-fallback mode if keys can't be shared
- [ ] **Record the demo video** (script below) and upload it to Google Drive (required link)

**20 Oct: submit**
- [ ] **12:00 ⏰ final validation**: every link opens in an incognito window
- [ ] Submit on HackOS: name, description, team, track, GitHub + live demo + Drive links, video, explanation (problem / solution / tech / sponsor tech)
- [ ] 🎯 **Aim to submit by 18:00**. The hard deadline is 23:45 and there are no fixes after it.

### After submission
| Date | Action |
|---|---|
| 20–30 Oct | Check HackOS Announcements daily and reply quickly if judges ask for clarification |
| **30 Oct 16:00** | Results call on HackOS |
| After | GenAI Works Discord community |

---

## ✅ Official success checklist, mapped to our plan

| Question | How we answer "yes" |
|---|---|
| One track, clearly defined problem? | Track 3 (or Tinkerer); procurement auditors, fraud risk networks |
| Scoped tightly enough to work reliably? | One country, 6–9 detectors, sample-data fallback |
| Value to a real user? | Weeks of manual cross-referencing become minutes, with evidence |
| Distinct, meaningful roles? | Planner / Hypothesis / Skeptic / Investigator / Reporter |
| Agents interact more than once? | Skeptic ⇄ Investigator loop + Skeptic → Planner re-plan |
| Critique, retry, escalation? | Skeptic critique, follow-ups, human escalation, fallbacks |
| Logs show reasoning? | Full trace in the UI and saved with each sample output |
| Clean setup, no manual steps? | `docker compose up`, with `.env` optional |
| Graceful failure? | LLM fallback, data fallback, partial results |
| Output usable by the user? | Ranked risk networks, evidence, dismissed flags, exportable briefing |
| Sponsor tech documented? | `docs/SPONSOR_TECH.md` |

## ⚠️ What judges discount, and how we avoid it
| Discounted | Our guard |
|---|---|
| Hardcoded demo paths | Multiple cases, including a clean market that flags nothing |
| Single-agent presented as multi-agent | LLM-driven Skeptic and Investigator with real tool choice |
| Sponsor tech bolted on | Zetaris is the data layer itself; NIM drives the reasoning |
| Unsupported claims of value | Validation against real public cases plus a time-saved measurement |
| UI polish without depth | UI shows the trace and evidence, i.e. the depth |

---

## 🎬 Demo video script (3 min)
1. **0:00–0:20 Hook.** "Procurement fraud drains public budgets. Auditors cross-reference registries by hand for weeks. Watch our agents do it in minutes, and argue with each other."
2. **0:20–1:30 Live run.** The trace streams. The Skeptic challenges, the Investigator fetches, and a decoy is **explained away** (registered-agent address).
3. **1:30–2:15 The why.** Top network: rotation + cover bids + shared officer + shared address, each with an evidence ID.
4. **2:15–2:35 Not hardcoded.** Run the clean-market case: nothing flagged.
5. **2:35–3:00 Architecture and sponsor tech.** Zetaris federation (data stays at the source), NVIDIA NIM reasoning, human escalation.

## Data sources (company-level, open)
| Need | Source |
|---|---|
| Contract awards | USAspending.gov (US), Contracts Finder (UK), TED (EU) |
| Bid-level data | OCDS publishers (e.g. Ukraine Prozorro). Check coverage first. |
| Company registry | UK Companies House / OpenCorporates (**company fields only**; pseudonymise people) |
| Sanctions | **Synthetic** (real lists name real people) |
