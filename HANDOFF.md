# HANDOFF

LIVING. Orientation note (FRAMEWORK §5.1). Replaced at every clean close; no session history here (that
is `docs/ledger/session-log.md`). The banner carries exactly one session key.

## Banner (2026-11-06d)

- **This repo builds the whole framework** (`docs/framework/FRAMEWORK.md`) to deploy across the owner's repos (DEC-10); the
  record engine (§8.0) runs this repo's own records (CE-8), and the repo dogfoods the framework as it is built (DEC-35).
- **NOW is CE-187: `decision accept <ids>`, with owner-actor decisions born ACCEPTED** (DEC-162: the owner adopted fable's
  2026-11-06b advice, `docs/evidence/owner-review-advice-2026-11-06b.md`). NEXT: CE-47, CE-156, CE-158, CE-161, CE-191 (cap 5);
  agent calls (PROVISIONAL): CE-164 and CE-18 to LATER, CE-192 (DEC-107 on by default) filed at LATER. No filed owner asks.
- **DEC-162 carried out (2026-11-06c, verify PASS round 2):** DEC-88 superseded by DEC-125; DEC-126 refs DEC-112; new CE-187..
  CE-192; CE-153, CE-159, CE-162 closed (merged or dropped), CE-163 became INV-98; INV-89+90 merged, INV-97 retired (register
  by hand: no op retires an entry, and `register show` hides `retired:`). The accept list waits for CE-187's op, not by hand.
- **audio-workspace feedback (2026-11-06d, not yet taken in):** `audio-workspace/docs/context-engine-feedback.md` has 10 items;
  item 1 is CE-177, item 3 is probably fixed by CE-44 (verify, then re-pin); items 2, 7, 8 need owner calls (green gate as a
  principle; close eagerly vs back-and-forth; model ids in actor strings). Digest: `.scratch/2026-11-06d/audit.md`.
- **CE-185 closed (2026-11-06a, US-19):** records are published at https://averykhoo.github.io/context-engine/ by
  `.github/workflows/pages.yml` calling the new read op `site build` (DEC-159); the stored `docs/decisions/index.md`, its
  regeneration and `hk_regen_index` are gone, and `decision index` only prints. Adopters' `decision_index` key still loads and
  orient names the remedy (DEC-160). Pages was turned on through the API (build_type workflow). Follow-up CE-186 (LATER): two
  unpinned site claims. **Restart Claude Code:** the MCP server runs stale code (refuses `context.toml`).
- **Engine findings from the cutovers:** CE-171..CE-175 (intervals), CE-176, CE-177..CE-181, CE-183, CE-184 (zanzibar); CE-177
  has its design (DEC-155); all LATER. CE-182: clones, both backups binned; 42 DLL names wait on a reboot; salvage kept.
- **Owner-held, not done:** CE-110 (owner pastes rules 1+2 into the global CLAUDE.md, then close). intervals' own records 2
  commits ahead of its origin (push is the owner's). A reboot frees CE-182's DLL names.
- **Pushed through 243efd0** (2026-11-06c, on the owner's "push when the gate is green"; local and Linux gate 1443 passed; CI
  green: gate 42184360650, pages 42184360702). Records commits after it are local.
- **Every clean close sets the banner** (G-W1).
- **Lesson (2026-11-02a..2026-11-06c):** a task runs as one workflow: builder, an independent verifier, fix rounds until PASS,
  then the push and a CI watcher (CE-167 about 3.9 h; CE-185 about 63 min, PASS on round 1). `task close` files a reviewed
  item's residuals itself: give `--residual` only for risks the review does not list.
- **The top-level session coordinates (DEC-44, DEC-60):** every task goes through subagents that persist to files; checks and
  verification go to agents; the top level keeps owner words, the final call on a verifier's report, and trivial bookkeeping.
- **Every push: gate, then `tools/linux_gate.py`, then a CI watcher.**
- **The engine commits at milestones (CE-45, CE-55, DEC-36);** commit your own work with `context-engine commit <paths> -m`;
  close a task after its work is committed (`task close` carries `Closes:`).
- **Procedures: `docs/runbooks/procedures.md`**, by hand in `manual-mode.md`; when the engine errors, do it by hand (US-11).
- **CRLF (CE-46):** merge with `git -c core.autocrlf=false`; kit copies must stay LF and byte-equal.
- **CI is Linux, this machine Windows (CE-67):** run `tools/linux_gate.py` before every push. The MCP server runs stale code
  after an engine change: restart Claude Code.
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
