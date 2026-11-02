---
type: Question
id: ASK-26
title: Delete the CE-11 rehearsal clones, and when the intervals backup?
brief: 'Recommend: copy live/ logs to the backup, bin rehearsals after merge, keep backup until CI green'
pri: LATER
state: open
deps: []
source: session 2026-11-02a
created: 2026-11-02
moved: 2026-11-02a
updated: 2026-11-02a
last_asked: 2026-11-02a
---

## Context

CE-11 left on disk, outside every repo: C:/Users/user/ce11-rehearsal/ (about 458 MB: two rehearsal
clones with their engine envs, the drafts, the cutover scripts, and the live cutover's logs in
`live/`), and the verified backup C:/Users/user/intervals-backup-2026-11-02/ (bundle, untracked files,
refs-before.txt, the ce-11-tools scripts). Both hold private intervals text. The `live/` logs were not
copied into the backup.

## Options

- After the merge, copy `live/` into the backup dir, then send ce11-rehearsal/ to the Recycle Bin;
  keep the backup until the push's CI is green.
- Keep both as they are for now.
- Delete both now.

## Recommendation

The first: the rehearsal clones are reproducible from the scripts, the live logs are evidence, and
the backup is the only undo until the merge is pushed.
