---
type: Task
id: CE-29
title: 'Unverified hazards and memory: where each lives, how it is promoted (to an invariant or the contract) or pruned'
brief: 'Hazards are volatile, invariants durable: keep them apart (FRAMEWORK §2.1); memory is promoted or pruned, never a rule'
pri: SOMEDAY
state: open
deps: []
source: session 2026-10-12b
created: 2026-10-12
moved: 2026-10-12b
updated: 2026-10-12b
---

Filed by CE-16 from the coverage map (docs/evidence/framework-coverage-2026-10-12.md): components 13 (unverified hazards) and 23 (memory), FRAMEWORK §2, §2.1, §6.7 and §7.4. Today hazards have no declared home (no route in context.toml, no record kind) and memory lives only in Claude Code's per-project auto-memory, outside the repo. Decide each one's home and route, and a housekeeping or close step that turns a confirmed hazard into a CE-23 register entry and a general memory lesson into a contract rule.
