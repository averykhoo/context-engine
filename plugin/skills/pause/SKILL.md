---
name: pause
description: Use in a repo run by context-engine (context.toml at its root) when work has to stop at an awkward point and continue in a later session - context running out, the owner leaving mid-task, a long job still running. The pause (FRAMEWORK §6.4) - owner words recorded, evidence out of .scratch, a pause record and a pause ledger entry, committed at once.
---

# Pause

Runbook: `docs/runbooks/procedures.md` § Pause

Open that section of this repo's own copy now and do its rows in order: it is the source, and its
"By hand" column is the fallback when the engine errs. This skill only points there, so it never
disagrees with the runbook the repo is pinned to. `context-engine` means the engine command the
repo's contract names (`<engine-python> -m context_engine`, with `CE_ACTOR` and `CE_SESSION` set).

What sessions miss here:
- anything only in `.scratch/` is already lost: move evidence into a tracked doc first;
- the pause record names every uncommitted path and the deferred steps; the gate, the commit of
  the work, re-ranking and the banner are deferred, never dropped.

If that section is missing, the repo's runbooks predate this plugin: read the runbook's headings
and use the one for FRAMEWORK §6.4. At a natural stopping point, use the clean-close skill instead.
