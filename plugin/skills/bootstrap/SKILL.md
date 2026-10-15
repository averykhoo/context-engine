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

What sessions miss here, word for word from the runbook (the engine's gate checks each line):
- Install the engine into its own environment, pinned to a release tag or commit
- put the real test command into `CLAUDE.md` § Gate
- Lint is green, then commit the kit's files by path, before the first session
- Every number you add there (a cap, a budget, a window) needs one ... then the literal words
  `; wrong if <what would show it is wrong>`
