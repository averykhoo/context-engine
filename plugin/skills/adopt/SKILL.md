---
name: adopt
description: Use when the owner wants an EXISTING repo - one with its own decision log, board, handoff notes or contract - brought under the context-engineering framework (context-engine). Adoption maps the framework onto the repo's files instead of moving them (FRAMEWORK §11.4) - pinned engine, init, the gate, routes and caps, importing decisions, board rows and questions, trimming the handoff note.
---

# Adopt an existing repo

Runbook: `kit/README.md` § 3. An existing repo: map, don't move
Runbook: `kit/README.md` § 2a. Bootstrap with the engine
Runbook: `docs/runbooks/procedures.md` § Bootstrap
Runbook: `kit/README.md` § Hook

These live in the installed engine's kit until `init` copies the runbooks: its path is printed by
`<engine-python> -c "import context_engine, pathlib; print(pathlib.Path(context_engine.__file__).parent / 'kit')"`.
Do the bootstrap rows in order, with § 3 of the kit README for every step that meets something
the repo already has.

The traps the first adoption hit (CE-7's dry run, `docs/evidence/adhoc-dryrun-2026-10-14.md` in
the engine repo), word for word from the runbook (the engine's gate checks each line):
- Before `init`, show the owner the plan (`init --dry-run`), and ask before each step that rewrites
  the repo's own files.
- Install the engine into its own environment, pinned to a release tag or commit
- The repo's own gate must be green where you work: data it needs may be gitignored, so a fresh
  clone or worktree can be red before you start.
- When the file already exists it holds the owner's permission grants ... show the owner, then run
  `init --merge-settings` (yes) or `init --skip-settings` (no).
- A `CLAUDE.md` that already has its own Gate (a level 1 or 2 heading reading `Gate`) keeps it as
  the one gate ... check that gate ends with `&& context-engine lint`
- each `[[routes]]` `path` points at the existing file for that component
- Every number you add there (a cap, a budget, a window) needs one
- `decision import <log> --dry-run`: save everything under its "Save everything below" line as a
  FROZEN evidence doc (the id map). ... review every entry it reports as set BUILT by default ...
  Retire the old log (a line pointing at the records) and rewrite the repo's own instructions that
  say to append to it
- Board items and open questions: `task new` or `ask new`, with `--id` to keep a number
- Move the durable facts out of the repo's old handoff note before the first `banner set` replaces
  it, and keep the banner short, so `orient` still shows the batons and the board.
