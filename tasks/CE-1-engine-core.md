---
type: Task
id: CE-1
title: "Engine core: OKF records, ids under a lock, op log, write-time refusal"
brief: "Round-trip must be byte-identical (ruamel); hash bodies only after normalising line endings"
pri: NOW
state: open
deps: []
source: session 2026-10-08a
created: 2026-10-08
moved: 2026-10-08a
updated: 2026-10-08a
closed:
---

Build step 1 of the plan: the core every record kind sits on. Claims AC-1 to AC-9
(`docs/criteria.md`). Suggested shape: `src/context_engine/` with `okf.py` (frontmatter read and
write), `store.py` (find records, allocate ids, file lock, operation log), `kinds.py` (schemas
and change modes), `errors.py` (refusals that name a remedy). Test first; claim criteria with
`@pytest.mark.criterion("AC-n")`.

## Traps

- **ruamel.yaml round-trip mode** (`YAML()`, default `rt`), not `typ='safe'`: safe drops
  comments and can reorder. Settle `preserve_quotes`, indentation and width so an untouched
  record writes back byte-identical (AC-1).
- **Line endings:** this checkout has `core.autocrlf`, so files on disk may be CRLF. Normalise
  before hashing (AC-7), and write back in the file's existing line ending.
- **The lock is a cross-process file lock and must work on Windows** (no `fcntl`). Each
  concurrent Claude Code session runs its own MCP server process (`spike/FINDINGS.md`).
  zanzibar `scripts/gate_lock.py` is prior art.
- **An unquoted colon in a YAML scalar breaks parsing**: it bit DEC-6 on 2026-10-08, and the
  shell heredocs that first tried to write this board. The writer must quote what needs it.
- OKF reserves `status` (`draft | stable | deprecated`); our states use their own keys (DEC-7).
- This repo's records are hand-written in the target shapes: use them as fixtures
  (`docs/decisions/`, `docs/stories/`, `tasks/`).

## Read first

- `docs/framework/FRAMEWORK.md` §8.0, §8.0.1 (record kinds, change modes), §9.3.1 (OKF constraints)
- `docs/criteria.md` § Core
- `spike/FINDINGS.md` (line endings, SDK 2.x)
- zanzibar (`PycharmProjects/graph-reachability-zanzibar-index`), ideas not code (DEC-2):
  `scripts/task.py::Store`, `::op_new`, `::op_promote`, `::ratchet_min_parsed`, `::slugify`;
  `tests/test_tasktool.py::test_shipped_config_is_measured_not_an_example`,
  `::test_new_ratchets_the_floor_to_the_measured_total_and_never_lowers_it`

## Log
