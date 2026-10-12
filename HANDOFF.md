# HANDOFF

Orientation note (FRAMEWORK §5.1). Replaced at every clean close; no session history here (that
is `docs/ledger/session-log.md`). The banner carries exactly one session key.

## Banner (2026-10-12c)

- **This repo builds the whole framework** in `docs/framework/FRAMEWORK.md`, to deploy across
  all the owner's repos (charter confirmed and widened, DEC-10). The record engine (§8.0) is
  the first piece. **Since 2026-10-08f it runs this repo's own records** (CE-8, DEC-7 amended).
- **FRAMEWORK.md holds the framework only (DEC-26, 2026-10-11c):** a summary and section guide
  on top, then §0 to §11; no history, prior art, owner Q&A or change log. Change it in place;
  the why goes in a decision or story. The pre-trim text (with the old §11.3, §12 owner answers
  and §13 changelog) is frozen in `FRAMEWORK-v0.5.md`; older records citing §12/§13 mean that file.
- **The command is `context-engine`** (DEC-15; `ce` before). Older records keep `ce`.
- **State:** CE-1 (core), CE-2 (working state), CE-8 (adoption), CE-3 (MCP server), CE-15
  (deploy path), CE-16 (coverage map), CE-23 (design review) are done; since 2026-10-12c also
  CE-22 (engine commits carry `Session:`), CE-20 (`task close ASK-n` refused) and CE-21 (G-D0).
  The CLI runs sessions, the board, questions, batons, pauses, the banner, `orient`, `lint`,
  `routes`, `init`, `register show`, and decisions and stories (`record new|stamp|amend`).
- **Priorities (owner-approved 2026-10-12c):** NOW CE-24; NEXT CE-5, CE-14, CE-10. The chain
  that matters is CE-24 + CE-5 -> CE-7 (adhoc trial) -> CE-11. CE-14 unblocks CE-25 and CE-30.
- **Deploy path (CE-15):** the adoption kit is package data at `src/context_engine/kit/`;
  `context-engine init` writes it into a target repo, never overwrites, never touches the target
  env (DEC-1). Config refuses unknown keys. Gaps: the kit ships no runbooks (CE-24), there is no
  release tag yet (owner's call; docs say `@<tag-or-commit-sha>`).
- **G-D0 (CE-21):** lint checks the contract's `framework:` line(s) and kit-block marker against
  the engine's major.minor; the contract path is `[engine] contract` (default `CLAUDE.md`). An
  Engine test fixture without a matching `CLAUDE.md` now lints red on G-D0.
- **Design review and register (CE-23, P17/P18, US-14):** work above the review threshold needs
  a `review:` field and a `## Design review` before promote or close; residual risks move to the
  register on close as `INV-n` (DEC-27; INV-1..12 so far; INV-7's text is stale, BTN-1).
- **Coverage map (CE-16):** `docs/evidence/framework-coverage-2026-10-12.md` (frozen) maps every
  FRAMEWORK component, ritual and guard to a task, prose-only, or deferred.
- **The MCP server is built (CE-3):** `mcp__context-engine__<group>_<verb>`, one tool per
  operation in `ops.OPS`, the same function the CLI calls. Set up on the owner's machine by a
  local-scope `claude mcp add` (DEC-25). Missing tools at session start: register it, use the
  CLI, ask the owner to restart (`CLAUDE.md` § Environment). Call `session_start` first.
  Actors must be plain `<producer>/<version>` (a subagent suffix is refused).
- **Rituals are `context-engine` commands** (`CLAUDE.md` § Rituals). When it errors, do the
  step by hand from `docs/runbooks/manual-mode.md` and fix the engine (US-11). `lint` is in the
  gate.
- **One source of truth for rituals (US-15):** FRAMEWORK.md plus the fallback runbook, pasted
  into a repo, must be all an agent needs. **CE-24 (NOW)** builds the rituals runbook (engine
  command and by-hand step side by side) and strips this repo's ids from the runbooks so the kit
  can ship them.
- **Several tasks in one request → the top level coordinates, it does not do** (DEC-16, amended
  2026-10-12b with owner words: trial run; if it works out it gets encoded). 2026-10-12b ran
  a workflow; 2026-10-12c ran CE-22/20/21 as sequential subagents (same file), which worked.
  Ultracode has standing approval when it keeps the session's tokens down (DEC-17).
- **History was rewritten on 2026-10-09c.** A checkout made before it must
  `git fetch origin && git reset --hard origin/main`; old SHAs quoted in text no longer resolve.
- **Anti-goal:** a server the owner starts or manages. Claude Code may start one as a ritual.
- **No owner questions are open.** Rollback and close (US-13) is FRAMEWORK §6.13, CE-18 LATER.
- **Owner rules in force:** no `fable` subagents unless asked or really necessary (DEC-18);
  every programmatic process has a ritual fallback (DEC-20, P16); an after-action review per
  session is a first note, not designed (US-12, §6.12).
- **The repo is PUBLIC. Ask before every push; push only on a green gate.** One task per commit,
  its id leading the title, a `Session:` trailer on every agent commit, engine ones included
  (DEC-22, CE-22). The engine's major.minor is the framework version (DEC-23, enforced by G-D0).
  Any session closes a baton with evidence (DEC-24).

## Open batons and pause blocks

None.

## Next session: start here

1. `CLAUDE.md` (loads automatically): environment, gate, rules, and the rituals as `context-engine` commands.
2. `context-engine session start`, then `context-engine orient` (the banner, batons, open sessions, the NEXT tier,
   questions to raise and the NOW item's Traps and Read first, under 6000 bytes). Raise any
   question it lists in chat, one line each, then `context-engine ask raised <ids>`.
3. `context-engine task show CE-3` (the NOW item). The board is `context-engine task list`; this note keeps no copy.
4. Read the rest of this note only if needed, and say which in your ledger entry's `read:` line.

## Facts not derivable from the code (dated)

- **2026-10-08d, the CLI:** run it as `<interpreter> -m context_engine ...`; the script (named `context-engine`
  since 2026-10-09a, DEC-15; `ce` before) lands in the env's `Scripts/`, which is not on PATH. Set `CE_ACTOR=claude-code/<model-id>` and
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
- **GitHub:** `averykhoo/context-engine` is PUBLIC (was private on 2026-10-08; owner, 2026-10-10); `main` tracks `origin/main`.
  `gh` is not logged in: source the token per command as global `CLAUDE.md § CI pipelines` shows.
- **2026-10-08, trial repos:** adhoc had a clean tree, 47 commits in 14 days, `CLAUDE.md`
  16,196 B, `HANDOFF.md` 28,407 B, `docs/decisions.md` 52,624 B (D-1 to D-33). intervals had 24
  uncommitted files from a live session and a 2.0.0 release pending (DEC-6).
- **2026-10-08, Remote Control spawn mode defaults to `same-dir`** (owner screenshot): spawned
  sessions share the checkout unless `--spawn=worktree` is chosen. This confirms FRAMEWORK §5.5's
  premise that the shared checkout is the default reality.
- **OKF spec** read at commit `0b87c52c6ef999286c745e19998fdfcd03d5dbee` (FRAMEWORK §9.3.1).
