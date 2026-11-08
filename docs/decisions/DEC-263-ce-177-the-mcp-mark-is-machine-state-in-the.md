---
type: Decision
id: DEC-263
title: 'CE-177: the MCP mark is machine state in the gitignored lock dir: not op-logged, not committed, a write failure swallowed'
tasks: [CE-177]
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:88b9e74846a743903c3ebf7a66a521f4803fd704388a0b56f1d1bf536f17da16
---

A build-time call for CE-177, the agent's own, PROVISIONAL until the owner reviews it.

The MCP mark is machine state under the gitignored lock directory (`Store.private_dir`): it is not op-logged and not committed, and a failure to write it is swallowed, so it never fails a tool call. A lockfile at the repo root has no private directory, so no mark is written and orient shows no notice there.
