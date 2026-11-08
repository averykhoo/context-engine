---
type: Decision
id: DEC-296
title: "Gate parts schema: [gate.parts.<name>] = command + required scope, run in declared order; exclusive with top-level `command` and with any scope's `readers`; part names `all` and `readers` reserved"
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:45f2d7ec0e04ec2d8af007c8878ac688eea8aa0e21a517b862417e9447d8452e
---

CE-181 (a): a gate too long for one command, such as zanzibar's ten phases (about 2.75 h), is
declared as parts. `[gate.parts.<name>]` holds `command` (a non-empty list of words, `{python}`
substituted as in the top-level command) and `scope` (required, a declared scope: the files the
part reads). Parts run in the order they are declared. A `[gate]` with parts has no top-level
`command`, and no scope may name `readers` beside them: either would be a second way to say one
thing, and it would be ambiguous which command the readers are appended to (a part keyed on a
wider scope does the readers' job). The part names `all` and `readers` are reserved, since a
single-command run already writes them as its row's `part`, so a part's row never collides with
one. Builds FRAMEWORK §8.5 G-V1's "a long suite may be split into parts, each keyed on its own
inputs" (gate.py::Part, gate.py::from_dict).
