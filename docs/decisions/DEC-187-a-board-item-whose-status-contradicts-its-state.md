---
type: Decision
id: DEC-187
title: A board item whose status contradicts its state is refused at create, never overwritten (CE-179)
actor: claude-code/claude-sonnet-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:1aba8db59ef7539924b479e92257bf580ee158d4aa79ae3534d070425de9af56
---

A board item whose `status` contradicts its `state` is refused at create and never overwritten: closed but not deprecated, or deprecated but not closed. It is G-W4's write-time twin, so there is no refusal when `[guards] off` names G-W4. Deriving the status when it is absent runs whatever `[guards] off` says. Silent overwrite was rejected: it loses the caller's data and hides an importer's bug.
