---
type: Decision
id: DEC-112
title: The decision_status/status agreement check is a clause of G-W4, not a new G-id
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:d1af8db4788ca0ae8a7ee2a24612821ae797b89016e00840b919530651c5190d
---

The agent's call on CE-137, made while building it in session 2026-10-30a.

Options:
(a) a clause of G-W4, which already compares a state key with the OKF `status` for board items;
(b) a new G-id;
(c) a clause of G-I3.

Chose (a). G-W4 is the guard for "the state key agrees with the derived status", and its "Not checked" already named decisions. A new id would need config LINT_IDS and the coverage map. G-I3 skips deprecated decisions, which is the very thing this check protects. The check lives in working.py::Engine._decision_status_failures, so `lint --working` runs it too.

Built in lane commits fd92d5d and 6d00948, on main as 0ec76ad and e528316. Cheap to undo: move the clause to its own id.
