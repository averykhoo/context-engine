# HANDOFF

LIVING. Orientation note (FRAMEWORK §5.1). Replaced at every clean close; no session history here (that
is `docs/ledger/session-log.md`). The banner carries exactly one session key.

## Banner (2026-10-20b)

- **This repo builds the whole framework** (`docs/framework/FRAMEWORK.md`) to deploy across the owner's repos (DEC-10); the
  record engine (§8.0) runs this repo's own records (CE-8), and the repo dogfoods the framework as it is built (DEC-35).
- **The adhoc trial (CE-7) runs on its pinned kit (engine `38ed38e`), with CE-79 about 2026-10-21:** the owner moves on
  meanwhile and integrates its feedback later (2026-10-15b, CE-7 log); no re-pin first. Owed: INV-31 probes, scoring against CE-4.
- **CE-43 is NOW (DEC-51): audio-workspace migrated, merged into its LOCAL main and set up (2026-10-20a); gate green there.**
  DEC-61: nothing is pushed to audio-workspace during its demo hold. Owed: the owner restarts Claude Code there; remove the
  ce-cutover worktree and branch on the owner's word; push after the hold lifts. 2026-10-17c's prep drafts are in
  `.scratch/ce-17c/` and beside the audio-workspace backup outside this repo (private content: never commit them here).
- **CE-93 moved to NEXT (2026-10-17b, for CE-43); DEC-50 still holds it until the trial's feedback.** CE-95..CE-97 from CE-27.
- **New owner direction (2026-10-15c, management-theory review):** DEC-47 rules cite their incident (CE-94); DEC-48 who decides
  by reversibility (CE-91); DEC-49 FRAMEWORK.md is for using the framework, not history (CE-93 archive + rewrite); AAR and
  periodic review, owner-triggered (CE-90, US-12). DEC-48 is in the rule text since CE-91 (2026-10-20b).
- **CE-99 (goal-driven rerank) design is settled (DEC-64 + amendment):** milestone = framework fully built (G-7); tasks carry
  required `goals`; full rerank when NOW and NEXT are both cleared or on owner request. Building it waits on ASK-15 (kit hold).
- **DEC-50 (2026-10-15e):** a trap lives where its lifetime matches: task `## Traps`, a hazard board row, or a register INV-n;
  never the banner (CE-29, spec text still held).
- **The top-level session coordinates (DEC-44, DEC-60):** every task goes through subagents that persist to files; checks and
  verification go to agents; the top level keeps owner words, the final call on a verifier's report, and trivial bookkeeping.
  In the rule text since CE-83 (17470c8, 2026-10-20b): contract § Rules, FRAMEWORK §6.6 "The coordinator".
- **2026-10-20b's commits are unpushed** (CE-60, CE-83, CE-91, CE-58, CE-65, INV-51): push only on the owner's word, after
  `tools/linux_gate.py`; the owner should read 17470c8 (the contract rewrite) first.
- **No other framework or kit edits while CE-7's trial waits**, except as the owner asks (2026-10-14c). Lifted for CE-77, CE-78,
  CE-81 (DEC-43), CE-92 (DEC-50), CE-27 (owner, 2026-10-16a), CE-43 (DEC-51), CE-98 (DEC-52), and CE-60, CE-58, CE-65, CE-83,
  CE-91 (DEC-63). CE-84, CE-85, CE-89, CE-93 and CE-99 wait on it.
- **The engine commits at milestones (CE-45, CE-55, DEC-36);** commit your own work with `context-engine commit <paths> -m`;
  close a task after its work is committed (`task close` carries `Closes:`). Each commit takes every uncommitted op line.
- **Procedures: `docs/runbooks/procedures.md`**, by hand in `manual-mode.md`; when the engine errors, do it by hand (US-11).
- **CRLF (CE-46):** merge with `git -c core.autocrlf=false`; kit copies must stay LF and byte-equal
  (`.gitattributes` pins them LF since CE-46's repo half; init's half waits for CE-43).
- **CI is Linux, this machine Windows (CE-67):** run `tools/linux_gate.py` before every push (from a
  worktree too since CE-86). The MCP server runs stale code after an engine change (it refused writes on
  2026-10-16a after CE-27 added `[working] archive`): restart Claude Code.
- **Owner rules:** `fable` only when asked (DEC-18); every process has a by-hand fallback (DEC-20). **The repo is PUBLIC:
  ask before every push; push only on a green gate** (DEC-22). Close eagerly, in the turn the last task finishes (DEC-31, CE-82).

## Open batons and pause records

None.

## Next session: start here

1. `CLAUDE.md` (loads automatically): environment, gate, rules, and the procedures as `context-engine` commands.
2. The `SessionStart` hook prints `context-engine orient` (the banner, batons, open sessions, the
   NEXT tier, questions to raise and the top item, under 6000 bytes); then `context-engine session
   start`, in the order `docs/runbooks/procedures.md` gives. Raise any question it lists in chat,
   one line each, then `context-engine ask raised <ids>`.
3. `context-engine task show <id>` for the top item orient names. The board is `context-engine task
   list`; this orientation note keeps no copy.
4. Read the rest of this orientation note only if needed, and say which in your ledger entry's `read:` line.

## Facts not derivable from the code (dated)

- **2026-10-08d, the CLI:** run it as `<interpreter> -m context_engine ...`; the script (named `context-engine`
  since 2026-10-09a, DEC-15; `ce` before) lands in the env's `Scripts/`, which is not on PATH. Set `CE_ACTOR=claude-code/<model-id>` and
  `CE_SESSION=<key>` for a session's writes.
- **2026-10-08d, `tools/sabotage_ce1.py` no longer runs:** CE-2 rewrote `Store.set`, so its AC-9
  row's pattern stops matching (by design). Its 13 red results stand as CE-1's evidence; G-T5 (CE-34, split
  out of CE-14) replaces both tables.
- **2026-10-08f, git checks committed files out with CRLF here** (autocrlf). The engine keeps
  each file's endings, but a script that string-matches source must normalise first, as
  `tools/sabotage_ce8.py` does; `tools/sabotage_ce2.py` was written before this caused trouble.

- **2026-10-08, heredocs in the Bash tool here can halve backslashes** (`"\n"` arrived as a
  newline in two Python heredocs): write probe scripts with the Write tool, as files.
- **2026-10-08, environment:** env `context-engine` has Python 3.12.15, `mcp` 2.3.0 (SDK 2.x:
  `MCPServer`, not `FastMCP`), `ruamel.yaml` 0.19.1, `pytest` 9.1.1; the package is installed
  editable. Claude Code on this machine is 2.1.280.
- **GitHub:** `averykhoo/context-engine` is PUBLIC (was private on 2026-10-08; owner, 2026-10-10); `main` tracks `origin/main`.
  `gh` is not logged in: source the token per command as global `CLAUDE.md § CI pipelines` shows.
- **2026-10-08, trial repos:** adhoc had a clean tree, 47 commits in 14 days, `CLAUDE.md`
  16,196 B, `HANDOFF.md` 28,407 B, `docs/decisions.md` 52,624 B (D-1 to D-33). intervals had 24
  uncommitted files from a live session and a 2.0.0 release pending (DEC-6).
- **2026-10-08, Remote Control spawn mode defaults to `same-dir`** (owner screenshot): spawned
  sessions share the checkout unless `--spawn=worktree` is chosen. This confirms FRAMEWORK §5.5's
  premise that a shared checkout is the normal case.
- **OKF spec** read at commit `0b87c52c6ef999286c745e19998fdfcd03d5dbee` (FRAMEWORK §9.3.1).
