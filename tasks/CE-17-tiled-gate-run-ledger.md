---
type: Task
id: CE-17
title: "Tiled gate with a run ledger keyed on each tile's input hash; orient() shows tested and untested"
brief: "Spec first (§8.5 G-V1, §8.0.1, §6.1, §11.1, §13 row), then build; generalise intervals gate.py and zanzibar gate_status.py"
pri: LATER
state: open
deps: [CE-1]
source: session 2026-10-08b
created: 2026-10-08
moved: 2026-10-08b
updated: 2026-10-08b
closed:
---

US-10; serves FRAMEWORK P15 (an agent that starts with no context knows what is tested). Two parts:

1. **Spec change** (a §13 row): add tiles to G-V1: a long suite is split into named tiles that
   run separately and may run in parallel; each tile's ledger row is keyed on a hash of its
   declared inputs (the source paths it covers, its own tests, config, interpreter and lockfile),
   with the whole content tree as the fallback when no inputs are declared. Make verification
   state an engine concern, not zanzibar-only (§8.0.1). Add "tested or untested on this tree,
   per tile" to `orient()` (§6.1, AC-17). Decide whether G-V1 joins the §11.1 minimum set.
2. **Build:** `gate run [tile...]` / `gate status [--require commit|push]`, a ledger file per
   tile run, under the G-V3 lock; criteria first.

## Traps

- **An input hash that misses an input says "tested" when it is not**, the worst failure this
  can have. Declared inputs need a check that catches an undeclared one (e.g. a tile importing a
  module outside its inputs), and the sabotage rule (DEC-11) applies: change an input, watch the
  row go stale.
- Parallel tiles share CPU and the 8 GB WSL cap with other sessions (global `CLAUDE.md`).
- G-V4: no exit codes through pipes; one tile per command; logs from `mktemp`.
- This repo's suite is one test today; the real trial needs intervals or zanzibar.

## Read first

- `docs/framework/FRAMEWORK.md` §8.5, §6.1, §8.0.1, §11.1
- intervals `tools/gate.py`, `tests/test_gate_ledger.py`; zanzibar `scripts/gate_status.py`,
  `scripts/gate_lock.py`, `.gate-runs/`

## Log
