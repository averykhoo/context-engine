---
type: Task
id: CE-140
title: "FRAMEWORK and release-note wording from CE-93's review: G-D5 generated blocks, 5.2 links floor, 3.2 retire and confirm, No rule changed"
brief: Text only; a cut status marker returns as a Not checked line or a board item, never as build status
pri: NOW
state: closed
deps: []
goals: [G-7]
source: session 2026-10-23f
created: 2026-10-24
moved: 2026-10-30a
updated: 2026-10-30a
status: deprecated
closed: 2026-10-30a
---

FRAMEWORK and release-note wording from CE-93's review

Three non-blocking findings of CE-93's second verifier (verify-2, N1, N2 and N4), on c5b812f. Filed in session 2026-10-23f.

- N1: two status markers were dropped with no open board item. (a) G-D5's "generated blocks inside a hand-written doc (no generator writes one yet)": a count inside such a block in a `numbers` doc would go red; `guards.py::numbers`' docstring still says it. Remedy: add it to G-D5's "Not checked:" sentence in FRAMEWORK §8.3. (b) §5.2's "floor on how many Read first links there are": file it as its own item or drop it.
- N2: §3.2 wording drift (verify-1's N4 still open): "is retired again / is confirmed by the operation" reads as automatic, and "made `live` by hand" omits `unspecified`. `docs/runbooks/manual-mode.md` § record retire / record confirm have the exact cases.
- N4: `docs/framework/RELEASE-NOTES.md` says "No rule changed" while listing one addition (the §6.12 release-notes rule and the upgrade procedure's first step). Could read "No existing rule changed; one added".

## Traps

- FRAMEWORK.md may carry no CE/DEC/US/AC/INV id (AC-33); put ids in RELEASE-NOTES.md, not the spec.
- A cut status marker comes back as a "Not checked:" sentence or a board item, never as build status (DEC-81).

## Read first

- `.scratch/ce-93/verify-2.md` (Nonblocking N1, N2, N4; gitignored, so the findings are restated above)
- FRAMEWORK §3.2, §5.2, §8.3 G-D5; `docs/framework/RELEASE-NOTES.md`; DEC-79, DEC-81

## Log

- 2026-10-30a (claude-code/claude-opus-5-5): closed: Done in dc11225 and 5b614a8 (lane 8b0562e, 1dd386b): FRAMEWORK §8.3 G-D5's Not checked sentence covers generated blocks inside a hand-written doc; §5.2's Read first gets a Not checked clause on how many links it holds (DEC-96); §3.2's retire and confirm wording says a hand edit is red (G-I2) until the operation is run on the right person's call, and names unspecified. RELEASE-NOTES reads 'No existing rule changed; one was added', and its header says an earlier version's notes are not rewritten.
