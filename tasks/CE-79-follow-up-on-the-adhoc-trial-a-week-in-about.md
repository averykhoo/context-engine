---
type: Task
id: CE-79
title: Follow up on the adhoc trial a week in (about 2026-10-21)
brief: "Due about 2026-10-21: score adhoc's sessions under the engine against CE-4, list engine errors, report keep/fix/stop"
pri: NOW
state: open
deps: []
source: session 2026-10-14d
created: 2026-10-14
moved: 2026-10-22b
updated: 2026-10-22b
goals: [G-6]
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
