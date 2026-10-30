---
type: Decision
id: DEC-125
title: "The ## Amendments refusal at the write covers every append-only kind and is no longer behind G-I3's off switch"
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:3366d2affe7c546e63d360602eea5591ae3f7cb93a90d32dfc82273a4158f413
---

PROVISIONAL decision (actor claude-code/claude-opus-5-5), for CE-147. Amends and narrows DEC-88.

**Options.**

- (a) A story-only check beside `_story_checks`, leaving the decision check behind G-I3's off switch. Rejected: the two kinds would keep different rules for the same break.
- (b) A general refusal in `store.new` (DEC-88 option c). Rejected: decision import legitimately writes entries that carry their own `## Amendments`, and it goes through `store.new`.
- (c) An Engine-level check, `guards.py::amendments_in_new_text`, called with no condition by `working.py::Engine.record_new` for every append-only kind and by `working.py::Engine._answer_decision` (`ask answer`, `ask new --answered`). **Chosen.**

**Why (c).** A `## Amendments` line in a new record's text puts the text below it outside `body_sha`, which breaks the integrity of any append-only record. That is not G-I3's rule, so no `[guards] off` entry should drop the refusal. This also removes the coupling DEC-88 listed as a cost and CE-148 item 1. The check sits at the Engine level, not in `store.new`, so decision import still works. Pinned by AC-140.

**Cost to undo.** Cheap: put the G-I3 condition back on the call. Landed in 9b5f35d on the lane, 7b5a75e on main.
