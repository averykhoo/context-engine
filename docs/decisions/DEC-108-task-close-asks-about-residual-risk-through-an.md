---
type: Decision
id: DEC-108
title: task close asks about residual risk through an optional statement plus a reply nudge, not a mandatory flag
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:f4d043ff2990aa096a2146baa8af32fff71811fbaab7a303f662460e68a55ee2
---

The agent's call on CE-120, made while building it in session 2026-10-30a: how `task close` asks about residual risk.

Options:
(a) make `--residual` mandatory on every close where a register is configured;
(b) optional `--residual` (`none` or risk lines), logged on the item when given, with a reply that says 'residual risk not stated' when a register is configured and the item has no review, plus a clean-close procedure step that asks;
(c) only a procedure step.

Chose (b): it makes the record tell 'none' from 'skipped' (entry 33's complaint) without turning every existing close in every adopting repo into a refusal. (a) stays open if the owner wants it enforced.

Built in lane commit 1a89d74, on main as 750aff7; pinned by AC-127. Cheap to undo.
