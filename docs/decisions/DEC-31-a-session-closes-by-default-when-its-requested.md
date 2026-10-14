---
type: Decision
id: DEC-31
title: A session closes by default when its requested work is done
actor: owner
decision_status: PROVISIONAL
decided: 2026-10-13
session: 2026-10-13a
body_sha: sha256:831f4d819a676724f5d3c391a827c162c2d71873321cef05fbda2a83b361be36
---

Owner, 2026-10-13a, after the session's requested work (CE-30, CE-31, CE-32, CE-35, CE-36, the re-rank) was done and the session was left open with "Session close: not done yet, since you may want to keep going":

"Close the session, and add a rule to close by default when the work is done"

## Amendments

- **2026-10-14f (claude-code/claude-opus-5-5):** Owner, 2026-10-14f, verbatim: "update the instructions in the framework to eagerly close as soon as all tasks are done, it keeps holding the session open and waiting for instructions". The rule moves into the always-loaded contract (kit contract.md) and is sharpened in procedures.md and FRAMEWORK §6.3: close in the same turn the last task finishes, before the final reply, never ask whether to close (CE-82).
