---
type: Decision
id: DEC-216
title: 'G-I4 is lint-only: no write (record new, ask answer, decision set title=) refuses a duplicate title, since a replacement is recorded with the old title before `decision supersede` runs (DEC-92 own birth)'
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
tasks: [CE-189]
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:d703017d342d99285847d6ca37b19b743235020a4dfa90b2946427c8f69019be
---

G-I4 is a lint check only. No write refuses a decision whose title another current decision already has: not `record new`, not `ask answer`, not `decision set --set title=`.

Why: the supersede path needs the replacement to exist before `decision supersede` runs, and a replacement is often recorded with the old title (DEC-92 was born with DEC-91's title, then `decision supersede DEC-91 DEC-92`). A write-time refusal would break that path. Lint catches the duplicate at rest, and its remedy names the supersede. A reply hint on `record new` was also left out: more surface than it is worth, since lint names the pair.

Cost to undo: cheap; add the check to the writers later if duplicates are seen to persist.
