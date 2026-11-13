---
type: Task
id: CE-236
title: "Close plan check's two (new)-mark edge cases: a shared basename, a wrong-case path on Windows"
pri: LATER
state: open
deps: []
goals: [G-7]
source: session 2026-11-13a
created: 2026-11-13
moved: 2026-11-13a
updated: 2026-11-13a
---

Close two edge cases verify-2 found in `plan check`'s ` (new)` mark (CE-225, DEC-341).

- A new path sharing a basename with an existing file (`tests/fixtures_zz/guards.py` (new))
  still exempts the bare-name citation of a dead symbol in guards.py (zz_dead_qq, an example), which G-D3 resolves to the
  existing `src/context_engine/guards.py`: a dead symbol passes. Possible fix: exempt a
  bare-name citation only when `Files.find(<bare name>)` is None.
- On a case-insensitive file system (Windows), a wrong-case path such as
  `SRC/context_engine/guards.py` (new) misses the case-exact check, counts as new and exempts a
  dead symbol under it; a builder writing it would overwrite the real file. Consistent with
  G-D3's case-exactness and correct on Linux CI.

Each fix: a test with these inputs, a row in `tools/sabotage_ce225.py`.

## Traps

## Read first

- `src/context_engine/guards.py::plan_problems`, `src/context_engine/guards.py::path_exists`

## Log
