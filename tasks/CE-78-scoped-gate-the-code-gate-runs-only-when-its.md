---
type: Task
id: CE-78
title: "Scoped gate: the code gate runs only when its inputs changed, proven by a per-scope content hash on each gate run's recorded result"
brief: "No framework or kit edits while CE-7's trial runs (owner; F18). Each scope exclusion fails open: guard it"
pri: NOW
state: open
deps: []
source: session 2026-10-14c
created: 2026-10-14
moved: 2026-10-14g
updated: 2026-10-14g
---

The framework (FRAMEWORK.md, the kit contract, `docs/runbooks/gate.md`) says the code gate runs only
when code changed, and the engine enforces it mechanically: each gate scope is a set of globs, and
every gate run records its result against a content hash of the files in its scope. A commit whose
scope hash already has a green row needs no re-run. A records-only commit needs lint, not the
711-test suite (207 s on 2026-10-14 for a one-task commit, CE-77's).

## Shape (from graph-reachability-zanzibar-index, read 2026-10-14)

The zanzibar repo (graph-reachability-zanzibar-index) does this in its scripts/gate_status.py,
documented in its docs/gate-runbook.md § 4, "The run ledger" and "Per-phase scopes" (its board row
GS-2). Its paths are written plain here because they are not in this repo:
- gate_status.py::tree_id gives a content address t2<scope>:<12 hex> over the tracked and
  untracked-non-ignored files in a phase's input scope. It holds no commit id, so it does not
  change on git add or git commit: a green row earned before a commit stays green after it.
- Every gate phase appends a row to a gitignored run ledger (.gate-runs/ledger.tsv): started,
  duration, phase, PASSED/FAILED/INCONSISTENT, tree id, observed counts, log file.
  gate_status.py --require-green exits 1 unless THIS tree is covered.
- Scopes: all (everything) and code (everything minus *.md and benchmarks/, keeping the markdown
  tests read: CODE_SCOPE_MD_KEEP). The scope tag goes into both the digest and the prefix, so ids
  from different scopes can never match. A phase opts IN to a narrow scope (phase_scope); the
  default is all.

## Traps zanzibar paid for

- **A scope exclusion fails open.** *.md was excluded because "no test reads markdown"; twelve
  days later a test linted the live tasks/ corpus, so a board edit could turn the suite red while
  the gate still reported covered (fixed 2026-09-03c). Here, `tests/test_kit.py` (kit byte copies),
  `tests/test_ci.py` (CLAUDE.md § Gate vs the workflow), `tests/test_method_runbooks.py` and the
  lint test all read docs. So the keep-list must be derived or verified, not just written down:
  e.g. a guard that runs the suite with each excluded path class corrupted and shows no test
  notices.
- **A committed deletion or rename moved the id** (fixed 2026-09-05b by skipping index entries
  with no worktree file). Pin it as zanzibar does (its
  test_tree_id_survives_a_commit_of_a_deletion_or_rename, with a control test).
- **The ledger must be gitignored**, or it falls inside its own hash.
- The hash does not see gitignored files or the environment (installed deps, interpreter). A
  matching id means "passed against this source", not full provenance; the push gate still runs in
  full, as does `tools/linux_gate.py` (CE-67).
- .scratch/ and other gitignored files are invisible to it by design. Records the gate reads must
  be tracked.

## Scope of the change

- FRAMEWORK.md (gate section, in place, DEC-19) and the kit contract § Gate and
  `kit/docs/runbooks/gate.md`, plus their byte-equal copies here (CE-26). The rule: the code gate
  runs when its scope hash has no green row; records-only changes need lint; the push runs
  everything.
- Engine: record each gate run's result against its scope hash (the gate is the repo's own command,
  so the engine wraps or reads it), and a check like `--require-green`. `context-engine commit` could
  refuse a commit whose code scope has no green row, which is a refusal rather than a doc rule (P7).
- By-hand fallback in `manual-mode.md` (DEC-20): hash the scope by hand, or run the full gate.
- This repo's CLAUDE.md § Gate narrows the contract until the kit text lands.
- Sabotage (DEC-11): edit a file in the code scope, then check the gate reports not covered; corrupt a
  kept doc and check the scoped run notices.

## Not now

The owner said not to change the framework while another agent runs CE-7 (2026-10-14c). A kit edit
mid-trial also moves adhoc's G-D0 (CE-7 trap F18).

## Log

- 2026-10-14c (claude-code/claude-opus-5-5): Owner, 2026-10-14c, verbatim: "yes the framework itself should say that the code gate only needs to run when code is changed, and that should be tested via glob and hash checksum tied to each gate's results. see zanzibar for an example. but don't make the change to the framework now, another agent has started ce7. just file a task"
- 2026-10-14g (claude-code/claude-opus-5-5): DEC-43 (owner, 2026-10-14g): start now; the CE-7 dep and the 2026-10-14c freeze are lifted for this task. adhoc keeps its pinned kit (DEC-41).
- 2026-10-14g (claude-code/claude-opus-5-5): Owner, 2026-10-14g: picked CE-78 for NOW while CE-7 waits (DEC-43).
