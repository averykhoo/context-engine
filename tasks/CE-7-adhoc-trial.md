---
type: Task
id: CE-7
title: "Adhoc trial cutover on a worktree branch, scored against the CE-4 rubric"
brief: "One revertible commit; adhoc keeps its paths and ids; stop if adhoc has a live session"
pri: NOW
state: open
deps: [CE-3, CE-4, CE-5, CE-8, CE-24, CE-38]
source: session 2026-10-08a
created: 2026-10-08
moved: 2026-10-13b
updated: 2026-10-13b
closed:
---

In a worktree of adhoc, on a branch: write `context.toml` and `.mcp.json`; import the board,
"still owed" (as batons), the decisions and the session log into records; rewrite the rituals in
adhoc's `CLAUDE.md` and `HANDOFF.md` to use the engine; run real sessions; score them against
the CE-4 baseline. The owner decides whether the branch merges.

## Read first

- `docs/framework/FRAMEWORK.md` §8.0.3, §11.4
- `docs/decisions/DEC-5-framework-before-migration.md`, `DEC-6-adhoc-first.md`

## Log

- 2026-10-08b: deps += CE-8 (owner, DEC-10: dogfood here before any other repo).
- 2026-10-13a (claude-code/claude-opus-5-5): Owner, DEC-28: import adhoc D-27 as BUILT with D-29 linked as narrowing it (decision link D-29 D-27 --rel relaxes, as D-12/D-30), not as SUPERSEDED.
- 2026-10-13b (claude-code/claude-opus-5-5): Owner, 2026-10-13b: "Let's try to get it ready for first use then trial it on a repo": CE-38 then CE-7 (the trial) lead; CE-25 waits on ASK-3.
- 2026-10-13b (claude-code/claude-opus-5-5): DEC-6 amended (owner, 2026-10-13b): adhoc confirmed for a QUICK trial; audio-workspace is the better testing ground and is next (CE-43). Keep the trial short: cutover, a few real sessions, score, owner decides the merge.
- 2026-10-13b (claude-code/claude-opus-5-5): Promoted to NOW as CE-38 closed, following the owner's order of 2026-10-13b (CE-38 then CE-7). CE-38's init now writes the bootloader, docs/framework/contract.md and the SessionStart hook; adhoc probably has a .claude/settings.local.json already, so init will refuse until the owner says yes (--merge-settings) or no (--skip-settings), per DEC-32. The live probes owed by CE-38 (missing @-import, hook output on resume, /clear and compaction, the shell that runs hooks on Windows, a failing hook) fit this trial's first session.
- 2026-10-13b (claude-code/claude-opus-5-5): Owner, 2026-10-13b: CE-7 stays NOW. A session is live in adhoc, working on untracked audio files: do the cutover in a worktree branch, touch nothing in adhoc's main checkout, and re-check adhoc's HANDOFF/decisions for commits made after the import before the owner decides the merge.
