---
type: Decision
id: DEC-322
title: 'CE-18 build-or-defer: rollback and close is designed (FRAMEWORK 6.13) and done by hand; the engine operation session rollback is deferred to CE-215'
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
tasks: [CE-18, CE-215]
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:20eb27b1362fe4a5cf4122d9df339d04da264179f7c10d100d613d08fe3e61a2
---

An agent's call under P8 (cheap to undo: a deferred item can be promoted), made by CE-18's builder in session 2026-11-07e on 2026-11-08, following the CE-18 planner's design. Not owner words; PROVISIONAL until the owner reviews it.

**The call.** Rollback and close (US-13) is designed (FRAMEWORK §6.13) and done by hand (`docs/runbooks/procedures.md` § Rollback and close, plugin skill `rollback-and-close`, its git recipe pinned by `tests/test_rollback_recipe.py`). The engine operation `session rollback` (a plan, a run of §6.13 items 3 to 6, and its own `kind: rollback` ledger entry) is DEFERRED to CE-215.

**Why.** Every step can be done today with existing operations and git by path. The build is large: a compensating action for each of the op log's op names, partial-hunk logic, a new ledger kind touching `ledger.py::KINDS`, G-W6, staleness, the `--follows` refusal and orient. No rollback has been done or asked for in the month since US-13 (2026-10-09). P16 asks for the by-hand fallback first.

**Un-defer:** the first rollback done by hand, or the owner asks.

**Options rejected.** Building the engine operation now (above). A `kind: rollback` ledger entry now, without the operation: it touches the same five places for a procedure nobody has run; a `kind: close` entry with one `rolled back:` summary line records the same facts with no engine change. A change to the framework contract (`kit/contract.md`) to name the procedure: a contract change reaches every adopted repo (G-D0) and needs a framework version bump, while the runbook's map row and the plugin skill already carry it. Cutting a new frozen coverage map so §6.13 reads `deferred`: a whole-map census for one row; until the next map, `context-engine coverage` shows §6.13 as open work, owned by CE-18 and CE-215.
