---
type: Decision
id: DEC-136
title: "Tier-0 housekeeping: the session runs hk run start/close; the hook only shows orient's owed line; the gate only checks"
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-11-01
session: 2026-11-01b
body_sha: sha256:9a598922b8a4fe17277bc58ec8e1ed5ede476873427f8b191330f742e177d741
---

Agent's call (CE-6 close-out, planned 2026-11-01b by a planner, attacked by a critic, revised; plan in the session's scratch, conclusions here). Who runs tier-0 housekeeping, and when:

- The session runs `hk run start` after `session start`, and `hk run close` before `session close`.
- The SessionStart hook runs no writes: it prints orient, which shows a keyless "Housekeeping owed" line when there is any.
- The gate only checks, through lint (G-W3, G-W9, G-W11, G-D6), and never writes.
- `session start` does not run housekeeping by itself. Making it do so is a cheap flip, left for later.
- `hk run` uses the hk_ actor rule: the caller's actor, else `process:housekeep`.
- The G-W10 cap, `[housekeeping] max_writes`, is off by default.

Options weighed: (a) the hook runs housekeeping at startup: refused, because the hook has no session key and a failing hook is silent; (b) the gate runs it: refused, because a gate that writes is no longer a check; (c) the session runs it at the two procedure points, with orient's owed line as the prompt: chosen. It is cheap to undo: one procedure step and one orient line.

Links: CE-6, US-3, FRAMEWORK §6.1, §6.11, §8.0.2, G-W10.
