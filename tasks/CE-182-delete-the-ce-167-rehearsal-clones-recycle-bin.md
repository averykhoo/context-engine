---
type: Task
id: CE-182
title: Delete the CE-167 rehearsal clones (Recycle Bin over its cap) and, later, the zanzibar backup
pri: LATER
state: open
deps: []
goals: [G-6]
source: session 2026-11-04a
created: 2026-11-04
moved: 2026-11-04a
updated: 2026-11-06b
---

Delete the CE-167 rehearsal clones (Recycle Bin over its cap) and, later, the zanzibar backup.

## Traps

- none yet

## Read first

- none yet

## Log

- 2026-11-04a (claude-code/claude-opus-5-5): From DEC-156 (owner, 2026-11-04a: "34 okay can you do that or make it a task"). C:/Users/user/ce167-rehearsal is 9.47 GB (180517 files); the C: Recycle Bin already holds 67.44 GB against a 48 GB cap, so SendToRecycleBin would silently delete permanently: not done. Owner picks: empty the bin, raise its cap, or approve a permanent delete. The clones are reproducible (bundle + import script in the backup), and their 7 live and 10 r3 gate logs were copied 2026-11-04a into zanzibar's .gate-runs and the backup's gate-logs/. The worktree is already removed. The backup C:/Users/user/zanzibar-backup-2026-11-03 goes after zanzibar's next engine session runs clean; .scratch/ce-167 (reports, tools) goes with it.
- 2026-11-05a (claude-code/claude-opus-5-5): Owner, 2026-11-05a: "okay i cleared the recycle bin, try again"
- 2026-11-05a (claude-code/claude-opus-5-5): 2026-11-05a: after the owner emptied the bin, C:/Users/user/ce167-rehearsal went to the Recycle Bin (180496 files, 9.48 GB; bin 0.017 -> 9.482 GB, so not a permanent delete). Left: 21 DLLs (5.7 MB) in r1/r2/r3 .context-engine/env, conda hardlinks loaded by live processes (in use); retry once those exit, or leave them. Report: .scratch/ce-167/merge/binner2.md. Backup stays until zanzibar's next clean engine session.
- 2026-11-06b (claude-code/claude-opus-5-5): 2026-11-06b, on DEC-161 (ASK-26): to the Recycle Bin (cap checked, +1.14 GB): ce11-rehearsal, intervals-ce-cutover worktree (branch ce-cutover pruned, = origin/master), intervals-backup bundle+untracked, zanzibar-backup bundle+untracked (condition met: zanzibar 2026-11-04a closed clean). Verified PASS by an independent agent. Left: 42 DLL hardlink names (0 bytes of their own) in ce11-rehearsal, ce167-rehearsal and intervals-ce-cutover, mapped by live MCP servers and hawker-bot: free on reboot, then rerun .scratch/2026-11-06b/probes/bin.ps1. Salvage kept (found nowhere tracked): intervals-backup-2026-11-02/salvage-2026-11-06b and zanzibar-backup-2026-11-03/{live-logs,gate-logs,ce-167-tools}, to transcribe into those repos' evidence before deleting. Not done: the .scratch/ce-167 audit; intervals HANDOFF.md still says the clones are on disk.
