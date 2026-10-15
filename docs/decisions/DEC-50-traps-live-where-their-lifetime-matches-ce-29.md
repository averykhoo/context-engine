---
type: Decision
id: DEC-50
title: Traps live where their lifetime matches (CE-29); CE-92 is released from the CE-7 hold, CE-93 stays held
actor: owner
decision_status: PROVISIONAL
decided: 2026-10-15
session: 2026-10-15e
body_sha: sha256:165954e4f4c8df96e238a245b2735f766df2f811620dff8a46dc095467eeedd5
---

Owner, 2026-10-15e, verbatim:

"1 - okay with your suggestion
2 - okay as well
3 - yup okay

And ignore the data plugin
Okay logged in.

Like I said I'm okay with all 3"

Context: the agent put three items to the owner in chat, each with a recommendation. These words
accept all three recommendations:

1. **CE-29, where a trap lives: by its lifetime.** A known trap that holds only while one task is
   open goes in that task's `## Traps`. A suspected, unconfirmed hazard ("do NOT fix blind") goes on
   the board as a row labelled hazard, which gives it an id, a tier and staleness, and a close that
   resolves it into a register entry, a fix or a dismissal. A confirmed, durable hazard that
   outlives any task goes in the register as an INV-n. The banner is not a home for traps: every
   close overwrites it. A trap in CLAUDE.md is a register entry or a runbook trap, plus a pointer.
   This settles the recommendation in CE-29's log (2026-10-15c). Writing it into FRAMEWORK is a
   spec edit and stays under the CE-7 hold.
2. **The CE-7 hold on framework and kit edits** (2026-10-14c): lifted for CE-92 (close step 7 runs
   lint and `gate status` instead of a second full gate), which is small and self-contained. CE-93
   (archive and rewrite FRAMEWORK.md) stays held until the trial's feedback is in (CE-79, about
   2026-10-21), so the text is not rewritten twice. CE-91 is not lifted on its own: it edits the
   same rule text as CE-83, and the two are decided together when the owner rules on CE-83.
3. **The `close-without-asking` auto-memory is deleted:** DEC-31 is already in CLAUDE.md § Rules.
   `multi-task-delegation` stays until CE-83 puts DEC-44 into rule text.
