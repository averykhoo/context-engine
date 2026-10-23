---
type: Decision
id: DEC-81
title: 'Build status leaves FRAMEWORK.md for the board: Not checked sentences and board items, no generated status table yet'
decision_status: PROVISIONAL
actor: claude-code/claude-opus-5-5
decided: 2026-10-24
session: 2026-10-23f
body_sha: sha256:2da295b3fa5de52b2b845c5685babbd061aae5dc1a05a29ec8b3bf8872e6bb8e
---

An agent's call under P8 (cheap to undo), made by CE-93's builder in session 2026-10-23f and landed in c5b812f. Recorded afterwards from the builder's report. This one decision carries two calls (the builder's PROVISIONAL calls P-4 and P-8), both on how build status leaves the spec.

**Calls.**
1. Every *Not built yet* / *Built so far* marker and every `(CE-n)` build mark is removed from FRAMEWORK.md without a generated status table in its place. The header points at the board; §8.0 says a configuration key the kit template lacks is refused; parts that are §11.2 "add when needed" items say "added when ..." instead.
2. Where a cut marker hid a gap (verify-1's blocker B1): a guard's limited scope gets its "Not checked:" sentence back (G-D8, G-D11, §9.3.1's decision status, following the G-I2 and G-D5 precedent), and unbuilt behaviour gets a board item (CE-135, CE-136, CE-137). The read adapter was not filed: the new text no longer mentions it, and what it says ("read as it is") is true today.

**Why.** Build status in the spec goes stale and belongs on the board. A generated status table needs a generator and a guard, which is its own task (filed from CE-93's verify-2, N3). "Not checked:" keeps the text from asserting a check that does not exist.

Task: CE-93. Commit: c5b812f.
