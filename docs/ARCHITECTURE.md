# Architecture Notes

The official Overview asks for these under *"To Support Your Technical and Demo Scores"*: agent roles, interaction flow, tools, models, decisions and trade-offs.

## Problem and user
**User:** a public-procurement auditor or integrity officer.
**Today:** they spend weeks manually cross-referencing contract awards, company registries and sanctions lists that live in separate systems.
**Output:** a ranked list of *risk networks*. Each network is backed by evidence IDs and a record of which suspicions were ruled out and why. The auditor can act on it straight away by requesting documents, opening a case, or dismissing it.

## Agent roles

| Agent | Responsibility | Reads | Writes |
|---|---|---|---|
| **Planner** | Chooses detectors and scope; *(build window)* re-plans when the Skeptic reports gaps | request, Skeptic feedback | plan |
| **Hypothesis** | Runs red-flag detectors and turns signals into hypotheses with source evidence | data layer | hypotheses, evidence |
| **Skeptic** (evaluator) | Tries to explain each hypothesis away, demands specific evidence, judges it, raises follow-ups, escalates | hypotheses, checks | status, confidence, open questions |
| **Investigator** (executor) | Answers the Skeptic's questions by running tools against the data | open questions, data layer | new evidence, check results |
| **Reporter** | Clusters supported flags into risk networks and writes the auditor briefing | supported hypotheses, evidence | report |

## Interaction flow

```
Planner → Hypothesis → Skeptic ⇄ Investigator (loop) → Reporter
             ▲                │
             └──── re-plan ───┘   (build window: Skeptic → Planner when evidence is insufficient)
```

- **Loop:** the Skeptic sets `open_questions`, the Investigator answers them, and the Skeptic re-judges. This repeats until nothing is open.
- **Follow-ups:** a judgement can raise new questions (e.g. sanctions: identity check, then corroboration).
- **Escalation:** anything still open when the iteration budget runs out goes to a human. The system never guesses.
- **Shared state:** one `InvestigationState` (LangGraph) holds the hypotheses, the evidence store and the trace. Every agent reads and writes it.

## Tools (Investigator checks)

| Check | Innocent explanation it tests |
|---|---|
| `market_depth` | "Only a few firms work in this category, so rotation is natural" |
| `sample_size` | "Too few tenders, so the pattern could be coincidence" |
| `address_density` | "The address is a registered-agent or virtual office" |
| `officer_role` | "The shared 'director' is a nominee service" |
| `identity_verification` | "The sanctions name match is a different person" |
| `corroboration` | "It's an isolated anomaly with no other red flags" |

## Models
- **NVIDIA NIM** (OpenAI-compatible endpoint), model set by `NVIDIA_MODEL`. Used by the Planner (detector selection) and the Reporter (briefing). *Build window:* the Skeptic and Investigator also become LLM-driven, with the checks above exposed as tools.
- **Fallback:** if the key is missing or a call fails, the system uses deterministic templates, so a run never fails because of the LLM.

## Key decisions and trade-offs

| Decision | Why | Trade-off |
|---|---|---|
| Detectors and checks are **deterministic**, and the LLM reasons *over* them | Every claim is traceable to data rows, and auditors need reproducibility | Less flexible than letting the LLM free-read the data |
| The Skeptic must clear a hypothesis before it's reported | Precision matters more than recall, because a false accusation is costly | Some real fraud may be downgraded to "weakened" (still visible in the report) |
| The data layer is an interface (`DataSource`) | Swap CSV for Zetaris federation without touching the agents | Column contract must stay fixed |
| Risk is capped at 0.99 and labelled "risk indicator" | Responsible framing; not a legal finding | None |
| LangGraph | Explicit state, conditional edges and loops, which suit the evaluator pattern | Extra dependency |

## Failure handling
- LLM unavailable: deterministic fallback text, and the run continues.
- Unresolved questions: escalation to a human, recorded in the trace.
- *(Build window)* Data source unavailable: partial results with a note in the trace.

## Known limitations
- Public data rarely includes **losing bids**. Cover-bidding detection needs bid-level data (e.g. OCDS publishers) or synthetic scenarios.
- Entity resolution is string-based. Transliteration and dates of birth aren't handled yet.
