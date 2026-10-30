---
type: Decision
id: DEC-126
title: record new's refusal of a preset status or SUPERSEDED on a decision is not behind G-W4's off switch
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:6391f43017272bc1db6fad2200e89334430756c289a3badf810c1ac7e84666ce
---

PROVISIONAL decision (actor claude-code/claude-opus-5-5), for CE-149. Relates to DEC-112.

**Options.**

- (a) Gate the refusal behind G-W4's off switch, as stories gate their twin behind G-I2. Rejected.
- (b) Make it unconditional, like `decision set`'s refusal of SUPERSEDED (`DECISION_OWNED`). **Chosen.**

**Why (b).** A decision's `status` key and `decision_status: SUPERSEDED` belong to `decision supersede`, which writes them together with both links. Refusing them in `record new` protects an operation's ownership; it does not enforce a lint rule, so no `[guards] off` entry should drop it. This also avoids the off-switch coupling that CE-148 had just documented. Pinned by AC-141.

**Cost to undo.** Cheap: add the G-W4 condition in `working.py::Engine.record_new`. Landed in cd6ab0e on the lane (c12d5af on main); the runbook was brought in line in 367016f (e1538eb on main).
