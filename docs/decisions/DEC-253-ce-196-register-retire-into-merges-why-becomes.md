---
type: Decision
id: DEC-253
title: 'CE-196: register retire --into merges: why becomes `merged into <id>[, <why>]`; the live target gains, or extends, one `merged:` line'
actor: claude-code/claude-opus-5-5
tasks: [CE-196]
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:8738f5ad13dcb0985761b3dd91b651ceaab992e0f1a301a41a9b4ced4e24c39b
---

A build-time call for CE-196, the agent's own, PROVISIONAL until the owner reviews it.

`register retire <id> --into <target>` merges one entry into another. The retired entry's reason becomes `merged into <target>`, followed by `, <why>` when a why is given. The target must exist and must still be live, and it gains one `- **merged:** <id> folded into this entry, session <session>` line. A later merge into the same target extends that one line with `; <id> folded into this entry, session <session>` instead of adding a second line. This is the hand form INV-89 and INV-90 were given on 2026-11-06c.
