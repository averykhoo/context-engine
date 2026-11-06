---
type: Task
id: CE-187
title: 'decision accept <ids>: owner-actor decisions born ACCEPTED, agent calls PROVISIONAL until accepted'
brief: 'DEC-162: accept the listed agent calls through the op once built, never by hand before'
pri: NEXT
state: open
deps: []
goals: [G-3, G-2]
source: session 2026-11-06c
created: 2026-11-06
moved: 2026-11-06f
updated: 2026-11-06f
---

Build `decision accept <ids>`, and make decisions whose actor is the owner born ACCEPTED (DEC-162).

Source: DEC-162, adopting docs/evidence/owner-review-advice-2026-11-06b.md § 2.1 and § 3. PROVISIONAL today means both "an owner's word awaiting nothing" and "an agent's call awaiting review", so 146 of 161 decisions read as unreviewed.

Shape the owner ruled:
- A decision recorded with `actor: owner` (record new, ask answer) is born ACCEPTED.
- An agent's call (its own actor, or `ruled_by`) stays PROVISIONAL until `decision accept <ids>` marks it reviewed; ids and ranges (`DEC-86..90`) are accepted in one op, one op line.
- BUILT stays for a decision a task carried out.
- The kit contract's "Who decides" changes with it, so this forces a contract version bump; CE-132's wording fixes ride that bump.

Once the op exists, accept in one op the agent calls DEC-162 lists (not by hand before then, and not with `decision set`): DEC-86..90, DEC-92..96, DEC-98..106, DEC-108..109, DEC-111..119, DEC-121..130, DEC-133, DEC-148..149, DEC-159..160. DEC-97, DEC-107, DEC-110 and DEC-120 were ruled on separately in DEC-162 (each linked to it); accept them with the rest unless their own task has superseded them by then.

## Traps

- Do not accept anything by hand before the op exists: 60 `decision set` lines would be op-log noise (DEC-162).
- The existing owner-actor PROVISIONAL decisions need a migration path (the op, or the born-ACCEPTED rule applied at rest); say which in the PROVISIONAL decision this build records.
- The accept op takes exactly DEC-162's list, and the body's last sentence overstates it (DEC-162). Never accept DEC-107: the owner overruled it ('on' against its chosen off), so the decision CE-192 records supersedes it. DEC-97, DEC-110 and DEC-120 are not on the list either: the owner gave each its own word in DEC-162 (text, optional, cut), so leave them out of this op.

## Read first

- docs/evidence/owner-review-advice-2026-11-06b.md
- DEC-162
- docs/framework/contract.md § Rules, Who decides

## Log

- 2026-11-06c (claude-code/claude-opus-5-5): Correction (DEC-162): DEC-107 is never accepted; it is superseded by the decision CE-192 records. DEC-97, DEC-110 and DEC-120 are outside DEC-162's accept list; the body's 'accept them with the rest' is withdrawn (see Traps).
