---
type: Decision
id: DEC-313
title: 'Hazard label match: case-insensitive and stripped for the refusal; task list --label stays exact-case'
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:2e8232a264a99b6bc752a4674d13989763529b1cc069e9df8476644d97e3e2ea
---

**Decision:** For the close refusal, the `hazard` label matches case-insensitively and stripped (`Hazard`, ` hazard ` count; `hazards` does not). `task list --label` stays an exact match, unchanged.

**Why:** a false negative closes a hazard blind, while a false positive costs one `--residual none`. Changing `task list --label` is out of scope for CE-29.

**Rejected:** exact-case matching for the refusal; a `[working] hazard_label` config key (no repo needs another word, and FRAMEWORK names the word).
