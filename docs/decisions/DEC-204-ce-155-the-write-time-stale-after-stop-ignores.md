---
type: Decision
id: DEC-204
title: "CE-155: the write-time stale_after stop ignores liveness and mirrors lint's boundary: it refuses on a closed item too (a bad or past value is never useful and goes red on reopen), and only now > stale_after counts as expired, exactly as guards.py::stale reads it (an instant equal to now is taken)"
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:cd502694e38d2e72e306c98e5b59a5459e8238a3403aa0d5a23eb36c1f4f5703
---

The write-time `stale_after` stop (working.py::Engine._stale_after_check) reads only the key being written and ignores the record's liveness: it refuses on a closed task or a deprecated record too. A bad or already-passed value is never useful there, and it goes red under G-D4 the moment the item is reopened; mirroring lint's liveness filter would need the post-change state inside the locked write callback for no gain.

It mirrors lint's boundary exactly: only `now > stale_after` counts as expired, as guards.py::stale reads it, so an instant equal to the engine's clock is taken. A `<=` boundary would make the write stop and lint disagree at that one instant. `--unset stale_after` is always allowed.
