---
name: resume
description: Use in a repo run by context-engine (context.toml at its root) when orient lists an open pause record of your line of work, or the owner says to continue where a paused session stopped. Resume (FRAMEWORK §6.1, §6.4) - read the pause record, re-check the tree against it, do the resume step and the deferred steps, mark the record resumed.
---

# Resume

Runbook: `docs/runbooks/procedures.md` § Resume

Open that section of this repo's own copy now and do its rows in order: it is the source, and its
"By hand" column is the fallback when the engine errs. This skill only points there, so it never
disagrees with the runbook the repo is pinned to. `context-engine` means the engine command the
repo's contract names (`<engine-python> -m context_engine`, with `CE_ACTOR` and `CE_SESSION` set).

What sessions miss here:
- the record, not memory, is the state: compare the branch and every uncommitted path it names
  with the tree, and explain each difference before going on;
- the deferred steps (gate, commit, re-ranking, banner) are done now, not skipped.

If that section is missing, the repo's runbooks predate this plugin: read the runbook's headings
and use the one for resuming a pause.
