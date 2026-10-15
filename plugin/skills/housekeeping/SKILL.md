---
name: housekeeping
description: Use in a repo run by context-engine (context.toml at its root) at session start after orient, and again before a clean close - stale open session stubs, expired batons, stamps owed, things recorded but never carried out. Housekeeping (FRAMEWORK §6.11) carries out intent already recorded and never forms new intent.
---

# Housekeeping

Runbook: `docs/runbooks/procedures.md` § Housekeeping

Open that section of this repo's own copy now and do its rows in order: it is the source, and its
"By hand" column is the fallback when the engine errs. This skill only points there and quotes it, so it never
disagrees with the runbook the repo is pinned to. `context-engine` means the engine command the
repo's contract names (`<engine-python> -m context_engine`, with `CE_ACTOR` and `CE_SESSION` set).

What sessions miss here, word for word from the runbook (the engine's gate checks each line):
- It **carries out intent already recorded somewhere and never forms new intent**.
- **At session start** (reconcile what happened since the last session)
- **Before close** (§6.3 item 6a: carry out what this session recorded but did not finish)
- committed by path with a `Session: <key>` trailer, so `git revert` undoes it ... The operation
  list goes into the owner digest.
- anything else housekeeping would close is proposed to the session, never closed by it

If that section is missing, the repo's runbooks predate this plugin: read the runbook's headings
and use the one for FRAMEWORK §6.11.
