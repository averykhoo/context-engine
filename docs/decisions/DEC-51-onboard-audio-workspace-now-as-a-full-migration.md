---
type: Decision
id: DEC-51
title: Onboard audio-workspace now as a full migration; vitest and smoke at push, not per commit
actor: owner
decision_status: PROVISIONAL
decided: 2026-10-17
session: 2026-10-17b
body_sha: sha256:fb8846a1ed2ea384f716c71e5cbc38828557615d63ae40d0b5aeabef42e7d0fd
tasks: [CE-43]
---

Owner, 2026-10-17b, after the onboarding assessment of audio-workspace (CE-43):

> Remove the aw owner worktree
>
> We'll do a full migration to this context engine, maybe do a backup first?
>
> We'll vitest before push instead of commit then, don't think we need that or the smoke test every commit
>
> We'll onboard this first then I'll figure out the feedback next week

Context the owner was answering: the assessment's open questions were (1) wait for CE-79 or onboard now; (2) import all of audio-workspace's decision log or freeze it as routed history; and it noted that a `code` gate scope covering vitest would re-run the slow gate before every commit and record write.
