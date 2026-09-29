# Procurement Fraud Investigator

> Open Agent Hackathon 2026 · Track 3: **The Agent That Can Explain Why** (planned)

> 🚨 **Status: pre-hackathon prototype** (tag `pre-hackathon-prototype`).
> The official FAQ says code written before 15 Oct **can't be submitted in Tracks 1–4**. See
> [ROADMAP.md](ROADMAP.md#-rule-that-shapes-everything-pre-hackathon-code) for the two legitimate paths
> (fresh Track 3 build vs. Tinkerer Track).

## 📚 Start here
| Doc | What's in it |
|---|---|
| [ROADMAP.md](ROADMAP.md) | **Next steps**: day-by-day plan to 20 Oct, checklists, demo script |
| [docs/HACKATHON_RULES.md](docs/HACKATHON_RULES.md) | **Things to keep in mind**: rules, judging, submission requirements (from all official docs) |
| [docs/USE_CASE_WORKSHEET.md](docs/USE_CASE_WORKSHEET.md) | APPROACH worksheet: problem statement, scope, data, self-score 19/20 |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Agent roles, flow, tools, models, decisions, trade-offs |
| [docs/SPONSOR_TECH.md](docs/SPONSOR_TECH.md) | Where Zetaris / NVIDIA / Meterless fit |
| [backend/data/README.md](backend/data/README.md) | Data sources, licences, schema, limitations |

## Problem
> We are building an agent that helps **a public-procurement integrity analyst** understand **why a group of
> suppliers is flagged as a bid-rigging or conflict-of-interest risk** by **tracing relationships between tenders,
> bidders, shared officers and addresses, and sanctions records, and forcing every red flag to survive a Skeptic agent**,
> producing **ranked risk networks with the evidence path behind each conclusion and the suspicions that were ruled out.**

## Architecture

```
            ┌─────────┐    ┌────────────┐    ┌─────────┐  questions  ┌──────────────┐
 request ──▶│ Planner │──▶ │ Hypothesis │──▶ │ Skeptic │ ──────────▶ │ Investigator │
            └─────────┘    └────────────┘    │         │ ◀────────── │  (tools)     │
                 ▲                            └────┬────┘  evidence   └──────────────┘
                 └──── re-plan (build window) ─────┤ all questions answered
                                                   ▼ (or budget spent → escalate to human)
                                             ┌──────────┐
                                             │ Reporter │──▶ risk networks + evidence + trace
                                             └──────────┘
```

| Agent | Job |
|---|---|
| **Planner** | Chooses the detectors and scope (LLM-driven when a question is given) |
| **Hypothesis** | Runs red-flag detectors and proposes hypotheses with source evidence |
| **Skeptic** | Challenges each hypothesis, demands evidence, judges it, raises follow-ups, escalates |
| **Investigator** | Answers the Skeptic's questions with tools (market depth, address density, identity, corroboration…) |
| **Reporter** | Groups supported flags into risk networks and writes the auditor briefing (NVIDIA NIM) |

Details: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Quick start

**No manual steps:** runs offline on the sample data if there's no `.env`.

```bash
docker compose up --build        # UI http://localhost:5173 · API http://localhost:8000
```

Or run it locally:
```bash
cd backend
python -m venv .venv && .venv/Scripts/activate   # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m scripts.run_demo       # full investigation + trace in the terminal
uvicorn app.main:app --reload    # API
pytest -q                        # tests

cd ../frontend && npm install && npm run dev
```

## Environment variables
Copy `.env.example` to `.env` (optional). **Never commit `.env`.**

| Variable | Default | Purpose |
|---|---|---|
| `SAMPLE_MODE` | `true` | Offline fallback on the bundled sample data, with no external calls |
| `DATA_BACKEND` | `local` | `local` CSVs or `zetaris` federation (needs `SAMPLE_MODE=false`) |
| `DATA_DIR` | `data/sample` | Sample data folder |
| `NVIDIA_API_KEY` | *(empty)* | NVIDIA NIM key; empty means deterministic fallback text |
| `NVIDIA_BASE_URL` | `https://integrate.api.nvidia.com/v1` | NIM endpoint |
| `NVIDIA_MODEL` | `meta/llama-3.3-70b-instruct` | Model |
| `ZETARIS_URL` / `_USER` / `_PASSWORD` | *(empty)* | Zetaris connection |

## Sample inputs and outputs
| Input | Output | Result |
|---|---|---|
| [input_examples/01_all_agencies.json](input_examples/01_all_agencies.json) | [JSON](output_examples/01_all_agencies.json) · [trace](output_examples/01_all_agencies_trace.txt) | 12 hypotheses → 2 risk networks, 5 explained away |
| [input_examples/02_port_authority.json](input_examples/02_port_authority.json) | [JSON](output_examples/02_port_authority.json) · [trace](output_examples/02_port_authority_trace.txt) | Sanctions link confirmed via a follow-up loop |

### What the synthetic scenario contains
| Scenario | Expected outcome |
|---|---|
| Apex / Summit / Ridgeline rotate wins, losing bids 2–4% above the winner, shared directors and address | **Flagged**: high-risk network |
| Orion Supply: sole bidder ×3, director fuzzy-matches a (synthetic) sanctions entry | **Flagged** after identity check + corroboration |
| Dover companies share an address | **Explained away**: registered-agent address (4 firms) |
| Two firms share a "director" | **Explained away**: nominee service |
| Bridge-inspection firms alternate wins | **Explained away**: thin market |
| Clearwater / Granite / Evergreen alternate wins | **Explained away**: small sample, competitive prices |

## Responsible use
The system outputs **risk indicators for human review, not accusations**. All people and sanctions entries in the sample
are fictional, and real data will be used at company level only, with no real personal data.
