---
type: Decision
id: DEC-311
title: 'Hazard home is a board row: an unverified hazard is a board task labelled `hazard`, not a record kind; HAZ stays reserved and FRAMEWORK P3 is unchanged'
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:5ee3051b5f8a754aed594c2224b808dd1f1febed50abfa593c146e2e70cb1fbe
---

**Decision:** An unverified (suspected) hazard is a board task carrying `labels: [hazard]`, not a record kind. The `HAZ` prefix stays reserved and FRAMEWORK P3 is unchanged. This writes DEC-50's second home (a hazard board row) into FRAMEWORK §7.4 for CE-29.

**Why:** DEC-50 rules a board row: it gives the hazard an id, a tier, `stale_after` (G-D4) and a close, with no new machinery (`labels` is already a typed list on `[kinds.task]`; `task set --set labels=[hazard]`, `task list --label hazard`).

**Rejected:** a `HAZ` record kind (a second backlog beside the board, plus schema, directory and lint); dropping the `HAZ` reservation (churn across config.py::RESERVED_PREFIXES, tests and the kit for no behaviour, and it closes off a later kind).
