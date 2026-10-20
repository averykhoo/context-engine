---
type: Question
id: ASK-16
title: May an agent re-confirm a replaced reconstruction by quoting the owner's earlier confirmation?
brief: From CE-58's verifier; docs state only the fact today
pri: NEXT
state: open
deps: []
source: session 2026-10-20b
created: 2026-10-20
moved: 2026-10-20b
updated: 2026-10-20b
last_asked: 2026-10-20b
blocks: [INV-51]
---

## Question

When retire --by agent replaces a story the owner already confirmed (record confirm, CE-58), the successor starts unconfirmed. May an agent run record confirm --by owner on it, quoting the owner's earlier confirmation words, or must the owner be asked again?

## Options

- Ask the owner again; record confirm refuses words already used on the predecessor.
- Allow quoting, with the predecessor's id cited in the amendment.

## Recommendation

Ask again: a confirmation says the owner saw this text, and the successor's text is new. Owner words are never the agent's call (DEC-48).
