---
type: Question
id: ASK-17
title: Keep INV-51's old title, or let G-W13 match a renamed register entry through an alias?
brief: Cosmetic; the entry's content is current (89aeb00)
pri: LATER
state: closed
deps: []
source: session 2026-10-20b
created: 2026-10-20
moved: 2026-10-20b
updated: 2026-10-20c
last_asked: 2026-10-20c
status: deprecated
closed: 2026-10-20c
answered: {on: 2026-10-20, session: 2026-10-20c, decision: DEC-67}
---

## Question

INV-51 should be retitled 'a hand edit between live and unspecified, or of a story's actor, passes lint' after CE-58, but G-W13 matches register entries to CE-49's closed review by title (working.py::Engine.lint_review, review.py::key), so a new title turns it red.

## Options

- Keep the old title.
- Add a 'was:' alias line that G-W13 also matches.

## Recommendation

Keep the old title: it is only a label, the content is updated, and an alias is new engine surface for little gain.

## Log

- 2026-10-20c (claude-code/claude-opus-5-5): answered by the owner: DEC-67
