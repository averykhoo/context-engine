---
type: Question
id: ASK-19
title: "CE-79 re-pin: finish it once the idle adhoc conversation is closed, or roll adhoc's env back to 38ed38e?"
brief: 'Recommend: owner closes the idle adhoc conversation, then the re-pin finishes'
pri: NEXT
state: closed
deps: []
source: session 2026-10-22b
created: 2026-10-22
moved: 2026-10-22b
updated: 2026-10-22b
last_asked: 2026-10-22b
blocks: [CE-79]
status: deprecated
closed: 2026-10-22b
answered: {on: 2026-10-22, session: 2026-10-22b, decision: DEC-70}
---

Context: the re-pin agent upgraded adhoc-microphone-array's engine env in place to 9f0e8ca (package only, deps unchanged), then a permission check stopped it because an idle Claude Code conversation in adhoc (started 2026-10-21, last wrote 08:59 when adhoc 2026-10-22c closed) still runs an MCP server from that env. adhoc is half-upgraded: env at 9f0e8ca, kit contract and 6 runbooks still 38ed38e's, so its lint will likely fail G-D0; nothing committed; adhoc tree clean.

Options:
1. Owner closes or restarts that idle adhoc conversation; an agent then copies the kit, runs lint and adhoc's gate (about 12 min), opens and closes an adhoc session for the ledger line, commits locally, and a verifier checks it.
2. Roll the env back to 38ed38e now (same pip command) and re-pin later.
3. Leave it half-state until the owner next works in adhoc.

Recommendation: option 1. The idle conversation has done nothing since its session closed, its MCP server already runs stale code and must be restarted anyway, and finishing costs one gate run; a rollback is the same kind of write and leaves the fixes unused.

## Log

- 2026-10-22b (claude-code/claude-opus-5-5): answered by the owner: DEC-70
