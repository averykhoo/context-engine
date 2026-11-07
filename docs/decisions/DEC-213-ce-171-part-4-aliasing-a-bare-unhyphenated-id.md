---
type: Decision
id: DEC-213
title: 'CE-171 part 4 (aliasing a bare unhyphenated id such as D17 at import) is split into its own task: no pinned design, and it needs a CLI/MCP knob and kit wording'
actor: claude-code/claude-opus-5-5
tasks: [CE-171]
decision_status: PROVISIONAL
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:ad4850c124bc84b96834d730749681ae5a06ccb898ca6dcf38902b5bab878b5b
---

CE-171 part 4, aliasing a log's bare unhyphenated ids (the `D17` form, about 287 uses in intervals) at import when the kind's prefix equals the log's, is split into its own task and not built under CE-171.

Why: it has no pinned design. `decisions.py::plan_import` writes an alias only when an id changes (`if e.old != e.id`); aliasing an unchanged id in another spelling needs a knob on the CLI and the MCP tool (for instance `--alias-form '{prefix}{n}'`), a ruling on how that alias meets G-D2's alias rule, kit runbook and FRAMEWORK §11.4 wording, and a path for a log already imported (intervals is). Parts 1 to 3 of CE-171 are independent of it.
