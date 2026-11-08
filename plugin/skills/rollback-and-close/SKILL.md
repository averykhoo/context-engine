---
name: rollback-and-close
description: Use in a repo run by context-engine (context.toml at its root) when the owner wants this session's work undone instead of saved - roll back and close (FRAMEWORK §6.13). Only on the owner's word, after showing them the plan; only this session's commits and files, undone by path and by the operations that own the records, never git stash, reset, clean or revert; owner words stay.
---

# Rollback and close

Runbook: `docs/runbooks/procedures.md` § Rollback and close

Open that section of this repo's own copy now and do its rows in order: it is the source, and its
"By hand" column is the fallback when the engine errs. This skill only points there and quotes it, so it never
disagrees with the runbook the repo is pinned to. `context-engine` means the engine command the
repo's contract names (`<engine-python> -m context_engine`, with `CE_ACTOR` and `CE_SESSION` set).

What sessions miss here, word for word from the runbook (the engine's gate checks each line):
- **Only on the owner's word**, and only after showing them the plan (step 2).
- The op log and the ledger are never rolled back, and a record is never put back or deleted by
  hand: its operation undoes it
- `--worktree` leaves the index as other writers staged it; a reversed hunk that does not apply
  overlaps another writer's work, so it is left, never forced
- `close`: `task reopen <id> -m "rolled back with session <key>; undoes <sha>, <sha>"`, naming every
  undone commit that carries `Closes: <id>`
- Commit by path, titled with no task id first

If that section is missing, the repo's runbooks predate this plugin: read the runbook's headings
and use the one for FRAMEWORK §6.13. To save the work instead, use the clean-close skill.
