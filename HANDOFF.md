# HANDOFF

LIVING. Orientation note (FRAMEWORK §5.1). Replaced at every clean close; no session history here (that
is `docs/ledger/session-log.md`). The banner carries exactly one session key.

## Banner (2026-10-14c)

- **This repo builds the whole framework** (`docs/framework/FRAMEWORK.md`) to deploy across the owner's repos (DEC-10); the
  record engine (§8.0) runs this repo's own records (CE-8), and the repo dogfoods the framework as it is built (DEC-35).
- **Ready for the adhoc trial (CE-7, NOW), 2026-10-14a:** a sync audit (`docs/evidence/sync-audit-2026-10-14.md`) and a
  cutover dry run in a clone of adhoc (`docs/evidence/adhoc-dryrun-2026-10-14.md`) found the drift and the blockers; fixed in
  CE-69 (sync), CE-51/70 (init), CE-73 (`--file`), CE-74 (DEC-37: import renames ids, old ids stay aliases), CE-75 (orient
  never cuts batons, sessions or questions); AC-42 reworded for it (DEC-40). CE-7 carries the trial's traps and commands.
- **No framework or kit edits while CE-7's trial runs** (owner, 2026-10-14c; CE-7 trap F18): CE-77 and CE-78 wait for it.
- **FRAMEWORK.md holds the framework only (DEC-26):** no history, no repo ids; unbuilt parts say *Not built yet*.
- **The engine commits at milestones (CE-45, CE-55, DEC-36);** commit your own work with `context-engine commit <paths> -m`;
  close a task after its work is committed (`task close` carries `Closes:`).
- **Procedures' order lives in `docs/runbooks/procedures.md`**; by hand in `manual-mode.md`; method in `gate.md`,
  `sabotage.md`, `fan-out.md`, `release.md`. Kit copies are byte-equal (CE-26). When the engine errors, do it by hand (US-11).
- **CRLF (CE-46):** a cherry-pick or fresh checkout here writes kit files with CRLF and the kit byte tests go red; merge
  with `git -c core.autocrlf=false` and re-check out the touched files with LF.
- **CI is Linux, this machine Windows (CE-67):** run `tools/linux_gate.py` before every push.
- **Several tasks in one request:** a task agent per item in its own worktree, merged and verified at the top (DEC-16).
- **Owner rules:** `fable` only when asked (DEC-18); every process has a by-hand fallback (DEC-20). **The repo is PUBLIC:
  ask before every push; push only on a green gate** (DEC-22).
- **Next after CE-7:** CE-78 (scoped gate: code tests only when code changed), CE-77 (procedures as skills, plugin),
  CE-43 (audio-workspace), CE-64 (`Session:` trailer placement), CE-56 (DEC-38's standard prefixes).

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
