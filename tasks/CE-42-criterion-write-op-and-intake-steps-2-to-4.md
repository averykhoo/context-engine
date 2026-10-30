---
type: Task
id: CE-42
title: Criterion write op and intake steps 2 to 4 tooling
brief: Rewrites or appends one row under the lock; setting tested refuses unless G-T2 finds a claim
pri: NOW
state: closed
deps: [CE-25]
source: session 2026-10-13b
created: 2026-10-13
moved: 2026-10-30a
updated: 2026-10-30a
goals: [G-2, G-1]
status: deprecated
closed: 2026-10-30a
---

Split from CE-25 by DEC-33 (owner, 2026-10-13b): the write-op half. CE-25's design review covers it: see its rows on the criterion write op (byte-identical outside the row, under the store lock, an op-log line; tested refuses unless G-T2 finds a claim) and intake steps 2 to 4. Criteria stay rows of docs/criteria.md (DEC-33). Needs review: [write-op, shipped] and its own design review before promote.

## Log

- 2026-10-30a (claude-code/claude-opus-5-5): closed: done in 7fa4dee (lane 5e8b773), cite in fa618ee: criterion new / criterion set (CLI, MCP, library) write one row of [working] criteria in place, under the lock, with an op line; byte-identical outside the row, the new row read back through guards.py::criteria_rows, tested/manual refused unless guards.py::claim_sites finds a claim (G-T2), a bad source refused through guards.py::source_problems (G-T6). Rest-time twins: a duplicate-row red and G-D2 reading criterion.new. Also intake steps 2-3 runbooks, manual-mode § Criteria (kit copy), FRAMEWORK §6.2/§8.0.1/§8.0.2, criteria AC-160..AC-164 (DEC-116..DEC-119).
  residual risk: INV-87
