---
type: Task
id: CE-89
title: Frozen wording owed after CE-41 and CE-87
brief: Kit/FRAMEWORK text edits held by the CE-7 freeze
pri: LATER
state: open
deps: []
source: session 2026-10-15b
created: 2026-10-15
moved: 2026-10-15b
updated: 2026-10-23f
goals: [G-7]
---

(1) FRAMEWORK.md G-D3 text says a bare file name resolves to any file of that name; since CE-41 (ea14d74) it is any file git does not ignore. (2) kit/context.toml.template comments lock_timeout as seconds to wait for the repo lock; since CE-87 (34ea268) it is how long the lock may stay with one holder. (3) Optional: CE-41's brief asked an ambiguous bare name to fail; not built because AC-71 cites byte-equal kit/repo runbook copies by bare name; if wanted, fail only when the matches differ.

## Log

- 2026-10-23f (claude-code/claude-opus-5-5): Items 1 (FRAMEWORK §8.3 G-D3 text: a bare name resolves to a file git does not ignore) and 2 (kit context.toml.template lock_timeout comment) landed in c5b812f (CE-93), checked by CE-93's verify-2. Item 3 (fail an ambiguous bare name only when the matches differ; engine code) refiled as CE-144.
