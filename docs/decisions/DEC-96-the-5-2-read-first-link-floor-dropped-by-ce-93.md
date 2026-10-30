---
type: Decision
id: DEC-96
title: The §5.2 Read-first link floor dropped by CE-93 returns as a Not checked clause, not as a board item
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:c3c091c24aa750e925d608e96aceabfb533dbdf5fb5374600578f701906b159f
---

The agent's call on CE-140, made while building it in session 2026-10-30a: what becomes of the FRAMEWORK §5.2 floor on a task's `## Read first` links, which CE-93's cut dropped.

Options:
(a) file a board item to build a floor on the number of Read first links;
(b) drop it silently;
(c) restate it as a "Not checked:" clause, per DEC-81's pattern.

Chose (c). Nothing checks how many links a task's `## Read first` holds (the task body template writes `- none yet`), and a Not checked clause stops the spec claiming a check that does not exist. Filing a floor stays possible if anyone wants one.

Built in lane commit 8b0562e, on main as dc11225 (wording fixed in 5b614a8). Cheap to undo: file the floor as a task.
