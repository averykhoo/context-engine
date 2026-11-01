---
type: Decision
id: DEC-141
title: hk comment's no-key case is a caller key with no ledger entry, refused with the remedy --since <rev>
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-11-01
session: 2026-11-01b
body_sha: sha256:98e080129d9eddcd9b10f2e7c75f2d7fdbdd35d58b3ef4f41dd0ab36738e1fc1
---

The agent's call on CE-6, made while building `hk comment` in session 2026-11-01b: what the plan's "no key" case means for the scan.

Options:
(a) "no key" as the caller passing no session key at all;
(b) "no key" as the caller's key having no ledger entry, refused with the remedy `--since <rev>`.

Chose (b): the caller check always needs a key, so (a) cannot reach the scan. A key with no ledger entry is the case where the scan has no start point of its own, and `--since <rev>` gives it one.

Built in lane commit 3230363, on main as 92c56bc; pinned by AC-174. Cheap to undo: the refusal and its remedy.
