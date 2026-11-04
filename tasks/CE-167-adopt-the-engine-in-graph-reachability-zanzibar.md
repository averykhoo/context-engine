---
type: Task
id: CE-167
title: Adopt the engine in graph-reachability-zanzibar-index, after intervals (CE-11)
brief: Not before CE-11 (DEC-134); never push, tag or release zanzibar without the owner's word
pri: NOW
state: closed
deps: [CE-11]
goals: [G-6]
source: session 2026-11-01a
created: 2026-11-01
moved: 2026-11-04a
updated: 2026-11-04a
status: deprecated
closed: 2026-11-04a
---

Adopt the engine in graph-reachability-zanzibar-index, after intervals (CE-11)

Owner, 2026-11-01a (DEC-134): zanzibar gets its own task, and intervals goes first. zanzibar runs its own board tooling (`scripts/task.py`, `tasks/closed/`) until this lands. Model the work on CE-43: survey the repo (HANDOFF, decision log, board shape, concurrent sessions, its PyPI release flow) before planning the import; back it up first; rehearse the import on a clone; check the import loses no lines; and fold in audio-workspace's open feedback (its `docs/context-engine-feedback.md` item 1: setup also registers the MCP server).

## Traps

- Never push zanzibar, nor tag or release it, without the owner's word: tags there trigger a PyPI release.

## Read first

- CE-43's log (how the audio-workspace cutover went), CE-11, DEC-6, DEC-134

## Log

- 2026-11-03b (claude-code/claude-opus-5-5): Owner, 2026-11-03b: "Let's do the Zanzibar adoption task" (answering the 2026-11-03a banner's ask: promote CE-167 and start it). Promoted LATER->NOW.
- 2026-11-03b (claude-code/claude-opus-5-5): Session 2026-11-03b: local cutover done and verified. zanzibar branch ce-cutover (worktree C:/Users/user/PycharmProjects/zanzibar-ce-cutover, head 3e63fd7, 7 commits on master 4826a01), engine pin 309641b; 303 board records and 9 decision sections conserved byte-equal (checkers sabotaged); zanzibar's full ten-phase gate green and engine lint clean on 3e63fd7; independent verifier 8/8 PASS. Backup C:/Users/user/zanzibar-backup-2026-11-03 (bundle verified). Nothing pushed, tagged or merged. Waits on the owner: merge-and-push and the design confirmations. Findings: CE-177..CE-181, comments on CE-172, CE-174, CE-56. Evidence: docs/evidence/ce167-zanzibar-cutover-2026-11-03.md
- 2026-11-04a (claude-code/claude-opus-5-5): 5e36527: CE-167: zanzibar cutover built and verified on a local branch; findings and owner questions filed
- 2026-11-04a (claude-code/claude-opus-5-5): Session 2026-11-04a, on the owner's go (DEC-151, ASK-35 confirmed DEC-150): zanzibar master fast-forwarded 4826a01 -> 3e63fd7 (no merge commit), main checkout bootstrapped (own .context-engine/env at 309641b, SessionStart hook merged); pre-push verifier PASS; pushed b743587..3e63fd7 (master only; remote tags unchanged, 16 lines); CI green: gate 41817387647 (10 jobs), docs 41817387643. Post-merge: worktree removed, ce-cutover deleted; zanzibar session 2026-11-04a recorded DEC-13 (coordinator rule, ASK-32 / DEC-154 here), DEC-14 + TK-301 (CI lint job, DEC-152), DEC-15 + TK-302 (charter, DEC-153), CLAUDE.md Delegation edited; its gate COVERED, lint clean; 12 commits local, unpushed (owner's word). Post verifier PASS but for the rehearsal clones (CE-182).
- 2026-11-04a (claude-code/claude-opus-5-5): closed: zanzibar adopted: master fast-forwarded to 3e63fd7 and pushed (b743587..3e63fd7, no tag) on the owner's go (DEC-151); CI green (gate 41817387647, docs 41817387643); pre- and post-push verifiers PASS; zanzibar's own records refreshed in its session 2026-11-04a (12 commits, local)
  residual risk: INV-94
