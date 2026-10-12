---
type: Task
id: CE-33
title: Doc liveness and typed numbers as lint guards (G-D4, G-D5)
brief: Measure false reds on this repo before choosing the exemptions; frozen provenance is never edited
pri: LATER
state: open
deps: [CE-14]
source: session 2026-10-12d
created: 2026-10-12
moved: 2026-10-12d
updated: 2026-10-12d
---

Split from CE-14 (2026-10-12d), which built the rest of the §8.3 doc guards in `src/context_engine/guards.py` with `[guards]` path lists in context.toml. Both are §11.2-triggered here: the repo keeps evidence docs ("the repo measures things").

- **G-D4:** every doc declares its liveness (LIVING, ACTIVE-PLAN, FROZEN) near the top; history directories are checked for frozen banners within a window. On 2026-10-12d only 5 of 26 tracked non-record docs declared one (counted by grep of the first 12 lines), and `docs/framework/FRAMEWORK-v*.md` (frozen provenance) cannot be edited to add one, so it needs a declared exemption or a route-level liveness. The kit's docs need the line too. Decide what "within a window" means (days since the item closed?).
- **G-D5:** derivable counts only in generated blocks; a typed number takes one of P5's four forms. A naive scan flags section numbers, ids, versions, list markers and rule values ("NEXT <= 5"); measure the false reds first.

## Traps

- A guard that fails by passing: sabotage each one (tools/sabotage_ce14.py is the pattern).
- Kit files must not carry this repo's ids (tests/test_kit.py leak check).

## Read first

- `docs/framework/FRAMEWORK.md` P2 (liveness), P5, §8.3 G-D4 and G-D5
- `src/context_engine/guards.py` (the shared prose reader and the `[guards]` lists)

## Log
