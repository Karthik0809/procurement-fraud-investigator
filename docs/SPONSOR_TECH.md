# Sponsor Technology Record

Required by the submission checklist ("documented where each sponsor technology fits").
Sponsor Tech = **10 points**. Judges penalise tech that is "bolted on at the end with no real role".
Fill this in during the build window as each integration becomes real.

| Sponsor | Role in our system | Where in code | Status |
|---|---|---|---|
| **Zetaris** | Federated access to the fragmented sources (contract awards, company/officer registry, sanctions list) *without copying them into one database*. Our core problem is fragmented data, so this is essential, not decorative. | `backend/app/tools/data_sources.py` → `ZetarisSource` | ⏳ Placeholder. Implement after the 7 Oct workshop. |
| **NVIDIA** | NIM-hosted LLM for Planner reasoning, Skeptic critique, Investigator tool selection and the Reporter briefing | `backend/app/llm.py` | ⏳ Code written. Test with a key after the 8 Oct workshop. |
| **Meterless** | TBD after the 12 Oct workshop. Use it only if it plays a real role. | — | ⏳ Unknown |

## Evidence to include in the demo
- [ ] A screenshot or clip of the sources registered in Zetaris
- [ ] The trace showing agent queries running through Zetaris
- [ ] The model name and a NIM call shown in the trace or logs
