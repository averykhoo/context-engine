# HANDOFF

Orientation note (FRAMEWORK §5.1). Replaced at every clean close; no session history here (that
is `docs/ledger/session-log.md`). The banner carries exactly one session key.

## Banner (2026-10-08f)

- **This repo builds the whole framework** in `docs/framework/FRAMEWORK.md`, to deploy across
  all the owner's repos (charter confirmed and widened, DEC-10). The record engine (§8.0) is
  the first piece. **Since 2026-10-08f it runs this repo's own records** (CE-8, DEC-7 amended).
- **State:** CE-1 (core), CE-2 (working state) and CE-8 (adoption) are done. The `ce` CLI runs
  sessions, the board, questions, batons, pauses, the banner, `orient`, `lint`, `routes`, and
  decisions and stories (`ce record new|stamp|amend`). AC-1 to AC-17 and AC-21 to AC-25 `tested`.
- **Rituals are `ce` commands** (`CLAUDE.md` § Rituals). When `ce` errors, do the step by hand
  from `docs/runbooks/manual-mode.md` and fix the engine (US-11). `ce lint` is in the gate: every
  decision and story is stamped, and the routing table is `[[routes]]` in `context.toml`.
- **NOW is CE-3**: the MCP server over the same `Engine` functions (AC-18, AC-19). NEXT: CE-4,
  CE-15 (deploy path, now unblocked), CE-16. CE-7 waits on CE-4 and CE-5.
- **Anti-goal:** a server the owner starts or manages. Claude Code may start one as a ritual.
- **No owner questions are open.** Push whenever while there is no CI (`CLAUDE.md`, close step 6).

## Open batons and pause blocks

None.

## Next session: start here

1. `CLAUDE.md` (loads automatically): environment, gate, rules, and the rituals as `ce` commands.
2. `ce session start`, then `ce orient` (the banner, batons, open sessions, the NEXT tier,
   questions to raise and the NOW item's Traps and Read first, under 6000 bytes). Raise any
   question it lists in chat, one line each, then `ce ask raised <ids>`.
3. `ce task show CE-3` (the NOW item). The board is `ce task list`; this note keeps no copy.
4. Read the rest of this note only if needed, and say which in your ledger entry's `read:` line.

## Facts not derivable from the code (dated)

- **2026-10-08d, the CLI:** run it as `<interpreter> -m context_engine ...`; the `ce` script lands
  in the env's `Scripts/`, which is not on PATH. Set `CE_ACTOR=claude-code/<model-id>` and
  `CE_SESSION=<key>` for a session's writes.
- **2026-10-08d, `tools/sabotage_ce1.py` no longer runs:** CE-2 rewrote `Store.set`, so its AC-9
  row's pattern stops matching (by design). Its 13 reds stand as CE-1's evidence; CE-14's G-T5
  replaces both tables.
- **2026-10-08f, git checks committed files out with CRLF here** (autocrlf). The engine keeps
  each file's endings, but a script that string-matches source must normalise first, as
  `tools/sabotage_ce8.py` does; `tools/sabotage_ce2.py` was written before this bit.

- **2026-10-08, heredocs in the Bash tool here can halve backslashes** (`"\n"` arrived as a
  newline in two Python heredocs): write probe scripts with the Write tool, as files.
- **2026-10-08, environment:** env `context-engine` has Python 3.12.15, `mcp` 2.3.0 (SDK 2.x:
  `MCPServer`, not `FastMCP`), `ruamel.yaml` 0.19.1, `pytest` 9.1.1; the package is installed
  editable. Claude Code on this machine is 2.1.280.
- **2026-10-08, GitHub:** `averykhoo/context-engine` is PRIVATE; `main` tracks `origin/main`.
  `gh` is not logged in: source the token per command as global `CLAUDE.md § CI pipelines` shows.
- **2026-10-08, trial repos:** adhoc had a clean tree, 47 commits in 14 days, `CLAUDE.md`
  16,196 B, `HANDOFF.md` 28,407 B, `docs/decisions.md` 52,624 B (D-1 to D-33). intervals had 24
  uncommitted files from a live session and a 2.0.0 release pending (DEC-6).
- **2026-10-08, Remote Control spawn mode defaults to `same-dir`** (owner screenshot): spawned
  sessions share the checkout unless `--spawn=worktree` is chosen. This confirms FRAMEWORK §5.5's
  premise that the shared checkout is the default reality.
- **OKF spec** read at commit `0b87c52c6ef999286c745e19998fdfcd03d5dbee` (FRAMEWORK §9.3.1).
