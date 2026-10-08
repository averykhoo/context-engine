---
type: Decision
id: DEC-12
title: "FRAMEWORK P15: design for an agent that starts with no context"
actor: owner
decided: 2026-10-08
session: 2026-10-08b
decision_status: ACCEPTED
tags: [principles, spec]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-08T18:00:00+08:00 }
---

The owner asked whether the principle behind tiled, hash-keyed tests (US-10) was *"designing for
context clears? or designing for handoffs?"*. The agent answered that both are the same event,
a reader with no memory, and proposed naming it as a principle. Owner: *"yup so any agent that
starts with no context. okay make the edit for mne"*.

Added to `docs/framework/FRAMEWORK.md` as P15, with a row in the §13 v0.4 → v0.5 table. The
spec stays v0.5; P15 names a principle the existing design already followed (P4, P5, P9, P10,
P12, `orient()`, batons, G-V1) and changes no mechanism.

## Amendments
