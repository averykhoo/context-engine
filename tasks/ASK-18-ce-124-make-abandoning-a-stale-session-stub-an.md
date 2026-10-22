---
type: Question
id: ASK-18
title: 'CE-124: make abandoning a stale session stub an engine op, and does it need your word?'
brief: "Recommend: op, run by housekeeping past DEC-29's window, no owner word"
pri: NEXT
state: closed
deps: []
source: session 2026-10-22b
created: 2026-10-22
moved: 2026-10-22b
updated: 2026-10-22b
last_asked: 2026-10-22b
blocks: [CE-124]
status: deprecated
closed: 2026-10-22b
answered: {on: 2026-10-22, session: 2026-10-22b, decision: DEC-69}
---

Context: DEC-29 keeps abandoning a stale session stub as a by-hand ledger edit (stale = 3 later closes or pauses after its last activity). In the adhoc trial it was done by hand three times (AAR entries 3 and 25), and clean close does not retire a dead stub. CE-104, now being built, gives orient each open session's last activity, which is the evidence an op would need.

Options:
1. Add `session abandon <key>` as an engine op; start-of-session housekeeping runs it on any stub past DEC-29's window, and orient lists it in the digest. No owner word needed, since a stale stub has been shown to you at least 3 times by then (your words in DEC-29).
2. Add the op, but it runs only on the owner's word; orient flags stubs past the window and asks.
3. Keep DEC-29 as is: by hand, from the runbook.

Recommendation: option 1. It is cheap to undo (one ledger edit plus a baton, revertible by git), the window already resets on activity, and the hand edits are where the trial lost time and made mistakes. Option 2 adds a question each time for a call you said you would make anyway.

## Log

- 2026-10-22b (claude-code/claude-opus-5-5): answered by the owner: DEC-69
