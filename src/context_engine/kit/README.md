# The adoption kit

LIVING. How a repo gets the framework (FRAMEWORK.md §6.9, §10, §11). The kit is text: everything here
can be copied by hand, and `context-engine init` copies it for you. Nothing in it is a server or
a process the owner starts: Claude Code starts the engine's MCP server itself, per session.

| Kit file | Goes to | What it is |
|---|---|---|
| `context.toml.template` | `context.toml` | the config, and its schema: every key the engine reads |
| `bootloader.md` | appended to `CLAUDE.md` | the kit block: the `framework:` line and an `@`-import of the contract; then a `## Gate` stub for the repo's own test command |
| `contract.md` | `docs/framework/contract.md` | the framework's rules (its Environment, Gate, Procedures and Rules sections), imported by `CLAUDE.md`; the framework's file, replaced whole on upgrade |
| `HANDOFF.md` | `HANDOFF.md` | the orientation note, with no banner yet |
| `docs/charter.md` | `docs/charter.md` | the charter, goals with `G-n` ids |
| `docs/criteria.md` | `docs/criteria.md` | the criteria table and how a test claims one |
| `docs/ledger/session-log.md` | `docs/ledger/session-log.md` | the empty session ledger |
| `docs/runbooks/procedures.md` | `docs/runbooks/procedures.md` | every procedure's steps in order, the engine command and the by-hand step side by side |
| `docs/runbooks/manual-mode.md` | `docs/runbooks/manual-mode.md` | every engine operation by hand, each step with its why |
| `docs/runbooks/gate.md` | `docs/runbooks/gate.md` | running the gate so its result is true, and the test baselines |
| `docs/runbooks/sabotage.md` | `docs/runbooks/sabotage.md` | seeing every new test, guard or refusal fail before believing it |
| `docs/runbooks/fan-out.md` | `docs/runbooks/fan-out.md` | delegating to agents, workflows, and the build rounds |
| `docs/runbooks/release.md` | `docs/runbooks/release.md` | tag, publish, confirm, and the fresh-user install trial |

`init` also writes the `SessionStart` hook (§ Hook) and creates `docs/decisions/`, `docs/stories/`, `docs/working/`, `docs/evidence/` and
`tasks/` (each with an empty `.gitkeep`), and `.context/` and `.scratch/`
(each carrying its own `.gitignore`, holding `*`). It appends `.context-engine/` (the engine's
environment, § 1) to the repo's own `.gitignore`, creating that file if it is absent, unless a
line there already ignores it.

## 1. Install and pin the engine

The engine runs from **its own environment** and is pointed at the repo. It is never installed
into the target repo's environment, and the target repo never imports it. **That environment is
`.context-engine/env/` in the repo's root**: a pinned, non-editable install of one engine
ref, kept inside the repo's folder and gitignored. Everything the repo runs lives in the repo, the
engine stays out of the repo's own environment, and a change to the engine's kit reaches the repo
only when its pin moves (§ 4). From the repo root:

```
<python3.12+> -m venv .context-engine/env     # or: conda create -y -p .context-engine/env python=3.12
<engine-python> -m pip install "context-engine @ git+https://github.com/averykhoo/context-engine@<tag-or-commit-sha>"
```

**`<engine-python>`**, the interpreter every step below names, is that environment's:
`.context-engine/env/bin/python` on Linux and macOS (venv or conda),
`.context-engine/env/Scripts/python.exe` for a venv on Windows, and
`.context-engine/env/python.exe` for a conda env on Windows. Tools that launch the engine look in
`.context-engine/env/` for it, in that order. Make it with a Python of the engine's
`requires-python` (3.12 or later), and never with `pip install -e`: an editable install follows
the engine repo's working tree, which is no pin.

**Ignore it:** `.context-engine/` must be in the repo's `.gitignore` before anything is committed,
or a commit can carry the whole environment. `init` (§ 2a) appends the line when nothing there
ignores it yet; by hand, add it yourself. The `.gitignore` is tracked, so every clone ignores the
environment too. **On a clone**, `.context-engine/env/` is absent: rebuild it with the two lines
above, at the ref the first ledger entry names (or the latest upgrade's ledger line, § 4). A repo
may copy those two lines, with its ref and its machine's paths, into its own `CLAUDE.md`, outside
the kit markers.

**The pin** is two things: the ref in that install line (a release tag once there are releases;
a full commit SHA until then), and the `framework: <major.minor>` line in `CLAUDE.md`, which
must match the engine's major.minor (`context-engine lint` checks, as G-D0, this line, the kit
block's marker version, the block's text and the imported contract). Write the ref into the first ledger entry's summary, so the
repo records which engine it was bootstrapped with.

The MCP server is optional (FRAMEWORK §11.1: not in the minimum set until the §8.0.3 trial
reports); the CLI carries every operation. To use it, register it once per machine, from the
repo root:

```
claude mcp add --scope local context-engine -- <engine-python> -m context_engine.mcp
```

This lives in `~/.claude.json`, not in the repo, because the interpreter path is machine-specific.
Restart Claude Code once; from then on it starts the server in every session. Until the restart,
use the CLI: `<engine-python> -m context_engine <group> <verb>`, with `CE_ACTOR` and
`CE_SESSION` set.

## 2a. Bootstrap with the engine

From the repo root:

```
<engine-python> -m context_engine init [--prefix kind=P ...] [--dry-run]
```

It writes every kit file the repo is missing and prints one line naming what it created and what
it skipped. It never overwrites a file. It appends `.context-engine/` to the repo's
`.gitignore` unless that already ignores it (§ 1), keeping the file's line endings. It appends
the kit block (`bootloader.md`) to an existing `CLAUDE.md` only when no kit block is there (`<!-- context-engine kit <version> begin -->`); a
block from an older kit, or the inline block of a kit from before `bootloader.md` (a block that
holds the rules themselves), is left for the upgrade to replace (§4), never doubled. A `CLAUDE.md`
that already has its own Gate (a level 1 or 2 heading reading `Gate`) keeps it as the one gate:
init appends the kit block without the bootloader's Gate stub, and says so. An existing `context.toml` is
kept if it loads (init refuses one that does not, or one whose prefixes disagree with
`--prefix`), and init then writes only the files and directories that config points at, so it
can be re-run after the config is edited. `--prefix` changes a kind's id series
(`--prefix task=PRJ`): pick prefixes no id already in the repo uses.

Then:
1. Fill `docs/charter.md` with the owner (goals get `G-n` ids).
2. Replace `<this repo's own test command>` in `CLAUDE.md` § Gate (below the kit block) with the
   real one (a `CLAUDE.md` with its own Gate got no stub: check that gate ends with
   `&& context-engine lint`), and read every `provenance:` note in `context.toml`. Every number
   you add there (a cap, a budget, a window) needs one as a comment on the number's own line, in
   the form lint (G-D9) checks:
   `# provenance: MEASURED <date, method>` or `# provenance: JUDGEMENT <why>`, then the literal
   words `; wrong if <what would show it is wrong>` (`wrong as above` for a run of lines). A note
   without `wrong if`, or one that cites an example, is red.
3. `context-engine lint` is green. Commit the kit's files by path: the engine commits its
   writes at milestones (FRAMEWORK §5.5 rule 4), but only once `context.toml` is tracked. The
   template's `commit = "milestones"` needs this engine or later on every machine: an older one
   refuses it (write `true` instead until they are upgraded). Then
   `context-engine session start` opens the first session.
4. The first clean close (FRAMEWORK §6.3): `session close`, then `banner show` (it says
   `no banner yet`, hash `none`) and `banner set --seen none --file <banner.md>`, which writes the
   `## Banner (<key>)` heading. Both are milestones, so the engine has committed them with
   every write before them; commit anything else the close changed with `context-engine commit
   <paths> -m "<message>"`, which takes any write still uncommitted with it.

## 2b. Bootstrap by hand

Copy each kit file to where the table above says, with `bootloader.md` appended to `CLAUDE.md`
(create it if absent) and `contract.md` copied to `docs/framework/contract.md`; add the hook
(§ Hook). Create the empty directories with a `.gitkeep`, and `.context/.gitignore`
and `.scratch/.gitignore` each holding the single line `*`, and add `.context-engine/` to the
repo's `.gitignore` (§ 1) if no line there ignores it. To change an id prefix, edit `prefix`
in that kind's `[kinds.<name>]` table; no two kinds may share one. Then follow steps 1 to 4
above, in the order `docs/runbooks/procedures.md` gives, doing each operation by hand from
`docs/runbooks/manual-mode.md` (both copied with the kit).

## Hook

A `SessionStart` hook runs `context-engine orient` and Claude Code puts its output in the
session's context at startup, resume, `/clear` and compaction, so the session-start read does not
rest on the agent remembering a rule. `init` writes it to `.claude/settings.local.json`, and
`.claude/.gitignore` (holding `settings.local.json`) beside it when that is absent, unless the
repo's own `.gitignore` already ignores the file; a merge into an existing file does the same, and
every later run that finds the hook with nothing ignoring it says so.
The command names this machine's engine interpreter and repo root, so the file is
machine-local, like the MCP registration: each clone runs `init` (or adds it by hand) once.
When the file already exists it holds the owner's permission grants (Claude Code writes them
there), so `init` changes it only with the owner's yes: without a flag it refuses, naming the one
entry it would append to `hooks.SessionStart` (`--dry-run` names it as a warning instead, beside
the rest of the plan); show the owner, then run `init --merge-settings`
(yes) or `init --skip-settings` (no). The merge parses the file strictly (it refuses, untouched,
a file that is not JSON, repeats a key, holds `NaN`, `Infinity` or a lone surrogate, sets
`disableAllHooks`, is hard-linked or read-only, or already runs orient with another command, such
as a moved repo's), keeps every other key and its order, re-reads the file right before an atomic
replace (a grant Claude Code writes in the instant between is lost: no lock is shared with it),
and is a no-op when the hook is there. By hand, add this entry, keeping every other key:

```json
{
  "hooks": {
    "SessionStart": [
      {"hooks": [{"type": "command", "command": "\"<engine-python>\" -m context_engine --root \"<repo root>\" orient"}]}
    ]
  }
}
```

Both paths are absolute, with forward slashes. The command runs under bash and cmd.exe; under
PowerShell a quoted program needs `& ` in front. A failing `SessionStart` hook is silent (Claude
Code shows its error to the user only, and the session goes on), so the contract keeps the
by-hand fallback: no orient output in the context means run `orient` and tell the owner.

## 3. An existing repo: map, don't move (FRAMEWORK §11.4)

`init` writes only what is missing, so run it (or copy by hand), then edit `context.toml` in
place:
- each kind's `dir` points at the records the repo already has, and its `prefix` is the
  framework's form, not the repo's old one: `DEC` for decisions and `ASK` for questions, and a
  task prefix of the repo's own (`init --prefix decision=DEC --prefix task=<yours>`). The old ids
  move over in the first session (below);
- each `[[routes]]` `path` points at the existing file for that component;
- a skeleton `init` wrote for a component the repo keeps elsewhere is deleted, not routed;
- a runbook `init` skipped because the repo already had a file of that name (`skipped` in its
  output) is now the framework's runbook of that name: the contract points agents at it and its
  route's caps apply. Merge the kit's copy into it by hand, or move the repo's own file aside
  and run `init` again;
- each doc the repo already had under `[guards] liveness` or `history` (G-D4: `HANDOFF.md`,
  `docs/runbooks`, `docs/evidence`) gets its liveness line near its top (LIVING, ACTIVE-PLAN or
  FROZEN), or a `liveness_given` entry when the repo may not edit its opening lines; list the repo's other
  docs under `liveness` too.

`context-engine lint` then shows what still disagrees (dead routes, records that break the
schema, docs that declare no liveness). Back-filled stories are reconstructions, never the owner's words (§11.4).

**The repo's existing ids** take the framework's form in the first session (every step needs
the session key), each keeping its number where it has one, and each old id stays in the
record's `aliases`, which `task show`, `decision show`, `why`, `decision find --links-to` and the
ids `decision link` and `decision supersede` take resolve, saying which record answered. History,
commit messages and code comments keep the old ids.
1. `decision import <log> --dry-run`: save everything under its "Save everything below" line as
   a FROZEN evidence doc (the id map). Under the prefix `DEC`, `D-27` becomes number 27 of that
   series with `aliases: [D-27]`; the rejected table's rows take new numbers and no alias.
2. Freeze the old log from now until the import is merged, then import without `--dry-run`, and
   review every entry it reports as set BUILT by default (`decision set <id> --set
   decision_status=<status>`).
3. Retire the old log (a line pointing at the records) and rewrite the repo's own instructions
   that say to append to it, then commit the import by path (`context-engine commit <paths> -m
   ...`): an import is not a milestone, so the engine does not commit it.
4. Board items and open questions: `task new` or `ask new`, with `--id` to keep a number (`Q8`
   as `--id ASK-8`), then `task set <id> --set aliases=[<old id>, ...]` (for a question too; a
   list may hold several, e.g. a rank and a slug, and the next `aliases=` replaces the whole list).
   An answered question stays history: its decision holds the answer.

## 4. Upgrade (FRAMEWORK §8.0)

1. Rebuild the engine's environment, `.context-engine/env/` (§ 1), at the new ref: with no
   session or MCP server running the engine from it (on Windows a running interpreter holds its
   files open), delete the directory and run § 1's two lines with the new ref; the hook and the
   MCP registration name the same interpreter path, so neither changes. A repo still on an
   environment elsewhere (from before this convention) moves it here now: build the new one, point
   the hook in `.claude/settings.local.json` (by hand, § Hook) and the MCP registration (§ 1) at
   its interpreter, and check `.gitignore` ignores `.context-engine/` (`init` adds the line).
   Delete the old environment only once nothing names it.
2. Copy the new kit's `contract.md` over `docs/framework/contract.md` (the framework's file: it is
   replaced whole, never merged). If the engine's major.minor moved, replace the text between the
   kit markers in `CLAUDE.md`, markers included, with the new kit's `bootloader.md` block. **From
   an inline block** (a kit from before `bootloader.md`, whose block holds the rules themselves):
   move its gate command to a `## Gate` section below the end marker first, then replace the
   block, then run `init`, which writes `docs/framework/contract.md` and the hook. Replace every
   runbook in `docs/runbooks/` with the new kit's copy, unless the repo edited its own (then merge
   by hand), and run `init` for any runbook the new kit adds. Copy every `[[routes]]` entry the
   new `context.toml.template` adds (a runbook's or any other component's) into `context.toml`
   too: lint cannot tell that one is missing. `init`
   never overwrites a runbook, so an upgrade is the only time they move. `[engine] commit` is a
   policy now (`"milestones"`, `"every-write"` or `"off"`, FRAMEWORK §5.5 rule 4). An older
   `true` reads as `"milestones"`, so the engine stops committing every write and commits at
   milestones: write `"every-write"` to keep the old behaviour. `false` reads as `"off"`. Keep
   `true` or `false` until every machine runs this engine: an older one refuses the words.
3. `context-engine lint`; fix every failure (the config refuses keys it does not know, so a renamed
   key shows up here; G-D0 names a `framework:` line, kit block or contract the new engine does
   not match).
4. Write a ledger line naming the new ref (in the session's close summary): it is the ref a
   clone rebuilds `.context-engine/env/` at.

## 5. The gate

`<this repo's own test command> && context-engine lint`, from the repo root, before every
commit that touches code, tests or records (the engine's own commits of its writes excepted;
your own `context-engine commit` does not run the gate, so run the gate before it),
and before every push. Guards the engine does not
run yet are checked by hand (FRAMEWORK §11.1).

## Runbooks

The kit ships the runbooks, and `init` copies them into the repo's `docs/runbooks/`, so a repo can
run the framework from its own tree with no engine (FRAMEWORK P16). The by-hand fallback:
- `procedures.md`: the order of every procedure (session start, intake, clean close, pause,
  resume, push and CI, bootstrap, reconciling foreign commits, housekeeping), each step with its engine command, its
  by-hand step and its why. It is the only place the order is written.
- `manual-mode.md`: every engine operation by hand, with its why; the reference for what the
  engine should have done when it errs.

The method runbooks (FRAMEWORK §7.5): `gate.md` (running the gate, and the test baselines),
`sabotage.md`, `fan-out.md` (delegation and the build rounds) and `release.md`. Each is routed on
its own in `context.toml`, with caps. None carries a repo value: the repo's test command, suites,
baselines outside the gate, models and release steps go in `CLAUDE.md`, which the runbooks point
at.

They are the repo's own copies from then on (see § 4 for upgrades).

## Skills, workflows and agents

The kit ships no `.claude/skills/`, `.claude/workflows/` or `.claude/agents/`; a repo adds them
when it needs them (FRAMEWORK §10, §11.2), and commits them.
