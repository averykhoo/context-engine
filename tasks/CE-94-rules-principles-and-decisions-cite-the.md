---
type: Task
id: CE-94
title: Rules, principles and decisions cite the incident that justified them (DEC-47)
brief: 'An incident is evidence, not a rule: a rule links its incident; an incident no longer possible lets the rule retire'
pri: LATER
state: open
deps: []
source: session 2026-10-15c
created: 2026-10-15
moved: 2026-10-15c
updated: 2026-10-15c
---

DEC-47 (owner). FRAMEWORK §0.2 says every component exists because its absence caused a recorded failure, but the failures are prose ("seen 2026-10-13", "a false green, seen 2026-10-08d") or sit in the archived FRAMEWORK-v0.5.md.

To design:
- **Where an incident lives.** It could be a record kind (an append-only `INC-n`: what happened, the harm, the evidence, the session) or an evidence doc with an id. The kind's guards would come with it.
- **How a rule cites one.** Principles (P1–P18), contract rules, guards (their docstrings) and decisions cite `INC-n` or `none: <why>`. A lint could check that every principle and every guard names one.
- **Back-fill.** Walk FRAMEWORK-v0.5.md's prior-art citations, the ledger and the `seen <date>` lines, and mint incidents from them. Rules with no findable incident are listed for the owner, not deleted.
- **The reverse use.** A rule whose incidents can no longer happen (the design eliminated them, P17 rung 1) is a candidate to retire.
- **The link to P17.** Design reviews and residual-risk register entries cite the incidents they answer.

Overlaps CE-93 (FRAMEWORK clean-up, DEC-49): history moves out of FRAMEWORK.md, and an incident id is how the spec keeps a pointer to it.

## Traps
- Owner words are never rewritten: back-filled incidents cite records, they do not edit them.

## Read first
- docs/decisions/DEC-47-rules-principles-and-decisions-cite-the.md
- docs/framework/FRAMEWORK.md §0.2, P17
