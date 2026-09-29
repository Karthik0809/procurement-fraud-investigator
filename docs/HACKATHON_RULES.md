# Hackathon Rules and Things to Keep in Mind

A consolidated summary of the official documents: Welcome Guide, Overview, Participant Journey Map,
Event Calendar, FAQ, and How to APPROACH Solutioning. **If anything conflicts, the Official Rules
on the event page win.** All times are UTC.

## 🔴 Hard rules (break these and you lose)
| Rule | Detail |
|---|---|
| **No pre-hackathon code** in Tracks 1–4 | Everything must be built 15 Oct 00:00 → 20 Oct 23:45. **Only the Tinkerer Track** may extend an existing project, and only the new work is judged. |
| Registration deadline | **13 Oct 00:00**, hard |
| Submission deadline | **20 Oct 23:45**, hard. No fixes after it; edits are allowed until then. |
| One account per person | Duplicate accounts **disqualify the whole team** |
| One team, one track | You can't join 2 teams or submit to 2 tracks. The track can change **until the end of 15 Oct**, then it's locked. |
| Team size | 1–5 builders |
| No committed secrets | `.env` in `.gitignore`; `.env.example` with placeholders only; never in README, notebooks, screenshots or logs |
| Data | Open and legal only. **No real personal data**, no private/proprietary/confidential data |
| Age | 16+ at the start of the build window |

## 🟡 What judges reward vs. discount
**Reward:** agents doing real work · a clear problem, user and usable output · critique, retries, branching, escalation ·
agents challenging each other · outputs refined through iteration · reliable execution · clear logs/traces ·
meaningful sponsor tech · a clear demo.

**Discount:** UI polish without depth · single-agent systems presented as multi-agent · **hardcoded demo paths** ·
broad concepts with weak implementation · **unsupported claims of value** · sponsor tech bolted on at the end ·
linear A→B→C pipelines · agents that are just prompt wrappers.

## 📊 Scoring (100)
Impact **30** · Technical **20** · Innovation **15** · Demo **15** · Product & UX **10** · Sponsor Tech **10**

## 📦 Submission (on HackOS)
**Required:** project name · description · team members · track · **GitHub link** · **live demo link** ·
**Google Drive link** (where relevant) · **short demo video** · explanation of problem / solution / technologies / sponsor tech.

**Needed for Technical and Demo scores:** runs from a clean setup with **no manual steps** · README (setup, run,
env vars, agents) · architecture notes (roles, flow, tools, models, decisions, trade-offs) · logs/traces ·
**sample inputs and outputs for more than one case** · sponsor tech record · `.env.example`.

> "A submission a judge cannot run cannot be scored properly." Test a fresh clone before submitting.

## ⚙️ Technical discipline (APPROACH guide)
- `SAMPLE_MODE=true` fallback: must work if an external API or the internet is down
- Timeouts on every external call; bounded retries; bounded agent turns (no endless debates)
- Keep the repo light: samples only; large data via a download script into a gitignored folder
- Document every data source in `backend/data/README.md` (URL, licence, subset, count, regenerate, limits)
- Runtime target: a full run in minutes, not tens of minutes
- Don't pass full documents between agents; use summaries and shared state
- Log errors from sponsor services clearly; fall back gracefully

## 🤝 Sponsors
| Sponsor | Workshop | Notes |
|---|---|---|
| Zetaris | 7 Oct 16:00 | Our data layer (federated sources). Required-or-optional: optional in Tracks 1–4, **required in Tinkerer** (NVIDIA or Zetaris) |
| NVIDIA | 8 Oct 16:00 | NIM LLMs for agent reasoning |
| Meterless | 12 Oct 16:00 | Decide after the workshop; use only if it plays a real role |
Workshops: GenAI Academy course "Open Agent Hackathon 2026". Recordings on HackOS. Set up access and **run a connection test on day 1**.

## 🆘 Where to get help (all on HackOS)
Track scope → track room · Sponsor errors → sponsor resource area, then track room · Agent design/debugging →
mentor office hours (mentors don't build for you) · Rules → Official Rules · Updates → **Announcements (check daily)**.
When asking: what you're trying to do, stack, error/trace, snippet, what you tried. Never post keys.

## 👥 Team agreements (settle before 15 Oct)
Track and use case · architecture · stack · **repo owner** · **submission owner** · demo/video owner ·
how prizes are shared (equal split by default) · IP: participants own what they build.
