---
type: Decision
id: DEC-2
title: Extract a standalone package; port ideas, not zanzibar's task.py
actor: owner + agent
decided: 2026-10-08
session: 2026-10-08a
decision_status: BUILT
tags: [packaging]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-08T15:00:00+08:00 }
body_sha: sha256:454ec559b530b41b2becd2118ce26e296030dcdbe9806f5a8efd29bd92c0c32f
---

The engine is a new package, generalised from zanzibar's `scripts/task.py`, not a copy of it.
`task.py` is 4,254 lines shaped around one repo (`wc -l`, 2026-10-08). Port its *ideas*, with
their tests: write-time budget refusal (`op_promote`), the floor ratchet
(`ratchet_min_parsed`), config provenance (`tests/test_tasktool.py::test_shipped_config_is_measured_not_an_example`),
no mechanical close (`write_op`), close requiring a message (`op_close`), title changes never
renaming files (`slugify`). zanzibar keeps its own tool until it adopts the engine.

Rejected: copying `task.py` into adhoc as a quick prototype (it would be the second copy).

## Amendments
