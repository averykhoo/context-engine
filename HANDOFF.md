# HANDOFF

Orientation note (FRAMEWORK §5.1). Replaced at every clean close; no session history here (that
is `docs/ledger/session-log.md`). The banner carries exactly one session key.

## Banner (2026-10-13a)

- **This repo builds the whole framework** in `docs/framework/FRAMEWORK.md`, to deploy across
  all the owner's repos (charter confirmed and widened, DEC-10). The record engine (§8.0) is
  the first piece. **Since 2026-10-08f it runs this repo's own records** (CE-8, DEC-7 amended).
- **FRAMEWORK.md holds the framework only (DEC-26, 2026-10-11c):** a summary and section guide
  on top, then §0 to §11; no history, prior art, owner Q&A or change log. Change it in place;
  the why goes in a decision or story. The pre-trim text (with the old §11.3, §12 owner answers
  and §13 changelog) is frozen in `FRAMEWORK-v0.5.md`; older records citing §12/§13 mean that file.
- **The command is `context-engine`** (DEC-15; `ce` before). Older records keep `ce`.
- **State:** CE-1, CE-2, CE-3, CE-5, CE-8, CE-10, CE-14..16, CE-20..24, CE-37 done; **since
  2026-10-13a also CE-30 (G-D12 coverage guard), CE-31, CE-32 (`decision set`), CE-35
  (`decision relink`) and CE-36 (close warns when NOW is left empty)**.
- **Priorities:** NOW CE-25 (intent-chain guards; design review written, **blocked on ASK-3**: five
  owner calls, each with a recommendation). NEXT: ASK-3, CE-38 (bootloader contract, US-17: before
  CE-7, which now depends on it), CE-33 (G-D4, G-D5), CE-26 (method runbooks). The chain that
  matters is CE-38 -> CE-7 -> CE-11. Filed 2026-10-13a: CE-39 (agent roster, the `fable` arbiter
  included), CE-40 (move framework rules out of the owner's global CLAUDE.md), CE-41 (G-D3 checks
  bare file names against stale `build/` copies: cite `src/...` paths in full).
- **US-17: the framework runs from files it owns.** CLAUDE.md is to carry a bootloader pointer
  (`@`-import of a framework-owned contract, a SessionStart hook running orient). Grants stay in
  owner-loaded files, never MCP output or orient (DEC-30); what Claude Code documents is in
  `docs/evidence/claude-code-hooks-2026-10-13.md`.
- **Session start shows the owner every other open session** (US-16, CE-37): one line each, or
  "none"; the session stops or closes none without the owner's word. Marking a dead stub
  `abandoned` stays by hand (DEC-29: window to be 3 later sessions counted from the stub's last op,
  when CE-6 builds it).
- **A session closes by default when its requested work is done** (DEC-31, FRAMEWORK §6.3,
  rituals § Clean close); more work after a close starts a new session.
- **Rituals: the order lives in `docs/runbooks/rituals.md`** (CE-24, US-15). `manual-mode.md` has
  the by-hand detail per operation. Both carry no repo ids and ship in the kit, byte-equal. When
  the engine errors, do the step by hand and fix the engine (US-11). `lint` is in the gate.
- **Decision records:** `record correct`, `decision supersede|link|relink|set|find|show|import`,
  `why`, and a generated index (G-D6). A `code:` link must name a repo file and symbol, written
  with `/` (CE-35). An answered ASK never reopens; change its decision instead (CE-31).
- **Guards:** `src/context_engine/guards.py` runs G-D1/D2/D3/D7/D8/D9/D12/T3/W7 in lint;
  `[guards]` in `context.toml` switches them off or scopes their paths. G-D12 needs every
  FRAMEWORK component, ritual and G-id in the newest coverage map or a board item body.
- **Deploy path (CE-15):** the adoption kit is package data at `src/context_engine/kit/`;
  `context-engine init` writes it into a target repo, never overwrites, never touches the target
  env (DEC-1). Copied runbooks go stale on upgrade (INV-13). No release tag yet (owner's call).
- **Design review and register (CE-23, US-14):** work above the review threshold needs a
  `review:` field and a `## Design review` **before promote** or close; residual risks move to
  the register on close as `INV-n` (DEC-27; INV-1..27 so far).
- **The MCP server is built (CE-3)**, one tool per operation in `ops.OPS`. **A server started
  before 2026-10-13a refuses `session_start` (route key `max_bytes`): restart Claude Code**; until
  then use the CLI. The new ops and the "ask for ultracode" instruction (DEC-30) appear on restart.
- **Several tasks in one request → the top level coordinates, it does not do** (DEC-16, FRAMEWORK
  §6.6). 2026-10-12d and 2026-10-13a ran tasks as one sequential workflow, build -> adversarial
  review -> fix; the reviewer found a real defect in every task both times. Ultracode has standing
  approval when it keeps the session's tokens down (DEC-17, DEC-30).
- **History was rewritten on 2026-10-09c.** A checkout made before it must
  `git fetch origin && git reset --hard origin/main`; old SHAs quoted in text no longer resolve.
- **Anti-goal:** a server the owner starts or manages. Claude Code may start one as a ritual.
- **Owner rules in force:** `fable` only when the owner asks, for the arbiter role or the hard
  parts of proofs (DEC-18 amended), or when really necessary; every programmatic process has a
  ritual fallback (DEC-20, P16); an after-action review per session is a first note (US-12).
- **The repo is PUBLIC. Ask before every push; push only on a green gate.** One task per commit,
  its id leading the title, a `Session:` trailer on every agent commit (DEC-22, CE-22). Any session
  closes a baton with evidence (DEC-24). Pushed to 058fee7 (CI green); everything from ab0b155 on
  (2026-10-12e and 2026-10-13a) is not pushed yet.

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
