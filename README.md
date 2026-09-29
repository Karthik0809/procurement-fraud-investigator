# Procurement Fraud Investigator

> Open Agent Hackathon 2026 · Track 3: **The Agent That Can Explain Why**

A multi-agent system that investigates public procurement data for **bid rigging, shell companies,
conflicts of interest, and sanctions exposure**. It then explains every conclusion with traceable
evidence. It is built for procurement auditors, who today spend weeks manually cross-referencing
contract awards, company registries and sanctions lists.

**Its core idea is that every red flag has to survive a Skeptic agent** that actively tries to explain it
away before it can reach the report.

## Architecture

```
            ┌─────────┐    ┌────────────┐    ┌─────────┐  questions  ┌──────────────┐
 request ──▶│ Planner │──▶ │ Hypothesis │──▶ │ Skeptic │ ──────────▶ │ Investigator │
            └─────────┘    └────────────┘    │         │ ◀────────── │  (tools)     │
                                              └────┬────┘  evidence   └──────────────┘
                                                   │ all questions answered
                                                   ▼  (or budget spent → escalate to human)
                                             ┌──────────┐
                                             │ Reporter │──▶ risk networks + evidence + trace
                                             └──────────┘
```

| Agent | Job |
|---|---|
| **Planner** | Chooses which red-flag detectors to run (LLM-driven when a question is given) |
| **Hypothesis** | Runs deterministic detectors → proposes hypotheses with source evidence |
| **Skeptic** | Challenges each hypothesis, demands specific evidence, judges supported / weakened / rejected, raises follow-ups |
| **Investigator** | Answers the Skeptic's questions with tools (market depth, address density, identity checks, corroboration…) |
| **Reporter** | Groups supported flags into risk networks and writes the auditor briefing (NVIDIA NIM LLM) |

Every step is logged to a **reasoning trace** shown in the UI.

**Data access:** all agents read through a `DataSource` interface. Setting `DATA_BACKEND=zetaris`
queries the original, fragmented sources through Zetaris federation, with no copying into one DB.

## Quick start

```bash
cp .env.example .env            # add NVIDIA_API_KEY (optional — runs offline without it)

# backend
cd backend
python -m venv .venv && .venv/Scripts/activate   # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m scripts.run_demo       # full investigation in the terminal
uvicorn app.main:app --reload    # API on :8000
pytest -q

# frontend
cd ../frontend
npm install && npm run dev       # UI on :5173
```

Or run everything with `docker compose up --build`.

## Sample data

`backend/data/sample/` is **synthetic**. It contains a planted fraud scenario plus decoys, to show that the Skeptic works:

| Scenario | Expected outcome |
|---|---|
| Apex / Summit / Ridgeline rotate wins on 6 road contracts, losing bids 2–4% above the winner, shared directors and address | **Flagged** as a high-risk network |
| Orion Supply: sole bidder ×3, director fuzzy-matches a sanctions entry | **Flagged** after identity check + corroboration (extra loop) |
| Dover companies share an address | **Explained away**: registered-agent address used by 4 firms |
| Two firms share a "director" | **Explained away**: nominee-director service |
| Bridge inspection firms alternate wins | **Explained away**: thin market (only 3 bidders) |
| Clearwater / Granite / Evergreen alternate wins | **Explained away**: small sample, genuinely competitive prices |

## Responsible use

The system outputs **risk indicators for human review, not accusations**. Evidence IDs link every claim back to source rows.

## Project status

See [ROADMAP.md](ROADMAP.md) for the build plan.
