---
name: adopt
description: Use when the owner wants an EXISTING repo - one with its own decision log, board, handoff notes or contract - brought under the context-engineering framework (context-engine). Adoption maps the framework onto the repo's files instead of moving them (FRAMEWORK §11.4) - pinned engine, init, the gate, routes and caps, importing decisions, board rows and questions, trimming the handoff note.
---

# Adopt an existing repo

Runbook: `kit/README.md` § 3. An existing repo: map, don't move
Runbook: `kit/README.md` § 2a. Bootstrap with the engine
Runbook: `docs/runbooks/procedures.md` § Bootstrap

These live in the installed engine's kit until `init` copies the runbooks: its path is printed by
`<engine-python> -c "import context_engine, pathlib; print(pathlib.Path(context_engine.__file__).parent / 'kit')"`.
Do the bootstrap rows in order, with § 3 of the kit README for every step that meets something
the repo already has. Show the owner the plan before `init`, and ask before each step that
rewrites the repo's own files.

The traps the first adoption hit (CE-7's dry run, `docs/evidence/adhoc-dryrun-2026-10-14.md` in
the engine repo), as a checklist:
- **Pin the engine in the repo's folder** (`.context-engine/env/`, gitignored, DEC-41): an engine
  shared with another repo turns this repo's lint red whenever the kit changes there.
- **The repo's own gate must be green where you work**: data it needs may be gitignored, so a
  fresh clone or worktree can be red before you start.
- **`init --dry-run` first**; an existing `.claude/settings.local.json` holds the owner's grants,
  so merging the hook into it is the owner's call (`--merge-settings` or `--skip-settings`).
- **One gate**: if `CLAUDE.md` already has a Gate section, keep that one and end it with
  `context-engine lint`; delete the kit's stub.
- **Map, don't move**: point routes at the files the repo has; raise a cap only with a provenance
  note that says `MEASURED` or `JUDGEMENT` and `wrong if ...`.
- **Decisions**: `decision import <log> --dry-run`, save the id map as a FROZEN evidence doc, import,
  then review every entry it set BUILT by default; freeze the old log with a redirect line and
  rewrite every instruction that says to append to it.
- **Board and questions**: `task new` per row, the old id kept in `aliases`; questions keep their
  number with `ask new --id ASK-n`.
- **The handoff note**: move durable facts out of the old banner before the first `banner set`
  replaces it, and keep the banner short so orient still shows batons and the board.
