---
type: Task
id: CE-58
title: "An op confirms a story: unconfirmed to live with the owner's words"
brief: Closes INV-51's commonest case; owner words verbatim, like record retire --by owner
pri: LATER
state: closed
deps: []
source: session 2026-10-13c
created: 2026-10-13
moved: 2026-10-20b
updated: 2026-10-20b
status: deprecated
closed: 2026-10-20b
---

From CE-49's review (2026-10-13c, residual INV-51): an agent-reconstructed story moves from unconfirmed to live only by a hand edit of story_status, which lint cannot tell from any other hand edit, and the op log records keys, not values. Recommendation: `record confirm <id> --file <owner words>` writing the amendment and an op line, plus a G-I2 check like the retire one.

## Log

- 2026-10-20b (claude-code/claude-opus-5-5): closed: done in 192f92c
