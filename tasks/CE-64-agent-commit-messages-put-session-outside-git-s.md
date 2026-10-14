---
type: Task
id: CE-64
title: "Agent commit messages put Session: outside git's trailer block, so reconciling foreign commits reads them as foreign"
brief: 'Session: and Co-Authored-By: go in one final paragraph; context-engine commit already does it'
pri: NEXT
state: open
deps: []
source: session 2026-10-13c
created: 2026-10-13
moved: 2026-10-13c
updated: 2026-10-13c
---

Found by CE-55's review (2026-10-13c): the prescribed agent message ends 'Session: <key>', a blank line, then 'Co-Authored-By: ...', so git's trailer block is only the last paragraph and %(trailers:key=Session) is empty for c3c949c, 2d1e303 and 068893f; procedures § Reconciling foreign commits then counts this session's own commits as foreign. Recommendation: one trailer paragraph (Closes:, Session:, Co-Authored-By:) in CLAUDE.md § Commits, the kit contract and fan-out.md, or commit through context-engine commit, which places Session: correctly; a test that reads the trailer back with git interpret-trailers.
