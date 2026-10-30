---
type: Decision
id: DEC-103
title: "A question's parts are read mechanically: a 5-word recommendation, two options, a Context part"
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:25a9319c5414eb057605c56c711352fba383442205691715c229c027c5a645ec
---

The agent's call on CE-44, made while building it in session 2026-10-30a: how DEC-34's question parts are read mechanically.

- "A recommendation with reasoning" is at least `RECOMMENDATION_MIN_WORDS` = 5 words (guards.py, provenance JUDGEMENT), or `none` naming cost or judgement (the two exemptions in DEC-34's amendment).
- "Several options" is two or more list items or `###` headings under Options.
- Context is read from a `Context` or `Background` part.

Options: (a) these mechanical readings; (b) leave the shape to review, with no write-time refusal.

Chose (a): DEC-34 asks for a refusal, which needs a mechanical reading. Known edges (verifier, 2026-10-31): an indented sub-bullet counts as an option, bold-label options count as none, and `none cheap: <why>` from the old template is refused.

Built in lane commit 143bb4b, on main as 10f8717 (guards.py::ask_parts, guards.py::ask_problems). Cheap to undo: constants and regexes in guards.py.
