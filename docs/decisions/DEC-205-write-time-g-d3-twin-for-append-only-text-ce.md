---
type: Decision
id: DEC-205
title: "Write-time G-D3 twin for append-only text (CE-183): record new, ask answer/ask new --answered, record amend, confirm, retire and correct refuse, before any write, a citation lint G-D3 would fail at rest; not import; behind G-D3's [guards] off switch"
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:a4c7111bbb5722b8832f00c411e1b54bc365a8c580299fc01f89a8048f6cdbbb
---

Every operation that writes append-only text checks the new text, before anything is written, exactly as lint's G-D3 record citations (guards.py::record_refs) would check it at rest: an id of a configured series that no record or alias has, or a `<id> § <heading>` naming a heading its target lacks, is refused with nothing written. The operations: `record new`, `ask answer` and `ask new --answered`, `record amend`, `record confirm`, `record retire` and `record correct`. A stamped text is never edited, so such a citation written once is a red lint for good (the zanzibar case behind CE-183: a decision stamped and auto-committed, then superseded only to be recorded again).

Not checked at write time: `decision import` (a bulk import of another log, where foreign ids are expected; lint reports them at rest as before), and task and question bodies (mutable, fixable by hand). The check is a twin of G-D3, so `[guards] off` naming G-D3 turns it off too, unlike the `## Amendments` stop of CE-147, which guards the stamp itself.
