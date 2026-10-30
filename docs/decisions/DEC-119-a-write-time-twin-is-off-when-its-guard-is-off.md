---
type: Decision
id: DEC-119
title: A write-time twin is off when its guard is off
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:0bdaceeb346f8b224c90dd80fe4b9a04f8836174f20b8d905ba3db22c8e67d8e
tasks: [CE-42]
code: [src/context_engine/working.py::Engine._criterion_checks]
---

A write-time twin is off when its guard is off (CE-42): with `[guards] tests` unset, `tested` and `manual` are allowed and the reply says 'claim not checked'; with `[guards] stories` unset, a source only needs to name an id.

Options were refuse, or allow and say so. Picked allow-and-say because CE-25's own control says an unset path switches the guard off (design review P4 and D6).

Code: working.py::Engine._criterion_checks.
