---
type: Decision
id: DEC-191
title: store.py::Store._criterion_prefixes keeps its own raw regex for now (store.py imports nothing from guards.py)
actor: claude-code/claude-sonnet-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:13961ccb10dc9cc2609762c89512f17ece1749b06b3f69ad20a2911dc08dca51
---

The agent's call on CE-150, made while building it in session 2026-11-07e: `store.py::Store._criterion_prefixes` keeps its own raw regex for now.

It has the same flaw `Engine._criteria` had (a raw read, not `guards.py::criteria_rows`). Moving it is a layering change: `guards.py` imports `store.py` and `store.py` imports nothing from `guards.py`. That is outside CE-150's scope, so it is a follow-on item.

Cheap to undo: nothing changes now.
