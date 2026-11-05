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
updated: 2026-11-05a
---

Delete the CE-167 rehearsal clones (Recycle Bin over its cap) and, later, the zanzibar backup.

## Traps

- none yet

## Read first

- none yet

## Log

- 2026-11-04a (claude-code/claude-opus-5-5): From DEC-156 (owner, 2026-11-04a: "34 okay can you do that or make it a task"). C:/Users/user/ce167-rehearsal is 9.47 GB (180517 files); the C: Recycle Bin already holds 67.44 GB against a 48 GB cap, so SendToRecycleBin would silently delete permanently: not done. Owner picks: empty the bin, raise its cap, or approve a permanent delete. The clones are reproducible (bundle + import script in the backup), and their 7 live and 10 r3 gate logs were copied 2026-11-04a into zanzibar's .gate-runs and the backup's gate-logs/. The worktree is already removed. The backup C:/Users/user/zanzibar-backup-2026-11-03 goes after zanzibar's next engine session runs clean; .scratch/ce-167 (reports, tools) goes with it.
- 2026-11-05a (claude-code/claude-opus-5-5): Owner, 2026-11-05a: "okay i cleared the recycle bin, try again"
