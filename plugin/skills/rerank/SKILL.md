---
name: rerank
description: Use in a repo run by context-engine (context.toml at its root) when orient says "rerank due" (NEXT holds no task), or when the owner asks to re-rank or reprioritise the board. The full re-rank (FRAMEWORK §5.2) - a ranking agent proposes moves against the charter's goals and next milestone, a second agent verifies, the coordinator applies promotes and demotes, drops wait for the owner, and the charter's Last rerank line is updated.
---

# Rerank

Runbook: `docs/runbooks/procedures.md` § Rerank

Open that section of this repo's own copy now and do its rows in order: it is the source, and its
"By hand" column is the fallback when the engine errs. This skill only points there and quotes it, so it never
disagrees with the runbook the repo is pinned to. `context-engine` means the engine command the
repo's contract names (`<engine-python> -m context_engine`, with `CE_ACTOR` and `CE_SESSION` set).

What sessions miss here, word for word from the runbook (the engine's gate checks each line):
- Every open item is read, so it costs tokens: run it once a sprint, not once a session.
- each with a one-line reason that cites a goal (`G-n`) or an exit criterion of the milestone
- A second, different agent verifies the proposal
- Drops, retirements and any change to the milestone wait for the owner
- Write this session's key on the charter's `Last rerank:` line, and commit it by path

If that section is missing, the repo's runbooks predate this skill: re-rank at clean close as its
runbook says. For the light reorder at a clean close, use the clean-close skill instead.
