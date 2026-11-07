---
type: Decision
id: DEC-195
title: ask raised refuses a question id ID_RE cannot read back, before any last_asked stamp (CE-152)
actor: agent (claude-sonnet-5-5)
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:73ddd705a61a5dcbddc7e96dd7012f328fe3b0ed185bbd9240645b165ae17023
---

The agent's call on CE-152, made while building it in session 2026-11-07e: `ask raised` refuses a question id that `ID_RE` cannot read back.

`Kind.id_re` accepts any prefix, but every reader of the `asked:` line uses `ID_RE.findall` (capital letters, a hyphen, digits), so an id such as `Ask-1` was written and then dropped out of every check unseen. `session tasks` already refuses the same shape for the `tasks:` line; `Engine.ask_raised` now mirrors it, in its first validation loop, so a refusal stamps no `last_asked` and writes nothing. The alternative, widening `ID_RE`, would change every reader. Cheap to undo: one check in `working.py::Engine.ask_raised`.
