---
type: Task
id: CE-10
title: "Run the gate in GitHub Actions on push"
brief: "Its own commit; CI changes stay out of feature work"
pri: NOW
state: open
deps: []
source: session 2026-10-08a
created: 2026-10-08
moved: 2026-10-12d
updated: 2026-10-12d
closed:
---

Add a workflow that installs the package with `[dev]` on Python 3.12 and runs pytest. Pushing
it needs the owner's permission, and its first run gets a CI watcher (global `CLAUDE.md`).

## Traps

- **The repo is public** (owner, 2026-10-10, DEC-22), so GitHub Actions minutes are free. The owner's earlier words (2026-10-08: *"its currently private so I don't have unlimited compute so let's not run that too much"*) no longer bind; a cheap workflow (one job, pip cache, `paths:` filter for docs-only pushes) is still the aim.
- Pushes are asked for every time and made only on a green gate (DEC-22); CI does not change that.

## Log

- 2026-10-12c (claude-code/claude-opus-5-5): 2026-10-12c prioritisation (owner approved): top of LATER; NEXT is full (CE-22, CE-20, CE-21, CE-5, CE-14). Next to promote when a NEXT slot frees.
- 2026-10-12d (claude-code/claude-opus-5-5): Built: .github/workflows/gate.yml (push + workflow_dispatch; ubuntu-latest; checkout@v7, setup-python@v7 at 3.12 = requires-python floor, pip cache on pyproject.toml; pip install -e .[dev]; python -m pytest -q; contents: read). No paths: filter, deliberately: docs/, tasks/ and context.toml are records lint checks (AC-23), so a docs-only push can turn the gate red; minutes are free on the public repo. Found: HEAD 6fe5c7e on a clean python:3.12-slim shallow checkout was 1 failed/339 passed: test_kit::test_the_wheel_carries_every_kit_file builds with --no-build-isolation and a clean 3.12 env has no setuptools; fixed by setuptools>=68 in [dev]. tests/test_ci.py pins the workflow to CLAUDE.md § Gate and pyproject (floor, install, gate, no filter, build requires in [dev]). Verified 2026-10-12: the same steps on that tree in python:3.12-slim (WSL docker), 344 passed. Open: push (owner's permission) and a watched first CI run; close after it is green.
- 2026-10-12d (claude-code/claude-opus-5-5): Review fix: rituals.md (and kit copy) § Push and CI gains the by-hand CI fallback row (fresh env at the requires-python floor, pip install -e .[dev], then the gate); tests/test_ci.py pins it, that CLAUDE.md § Gate names .github/workflows/gate.yml, and that no if:/continue-on-error on the job or a step can skip or mask the gate. Still open: push (owner's permission) and a watched first CI run.
