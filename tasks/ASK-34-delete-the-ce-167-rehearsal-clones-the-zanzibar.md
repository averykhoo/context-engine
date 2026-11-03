---
type: Question
id: ASK-34
title: Delete the CE-167 rehearsal clones, the zanzibar worktree, and when the backup?
brief: 'Recommend: bin rehearsal clones now; worktree and backup after merge and green CI'
pri: LATER
state: open
deps: []
source: session 2026-11-03b
created: 2026-11-04
moved: 2026-11-03b
updated: 2026-11-03b
last_asked: 2026-11-03b
---

## Context

CE-167 left on disk, outside every repo: C:/Users/user/ce167-rehearsal/ (rehearsal clones r1, r2, r2b-d, r3,
r3b-d and live/gate-b..d; r2 alone holds a 7.5 GB .lake build cache) and the verified backup
C:/Users/user/zanzibar-backup-2026-11-03/ (bundle, untracked files with sha256 sums, the import tools,
live-logs). The worktree C:/Users/user/PycharmProjects/zanzibar-ce-cutover holds the branch until it is merged.

## Options

- After the merge and a green CI: Recycle-Bin ce167-rehearsal/, remove the worktree, and keep the backup
  until the next zanzibar session has run cleanly on the engine.
- Keep everything for now.
- Delete the rehearsal clones now; keep the worktree and the backup.

## Recommendation

The third now (the clones are reproducible from the script and the space is large), then the first's
worktree and backup steps after the merge.
