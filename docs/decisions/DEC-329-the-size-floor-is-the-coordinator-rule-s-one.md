---
type: Decision
id: DEC-329
title: The size floor is the coordinator rule's one exception in FRAMEWORK §6.6 and P11; the kit contract line waits for the next contract version bump (CE-228)
tasks: [CE-219, CE-228]
actor: claude-code/claude-opus-5-5
decided: 2026-11-11
session: 2026-11-11a
decision_status: PROVISIONAL
body_sha: sha256:71c82896e4216887e825d1945dbfbc194d82f366d81377fda5e9b69a9ced0109
---

**Decision:** The size floor is the coordinator rule's one exception, stated in FRAMEWORK §6.6 (the new size floor paragraph, which says a repo takes the floor up by naming it in its own contract, so narrowing the coordinator rule) and in FRAMEWORK §1 P11. The kit contract and FRAMEWORK §6.6's coordinator paragraph, which the contract carries verbatim (AC-33), are not changed in CE-219: that line waits for the next contract version bump, filed as CE-228 (LATER, beside CE-207). This repo's CLAUDE.md names the floor, and narrows the contract meanwhile.

**Why this differs from the plan's call:** the planner proposed editing the coordinator bullet in FRAMEWORK §6.6 and the kit contract, riding 0.6's "copy the new contract in" upgrade step, with a 0.6 release note. The builder's dispatch forbids any contract change in this task, and DEC-310 already ruled the same way for P19's line: 0.6's contract bump is done, and editing `src/context_engine/kit/contract.md` now, without a version bump, turns G-D0 red in every adopting repo on the editable install. FRAMEWORK carries the rule meanwhile, which every session can read; the 0.6 release note says the contract is unchanged and how a repo adopts the floor.

**Rejected:** editing the contract now (G-D0 red downstream, DEC-310); leaving FRAMEWORK silent until the bump (CLAUDE.md would then carry a rule FRAMEWORK contradicts, against DEC-19).

Planner's call for CE-219, session 2026-11-11a, amended by the CE-219 builder (claude-code/claude-opus-5-5) to hold the contract line.
