---
type: Task
id: CE-79
title: Follow up on the adhoc trial a week in (about 2026-10-21)
brief: "Due about 2026-10-21: score adhoc's sessions under the engine against CE-4, list engine errors, report keep/fix/stop"
pri: NOW
state: closed
deps: []
source: session 2026-10-14d
created: 2026-10-14
moved: 2026-10-26c
updated: 2026-10-26c
goals: [G-6]
status: deprecated
closed: 2026-10-26c
---

Owner, 2026-10-14d, verbatim: "make a new task to follow up in about a week to see how the trial is going."

Due on or about **2026-10-21**, a week after CE-7's cutover started (2026-10-14d).

## What to check

- How many sessions have run in adhoc under the engine since the cutover, and whether each opened and closed through it (adhoc's ledger and op log).
- Score those sessions against the CE-4 baseline (`docs/evidence/adhoc-baseline-2026-10-11.md`): start and close cost, and what was forgotten or done by hand.
- Engine errors, refusals and by-hand fallbacks seen in adhoc: each one becomes a row here.
- INV-31's live probes: did orient appear on startup, resume, /clear and compaction.
- Whether adhoc's pinned engine env (DEC-41) needs an upgrade, and whether the worktree branch is ready for the owner's merge decision.
- Report to the owner in a few lines: keep going, fix first, or stop.

## Log

- 2026-10-14f (claude-code/claude-opus-5-5): 2026-10-14f: the trial has started (owner: "okay its running now"); the first real session in adhoc is running. Check back about 2026-10-21.
- 2026-10-21b (claude-code/claude-opus-5-5): 2026-10-21b: CE-7 closed (scored, f022af4). Left here: the INV-31 live probes (resume, /clear, compaction) in adhoc, which need the owner; the re-pin off 38ed38e after CE-124, CE-104, CE-63, CE-125; adhoc's 3 dropped owed items (INV-31 probes, 19a .scratch inventory, 16b AD-17 -187 dB outlier) belong on adhoc's board.
- 2026-10-21c (claude-code/claude-opus-5-5): 2026-10-21c: adhoc start-cost cleanup done (owner-approved), adhoc commits ebfdbe9, f3898c5, 09ae685, 273b183 (local, not pushed): CLAUDE.md no longer says read HANDOFF in full; HANDOFF banner-only (7,847 -> 1,254 B), banner 4.2 KB -> 884 B, orient 5,402 -> 2,095 B; durable content moved to adhoc docs/facts.md and docs/methods.md; AD-28 (-187 dB outlier), AD-29 (.scratch inventory, 32 GB) filed. Verified line by line by a second agent: nothing lost. Still for the re-pin: drop adhoc CLAUDE.md's coordinator section (917 B), now in the kit contract. Open in adhoc: DEC-75 pyannote SpeechSeparation check (AD-2) has no row; .scratch 32 GB sweep is AD-29.
- 2026-10-22b (claude-code/claude-opus-5-5): 2026-10-22b: fix-first CE-104/125/63/124 done (fec65a7). Re-pin of adhoc-microphone-array STOPPED half-done: env reinstalled in place to 9f0e8ca (package only), kit contract + 6 runbooks still 38ed38e's, nothing committed, tree clean; stopped because an idle adhoc Claude Code conversation (since 2026-10-21) still runs an MCP server from that env. Waits on ASK-19 (finish vs roll back) and ASK-20 (coordinator line). Checklist: .scratch/ce-79-repin/repin.md.
- 2026-10-23c (claude-code/claude-opus-5-5): 2026-10-23c: re-pin still blocked after the owner paused adhoc: python PID 22024 (adhoc .context-engine/env, context_engine.mcp, started 2026-10-21) still runs under claude.exe PID 1744 (remote session cse_01TkdBP39oNY5iDa4fja5ERj); pausing did not stop it. Env confirmed at 9f0e8ca. ASK-20 answered by DEC-71: drop coordinator section after recording the owner's 2026-10-17 words as an adhoc decision. Report: .scratch/ce-79-repin/finish-2026-10-23c.md
- 2026-10-23c (claude-code/claude-opus-5-5): 2026-10-23c: adhoc re-pin to 9f0e8ca DONE after the owner killed PID 22024: adhoc e939727 (5 kit runbooks; contract.md already current via e78beac), 687a7ad (banner set, cured G-W1 left by adhoc 2026-10-23b), e9f67cb (adhoc session close); adhoc gate green (pytest 826 passed, lint clean); verified by a second agent (byte-equal, LF, env at 9f0e8ca). Local only, not pushed. Left: push (owner); record the owner's 2026-10-17 coordinator words as an adhoc decision, then drop adhoc CLAUDE.md's coordinator section (DEC-71); INV-31 probes (owner).
- 2026-10-23e (claude-code/claude-opus-5-5): 2026-10-23e: DEC-71 step done in adhoc: owner's 2026-10-17 coordinator words recorded as adhoc DEC-95 (byte-identical quote), coordinator section dropped from adhoc CLAUDE.md (9cdaaf9; contract covers both halves), adhoc pytest 826 passed, lint clean; commits 4831738, c310fef, 9cdaaf9, a35613a local, not pushed. Verified by a second agent (.scratch/ce-79-dec71/verifier.md). Owner answered ASK-16 in a live adhoc session (adhoc DEC-96, e98d25c). Left: INV-31 live probes (owner); adhoc push (owner).
- 2026-10-23f (claude-code/claude-opus-5-5): Owner, 2026-10-23f (DEC-72): finish CE-79 through ultracode in the background. Workflow wf_1c58e4ae-336 running: INV-31 probe from adhoc transcripts + independent verify, adhoc push readiness (.scratch/ce-79-final/). Adhoc push itself asked of the owner.
- 2026-10-23f (claude-code/claude-opus-5-5): 2026-10-23f: INV-31 probe done and verified (a42a66d, docs/evidence/inv31-adhoc-probe-2026-10-23.md): startup, resume (n=1), /clear SEEN; compaction never occurred (needs a manual /compact in adhoc, owner). Adhoc push READY (10 ahead, gate green with the live session's WIP in tree, no CI); held for the owner's word. Left: /compact probe and adhoc push, both owner's.
- 2026-10-26a (claude-code/claude-opus-5-5): 2026-10-26a: INV-31 compaction probe: owner ran /compact in adhoc; transcript 64c998d9 L658 compact_boundary 2026-10-23T17:55:13Z, L673 hook_success SessionStart:compact 17:55:14Z, exit 0, empty stderr, 4474 B orient (banner 2026-10-23f) injected. Hook half SEEN. Agent half (keeps its key, no second session start) not yet observable: no turn after the compaction. Left: adhoc push (owner).
- 2026-10-26c (claude-code/claude-opus-5-5): 2026-10-26c: report to owner: KEEP GOING. Trial scored under CE-7 (f022af4); engine fixes from it landed (CE-104/125/63/124, fec65a7); adhoc re-pinned to 9f0e8ca, start cost cut (orient 5,402 -> 2,095 B); INV-31 hook seen on startup, resume, /clear, compaction. Adhoc push done: adhoc origin/main at 4488738 by push (reflog), checked by fetch 2026-10-26c. Owner (MCQ, 2026-10-26c): close CE-79, file the unobserved agent half as a follow-up.
- 2026-10-26c (claude-code/claude-opus-5-5): closed: trial reviewed: keep going; adhoc pushed through 4488738; INV-31 agent half split to a follow-up task
