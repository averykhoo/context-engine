---
type: Decision
id: DEC-246
title: 'CE-188: the rerank skips HOLD by procedure (step 1 reads no HOLD item, step 2 checks no move touches one); an item enters HOLD with a task comment naming what releases it: rejected an engine-side rerank list, there is no rerank op to make it mechanical (refs DEC-162)'
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:6d78ad0029cc728c5fd577eaafa1985995ed41c8ed357a17c2babaa0f0339157
---

Ruled at build time under DEC-162.

The rerank skips HOLD by procedure (procedures.md § Rerank and FRAMEWORK §6.14): step 1's ranking agent reads every open item not at HOLD, and step 2's verifier also checks that no move touches a HOLD item. An item enters HOLD with a `task comment` naming what releases it, and leaves by `task promote` when that happens or the owner says so.

Rejected: an engine-side rerank list that leaves HOLD out mechanically. There is no rerank operation in the engine to make it mechanical (the rerank is agent judgement over `task list` and `task show`), and orient's "rerank due" already leaves held tasks out.
