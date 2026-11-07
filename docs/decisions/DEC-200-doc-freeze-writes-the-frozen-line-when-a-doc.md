---
type: Decision
id: DEC-200
title: 'doc freeze writes the FROZEN line when a doc declares no liveness: by default, with no flag, since the refusal protected nothing and three adopters wrote the line by hand (CE-43, CE-11, CE-167)'
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:4b7a9844c21360a3ad045d3b896ab4ff1673c019c1b7217ff2e815f0632e2992
---

`context-engine doc freeze` on a doc that declares no liveness in G-D4's window now writes the FROZEN line itself instead of refusing. It is the default, with no flag. The refusal protected nothing: there was no declaration to overwrite, the write is logged as `doc.freeze` and git undoes it, and manual-mode.md already prescribed the same step by hand. Three adopters hit the refusal and wrote the line by hand (CE-43, CE-11, CE-167). Rejected: an opt-in flag such as `--add`, which keeps a step that guards nothing. The other refusals (already FROZEN, a frontmatter `liveness:` key, `[guards] liveness_given`, a declaration problem) are unchanged. CE-172.
