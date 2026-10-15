---
name: clean-close
description: Use in a repo run by context-engine (context.toml at its root) as soon as every task the owner asked for is done, in that same turn and before the final reply, or when the owner says to close or wrap up. The clean close (FRAMEWORK §6.3) - owner words recorded, lint, board, batons, gate, ledger entry, banner, commit by path, a digest of at most 7 lines. Never ask whether to close.
---

# Clean close

Runbook: `docs/runbooks/procedures.md` § Clean close

Open that section of this repo's own copy now and do its rows in order: it is the source, and its
"By hand" column is the fallback when the engine errs. This skill only points there and quotes it, so it never
disagrees with the runbook the repo is pinned to. `context-engine` means the engine command the
repo's contract names (`<engine-python> -m context_engine`, with `CE_ACTOR` and `CE_SESSION` set).

What sessions miss here, word for word from the runbook (the engine's gate checks each line):
- **Close eagerly: as soon as every task you were asked for is done, in that same turn, before
  the final reply.** Never ask whether to close, and never wait for more instructions; what is left
  for the owner goes in the digest
- Lint, to see which failures earlier sessions left, before adding any of your own
- `guards` = the gate result verbatim
- commit by path what the engine did not, never the whole tree, never `git stash`

If that section is missing, the repo's runbooks predate this plugin: read the runbook's headings
and use the one for FRAMEWORK §6.3. At an awkward stopping point, use the pause skill instead.
