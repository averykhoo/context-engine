---
type: Task
id: CE-96
title: 'doc archive beyond whole .md docs: partial prune, frontmatter and non-.md material, repointing links'
brief: CE-27 built whole-doc archive only; the rest is by hand in manual-mode
pri: NOW
state: closed
deps: []
source: session 2026-10-16a
created: 2026-10-16
moved: 2026-10-30a
updated: 2026-10-30a
goals: [G-2]
status: deprecated
closed: 2026-10-30a
---

CE-27 (c901367, 5fa4fcb) archives a whole tracked .md doc. Still by hand: pruning part of a file under ## Pruned from (a judgement), archiving docs with liveness in frontmatter or non-.md material, and repointing links that still use the old path (G-D3 reports them).

## Log

- 2026-10-30a (claude-code/claude-opus-5-5): closed: doc archive now covers the parts CE-27 left to be done by hand. It archives a doc with frontmatter: the ARCHIVED line goes first after the frontmatter, and a liveness: key there becomes FROZEN. Material that is not markdown moves byte for byte. --lines A-B prunes a passage into <dir>/<stem>-pruned.md under '## Pruned from <doc> on <date>'. The reply names each pointer G-D3 newly reports and rewrites none. Done in 5beed46 (lane 2b218a5), DEC-121..123 cited in 59ea3ac. AC-147, AC-148 and AC-149 are tested.
