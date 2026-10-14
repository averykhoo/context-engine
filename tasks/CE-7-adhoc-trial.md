---
type: Task
id: CE-7
title: "Adhoc trial cutover on a worktree branch, scored against the CE-4 rubric"
brief: "One revertible commit; adhoc keeps its paths and ids; stop if adhoc has a live session"
pri: NOW
state: open
deps: [CE-3, CE-4, CE-5, CE-8, CE-24, CE-38, ASK-5, CE-74, CE-75]
source: session 2026-10-08a
created: 2026-10-08
moved: 2026-10-13b
updated: 2026-10-14e
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
- 2026-10-14a (claude-code/claude-opus-5-5): 2026-10-14a: ready. CE-74 and CE-75 are done; the blockers from the dry run are fixed except adhoc's own gate in a worktree (a trap). Commands for the cutover, verified 2026-10-14a by importing adhoc's real decisions.md into a temp repo (DEC-1..44, aliases D-1..44, lint clean). Run each as `<engine-python> -m context_engine --root <adhoc worktree>` with CE_ACTOR and CE_SESSION set: `init --prefix task=AD --prefix decision=DEC` (in adhoc main the settings question needs --merge-settings or --skip-settings: owner's call); set CLAUDE.md § Gate, lint, commit the kit's files by path; `session start`; `decision import docs/decisions.md --dry-run` and save the id map it prints as docs/evidence/<date>-decision-id-map.md; `decision import docs/decisions.md`; review the ones it set BUILT by default with `decision set DEC-n --set decision_status=...`; `context-engine commit <paths> -m ...` (import is not a milestone); freeze docs/decisions.md and repoint adhoc's CLAUDE.md. Board rows: `task new` then `task set AD-n --set "aliases=[1h]"`; open questions keep their number: `ask new "<title>" --id ASK-9 ...` then `task set ASK-9 --set "aliases=[Q9]"`. Residuals: INV-78..INV-83.
- 2026-10-14d (claude-code/claude-opus-5-5): Owner, 2026-10-14d, verbatim: "the engine should run within the adhoc repo so thats where everything should exist. make a new task to follow up in about a week to see how the trial is going." and "we will start ce7 now". Settled as DEC-41: a pinned, non-editable engine env lives inside the adhoc folder, gitignored (this replaces the pin trap F18). The follow-up is CE-79. Session 2026-10-14c keeps running here on other work.
- 2026-10-14d (claude-code/claude-opus-5-5): 2026-10-14d: cutover done on adhoc branch context-engine-trial (worktree adhoc-microphone-array-ce): 7100077 kit (engine pin 38ed38e, env at .context-engine/env/, DEC-41); 140d1eb/3316747 decisions DEC-1..DEC-67 imported, statuses reviewed, owner's calls as adhoc DEC-68; 0d6d9df board AD-1..AD-14 + ASK-9, HANDOFF 605->78 lines; e3f5c40 decisions.md frozen; fc7bdff/eef0ecc adhoc session 2026-10-14a closed with banner. adhoc gate green (pytest 366 passed, 425 s). Hook command runs rc 0 under bash and cmd.exe. Owed: real Claude Code sessions in the worktree (INV-31 probes: startup, resume, /clear, compaction), scoring against CE-4 (CE-79, about 2026-10-21), the owner's merge decision (DEC-32 settings question comes up then). Findings filed: CE-80 (import SUPERSEDED note irreversible), CE-81 (DEC-41 into kit and FRAMEWORK). Friction: engine milestone commits sweep every uncommitted op line, including other tasks' (CE-45 by design), so one-task-per-commit breaks.
- 2026-10-14e (claude-code/claude-opus-5-5): 2026-10-14e: owner, verbatim: "oh wait no it needs to be in the actual folder, not a separate worktree", "delete the worktree" (DEC-42). Done: adhoc main fast-forwarded to eef0ecc, worktree and branch deleted (junctions unlinked first; main's data/ and references/originals/ intact), engine env rebuilt in adhoc's folder at 38ed38e, MCP registered there, hook merged (owner: yes), adhoc session 2026-10-14b closed (fbe3090, 8d244e5).

## Traps

- The trial runs in adhoc's own folder, C:/Users/user/PycharmProjects/adhoc-microphone-array, on main (DEC-42, owner 2026-10-14e): the trial branch was fast-forwarded into main at eef0ecc and the worktree deleted. The merge decision is made; reverting means resetting main to 444efcc.
- Engine pin 38ed38e in adhoc's .context-engine/env/ (DEC-41): kit edits here do not reach adhoc until it is re-pinned; the owner froze kit edits for the trial anyway (2026-10-14c).
- The hook (owner said yes to --merge-settings, DEC-32) and the MCP server (local scope) point at adhoc's folder. A Claude Code session already open there has neither until it restarts.
- The first real session there runs INV-31's probes: orient on startup, resume, /clear, compaction.
- adhoc's pytest takes about 7 min (425 s, 2026-10-14), not seconds as its CLAUDE.md says.
