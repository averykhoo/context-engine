---
type: Decision
id: DEC-62
title: audio-workspace cutover goes today on a local branch; asks LATER; engine commits exempt; charter and stories as drafts
actor: owner
decision_status: PROVISIONAL
decided: 2026-10-19
session: 2026-10-19d
body_sha: sha256:d837d8a8d58cca6142db70166ca66d8f5d3ab1bd7d474e677a27cda3dd835461
---

Owner, 2026-10-19d, verbatim, the request and answers to the session's questions (AskUserQuestion, options chosen as given):

Request: "Migrate audio workspace to use this context framework, but don't push it." Then: "Wait another session is handling 98, you just do audio workspace".

- On CE-98 blocking the import: "Finish it first (Recommended)" (since done by session 2026-10-19e, a8879f9).
- On starting before Wednesday 2026-10-21: "Go today, no AW session" (the owner overrides the Wednesday start date and confirms no other audio-workspace session runs during the cutover; everything stays local, DEC-61).
- Where the live cutover commits go: "Local branch (Recommended)": the cutover goes on a local branch (ce-cutover), main stays as the demo (2026-10-20) expects; merge locally after the demo when the owner says; no push.
- The 41 imported asks: "All LATER, one digest (Recommended)".
- AW's AGENTS.md "commit only from the orchestrator after owner sign-off": "Exempt engine commits (Recommended)": the rule stays for code commits; the engine's own record commits are allowed.
- 17c's draft charter (G-1..G-7), 11 stories, and two normalisation calls (D-4's lone amendment becomes D-4's entry; 19 actorless headings get actor 'unrecorded'): "Drafts + keep calls (Recommended)": charter and stories import as drafts for one later confirmation; both calls kept, recorded in the evidence doc.
