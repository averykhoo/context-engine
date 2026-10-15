---
name: reconcile-foreign-commits
description: Use in a repo run by context-engine (context.toml at its root) at session start when commits have landed since the newest ledger entry without a Session trailer - a human's edits, another tool's, a merge made outside the procedures. Reconciling foreign commits (FRAMEWORK §6.10) - a foreign ledger entry, stale text filed, stated intent recorded, a red guard fixed rather than reverted.
---

# Reconciling foreign commits

Runbook: `docs/runbooks/procedures.md` § Reconciling foreign commits

Open that section of this repo's own copy now and do its rows in order: it is the source, and its
"By hand" column is the fallback when the engine errs. This skill only points there and quotes it, so it never
disagrees with the runbook the repo is pinned to. `context-engine` means the engine command the
repo's contract names (`<engine-python> -m context_engine`, with `CE_ACTOR` and `CE_SESSION` set).

What sessions miss here, word for word from the runbook (the engine's gate checks each line):
- Humans are never required to follow the procedures: the next agent session absorbs the cost.
- with the author as its actor (`human:<id>`)
- A human commit that turned a guard red is not reverted: fix or reconcile it

If that section is missing, the repo's runbooks predate this plugin: read the runbook's headings
and use the one for FRAMEWORK §6.10.
