---
name: bootstrap
description: Use when the owner wants a NEW repo, or one with no records worth keeping, brought under the context-engineering framework (context-engine) - "set up the framework here", "bootstrap this repo". Bootstrap (FRAMEWORK §6.9) - charter, pinned engine install, init, gate, first session, first board, first clean close. For a repo with its own decisions, board or handoff notes, use the adopt skill.
---

# Bootstrap

Runbook: `docs/runbooks/procedures.md` § Bootstrap
Runbook: `kit/README.md` § 2a. Bootstrap with the engine

Before `init` the repo has no runbooks of its own: read both from the installed engine's kit. Its
path is printed by `<engine-python> -c "import context_engine, pathlib;
print(pathlib.Path(context_engine.__file__).parent / 'kit')"`, and the procedures runbook is
`docs/runbooks/procedures.md` under it. After `init` the repo's own copy is the source. Do the
rows in order; the "By hand" column is the fallback when the engine errs.

What sessions miss here:
- the engine is installed pinned into the repo's own folder (`.context-engine/env/`, gitignored),
  never into the repo's own environment (DEC-1, DEC-41);
- the real test command goes into `CLAUDE.md` § Gate, and the kit is committed by path, before the
  first session;
- every cap added to `context.toml` carries a provenance note with its `wrong if` clause.
