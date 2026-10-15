# context-engine: contract

<!-- context-engine kit 0.5 begin -->
framework: 0.5

This repo runs the context-engineering framework through `context-engine`. Its rules are the file
imported on the next line, which the framework owns: an upgrade replaces it whole, so it is never
edited here, and this repo's own rules go in this file, outside these markers. If those rules are
not in your context, read that file; if it is missing, run the engine's lint
(`<engine-python> -m context_engine lint`), which names the fix.

@docs/framework/contract.md
<!-- context-engine kit 0.5 end -->

Engine mode since 2026-10-08f (CE-8); manual mode is the fallback (US-11).

This repo builds the record engine specified in `docs/framework/FRAMEWORK.md` (§8.0), and runs
that framework on itself **through the engine** (`context-engine`). What is true now and what is next live in
`HANDOFF.md`; this file holds only what is durable.

## Where things live

The routing table is `[[routes]]` in `context.toml`; print it with `context-engine routes`. Lint (G-R1) fails
if a routed path disappears. Record kinds, their directories and schemas are `[kinds.*]` in the
same file. In short: the spec is `docs/framework/FRAMEWORK.md`; owner words are stories
(`docs/stories/`) and decisions (`docs/decisions/`), both append-only; the board is `tasks/`;
the ledger and op log are `docs/ledger/`; `docs/runbooks/procedures.md` gives every
procedure's steps in order and `docs/runbooks/manual-mode.md` does every `context-engine`
operation by hand; both are copies of the kit's (`src/context_engine/kit/docs/runbooks/`), kept
byte-equal by the gate.

**Id prefixes** (zero collisions on 2026-10-08, DEC-7): tasks `CE-n`, decisions `DEC-n`,
stories `US-n`, criteria `AC-n`, owner questions `ASK-n`, residual-risk register entries
`INV-n` (DEC-27), batons `BTN-n`, pause records `PAU-n`, goals `G-n`. Never reuse or renumber an id.
OKF reserves `status`: use `state`, `decision_status`, `story_status`, `charter_status`.

## Environment

- Interpreter: `C:/Users/user/anaconda3/envs/context-engine/python.exe` (Python 3.12).
  Bare `python` is broken on this machine; always use the full path.
- Install for development: `<interpreter> -m pip install -e ".[dev]"`.
- **The engine runs from its own env and is pointed at a repo; it is never installed into a
  target repo's environment** (DEC-1).
- **`context-engine` below means `<interpreter> -m context_engine`** (the `context-engine` script is not on PATH). Set
  `CE_ACTOR=claude-code/<model-id>` and `CE_SESSION=<key>` in every command: shell state does
  not persist between tool calls.
- **The MCP server** (CE-3) carries the same operations as `mcp__context-engine__<group>_<verb>`
  tools (`session_start`, `task_list`, ...). Call `session_start(actor=...)` first: the server
  remembers the key and actor, and a subagent passes its own `actor`.
- **If the MCP tools are missing at session start, set the server up, use the CLI for this
  session, and ask the owner to restart Claude Code** (DEC-25). Set-up is one command, run once
  per machine: `claude mcp add --scope local context-engine -- <interpreter> -m
  context_engine.mcp` (stored in `~/.claude.json` for this project; no env var, no new
  terminal). `.mcp.json`'s `${CE_PYTHON}` also works, but only from the environment Claude Code
  was started in: an `env` block in `.claude/settings.local.json` does NOT reach it (tested
  2026-10-10d). Neither takes effect until Claude Code restarts.

## Gate

`<interpreter> -m pytest -q` from the repo root; it runs `context-engine lint` on this repo's records too (AC-23). Run it
as `context-engine gate run` (CE-78: `[gate]` in `context.toml`), which records the result against the `code` scope's
content id. Before a commit touching `src/`, `tests/` or a record, `context-engine gate status --require code` says if
the whole gate is left; after a hand edit to a file the scope excludes, `--require code+readers` (`gate run --readers`).
`context-engine commit` refuses a code path until `code` is green; `tests/conftest.py` fails other tests that read them.
Every push runs the whole gate, and so does CI (`.github/workflows/gate.yml`, CE-10): a clean checkout, Python 3.12 (the
`requires-python` floor), `pip install -e ".[dev]"`, then the gate; `tests/test_ci.py` keeps the workflow in step with
this section and `pyproject.toml`. A red CI run is a red gate; without CI, run those two commands in a fresh 3.12 env.
**Before every push, also run CI's job on Linux here:** `<interpreter> tools/linux_gate.py` (CE-67; Docker in WSL, about
a minute once the image is cached). This machine is Windows and CI is Linux, so a green local gate can be a red CI run
(`39e09ca`, 2026-10-13; `docs/evidence/ci-divergence-2026-10-13.md` names the traps). Push only when both are green.

## Sabotage rule (owner mandate, DEC-11)

**No test or guard is believed until it has been seen to fail.** For every new test, guard or
refusal: break what it protects (edit the code, corrupt the fixture, drop the check), run it and
watch it go red for the right reason, then restore. Record it in the commit message as
`Sabotage: <what was broken> -> <test> red`. A criterion moves to `tested` only after its
claiming test was sabotaged. When G-T5 (mutation per criterion, CE-34) exists, it does this
mechanically and this hand step becomes its fallback.

**Run every scripted sabotage with a fresh bytecode cache** (`PYTHONPYCACHEPREFIX=<new temp
dir>`, as `tools/sabotage_ce2.py` does). Python trusts a `.pyc` whose source has the same size
and the same mtime second, so a same-length sabotage written right after a restore runs the
old code and passes: a false green, seen 2026-10-08d.

## Procedures (FRAMEWORK §6, through `context-engine`)

**Session start:** as the contract says, in the order `docs/runbooks/procedures.md` gives: the hook
prints orient, a session that already holds a key keeps it, otherwise `context-engine session start`.

**Every procedure's steps, in order, are in `docs/runbooks/procedures.md`, and only there**:
intake, clean close, pause, resume, push and CI, bootstrap, reconciling foreign commits,
housekeeping. Each step gives its `context-engine` command, its by-hand step in
`docs/runbooks/manual-mode.md`, and why it is done. **When `context-engine` errors or refuses
something it should allow, do that step by hand from the runbooks, then fix the engine**
(manual-mode § When the engine and this runbook disagree). A refusal with a sensible remedy is
not an error: follow the remedy.

This repo's values for those steps:
- `<gate>` is `<interpreter> -m pytest -q` (§ Gate above); lint runs inside it.
- Owner intent (procedures § Intake): `context-engine record new story "<title>" --file <words.md>
  --set actor=owner --set story_status=live --set goals=[G..]`, `context-engine record amend US-n
  --file <words.md>`, `context-engine record new decision "<title>" --file <words.md> --set actor=owner
  --set decision_status=PROVISIONAL`, or `context-engine ask answer ASK-n --file <words.md> --title
  "<decision title>"`. Write owner words to a file with the Write tool, not a heredoc (heredocs
  here can mangle backslashes and quotes).
- Clean close: `context-engine task list` is the board; HANDOFF keeps no copy. `session close`
  takes one `--summary` per line of the digest, at most 7. **Ask before every push, and push only
  on a green gate** (DEC-22); every push gets a CI watcher (global `CLAUDE.md`).

## Rules

- **Never run `context-engine init` here** (it holds the kit's sources). Close eagerly, without asking (DEC-31).
- **Several tasks in one request** (DEC-16, FRAMEWORK §6.6): one subagent per task; it hands
  the work to its own subagents or a workflow; the top level only reports progress, blockers
  and delays. Owner words and first-hand verification stay with the top-level session.
- Commit by path through `context-engine commit <paths> -m ...` (a plain `git commit -o` only for paths no uncommitted op
  line names, and for a `code` path only on a green `gate status --require code`); never `git add -A`, never `git stash`.
- **Commits** (DEC-22): commit whenever progress is made, on a green gate unless a really huge
  change cannot be split. One task per commit, its id leading the title (`CE-n: what changed`);
  a commit serving no task has a plain title. Small tasks may be done together: gate green over
  all, then one commit per task by path (not surgical: a shared file goes with whichever task fits
  best, DEC-22). Every agent commit ends with a `Session: <key>` trailer; `Closes: CE-n` is on the
  engine's `task close` commit, made after the work is committed (CE-45).
- Re-run `git status` and `git log -3` right before editing HANDOFF or the ledger and before
  committing: sessions here may run concurrently.
- Frozen provenance is never edited (`context-engine routes`).
- Never hand-edit what an operation owns: `body_sha`, `type`, `id`, a board item's `state`,
  `status`, `pri`, `deps`, `moved`, `updated`; a story's or decision's text above
  `## Amendments`. Lint catches most of it; the rest is in the runbook's "What every write does".
- `spike/` holds probes whose findings are transcribed into the spec; the probes are kept as
  evidence of how a finding was reached.
- Cite code as `file::symbol`, never by line number; grep that a symbol exists before citing it.
- **No `fable` subagents** unless the owner asks or it is really necessary; never fan out with
  it; when necessary, minimize its cost (DEC-18, FRAMEWORK §6.6).
- **Keep `FRAMEWORK.md` current as we build** (DEC-19, §6.12): change in place; archive to
  `FRAMEWORK-v<version>.md` only what the future must reference. Every programmatic process has
  a by-hand fallback in a runbook (DEC-20, P16).
- **After-action review** (US-12, §6.12) is an open idea, not built: if a session has a note on
  what worked or could improve, put it in the ledger `summary:` for now.
