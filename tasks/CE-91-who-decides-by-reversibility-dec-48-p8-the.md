---
type: Task
id: CE-91
title: 'Who decides by reversibility (DEC-48): P8, the contract and the owner-question rules'
brief: "Kit and FRAMEWORK edit: wait for the CE-7 hold or the owner's word; an undo that is cheap in time and tokens is the test"
pri: LATER
state: closed
deps: []
source: session 2026-10-15c
created: 2026-10-15
moved: 2026-10-20b
updated: 2026-10-20b
status: deprecated
closed: 2026-10-20b
---

DEC-48 (owner): a call that can easily be undone, without wasting much time or tokens, is the agent's (opus, or fable where DEC-18 allows it).

To carry it:
- **FRAMEWORK P8 "who decides".** Add reversibility as the first test, before the type of decision. Define "cheap to undo": a local commit or a record write reverts with git; a push, a release, a published tag, deleting untracked files, owner words and anything outside the repo do not.
- **§5.3 owner questions.** A question whose recommendation is reversible becomes an agent decision (with the recommendation), not an ASK row. It might go out as PROVISIONAL, with the digest flagging it so the owner can push back.
- **The kit contract and procedures § Intake step 4**, with their by-hand wording.
- **Check the fit with existing rules.** Push and release stay owner-gated (they are not reversible). Owner words are never the agent's to decide.

Do it with CE-83, which edits the same rule text (P8 and P11, §6.6).

## Traps
- Kit edits are on hold while CE-7 waits (banner 2026-10-15b) unless the owner says otherwise.
- AC-33 checks that the kit contract carries §6.6 text verbatim: change both together.

## Read first
- docs/decisions/DEC-48-who-decides-is-set-by-reversibility-a-call-that.md
- docs/framework/FRAMEWORK.md P8, §5.3

## Log

- 2026-10-15e (claude-code/claude-opus-5-5): DEC-50 (owner, 2026-10-15e): not released on its own; it is decided together with CE-83 when the owner rules on that kit edit.
- 2026-10-20b (claude-code/claude-opus-5-5): closed: done in 5e7d887 (rule text in 17470c8, by-hand wording in 6d6983e)
