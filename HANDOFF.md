# HANDOFF

LIVING. Orientation note (FRAMEWORK §5.1). Replaced at every clean close; no session history here (that
is `docs/ledger/session-log.md`). The banner carries exactly one session key.

## Banner (2026-10-13b)

- **This repo builds the whole framework** in `docs/framework/FRAMEWORK.md`, to deploy across
  all the owner's repos (charter confirmed and widened, DEC-10). The record engine (§8.0) is
  the first piece. **It runs this repo's own records (CE-8), and this repo dogfoods the whole
  framework as it is built (DEC-35).**
- **FRAMEWORK.md holds the framework only (DEC-26):** no history, prior art, owner Q&A or change
  log, and no repo ids (a kit test reds a `DEC-n` in it). Change it in place; the why goes in a
  decision or story. The pre-trim text is frozen in `FRAMEWORK-v0.5.md`.
- **The command is `context-engine`** (DEC-15; `ce` before). Older records keep `ce`.
- **Bootloader (CE-38, adopted here 2026-10-13b):** `CLAUDE.md` carries the kit block, which
  `@`-imports `docs/framework/contract.md` (a byte copy of `kit/contract.md`; G-D0 reds a
  difference or a missing file); a `SessionStart` hook in `.claude/settings.local.json` prints
  orient. A failing hook is silent: if orient is not in context at start, say so. `init` merges
  into an existing settings file only with `--merge-settings` (DEC-32). Never run `init` here.
- **State:** CE-1..3, CE-5, CE-8, CE-10, CE-14..16, CE-20..25, CE-30..32, CE-35..38 done. **Since
  2026-10-13b: CE-38 (bootloader) and CE-25 (intent-chain guards G-I1, G-I2, G-T1, G-T2, G-T6 in
  lint; goal ids `G-n`; stamped stories keep `G1`, read as `G-1`).** AC-60..64 are agent-drafted
  planned criteria for US-10, US-12, US-13: the owner has not read them yet.
- **Priorities:** NOW CE-7 (quick adhoc trial; its import waits on **ASK-5**: rename a repo's ids at
  adoption or keep them, recommendation in the item). Then CE-43 (audio-workspace, the owner's
  better testing ground, DEC-6 amendment). NEXT: ASK-5, CE-45 (commit the op log with every
  commit: a mid-session commit is red on G-W7 alone), CE-49 (retire a story), CE-26, CE-33.
  CE-42 is CE-25's write-op half (DEC-33).
- **Every owner question carries a recommendation** held with reasonable confidence, where one
  is cheap to reach (DEC-34, FRAMEWORK §5.3); CE-44 makes it mechanical.
- **One id form for minted ids: `[A-Z]+-[1-9][0-9]*`** (DEC-33, FRAMEWORK P3). Imported ids: ASK-5.
- **Session start shows the owner every other open session** (US-16), one line each, or "none".
  Marking a dead stub `abandoned` stays by hand (DEC-29). A session closes by default when its
  requested work is done (DEC-31); more work after a close starts a new session.
- **Rituals: the order lives in `docs/runbooks/rituals.md`** (CE-24, US-15); `manual-mode.md` has
  the by-hand detail. Both ship in the kit, byte-equal. When the engine errors, do the step by
  hand and fix the engine (US-11). `lint` is in the gate.
- **Guards:** `src/context_engine/guards.py` runs G-D0..D3/D7/D8/D9/D12, G-I1/I2, G-T1/T2/T3/T6
  and G-W7 in lint; `[guards]` in `context.toml` switches them off or scopes their paths.
- **Deploy path (CE-15):** the kit is package data at `src/context_engine/kit/`; `init` writes it
  into a target repo, never overwrites, never touches the target env (DEC-1). No release tag yet.
- **Design review and register (CE-23, US-14):** work above the review threshold needs `review:`
  and a `## Design review` before promote or close; `task close` files the residuals as `INV-n`
  (INV-1..35 so far).
- **The MCP server is built (CE-3).** A server started before 2026-10-13a refuses every call (route
  key `max_bytes`): the owner restarts Claude Code after the 2026-10-13b push; until then, the CLI.
- **Several tasks in one request → the top level coordinates** (DEC-16). Ultracode workflows
  (build in a worktree, three review lenses, a skeptic each, fix) found real defects every time;
  gate a worktree with `PYTHONPATH=<worktree>/src` (the editable install points at the main tree)
  and check it out with `git -c core.autocrlf=false` (CE-46).
- **Anti-goal:** a server the owner starts or manages. Claude Code may start one as a ritual.
- **Owner rules in force:** `fable` only when the owner asks, or for the arbiter role (DEC-18);
  every programmatic process has a ritual fallback (DEC-20, P16).
- **The repo is PUBLIC. Ask before every push; push only on a green gate.** One task per commit,
  a `Session:` trailer on every agent commit (DEC-22). Pushed through the 2026-10-13b close.

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
