---
type: Task
id: CE-145
title: "INV-31 agent half: after a compaction in adhoc, the agent's first turn keeps its key (no second session start)"
brief: Observe when it happens naturally in adhoc; do not force it. Hook half already seen (CE-79).
pri: SOMEDAY
state: closed
deps: []
goals: [G-6]
source: session 2026-10-26c
created: 2026-10-26
moved: 2026-10-31a
updated: 2026-10-31a
status: deprecated
closed: 2026-10-31a
---

INV-31 agent half: after a compaction in adhoc, the agent's first turn keeps its key (no second session start).

## Traps

- none yet

## Read first

- none yet

## Log

- 2026-10-30a (claude-code/claude-opus-5-5): rerank: G-6: nothing to build here. It waits for a natural compaction in adhoc that INV-31 already tracks. Retiring it is put to the owner.
- 2026-10-31a (claude-code/opus-subagent): closed: folded into INV-31 by DEC-132 (6c31b41): the agent half of the compaction probe is now INV-31's control clause, with its evidence going to a new dated doc (DEC-133)
  residual risk: none
