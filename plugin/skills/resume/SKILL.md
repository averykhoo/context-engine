---
name: resume
description: Use in a repo run by context-engine (context.toml at its root) when orient lists an open pause record of your line of work, or the owner says to continue where a paused session stopped. Resume (FRAMEWORK §6.1, §6.4) - read the pause record, re-check the tree against it, do the resume step and the deferred steps, mark the record resumed.
---

# Resume

Runbook: `docs/runbooks/procedures.md` § Resume

Open that section of this repo's own copy now and do its rows in order: it is the source, and its
"By hand" column is the fallback when the engine errs. This skill only points there and quotes it, so it never
disagrees with the runbook the repo is pinned to. `context-engine` means the engine command the
repo's contract names (`<engine-python> -m context_engine`, with `CE_ACTOR` and `CE_SESSION` set).

What sessions miss here, word for word from the runbook (the engine's gate checks each line):
- the record, not memory, is the state to resume from
- explain every difference before going on
- Do the resume step, then the deferred steps (gate, commit of the work, re-ranking, banner,
  runbook filing) ... a pause defers these; it never drops them

If that section is missing, the repo's runbooks predate this plugin: read the runbook's headings
and use the one for resuming a pause.
