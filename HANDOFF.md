# HANDOFF

Orientation note (FRAMEWORK §5.1). Replaced at every clean close; no session history here (that
is `docs/ledger/session-log.md`). The banner carries exactly one session key.

## Banner (2026-10-08b)

- **This repo builds the whole framework** in `docs/framework/FRAMEWORK.md`, to deploy across
  all the owner's repos (charter confirmed and widened, DEC-10). The record engine (§8.0) is
  the first piece. **It uses the framework on itself, by hand, until the engine exists** (DEC-7).
- **State:** a package skeleton (one test), the framework spec, and a step-0 spike that verified
  the MCP and hook assumptions (`spike/FINDINGS.md`). No engine code yet.
- **NOW is CE-1, the engine core.** Order (DEC-10): dogfood here first (CE-8), then other
  repos (CE-15, then the adhoc trial CE-7, whose baseline CE-4 must be measured first).
- **Anti-goal:** a server the owner starts or manages. Claude Code may start one as a ritual.
- **One owner question is open** (ASK-2): raise it at session start, one line.
- Commits `0964993` onward are **local and unpushed**; push only with permission.

## Open batons and pause blocks

None.

## Next session: start here

1. `CLAUDE.md` (loads automatically): environment, gate, rules, the routing table.
2. Raise **ASK-2** in chat, one line, unless answered; record any answer at
   once (a decision with `actor: owner`, then close the question file).
3. Read the board below, then the NOW item's file: `tasks/CE-1-engine-core.md`, its Traps and
   its Read first.
4. Read the rest of this note only if needed, and say which in your ledger entry's `read:` line.

## Board

Source of truth: one file per item in `tasks/` (board size 2). This table is a view; keep it in
step by hand until CE-8. Caps: NOW exactly 1, NEXT at most 5.

| pri | id | what | deps |
|---|---|---|---|
| NOW | CE-1 | Engine core: OKF records, ids under a lock, op log, write-time refusal (AC-1 to AC-9) | |
| NEXT | CE-2 | Working state: tasks, questions, batons, pauses, ledger; session ops; `orient`; lint (AC-10 to AC-17) | CE-1 |
| NEXT | CE-3 | MCP server over the CLI operations; dogfood it here (AC-18, AC-19) | CE-2 |
| NEXT | CE-4 | Measure adhoc's start and close cost today, before any cutover (read-only) | |
| NEXT | CE-16 | Coverage map: every FRAMEWORK component, ritual and guard → a task, prose-only, or deferred (G7) | |
| NEXT | ASK-2 | Owner: may append-only records take logged typo fixes? | blocks CE-5 |
| LATER | CE-5 | Decision records, `why()`, generated index, adhoc importer | CE-1, ASK-2 |
| LATER | CE-6 | Tier-0 housekeeping script and the `hk_` operations | CE-2 |
| LATER | CE-7 | adhoc trial cutover on a worktree branch, scored against CE-4 | CE-3, CE-4, CE-5, CE-8 |
| LATER | CE-8 | The engine adopts this repo's hand-written records | CE-3 |
| LATER | CE-9 | Trim FRAMEWORK.md (112 KB) and move its change history out | |
| LATER | CE-10 | Run the gate in GitHub Actions | |
| LATER | CE-14 | The guard catalogue (§8.1 to §8.5) as engine lint guards | CE-2 |
| LATER | CE-15 | Deploy path: how any repo gets the system, as text Claude Code manages | CE-8 |
| SOMEDAY | CE-11 | intervals after its 2.0.0, then zanzibar and audio-workspace | CE-7 |
| SOMEDAY | CE-12 | Tier-1 housekeeping agents restricted to `hk_` tools | CE-6 |
| SOMEDAY | CE-13 | Check what `/clear` does to the MCP server, interactively | |

## Facts not derivable from the code (dated)

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
