---
type: Task
id: CE-32
title: "decision set: an op for a decision's own frontmatter (decision_status, reopen_if, tags)"
brief: No op changes a decision's status, reopen_if or tags; Engine.set refuses decisions, so they are hand-edited
pri: NEXT
state: open
deps: []
source: session 2026-10-12d
created: 2026-10-12
moved: 2026-10-13a
updated: 2026-10-13a
---

Found reviewing CE-5 (2026-10-12d). `working.py::Engine.set` refuses a decision ("not a board item"), and `decision supersede` / `decision link` touch only their own fields. So moving a decision PROVISIONAL -> BUILT, adding `reopen_if:` to a REJECTED one, or fixing `tags` has no operation. In 2026-10-12d DEC-15 and DEC-16 had `tags` fixed by hand, with hand-written op-log lines (docs/ledger/ops.jsonl, op `set`, fields [tags]) recording an op the engine cannot perform for that kind. The op log is append-only, so those lines stay; this row closes the gap. Shape to decide: a `decision set` (or `record set` over append-only kinds) that takes only frontmatter keys, never body_sha/id/type, refuses `decision_status: SUPERSEDED` (that is `decision supersede`), regenerates the index, and has a manual-mode section.
