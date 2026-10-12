# HANDOFF

Orientation note (FRAMEWORK §5.1). Replaced at every clean close; no session history here (that
is `docs/ledger/session-log.md`). The banner carries exactly one session key.

## Banner (2026-10-12e)

- **This repo builds the whole framework** in `docs/framework/FRAMEWORK.md`, to deploy across
  all the owner's repos (charter confirmed and widened, DEC-10). The record engine (§8.0) is
  the first piece. **Since 2026-10-08f it runs this repo's own records** (CE-8, DEC-7 amended).
- **FRAMEWORK.md holds the framework only (DEC-26, 2026-10-11c):** a summary and section guide
  on top, then §0 to §11; no history, prior art, owner Q&A or change log. Change it in place;
  the why goes in a decision or story. The pre-trim text (with the old §11.3, §12 owner answers
  and §13 changelog) is frozen in `FRAMEWORK-v0.5.md`; older records citing §12/§13 mean that file.
- **The command is `context-engine`** (DEC-15; `ce` before). Older records keep `ce`.
- **State:** CE-1, CE-2, CE-3, CE-8, CE-15, CE-16, CE-20..23 done; **since 2026-10-12d also
  CE-24 (rituals runbook), CE-5 (decision records) and CE-14 (guard catalogue)**; **since
  2026-10-12e also CE-10 (CI: `.github/workflows/gate.yml`, first run watched green) and CE-37**.
- **Priorities:** NOW CE-30 (coverage guard; the owner's pick, design review written). **NEXT is
  empty: the owner picks** (candidates: CE-7 adhoc trial, whose deps are built; CE-25). The
  chain that matters is CE-7 -> CE-11. Open rows filed since 2026-10-12d: CE-31 (refuse
  reopening an answered ASK), CE-32 (op to set decision frontmatter), CE-33 (G-D4, G-D5), CE-34
  (G-T5 mutation), CE-35 (op to remove or rewrite a decision link), CE-36 (task close warns when
  NOW would be left empty).
- **Session start shows the owner every other open session** (US-16, CE-37, 2026-10-13): one
  line each, or "none"; the session stops or closes none without the owner's word. 2026-10-12e
  was found that way: its conversation was cleared without a close, and a later one adopted the
  key and closed it. Marking a dead stub `abandoned` is still by hand (CE-6, G-W11).
- **Rituals: the order lives in `docs/runbooks/rituals.md`** (CE-24, US-15): every ritual's steps,
  engine command and by-hand step side by side; FRAMEWORK §6 keeps rules and reasons, its step
  numbers are stable labels (P3). `manual-mode.md` has the by-hand detail per operation. Both
  runbooks carry no repo ids and ship in the kit. When the engine errors, do the step by hand
  and fix the engine (US-11). `lint` is in the gate.
- **Decision records (CE-5):** `record correct` (insertions only; G-D10 hashes the body with
  corrections undone, so `body_sha` is never replaced), `decision supersede|link|find|show|import`,
  `why`, and a generated index checked by G-D6. Link targets must be records or criteria rows.
- **Guards (CE-14):** `src/context_engine/guards.py` runs G-D1/D2/D3/D7/D8/D9/T3/W7 in lint;
  `[guards]` in `context.toml` switches them off or scopes their paths. G-T3 checks current
  decisions' `code:` links.
- **Deploy path (CE-15):** the adoption kit is package data at `src/context_engine/kit/`;
  `context-engine init` writes it (runbooks included since CE-24) into a target repo, never
  overwrites, never touches the target env (DEC-1). Copied runbooks go stale on upgrade (INV-13).
  There is no release tag yet (owner's call).
- **G-D0 (CE-21):** lint checks the contract's `framework:` line(s) and kit-block marker against
  the engine's major.minor; the contract path is `[engine] contract` (default `CLAUDE.md`).
- **Design review and register (CE-23, P17/P18, US-14):** work above the review threshold needs
  a `review:` field and a `## Design review` **before promote** or close; residual risks move to
  the register on close as `INV-n` (DEC-27; INV-1..21 so far). CE-14 was promoted before its
  review (recorded in its Log; INV-4 covers the risk): check `review:` before promoting.
- **The MCP server is built (CE-3):** `mcp__context-engine__<group>_<verb>`, one tool per
  operation in `ops.OPS`; exceptions are named in `rituals.md` (e.g. `baton expire` is
  `hk_expire_batons`). New ops from CE-5/CE-14 appear after Claude Code restarts. Call
  `session_start` first. Actors must be plain `<producer>/<version>`.
- **Several tasks in one request → the top level coordinates, it does not do** (DEC-16, trial).
  2026-10-12d ran four tasks as one sequential workflow, build -> adversarial review -> fix per
  task; the reviewer found a real defect in every task. Ultracode has standing approval when it
  keeps the session's tokens down (DEC-17).
- **History was rewritten on 2026-10-09c.** A checkout made before it must
  `git fetch origin && git reset --hard origin/main`; old SHAs quoted in text no longer resolve.
- **Anti-goal:** a server the owner starts or manages. Claude Code may start one as a ritual.
- **No owner questions are open.** For the owner's glance (CE-7 inputs): adhoc D-27 was imported
  as wholly SUPERSEDED though only its gate backend was; rituals.md sets provisional by-hand
  conventions for foreign/abandoned ledger entries and a default stale-stub window (CE-6).
- **Owner rules in force:** no `fable` subagents unless asked or really necessary (DEC-18);
  every programmatic process has a ritual fallback (DEC-20, P16); an after-action review per
  session is a first note, not designed (US-12, §6.12).
- **The repo is PUBLIC. Ask before every push; push only on a green gate.** One task per commit,
  its id leading the title, a `Session:` trailer on every agent commit (DEC-22, CE-22). The
  engine's major.minor is the framework version (DEC-23, G-D0). Any session closes a baton with
  evidence (DEC-24). Pushed to 058fee7 (CI green); 2026-10-12e's commits (ab0b155 on) are not pushed yet.

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
