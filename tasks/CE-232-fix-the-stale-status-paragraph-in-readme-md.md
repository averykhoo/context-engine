---
type: Task
id: CE-232
title: Fix the stale status paragraph in README.md (housekeeping built, adopted in three repos, drop the 2026-10-13 gate snapshot)
pri: NEXT
state: open
deps: []
goals: [G-6]
created: 2026-11-12
---

**Why:** `README.md` lines 17-19 say the no-model housekeeping script is not built yet, the engine has not yet been adopted in a second repo, and the gate and CI were green at `8990dd0` (2026-10-13). All three are stale: CE-6 closed 2026-11-01b (Tier-0 housekeeping finished), CE-43 closed 2026-10-22a (audio-workspace), CE-11 closed 2026-11-03a (intervals) and CE-167 closed 2026-11-04a (zanzibar).

**What:** replace only `README.md` lines 17-19 with:
**Status: alpha, no release tag yet.** The engine runs this repo's own records, and CI runs the gate on every push to `main`. Tier-0 housekeeping is built (`hk run start|close`, CE-6). It has been adopted in other repos: audio-workspace (CE-43), intervals (CE-11) and zanzibar (CE-167).

Do not replace the dated gate snapshot with a new dated snapshot — that would go stale the same way.

**Acceptance:** every cited task id/state/date in the new paragraph matches its task file; `python -m context_engine lint` is clean.

## Log

- 2026-11-12: closed: README.md lines 17-19 replaced with the timeless status paragraph (CI runs the gate on every push; Tier-0 housekeeping built, CE-6; adopted in audio-workspace CE-43, intervals CE-11, zanzibar CE-167). Verification: every cited task checked closed in its task file; `python -m context_engine lint` clean; full gate 2107 passed (see CE-231 log for the one pre-existing failure).
