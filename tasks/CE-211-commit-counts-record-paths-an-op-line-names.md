---
type: Task
id: CE-211
title: commit counts record paths an op line names against the gate scope, unlike check_commit's docstring (audio-workspace item 11)
brief: DEC-36 keeps board writes uncommitted; fix the check, not the commit policy
pri: LATER
state: open
deps: []
goals: [G-6]
source: session 2026-11-07e
created: 2026-11-08
moved: 2026-11-07e
updated: 2026-11-07e
---

`commit` counts record paths that an op line names against the gate scope, unlike gate.py::check_commit's docstring, so a records-only commit waits on a green run under a scope that covers records (audio-workspace feedback item 11).

**What happened** (audio-workspace `docs/context-engine-feedback.md` entry 11, agent-raised, 2026-11-06): `context-engine commit` of seven `tasks/*.md` files (task comments, a new task and a new ask) was refused for about 90 minutes, because its `[gate]` scope `all` covers every file and the tree also held a running wave's uncommitted code, so no green run could cover it. `task close`, `record amend` and `ask new` committed themselves at once in the same tree; `task comment` and `task new` did not.

**At HEAD cb362ca (read from the code, not reproduced):** gate.py::check_commit's docstring says "Paths the op log's lines name are not counted: the engine's own commits of its writes are the gate's one exception", but working.py::Engine.commit passes it every given path (`rels`) unfiltered, and check_commit, gate.py::listing and gate.py::_under do no op-log filtering. So a record path given to `commit` is refused whenever the gate scope covers it. `commit -m` with no paths is never checked (`if not gate.require or not paths: return`), which is today's workaround. This repo never sees it: `[gate.scopes.code]` in context.toml excludes tasks/, docs/decisions/, docs/stories/ and docs/ledger/. The entry's other option, every board write committing itself, is DEC-36's opposite as a default, but already exists per repo as `[engine] commit = "every-write"` (config.py::COMMIT_POLICIES); that is not this task.

**The fix to design:** check_commit counts only the given paths that no carried op line names (commit.py::carried_paths), as its docstring says. Reproduce first in a temporary repo whose gate scope includes `**`. The test gives a record path an op line names under a covering scope while unrelated code is dirty; sabotage it by restoring the unfiltered call.

## Traps

- A hand edit to a record that an op line also names would then skip the gate. working.py::Engine._lint_carried still lints it; say so in check_commit's docstring.
- Reproduce before changing anything: the bug is read from the code, not seen here.

## Read first

- src/context_engine/gate.py::check_commit
- src/context_engine/working.py::Engine.commit
- src/context_engine/working.py::Engine._lint_carried
- src/context_engine/commit.py::carried_paths
- docs/decisions/DEC-36-the-engine-commits-at-milestones-not-at-every.md
- C:/Users/user/PycharmProjects/audio-workspace/docs/context-engine-feedback.md entry 11

## Log
