# context-engine: contract

framework: 0.5-draft (engine mode since 2026-10-08f, CE-8; manual mode is the fallback, US-11)

This repo builds the record engine specified in `docs/framework/FRAMEWORK.md` (§8.0), and runs
that framework on itself **through the engine** (`context-engine`). What is true now and what is next live in
`HANDOFF.md`; this file holds only what is durable.

## Where things live

The routing table is `[[routes]]` in `context.toml`; print it with `context-engine routes`. Lint (G-R1) fails
if a routed path disappears. Record kinds, their directories and schemas are `[kinds.*]` in the
same file. In short: the spec is `docs/framework/FRAMEWORK.md`; owner words are stories
(`docs/stories/`) and decisions (`docs/decisions/`), both append-only; the board is `tasks/`;
the ledger and op log are `docs/ledger/`; `docs/runbooks/manual-mode.md` does every `context-engine`
operation by hand.

**Id prefixes** (zero collisions on 2026-10-08, DEC-7): tasks `CE-n`, decisions `DEC-n`,
stories `US-n`, criteria `AC-n`, owner questions `ASK-n`. Never reuse or renumber an id.
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

## Gate

`<interpreter> -m pytest -q` from the repo root. Run it before every commit that touches
`src/`, `tests/` or any record, and before every push. It includes `context-engine lint` on this repo's own
records (AC-23), so a hand edit to a stamped story, a broken record or a dead route turns it red.

## Sabotage rule (owner mandate, DEC-11)

**No test or guard is believed until it has been seen to fail.** For every new test, guard or
refusal: break what it protects (edit the code, corrupt the fixture, drop the check), run it and
watch it go red for the right reason, then restore. Record it in the commit message as
`Sabotage: <what was broken> -> <test> red`. A criterion moves to `tested` only after its
claiming test was sabotaged. When G-T5 (mutation per criterion, CE-14) exists, it does this
mechanically and this hand step becomes its fallback.

**Run every scripted sabotage with a fresh bytecode cache** (`PYTHONPYCACHEPREFIX=<new temp
dir>`, as `tools/sabotage_ce2.py` does). Python trusts a `.pyc` whose source has the same size
and the same mtime second, so a same-length sabotage written right after a restore runs the
old code and passes: a false green, seen 2026-10-08d.

## Rituals (FRAMEWORK §6, through `context-engine`)

Every step below is a `context-engine` command. **When `context-engine` errors or refuses something it should allow, do
that step by hand from `docs/runbooks/manual-mode.md` (its section has the same name), then fix
the engine** (runbook § When the engine and this runbook disagree). A refusal with a sensible
remedy is not an error: follow the remedy.

**Session start:** `context-engine session start` (prints the key; use it as `CE_SESSION`), then `context-engine orient`.
Do the batons and pauses it lists first. Raise every question it lists in chat, one line each,
then `context-engine ask raised <ids>`. Read the NOW item with `context-engine task show <id>`.

**Owner gives intent** (§6.2): record it **verbatim, now**, then tell the owner in one line which
it became.
- Behaviour-shaped: `context-engine record new story "<title>" --file <words.md> --set actor=owner --set
  story_status=live --set goals=[G..]`, or `context-engine record amend US-n "<words>"` on an existing story.
- Choice-shaped: `context-engine record new decision "<title>" --file <words.md> --set actor=owner --set
  decision_status=PROVISIONAL`, or a charter edit.
- An answer to an `ASK-n`: `context-engine ask answer ASK-n "<words>" --title "<decision title>"`.
- Write owner words to a file with the Write tool, not a heredoc (heredocs here can mangle
  backslashes and quotes).

**Clean close** (§6.3), in this order:
0. Every owner word from this session is recorded.
1. The board: `context-engine task touch|comment|promote|close|section` on every item this session moved
   (the engine bumps `moved`/`updated` and enforces NOW = 1, NEXT <= 5). `context-engine task list` is the
   board; HANDOFF keeps no copy.
2. Anything skipped: `context-engine baton add "<step>" --why "<why>"`.
3. Durable rules come here; method lessons go into a runbook.
4. Gate, then `context-engine session close --rows ... --summary ... (one per line, at most 7) --guards
   "<gate result>" --read "<what was read>" --asked "<ids>" --owed ...`.
5. The banner: `context-engine banner show`, then `context-engine banner set --seen <hash> --file <banner.md>`. If it
   refuses, another session wrote it: read theirs, merge, retry.
6. `context-engine lint` and the gate again, then commit by path. **Push whenever, while the repo has no
   CI** (owner, 2026-10-08: *"if there's no cicd then push whenever for now"*); once CE-10 adds
   CI, ask again, because the repo is private and its CI minutes are limited. Every push gets a
   CI watcher (global `CLAUDE.md`).
7. The digest in chat.

**Pause** (§6.4): owner words recorded, evidence out of `.scratch/`, `context-engine pause open --in-flight
"<what>" --resume "<first step>"` (it commits its own record), then `context-engine session pause --rows ...
--deferred "<what was skipped>"`; commit the ledger by path.

## Rules

- **Several tasks in one request** (DEC-16, FRAMEWORK §6.6): one subagent per task; it hands
  the work to its own subagents or a workflow; the top level only reports progress, blockers
  and delays. Owner words and first-hand verification stay at the top.
- Commit by path (`git commit -o <paths>`); never `git add -A`, never `git stash`.
- Re-run `git status` and `git log -3` right before editing HANDOFF or the ledger and before
  committing: sessions here may run concurrently.
- Frozen provenance is never edited (`context-engine routes`).
- Never hand-edit what an operation owns: `body_sha`, `type`, `id`, a board item's `state`,
  `status`, `pri`, `deps`, `moved`, `updated`; a story's or decision's text above
  `## Amendments`. Lint catches most of it; the rest is in the runbook's "What every write does".
- `spike/` holds probes whose findings are transcribed into the spec; the probes are kept as
  evidence of how a finding was reached.
- Cite code as `file::symbol`, never by line number; grep that a symbol exists before citing it.
