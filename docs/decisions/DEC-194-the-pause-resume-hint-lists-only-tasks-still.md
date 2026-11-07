---
type: Decision
id: DEC-194
title: The pause resume hint lists only tasks still open and not yet named by the resuming session (CE-152)
actor: agent (claude-sonnet-5-5)
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:917739e07fe17ce92007b84ec3946f4a8487082c03d944573bc2f8d3236ef34d
---

The agent's call on CE-152, made while building it in session 2026-11-07e: which tasks the `pause resume` reply lists.

It lists the paused session's `tasks:` ids that are not already on the resuming session's own `tasks:` line and whose board state is not `closed`. An id with no record (`missing`) stays listed, so that `session tasks` then refuses it loudly instead of the loss being silent. A resuming session that is the paused session, a paused session with no ledger entry, and a paused session with no `tasks:` line each get the plain reply. Cheap to undo: the filter in `working.py::Engine.pause_resume`.
