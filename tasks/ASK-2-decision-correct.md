---
type: Question
id: ASK-2
title: "May append-only records take logged typo fixes?"
pri: NEXT
state: closed
blocks: [CE-5]
last_asked: 2026-10-08c
source: session 2026-10-08a
created: 2026-10-08
closed: 2026-10-08c
answered: {on: 2026-10-08, session: 2026-10-08c, decision: DEC-13}
---

**Question:** FRAMEWORK §12.3 Q-I. A strict body hash forbids fixing even a typo in a decision
or a story. Allow a `decision.correct` operation that changes the text, re-stamps the hash and
logs a `corrected:` line under Amendments, or forbid every body change except `amend`?

**Why owner-only:** it is a preference about how strictly your recorded words are protected.

**Options:** allow logged corrections (the agent's recommendation: every edit stays visible) ·
forbid them, so typos are fixed by an amendment.

**Blocks:** CE-5.

## Answer

2026-10-08c, owner: corrections are bracketed insertions; the typed words always survive; a
change of meaning is an amendment (DEC-13, FRAMEWORK §6.5).
