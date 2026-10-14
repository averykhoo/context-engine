---
name: clean-close
description: Use in a repo run by context-engine (context.toml at its root) as soon as every task the owner asked for is done, in that same turn and before the final reply, or when the owner says to close or wrap up. The clean close (FRAMEWORK §6.3) - owner words recorded, lint, board, batons, gate, ledger entry, banner, commit by path, a digest of at most 7 lines. Never ask whether to close.
---

# Clean close

Runbook: `docs/runbooks/procedures.md` § Clean close

Open that section of this repo's own copy now and do its rows in order: it is the source, and its
"By hand" column is the fallback when the engine errs. This skill only points there, so it never
disagrees with the runbook the repo is pinned to. `context-engine` means the engine command the
repo's contract names (`<engine-python> -m context_engine`, with `CE_ACTOR` and `CE_SESSION` set).

What sessions miss here:
- close eagerly, without asking; what is left for the owner (an answer, a check, a push) goes in
  the digest, not in a question at the end;
- lint before your own changes, so an earlier session's failure is not taken for yours;
- the gate result goes into the ledger entry verbatim, and the commit is by path, never the tree.

If that section is missing, the repo's runbooks predate this plugin: read the runbook's headings
and use the one for FRAMEWORK §6.3. At an awkward stopping point, use the pause skill instead.
