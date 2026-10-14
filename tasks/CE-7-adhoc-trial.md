---
type: Task
id: CE-7
title: "Adhoc trial cutover on a worktree branch, scored against the CE-4 rubric"
brief: "One revertible commit; adhoc keeps its paths and ids; stop if adhoc has a live session"
pri: NOW
state: open
deps: [CE-3, CE-4, CE-5, CE-8, CE-24, CE-38, ASK-5]
source: session 2026-10-08a
created: 2026-10-08
moved: 2026-10-13b
updated: 2026-10-14a
closed:
---

In a worktree of adhoc, on a branch: write `context.toml` and `.mcp.json`; import the board,
"still owed" (as batons), the decisions and the session log into records; rewrite the procedures in
adhoc's `CLAUDE.md` and `HANDOFF.md` to use the engine; run real sessions; score them against
the CE-4 baseline. The owner decides whether the branch merges.

## Read first

- `src/context_engine/kit/README.md` (init, § Hook, § 4 Upgrade) and `docs/runbooks/procedures.md` § Bootstrap
- ASK-5, DEC-32, DEC-6 and its amendment; INV-28 to INV-32 in `src/context_engine/REGISTER.md`
- `docs/framework/FRAMEWORK.md` §8.0.3, §11.4

## Log

- 2026-10-08b: deps += CE-8 (owner, DEC-10: dogfood here before any other repo).
- 2026-10-13a (claude-code/claude-opus-5-5): Owner, DEC-28: import adhoc D-27 as BUILT with D-29 linked as narrowing it (decision link D-29 D-27 --rel relaxes, as D-12/D-30), not as SUPERSEDED.
- 2026-10-13b (claude-code/claude-opus-5-5): Owner, 2026-10-13b: "Let's try to get it ready for first use then trial it on a repo": CE-38 then CE-7 (the trial) lead; CE-25 waits on ASK-3.
- 2026-10-13b (claude-code/claude-opus-5-5): DEC-6 amended (owner, 2026-10-13b): adhoc confirmed for a QUICK trial; audio-workspace is the better testing ground and is next (CE-43). Keep the trial short: cutover, a few real sessions, score, owner decides the merge.
- 2026-10-13b (claude-code/claude-opus-5-5): Promoted to NOW as CE-38 closed, following the owner's order of 2026-10-13b (CE-38 then CE-7). CE-38's init now writes the bootloader, docs/framework/contract.md and the SessionStart hook; adhoc probably has a .claude/settings.local.json already, so init will refuse until the owner says yes (--merge-settings) or no (--skip-settings), per DEC-32. The live probes owed by CE-38 (missing @-import, hook output on resume, /clear and compaction, the shell that runs hooks on Windows, a failing hook) fit this trial's first session.
- 2026-10-13b (claude-code/claude-opus-5-5): Owner, 2026-10-13b: CE-7 stays NOW. A session is live in adhoc, working on untracked audio files: do the cutover in a worktree branch, touch nothing in adhoc's main checkout, and re-check adhoc's HANDOFF/decisions for commits made after the import before the owner decides the merge.
- 2026-10-13c (claude-code/claude-opus-5-5): Owner, 2026-10-13c: "adhoc mic array's agent is done, lmk when you're done, clean up, then we'll migrate that repo in a new session". adhoc's live session has ended; ASK-5 is answered (DEC-37, option c: rename with aliases); DEC-38 sets the standard prefixes (adhoc's tasks take their own prefix, e.g. AD). Since CE-55 the engine commits at milestones and task close carries Closes:; commit through context-engine commit.
- 2026-10-14a (claude-code/claude-opus-5-5): Owner, 2026-10-14a, verbatim: "Get it all ready for first use, we'll trial it in the adhoc repo as soon as you're done"

## Traps

- The body predates CE-38: there is no .mcp.json step and no rewriting of procedures into adhoc's CLAUDE.md. Run init from the engine's env (kit README); it appends the kit block and copies docs/framework/contract.md.
- adhoc very likely has .claude/settings.local.json already, so init refuses until the owner says yes (--merge-settings) or no (--skip-settings) (DEC-32).
- A session is live in adhoc's main checkout (untracked audio, 2026-10-13b): work only in a worktree branch, and re-check adhoc's HANDOFF and decisions for commits made after the import before the merge.
- The import waits on ASK-5 (rename ids or keep them); leave [guards] charter, stories and tests unset until adhoc's charter holds the owner's goals (procedures § Bootstrap).
- The first session there runs INV-31's live probes: does orient output appear on startup, resume, /clear and compaction; what a missing import or a broken interpreter path looks like.
