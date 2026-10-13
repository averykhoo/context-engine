---
type: Task
id: CE-36
title: task close warns or refuses when it would leave NOW empty with NEXT empty
brief: Closing the only NOW item with NEXT empty turns the gate red on G-W5; say so at close time, with the promote remedy
pri: NEXT
state: closed
deps: []
source: session 2026-10-12e
created: 2026-10-12
moved: 2026-10-13a
updated: 2026-10-13a
review: [shipped]
status: deprecated
closed: 2026-10-13a
---

Seen 2026-10-12e: closing CE-10 (the only NOW item; NEXT empty since 2026-10-12d) left NOW at 0, and the next gate run was red on G-W5 before anything could be committed. The close itself succeeded silently. Options: refuse unless a successor id is named (e.g. `--then CE-n`), or close and print the G-W5 consequence plus the promote remedy. Picking the next NOW item stays the owner's call either way.

## Design review

affects: the session that closes the only NOW item, which until now learned of the red G-W5 only at its next gate run; the owner, whose call the next NOW item stays; every deployed repo, whose close result line and kit runbook copy change
- eliminated: the warning blocks a close the owner wants (the design never refuses: the close writes the same bytes as before and only its result line grows; a test closes the only NOW item and finds it closed)
- reduced: closing the only NOW item leaves G-W5 red with no word at close time, so the next gate run fails before anything is committed | rung: reduce | control: Engine.close appends the G-W5 consequence and the `task promote <id> NOW` remedy to its one result line, naming NEXT's items or saying NEXT is empty; sabotaged
- reduced: the close's warning and G-W5 drift apart, one red where the other is silent | rung: reduce | control: both read one helper, Engine._now_short; a test runs lint after each close outcome and checks they agree
- reduced: the warning reads as the engine choosing the next NOW item | rung: reduce | control: it promotes nothing, lists NEXT as candidates only, and says the owner picks
- residual: a by-hand close (manual mode) or a raw edit still learns of the empty NOW only at the next gate run | rung: collective | why: a by-hand step has no engine to warn it | control: manual-mode.md § task close tells the by-hand closer to count NOW after closing a NOW item and ask the owner which to promote; G-W5 reds it at rest
F: goes stale if G-W5's NOW rule, `[working.caps]` or the close's result line changes; the shared helper keeps the rule in one place, and a CLI test pins the clause
A: by hand, manual-mode.md § task close says to count NOW after closing a NOW item and, if it is short while anything is open, ask the owner which item to promote before running the gate
M: one helper, Engine._now_short, read by Engine.close and by G-W5 in Engine.lint; tests close through the engine and the CLI and run lint
E: reuses G-W5's message and the close line's `; residuals filed as` clause shape; one paragraph in manual-mode § task close (both copies) and one sentence in FRAMEWORK §5.2 Closing

## Log

- 2026-10-13a (claude-code/claude-opus-5-5): closed: done in 896ef8d, dc1c1d3: close, ask answer and a demoting promote warn that G-W5 is red, with the promote remedy; never refuse
