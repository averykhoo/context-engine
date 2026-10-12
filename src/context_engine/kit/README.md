# The adoption kit

How a repo gets the framework (FRAMEWORK.md §6.9, §10, §11). The kit is text: everything here
can be copied by hand, and `context-engine init` copies it for you. Nothing in it is a server or
a process the owner starts: Claude Code starts the engine's MCP server itself, per session.

| Kit file | Goes to | What it is |
|---|---|---|
| `context.toml.template` | `context.toml` | the config, and its schema: every key the engine reads |
| `contract.md` | appended to `CLAUDE.md` | the framework block: `framework:` line, environment, gate, rituals, rules |
| `HANDOFF.md` | `HANDOFF.md` | the orientation note, with no banner yet |
| `docs/charter.md` | `docs/charter.md` | the charter, goals with `G-n` ids |
| `docs/criteria.md` | `docs/criteria.md` | the criteria table and how a test claims one |
| `docs/ledger/session-log.md` | `docs/ledger/session-log.md` | the empty session ledger |

`init` also creates `docs/decisions/`, `docs/stories/`, `docs/working/`, `docs/runbooks/`,
`docs/evidence/` and `tasks/` (each with an empty `.gitkeep`), and `.context/` and `.scratch/`
(each with a `.gitignore` holding `*`, so they ignore themselves).

## 1. Install and pin the engine

The engine runs from **its own environment** and is pointed at the repo. It is never installed
into the target repo's environment, and the target repo never imports it.

```
<python3.12+> -m venv <engine-env>            # or: conda create -n context-engine python=3.12
<engine-env-python> -m pip install "context-engine @ git+https://github.com/averykhoo/context-engine@<tag-or-commit-sha>"
```

**The pin** is two things: the ref in that install line (a release tag once there are releases;
a full commit SHA until then), and the `framework: <major.minor>` line in `CLAUDE.md`, which
must match the engine's major.minor (`context-engine lint` checks it, and the kit block's marker
version, as G-D0). Write the ref into the first ledger entry's summary, so the
repo records which engine it was bootstrapped with.

The MCP server is optional (FRAMEWORK §11.1: not in the minimum set until the §8.0.3 trial
reports); the CLI carries every operation. To use it, register it once per machine, from the
repo root:

```
claude mcp add --scope local context-engine -- <engine-env-python> -m context_engine.mcp
```

This lives in `~/.claude.json`, not in the repo, because the interpreter path is machine-specific.
Restart Claude Code once; from then on it starts the server in every session. Until the restart,
use the CLI: `<engine-env-python> -m context_engine <group> <verb>`, with `CE_ACTOR` and
`CE_SESSION` set.

## 2a. Bootstrap with the engine

From the repo root:

```
<engine-env-python> -m context_engine init [--prefix kind=P ...] [--dry-run]
```

It writes every kit file the repo is missing and prints one line naming what it created and what
it skipped. It never overwrites a file. It appends the contract block to an existing `CLAUDE.md`
only when no kit block is there (`<!-- context-engine kit <version> begin -->`); a block from an
older kit is left for the upgrade to replace (§4), never doubled. An existing `context.toml` is
kept if it loads (init refuses one that does not, or one whose prefixes disagree with
`--prefix`), and init then writes only the files and directories that config points at, so it
can be re-run after the config is edited. `--prefix` changes a kind's id series
(`--prefix task=PRJ`): pick prefixes no id already in the repo uses.

Then:
1. Fill `docs/charter.md` with the owner (goals get `G-n` ids).
2. Replace `<this repo's own test command>` in the `CLAUDE.md` block with the real one, and read
   every `provenance:` note in `context.toml`.
3. `context-engine lint` is green; `context-engine session start` opens the first session.
4. The first clean close (FRAMEWORK §6.3): `session close`, then `banner show` (it says
   `no banner yet`, hash `none`) and `banner set --seen none --file <banner.md>`, which writes the
   `## Banner (<key>)` heading. Commit by path.

## 2b. Bootstrap by hand

Copy each kit file to where the table above says, with `contract.md` appended to `CLAUDE.md`
(create it if absent). Create the empty directories with a `.gitkeep`, and `.context/.gitignore`
and `.scratch/.gitignore` each holding the single line `*`. To change an id prefix, edit `prefix`
in that kind's `[kinds.<name>]` table; no two kinds may share one. Then follow steps 1 to 4
above, doing each operation by hand from the engine repo's `docs/runbooks/manual-mode.md`.

## 3. An existing repo: map, don't move (FRAMEWORK §11.4)

`init` writes only what is missing, so run it (or copy by hand), then edit `context.toml` in
place:
- each kind's `dir` and `prefix` point at the records and id series the repo already has. Ids are
  never renumbered: an existing `D-n` series stays `D-n`;
- each `[[routes]]` `path` points at the existing file for that component;
- a skeleton `init` wrote for a component the repo keeps elsewhere is deleted, not routed.

`context-engine lint` then shows what still disagrees (dead routes, records that break the
schema). Back-filled stories are reconstructions, never the owner's words (§11.4).

## 4. Upgrade (FRAMEWORK §8.0)

1. Reinstall the engine in its own environment at the new ref.
2. Bump `framework:` in `CLAUDE.md` if the engine's major.minor moved, and replace the block
   between the kit markers with the new kit's `contract.md`.
3. `context-engine lint`; fix every red (the config refuses keys it does not know, so a renamed
   key shows up here; G-D0 names a `framework:` line or kit block the new engine does not match).
4. Write a ledger line naming the new ref (in the session's close summary).

## 5. The gate

`<this repo's own test command> && context-engine lint`, from the repo root, before every
commit that touches code, tests or records, and before every push. Guards the engine does not
run yet are checked by hand (FRAMEWORK §11.1).

## Runbooks

The by-hand fallback for every engine operation is `docs/runbooks/manual-mode.md` in the engine
repo, at the pinned ref; copy it into `docs/runbooks/` if the repo must work without the engine.
The kit does not ship it yet. The ritual order is FRAMEWORK §6.1 to §6.4. Neither file is
installed with the engine: read them in the engine repo at the pinned ref.

## Skills, workflows and agents

The kit ships no `.claude/skills/`, `.claude/workflows/` or `.claude/agents/`; a repo adds them
when it needs them (FRAMEWORK §10, §11.2), and commits them.
