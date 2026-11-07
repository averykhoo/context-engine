---
type: Decision
id: DEC-219
title: "Explicit '' stays the off switch: gate_receipt = '' turns the check off and an absent key means the default; no separate None sentinel"
tasks: [CE-192]
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:9a92f6be356c2060ebc598dbc8495374efa809eaae200bfe9f6899968e044a82
---

The agent's call on CE-192: how a repo turns the guards-receipt check off once it is on by default.

An explicit `gate_receipt = ''` under `[working]` turns the check off; an absent key means the engine's default (config.py::GATE_RECEIPT). config.py::from_dict already passes `''` through and compile-checks only a non-empty value, so it is unchanged. No separate `None` "unset" sentinel is added: `''` already means off and absence already means the default, so a sentinel would be a third state with nothing to say.

Cost to undo: cheap.
