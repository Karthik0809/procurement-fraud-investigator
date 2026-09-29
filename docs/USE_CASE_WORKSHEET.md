# Use Case Decision Worksheet (APPROACH method)

Filled in from the official "How to APPROACH Solutioning" guide. Revisit at onboarding (14 Oct).

## A: Assess the problem
> We are building an agent that helps **a public-procurement integrity analyst** understand **why a group
> of suppliers is flagged as a likely bid-rigging or conflict-of-interest risk** by **tracing the relationships
> between tenders, bidders, shared officers/addresses and sanctions records, and forcing every red flag
> to survive a Skeptic agent**, using **open contract-award data plus company-registry and sanctions
> samples**, producing **a ranked list of risk networks with the evidence path behind each conclusion
> and the suspicions that were ruled out.**

This closely matches the official **Track 3 example** (compliance analyst, supplier–owner–incident relationships, Challenge Agent, evidence path).

## P: Pick the ambition level
**Level 2: Ambitious** (3–5 agents, 1–2 bounded data sources, one domain, branch and retry paths).
It is not Level 3: there is no GPU training, no medical claims, and the output is "risk indicators for human review".

## P: Prove data availability

| Source | Access | Size | Runtime API? | Sensitivity |
|---|---|---|---|---|
| Synthetic sample (5 CSVs) | In repo | < 10 KB | No | None (fictional) |
| Contract awards (one country) | Open API, no key (USAspending) or open download (Contracts Finder) | Filtered sample < 1 MB | Optional, cached | Organisations only |
| Company registry | Open (Companies House needs a free key, so **commit a small sample** instead) | < 500 KB | No | **Company fields only; people pseudonymised** |
| Sanctions | **Synthetic** | Tiny | No | Real lists name people, so avoid |

Fallback: `SAMPLE_MODE=true` / `DATA_BACKEND=local` runs entirely offline.

## R: Reduce the scope
**One user + one decision + one data slice + one strong output + clear agent behaviour.**

| We WILL build | We will NOT build |
|---|---|
| One country, one or two agencies, one year | All countries or all procurement |
| 6–9 detectors | A general fraud platform |
| ~50–200 tenders, ~30–60 companies | Full national datasets |
| Web view of networks + evidence + trace | Case management, users, auth |
| Cached sample + optional live fetch | Real-time ingestion |

**Main demo scenario:** road-maintenance tenders in one agency, where a 3-company ring is caught and 4 decoys are explained away.

## O: Outline agent collaboration

| Agent | Role | Input | Output | Collaborates with |
|---|---|---|---|---|
| Planner | Scope, detectors, re-plan | request, Skeptic feedback | plan | Hypothesis, Skeptic |
| Hypothesis (Relationship Mapper) | Detect signals, build links | data | hypotheses + evidence | Planner, Skeptic |
| Skeptic (Challenge Agent) | Test each link, demand evidence, judge, escalate | hypotheses | questions, verdicts | Investigator, Planner |
| Investigator (Evidence Tracer) | Run tools to answer questions | questions | new evidence | Skeptic |
| Reporter (Explainer) | Networks + evidence path + limitations | supported flags | briefing | — |

Collaboration: ☑ Delegation ☑ Critique ☑ Revision loop ☑ Shared memory/state ☑ Branching ☑ Retry ☑ Escalation ☑ Confidence scoring ☑ Human-in-the-loop

## A: Align with constraints (runtime budget)
| Step | Target |
|---|---|
| Startup | < 30 s |
| Data load | < 30 s (sample) |
| Full investigation incl. LLM loop | **< 2 min** (cap: max 3–4 iterations, timeouts on every call) |

## C: Confirm evaluation fit (self-score, 0–2 each)
| Question | Score |
|---|---|
| Explain the problem in 30 s? | 2 |
| Know the user? | 2 |
| Accessible data? | 1. Losing bids are rare in public data (mitigation: synthetic scenario + company-level real data) |
| Buildable in 144 h? | 2 |
| Runs quickly and predictably? | 2 |
| Light repo? | 2 |
| Agents interact more than once? | 2 |
| Critique / validation / retry? | 2 |
| Useful demo output? | 2 |
| Limitations documented? | 2 |
| **Total** | **19/20: strong candidate** |

## H: Harden. Constraints checklist
- [ ] Runs from a clean setup with no manual steps (`docker compose up`, `.env` optional)
- [ ] Runs quickly and predictably
- [ ] Repository is light
- [ ] No hardcoded outputs (clean-market case flags nothing)
- [ ] No committed API keys
- [ ] Logs show how the agent worked
- [ ] Sample inputs and outputs included (`input_examples/`, `output_examples/`)
- [ ] Sponsor technology use documented (`docs/SPONSOR_TECH.md`)
