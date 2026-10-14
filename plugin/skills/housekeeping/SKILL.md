---
name: housekeeping
description: Use in a repo run by context-engine (context.toml at its root) at session start after orient, and again before a clean close - stale open session stubs, expired batons, stamps owed, things recorded but never carried out. Housekeeping (FRAMEWORK §6.11) carries out intent already recorded and never forms new intent.
---

# Housekeeping

Runbook: `docs/runbooks/procedures.md` § Housekeeping

Open that section of this repo's own copy now and do its rows in order: it is the source, and its
"By hand" column is the fallback when the engine errs. This skill only points there, so it never
disagrees with the runbook the repo is pinned to. `context-engine` means the engine command the
repo's contract names (`<engine-python> -m context_engine`, with `CE_ACTOR` and `CE_SESSION` set).

What sessions miss here:
- it has two passes, one at session start and one before close; do the one you are at;
- every write is mechanical and committed by path with the session trailer, so `git revert`
  undoes it; the list of operations goes into the owner digest;
- a judgement call is not housekeeping: file it as a task or a question instead.

If that section is missing, the repo's runbooks predate this plugin: read the runbook's headings
and use the one for FRAMEWORK §6.11.
