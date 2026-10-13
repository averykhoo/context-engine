---
type: Task
id: CE-50
title: Lint requires every runbook the installed kit ships to be routed and present
brief: "Closes INV-36's gap: an upgraded repo lacks the method runbooks with lint clean; never rewrite the owner's context.toml"
pri: LATER
state: open
deps: []
source: session 2026-10-13c
created: 2026-10-13
moved: 2026-10-13c
updated: 2026-10-13c
---

From CE-26's review (2026-10-13c, residual INV-36): init never edits an existing context.toml, so a repo upgraded to a kit with new runbooks gets no routes for them while its contract names them, and lint stays clean. Recommendation: G-D0 or G-R1 compares the kit's shipped runbooks (bootstrap.FILES) with the repo's [[routes]] and reds a missing file or route, naming the README § 4 step.
