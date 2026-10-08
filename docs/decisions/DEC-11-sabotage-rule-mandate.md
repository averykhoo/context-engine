---
type: Decision
id: DEC-11
title: "Sabotage rule is an owner mandate: no test or guard is believed until seen red"
actor: owner
decided: 2026-10-08
session: 2026-10-08b
decision_status: ACCEPTED
tags: [assurance, charter]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-08T17:30:00+08:00 }
---

Owner: *"also i want the test sabotage rule to be in there somewhere"* (said right after
confirming the charter, DEC-10).

Placed in three spots, so it is both stated and applied:

- `docs/charter.md § Owner mandates`: the rule, for this repo and for every guard the system
  ships to other repos.
- `CLAUDE.md § Sabotage rule`: the procedure here, with the record kept in the commit message
  (`Sabotage: <what was broken> -> <test> red`).
- `docs/criteria.md`: a criterion becomes `tested` only after its claiming test was sabotaged.

FRAMEWORK P7 already carried it; no spec change. The mechanical form is G-T5 (mutation per
criterion), part of CE-14.

## Amendments
