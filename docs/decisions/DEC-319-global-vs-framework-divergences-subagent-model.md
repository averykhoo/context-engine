---
type: Decision
id: DEC-319
title: Global-vs-framework divergences (subagent model default, HANDOFF read in full, BROKEN repros and verification first-hand) are flagged in CE-40's doc, not resolved
tasks: [CE-40]
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:62c4ae7a8b069ce1a3da87023518e04a114cf87c7fbb560f775b741292a643cb
---

An agent's call under P8 (cheap to undo: a flag in a tracked doc), made by CE-40's builder in session 2026-11-07e on 2026-11-08, following the planner's design. Not owner words.

Where the owner's global `CLAUDE.md` and the framework say different things, CE-40's doc flags the difference and does not settle it:

- the subagent model default (global: `opus` by default; FRAMEWORK §6.6: the cheapest model that can do it, named by the repo's contract);
- reading HANDOFF.md in full at session start (global) against reading it only if needed after orient (procedures § Session start);
- re-running BROKEN install-trial repros, and verifying, first-hand (global) against a verifier agent that is not the trial agent (release.md § After the trial; contract § Rules, the coordinator).

In a framework repo the pointer section of the trimmed text defers to the repo's contract. The optional baseline for repos without the framework keeps the owner's current words. Each is an owner preference, and the pasted text applies machine-wide, so which one wins is the owner's call.
