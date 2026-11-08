---
type: Decision
id: DEC-245
title: "CE-188: held means never ready: G-W5's NOW rule, the task close / session close empty-NOW warnings and orient's rerank due count only items not at HOLD; orient flags a NOW/NEXT item whose dep is held; promote into or out of HOLD is unrestricted: rejected owner-only release refusal, hiding HOLD rows from task list, a lint nag when the enum lacks HOLD (refs DEC-162)"
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:25dee8e6a1d54d0a5487b968557e74274401fe84c20bb2fe3f58ee208efd5ac1
refs: [DEC-162]
tasks: [CE-188]
code: [src/context_engine/working.py::Engine._now_short]
---

Ruled at build time under DEC-162.

An open task at HOLD is never ready. G-W5's NOW rule counts only open items not at HOLD (`src/context_engine/working.py::Engine._now_short`, through `::_unheld`), so a board whose only open items are held may leave NOW empty; the empty-NOW warnings of `task close`, `ask answer`, a demoting `promote` and `session close` follow, since they share `Engine._now_refill`. Orient's "rerank due" (`Engine.rerank_due`) leaves held tasks out of its count. Orient's parked-deps part (`Engine.parked_deps`) flags a NOW or NEXT item, or the banner's next, whose dep is open at HOLD, as `<dep>, which is HOLD (held)`. Promoting into or out of HOLD is unrestricted, and HOLD has no cap; `task promote <id> HOLD` where the task enum lacks HOLD is refused as any unknown tier is, with a remedy saying how to enable it.

Not changed: caps (`[working.caps]` can already name HOLD), `task list` (it sorts HOLD last from the enum's order and still shows held items), G-I1, orient's Top item and Board parts.

Rejected:
- Refusing a promote out of HOLD unless the owner gives it: a move is cheap to undo (P8), and an actor string does not prove the owner is present.
- Hiding HOLD rows from `task list`: hidden open items get lost, and the ranking agent reads the pri column.
- A lint or G-D0 nag when a repo's enum lacks HOLD: HOLD is optional and nothing is lost without it.
