---
type: Story
id: US-13
title: A session can be rolled back and closed, without breaking others in the same checkout
actor: owner
story_status: live
goals: [G7]
date: 2026-10-09
body_sha: sha256:80deafe11aa89baf96584315538f1edd1a1d92f9ca599564361751aa9951704f
---

The owner, 2026-10-09 (session 2026-10-09e), after answering FRAMEWORK §12.3:

> sessions starts might need a way to rollback and close instead of save and close, not sure how this works with git but maybe something there can be used that won't break other users or other bots in the same dir (not worktree). alternatively if theres no way a way to rollback is probably still needed

Intent: besides the clean close (save and close), a session can be rolled back and closed: what it changed is undone and the session ends. It must not break other humans or other agents working in the same checkout (a shared directory, not a worktree). The owner is unsure how git fits; if no git mechanism is safe, a rollback is still needed by some other means. Not designed, not built.
