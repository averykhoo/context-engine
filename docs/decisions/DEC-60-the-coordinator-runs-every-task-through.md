---
type: Decision
id: DEC-60
title: The coordinator runs every task through ultracode subagents, even a single task, and is the default whenever the board is worked
actor: owner
decision_status: PROVISIONAL
decided: 2026-10-19
session: 2026-10-19a
body_sha: sha256:160512b596e99d307295ed5413d5ffede028ec69fc01067e6bb65b3c299179e5
---

Owner, 2026-10-19a, verbatim:

"help me add this note about the coordinating agent: \"you should be coordinating subagents in ultracode to get each task done, even if there is only one task, don't do the task yourself\" and i think we might want to default to the coordinating agent whenever we work with the board. also the subagents should be writing to some file in case the session dies, which it did last weekend when windows decided to die on me"

Context: extends DEC-44 (the top-level session coordinates) and DEC-16 (one subagent per task, several tasks). Three parts: (1) every task, even a lone one, goes to subagents through ultracode (the Workflow tool), never done by the coordinator itself; (2) working the board puts the session in the coordinator role by default; (3) every subagent persists its output to a file as it goes, so a dead session loses nothing. Incident for (3) (DEC-47): the owner's Windows machine crashed the weekend of 2026-10-17/18 and killed a session. Part (3) is already in fan-out.md § Delegating reading and auditing ("Persist incrementally, one file per agent"); parts (1) and (2) join CE-83's rewrite.
