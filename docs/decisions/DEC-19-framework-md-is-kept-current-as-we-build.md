---
type: Decision
id: DEC-19
title: FRAMEWORK.md is kept current as we build; archive only what the future must reference
actor: owner
decision_status: PROVISIONAL
decided: 2026-10-09
session: 2026-10-09d
body_sha: sha256:2b1256c0766d747b96503c4ede8deb5b46188183512e745bbf3862a3d8219069
---

The owner, 2026-10-09 (session 2026-10-09d), asking for a few notes to be added:

> keep framework.md updated as we build, and archive if needed when there are huge changes that need backing up and need referencing from the future. if we never need to see it again then leave it in git history and just change it in-place

So: FRAMEWORK.md is updated in the same session as the work it describes. A change small enough to leave in git history is made in place. A huge change that will need referencing later archives the old version beside it first (as `FRAMEWORK-v0.1.md` and `FRAMEWORK-v0.4.md` already are). If the old text will never be needed again, git history is the archive.
