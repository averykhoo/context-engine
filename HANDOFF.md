# HANDOFF

LIVING. Orientation note (FRAMEWORK §5.1). Replaced at every clean close; no session history here (that
is `docs/ledger/session-log.md`). The banner carries exactly one session key.

## Banner (2026-11-05a)

- **This repo builds the whole framework** (`docs/framework/FRAMEWORK.md`) to deploy across the owner's repos (DEC-10); the
  record engine (§8.0) runs this repo's own records (CE-8), and the repo dogfoods the framework as it is built (DEC-35).
- **NOW is CE-164 (coverage op), the agent's pick on the owner's delegation (DEC-158, 2026-11-05a; rerank NEXT 1).**
  NEXT: CE-18, CE-156, CE-161. Open owner asks: ASK-26 (CE-11 clones and backup); a HOLD tier for this repo and a louder
  close when NOW is empty (both asked in chat, not filed). ASK-36 closed: leave zanzibar's token rules and tag push (DEC-157).
- **CE-167 closed (2026-11-04a):** zanzibar master fast-forwarded to 3e63fd7 and pushed (b743587..3e63fd7, no tag) on the owner's
  go (DEC-151; ASK-35 confirmed DEC-150); CI green (gate 41817387647, docs 41817387643); verifiers PASS. Owner answers
  DEC-152..DEC-156; zanzibar's own records (DEC-13..15, TK-301, TK-302, coordinator rule) refreshed in its session 2026-11-04a:
  pushed 3e63fd7..ebfe7d2 2026-11-05a, CI green. CE-182: clones binned but 21 locked DLLs; backup kept; INV-94 (CRLF drift, CE-184).
- **Engine findings from the cutovers:** CE-171..CE-175 (intervals), CE-176, CE-177..CE-181, CE-183, CE-184 (zanzibar); CE-177
  has its design (DEC-155); all LATER.
- **CE-11 closed (2026-11-03a, 32f4fd9):** intervals adopted and pushed (DEC-147); agent rulings DEC-148, DEC-149
  PROVISIONAL; intervals' own records 2 commits ahead of its origin, push is the owner's.
- **Owner to review:** agent calls DEC-86..DEC-130 PROVISIONAL from the 2026-10-30a build waves (35 tasks closed); residual
  follow-ups CE-150..CE-166; register INV-84..INV-90. DEC-133 PROVISIONAL (2026-10-31a).
- **Owner-held, not done:** CE-110 (owner pastes rules 1+2 into the global CLAUDE.md, then close), CE-40, CE-47, CE-56 (rename
  half), CE-132 (contract bump), CE-166 (adhoc), CE-28.
- **Pushed through 602aeac** (2026-11-05a, DEC-158; local gate 1429 passed, Linux gate 1429 passed; CI green, run 41994088181).
  Records commits after it are local.
- **Every clean close sets the banner** (G-W1).
- **Lesson (2026-11-02a, 2026-11-03a, 2026-11-03b):** an adoption runs as survey, verified bundle backup, scripted rehearsal on
  a clone, the same script live on a local branch, an independent verifier, then the owner's merge-and-push with a CI watcher,
  and last the adopter's own records refreshed in its own engine session; CE-43, CE-11 and CE-167 took this shape (CE-167 as
  one workflow: 2 surveys, builder, verifier, about 3.9 h).
- **The top-level session coordinates (DEC-44, DEC-60):** every task goes through subagents that persist to files; checks and
  verification go to agents; the top level keeps owner words, the final call on a verifier's report, and trivial bookkeeping.
- **Every push: gate, then `tools/linux_gate.py`, then a CI watcher.**
- **The engine commits at milestones (CE-45, CE-55, DEC-36);** commit your own work with `context-engine commit <paths> -m`;
  close a task after its work is committed (`task close` carries `Closes:`).
- **Procedures: `docs/runbooks/procedures.md`**, by hand in `manual-mode.md`; when the engine errors, do it by hand (US-11).
- **CRLF (CE-46):** merge with `git -c core.autocrlf=false`; kit copies must stay LF and byte-equal.
- **CI is Linux, this machine Windows (CE-67):** run `tools/linux_gate.py` before every push. The MCP server runs stale code
  after an engine change: restart Claude Code (it refused `housekeeping` at 2026-11-03b start).
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
