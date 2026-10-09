---
type: Decision
id: DEC-20
title: Every programmatic process has a ritual-based fallback (business continuity)
actor: owner
decision_status: PROVISIONAL
decided: 2026-10-09
session: 2026-10-09d
body_sha: sha256:a4014ec57e28c3cdde1899e4ecdabcfeff1a5989c86b9b892dbe039c626091df
---

The owner, 2026-10-09 (session 2026-10-09d), asking for a few notes to be added:

> framework.md should mention ritual based fallbacks for programmatic processes. think of it as a sort of business continuity

So: every programmatic process in the framework (an engine command, a guard, a housekeeping run, the MCP server) has a written, ritual-based fallback that a session can do by hand when the programme is unavailable or wrong, like business continuity planning. FRAMEWORK.md says so as a principle; `docs/runbooks/manual-mode.md` is the existing instance (US-11).
