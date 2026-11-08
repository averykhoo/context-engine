---
type: Decision
id: DEC-308
title: 'A hand-run check is verification, not a P17 control: P19 sends it to the board as an item to automate, never to the register as a residual (US-20)'
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:55459943d8ac22ac3f869ec9f422681d33c3f9f2ba806f74227f39c7399bad5b
---

**Decision:** a check only a human runs (a `manual` criterion's hand-run driver, a smoke script run by hand, a playtest) is verification, not a P17 control. P19 sends such a check to the board, as an item to automate it, and never to the residual-risk register (§7.4) as an accepted residual. A rule a reader must remember (P17's individual rung) is still a residual and still goes to the register.

**Why:** US-20: the owner wants a change made blindly, with no human playtest, to be shippable on a green gate alone. A hand-run check accepted as a residual would leave a part of the release decision outside the gate for good. A rule a reader must remember is a different thing: it guards how work is done, not whether a change is correct, so P17's ladder still applies to it.

**Rejected:** treating a hand-run check as an individual-rung control (it would be accepted as settled and never automated).

**Pinned by:** `tests/test_principles.py::test_p19_makes_a_green_gate_the_whole_release_decision` (CE-194, AC-184).
