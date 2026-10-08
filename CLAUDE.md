# context-engine: contract

The spec is `docs/framework/FRAMEWORK.md`. The engine is §8.0; the build order is the
"what's needed to start" plan: step 0 spike (`spike/`), then core, working state, MCP,
decisions, housekeeping. A change to the spec gets a row in its §13 change table.

## Environment

- Interpreter: `C:/Users/user/anaconda3/envs/context-engine/python.exe` (Python 3.12).
  Bare `python` is broken on this machine; always use the full path.
- Install for development: `<interpreter> -m pip install -e ".[dev]"`.
- **The engine runs from its own env and is pointed at a repo; it is never installed into a
  target repo's environment** (target repos may be node, uv or conda).

## Gate

`<interpreter> -m pytest -q` from the repo root. Run it before every commit that touches
`src/` or `tests/`, and before every push.

## Rules

- Commit by path (`git commit -o <paths>`); never `git add -A`, never `git stash`.
- `docs/framework/FRAMEWORK-v0.*.md`, `A-*.md` to `D-*.md` and `review/` are frozen
  provenance: never edit them.
- `spike/` holds throwaway probes whose findings are transcribed into the spec; the probes are
  kept as evidence of how a finding was reached.
