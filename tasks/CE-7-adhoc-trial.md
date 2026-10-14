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
updated: 2026-10-14d
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

## Traps

- The body predates CE-38: there is no .mcp.json step and no rewriting of procedures into adhoc's CLAUDE.md. Run init from the engine's env (kit README); it appends the kit block and copies docs/framework/contract.md.
- Dry run 2026-10-14a (docs/evidence/adhoc-dryrun-2026-10-14.md) walked this cutover in a throwaway clone; its findings are the traps below, and CE-74, CE-75 and CE-76 fix the engine side.
- Worktree and settings (dry run F36): a fresh worktree has no .claude/, so init there meets no settings file and the DEC-32 question (--merge-settings or --skip-settings) only comes up in adhoc main at merge. The hook written in the worktree names the worktree's root and goes when the worktree does.
- Pin the engine for the trial (F18): G-D0 compares adhoc's contract.md with the installed kit's text, so an editable install picks up every kit change made here mid-trial and turns adhoc's lint red. Install a pinned commit into a separate env, or freeze kit changes for the trial.
- adhoc's gate in a worktree (F10): `scripts/extract_text.py --check` exits 1 when the gitignored references/originals/ is missing, and tests skip without the gitignored data/. Copy or junction both into the worktree first. Pytest took 571 s, not "seconds".
- Ids (DEC-37, CE-74): import renames D-n to DEC-n with D-n kept as an alias. Rejected rows get fresh numbers, so re-check adhoc's decisions.md for entries written after the import before the merge (F21). After import, freeze or redirect docs/decisions.md and change adhoc's CLAUDE.md, which tells sessions to append there (F23). Check each imported decision's status, because the import defaults most of them to BUILT (F22).
- No board or question import tool (F25, F26): script it through `task new` and record each old id (`1h`, Q5..Q9) as an alias. Keep rank order and the D-n links by hand.
- HANDOFF (F17, F27, F32): adhoc's 43 KB HANDOFF exceeds the kit caps and its banner holds durable facts (the best-rung table). Move those facts before any `banner set`. Its "still owed" is a .scratch inventory, not batons.
- Lint on adhoc's docs went green from config plus 4 one-line edits (F13, F14). G-D5 flags adhoc's domain words "three kinds"/"six kinds" (F15): narrow count_nouns in [guards].
- leave [guards] charter, stories and tests unset until adhoc's charter holds the owner's goals (procedures § Bootstrap).
- The first session there runs INV-31's live probes: does orient output appear on startup, resume, /clear and compaction; what a missing import or a broken interpreter path looks like. The dry run saw the hook run rc 0 under bash and cmd.exe.
