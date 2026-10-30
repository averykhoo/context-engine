---
type: Task
id: CE-109
title: G-D1 remedy names where a cut rule goes, so rules are not lost
brief: G-D1's remedy must say where a cut rule goes (CLAUDE.md to contract/runbook), not just cut
pri: NOW
state: closed
deps: []
goals: [G-2]
source: session 2026-10-21b
created: 2026-10-21
moved: 2026-10-30a
updated: 2026-10-30a
status: deprecated
closed: 2026-10-30a
---

G-D1 remedy names where a cut rule goes, so rules are not lost

What went wrong (adhoc AAR entry 10, docs/evidence/adhoc-feedback-2026-10-21.md) and what to change: G-D1 caught CLAUDE.md growth at once, but its remedy says to cut with no destination, and rules were lost in the trimming (entry 10). Make the remedy name the destinations (contract, runbook, decision, task) and require the cut text to land there first. Census F7: partly tracked by CE-47 and CE-40; this is the remedy text only. Filed 2026-10-21b from the CE-7 census (.scratch/ce7-feedback/census.md, row F7).

## Traps

## Read first

- docs/evidence/adhoc-feedback-2026-10-21.md

## Log

- 2026-10-30a (claude-code/claude-opus-5-5): closed: done in 1394067 (lane 4c4c99e), integration fix c377040: G-D1's remedy for a line or byte cap says where cut text goes (a rule to the contract or a runbook, a ruling to a decision, owed work to a task, stale text to the archive, ledger or evidence) and to delete it only once it has landed (guards.py::cap_failures; FRAMEWORK §8.3; manual-mode G-D1); AC-105 tested
  residual risk: none
