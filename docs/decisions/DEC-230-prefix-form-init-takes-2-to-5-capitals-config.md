---
type: Decision
id: DEC-230
title: 'Prefix form: init takes 2 to 5 capitals; config load refuses only a prefix that is not capital letters, so configs from the old kit (D, S, T) keep loading'
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
tasks: [CE-56]
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:e1cf40ca746e0f3f1f34ec103697b3e4e7c22f2ad2453cba5a6497690c192c36
---

For CE-56: FRAMEWORK P3 gives ids the form `[A-Z]+-[1-9][0-9]*` and DEC-38 gives prefixes 2 to 5 capitals, but bootstrap.py::PREFIX_RE took digits (its remedy even suggested T2) and config load checked no form at all.

The call: `init --prefix` takes 2 to 5 capitals only (bootstrap.py::PREFIX_RE). Config load (config.py::from_dict) refuses only a prefix that is not capital letters (config.py::PREFIX_FORM), with no length check, so a config written by the old kit (D, S, T) and every one-letter test fixture keep loading.

Options:
(a) 2 to 5 at init, capitals only at load: chosen;
(b) 2 to 5 at load or in lint: rejected, it bricks or reds every repo bootstrapped with the old kit;
(c) no check at load: rejected, a digit or a lower-case prefix makes ids outside P3's form that other guards cannot read.

Cost to undo: cheap (two regexes and their tests).
