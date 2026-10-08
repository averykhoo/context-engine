# HANDOFF

Orientation note (FRAMEWORK §5.1). Replaced at every clean close; no session history here (that
is `docs/ledger/session-log.md`). The banner carries exactly one session key.

## Banner (2026-10-08d)

- **This repo builds the whole framework** in `docs/framework/FRAMEWORK.md`, to deploy across
  all the owner's repos (charter confirmed and widened, DEC-10). The record engine (§8.0) is
  the first piece. **It uses the framework on itself, by hand, until CE-8 switches it over** (DEC-7).
- **State:** core (CE-1) and working state (CE-2, closed 2026-10-08d) are built. The `ce` CLI
  (`python -m context_engine`) runs sessions (`session start | close | pause`, keys minted under
  the lock), the board, owner questions, batons and pauses, `banner show | set`, `orient` and
  `lint` (schema, G-D10, G-D11, G-W1 to G-W6). AC-1 to AC-17 `tested`, each sabotaged red.
  Session 2026-10-08d was opened and closed through the engine itself.
- **NOW is CE-8: switch this repo to the engine.** Stamp bodies, then rewrite `CLAUDE.md`'s
  rituals as `ce` commands. Then CE-3 (MCP), other repos (CE-15), the adhoc trial (CE-7; CE-4 first).
- **Anti-goal:** a server the owner starts or manages. Claude Code may start one as a ritual.
- **No owner questions are open.** Push whenever while there is no CI (`CLAUDE.md`, close step 7).

## Open batons and pause blocks

None.

## Next session: start here

1. `CLAUDE.md` (loads automatically): environment, gate, rules, the routing table.
2. Run `<interpreter> -m context_engine orient` (it prints the banner, batons, open sessions, the
   NEXT tier, questions to raise and the NOW item's Traps and Read first, under 6000 bytes).
   Raise any open `ASK-n` in chat, one line each (none on 2026-10-08d); record an answer at once
   (`ask answer`, or by hand: a decision with `actor: owner`, then close the question file).
3. Read the NOW item's file: `tasks/CE-8-dogfood-adoption.md`. Optionally open the session
   through the engine as 2026-10-08d did: `session start`, then `--session <key>` or `CE_SESSION`.
4. Read the rest of this note only if needed, and say which in your ledger entry's `read:` line.

## Board

Source of truth: one file per item in `tasks/` (board size 2). This table is a view; keep it in
step by hand until CE-8. Caps: NOW exactly 1, NEXT at most 5.

| pri | id | what | deps |
|---|---|---|---|
| NOW | CE-8 | The engine adopts this repo's records: stamp bodies, rituals as `ce` commands | |
| NEXT | CE-3 | MCP server over the CLI operations; dogfood it here (AC-18, AC-19) | |
| NEXT | CE-4 | Measure adhoc's start and close cost today, before any cutover (read-only) | |
| NEXT | CE-16 | Coverage map: every FRAMEWORK component, ritual and guard → a task, prose-only, or deferred (G7) | |
| LATER | CE-5 | Decision records, insert-only `correct`, `why()`, generated index, adhoc importer | |
| LATER | CE-6 | Tier-0 housekeeping script, the `hk_` operations, G-W11's window | |
| LATER | CE-7 | adhoc trial cutover on a worktree branch, scored against CE-4 | CE-3, CE-4, CE-5, CE-8 |
| LATER | CE-9 | Trim FRAMEWORK.md (112 KB) and move its change history out | |
| LATER | CE-10 | Run the gate in GitHub Actions | |
| LATER | CE-14 | The guard catalogue (§8.1 to §8.5) as engine lint guards | |
| LATER | CE-15 | Deploy path: how any repo gets the system, as text Claude Code manages | CE-8 |
| LATER | CE-17 | Tiled gate, run ledger keyed on each tile's input hash; `orient()` shows tested/untested | |
| SOMEDAY | CE-11 | intervals after its 2.0.0, then zanzibar and audio-workspace | CE-7 |
| SOMEDAY | CE-12 | Tier-1 housekeeping agents restricted to `hk_` tools | CE-6 |
| SOMEDAY | CE-13 | Check what `/clear` does to the MCP server, interactively | |

## Facts not derivable from the code (dated)

- **2026-10-08d, the CLI:** run it as `<interpreter> -m context_engine ...`; the `ce` script lands
  in the env's `Scripts/`, which is not on PATH. Set `CE_ACTOR=claude-code/<model-id>` and
  `CE_SESSION=<key>` for a session's writes.
- **2026-10-08d, `tools/sabotage_ce1.py` no longer runs:** CE-2 rewrote `Store.set`, so its AC-9
  row's pattern stops matching (by design). Its 13 reds stand as CE-1's evidence; CE-14's G-T5
  replaces both tables.

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
