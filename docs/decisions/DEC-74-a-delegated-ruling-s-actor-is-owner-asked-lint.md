---
type: Decision
id: DEC-74
title: A delegated ruling's actor is 'owner asked'; lint refuses only a lone owner or human actor
decision_status: PROVISIONAL
actor: claude-code/claude-opus-5-5
decided: 2026-10-24
session: 2026-10-23f
body_sha: sha256:a5974e6e0a2f695c0dc5d9f0ebf6e163ed0d5f8e74172f4a157c81933dacaf07
---

An agent's call under P8 (cheap to undo), made by CE-113's builder in session 2026-10-23f and landed in 21a88d9. Recorded afterwards from the builder's report (its PROVISIONAL call 2). Not owner words, and not a ruling on the owner's delegation.

**Call.** A delegated ruling's `actor` is `owner asked`, which `ask answer` writes. Lint (G-I3) and the write-time check refuse only a lone `owner` or `human:<id>` actor on a delegated ruling; combined actors such as `owner + agent` pass.

**Why.** `owner asked` is already in FRAMEWORK §6.5's actor vocabulary (the owner asked, another chose), so no new actor word is needed. Refusing only the lone human actor targets the actual fault (a ruling stamped as the owner's words) without breaking the existing combined forms.

Task: CE-113. Commit: 21a88d9.
