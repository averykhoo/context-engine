---
type: Decision
id: DEC-282
title: 'CE-126: no `Lane:` commit trailer'
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:13cf6b252df06ca7a1d6628255635b5b7f4ba20e4b8df34a3d30e39c82ed090d
---

The agent's call on CE-126, building DEC-84's option B in session 2026-11-07e: no `Lane:` commit trailer.

A lane's commit carries the same trailer paragraph as any commit (`Session:` and `Co-Authored-By:`); the lane shows only in the reply and in the message's "Also carries ... left uncommitted by session(s) <key> lane <lane>" paragraph when another lane's lines ride along. Foreign-commit reconciliation reads `Session:`, and a lane is inside a session, so nothing needs a lane trailer; adding one would add parse rules nothing asked for.

Cheap to undo: a trailer could be added later without changing any op line.
