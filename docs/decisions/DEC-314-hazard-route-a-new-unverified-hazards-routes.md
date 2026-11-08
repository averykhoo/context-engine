---
type: Decision
id: DEC-314
title: "Hazard route: a new 'Unverified hazards' [[routes]] entry on tasks in context.toml and kit/context.toml.template; no orient line and no task new --labels flag"
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:3885c17706cb0bf03056144657db8c05230ca1d826346a51e19fa51947f7a1ab
---

**Decision:** A new `Unverified hazards` `[[routes]]` entry on `tasks`, after "Tasks and owner questions", in this repo's context.toml and in kit/context.toml.template, with no caps. No orient line lists hazard rows, and `task new` gets no `--labels` flag (a hazard row is filed with `task new`, then `task set <id> --set labels=[hazard]`).

**Why:** the route makes the home visible in `context-engine routes`. A duplicate route path is safe (bootstrap.py::_uses is a set; G-D1 skips capless routes). An orient line would be new §5.1 behaviour DEC-50 does not ask for; `--labels` is CLI, MCP and kit churn to save one `task set`.

**Rejected:** an orient line for hazards; `task new --labels`.
