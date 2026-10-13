---
type: Task
id: CE-41
title: G-D3 resolves a bare file name against stale build/ copies
brief: Files.named walks build/ and Files.find takes the first match, so file::symbol can check a stale copy
pri: LATER
state: open
deps: []
source: session 2026-10-13a
created: 2026-10-13
moved: 2026-10-13a
updated: 2026-10-13a
---

Found by the CE-25 design-review agent (2026-10-13a): its first gate run went red because G-D3 read a bare-file-name citation of `src/context_engine/working.py::CRITERION_ROW_RE` against `build/lib/context_engine/working.py`, a gitignored stale copy. `guards.py::Files.named` walks into `build/`, which is not in `SKIP_DIRS`, and `guards.py::Files.find` takes the first match. Fix: skip gitignored trees (at least build/ and dist/), and when a bare name matches more than one tracked file, red as ambiguous rather than picking one. Sabotage both.
