---
type: Decision
id: DEC-61
title: 'audio-workspace is never pushed during its migration (demo hold): the cutover stays local'
actor: owner
decision_status: PROVISIONAL
decided: 2026-10-19
session: 2026-10-19c
body_sha: sha256:ac1d6e630c7af55fb72b4f4bc8345d793baf2850427ae25421dbf17e0807bc29
---

Owner, 2026-10-19c, verbatim, after relaying a note from an audio-workspace session:

"so don't push that repo at all, can you add this to the migration plan"

The relayed note (an audio-workspace agent's words, not the owner's), in part: "This clashes with the demo hold. The migration plan includes pushing a tag of the repo as it stood before the migration (ASK-13). It also rewrites CLAUDE.md and HANDOFF.md, the two files where I just put the hold notice. I'd start it no earlier than Wednesday, once CE-98 is fixed."

Context: audio-workspace is under a demo hold, whose notice sits in its CLAUDE.md and HANDOFF.md. Read here as: CE-43 pushes nothing to audio-workspace (no branch, no tag, no cutover commit) until the owner lifts the hold; the migration's commits and backup stay local. The tag the note mentions was already dropped by DEC-59 (ASK-13: "no tag; the backup names the commit hash, and the git bundle is the backup"), so the note is stale there. The pruning of CLAUDE.md and HANDOFF.md must keep the hold notice.
