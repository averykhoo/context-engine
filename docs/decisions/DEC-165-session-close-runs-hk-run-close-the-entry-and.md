---
type: Decision
id: DEC-165
title: session close runs hk run close, the entry and an optional banner in one batch and one commit (CE-195)
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
refs: [DEC-163, US-21]
decided: 2026-11-06
session: 2026-11-06f
body_sha: sha256:5512aaa802a4532531a838b15dda01a0e8eacfd85aea52c5fcfee6f32cfde393
---

The agent's call on CE-195 (DEC-163, US-21), made while building it in session 2026-11-06f: what "session close becomes one call" does.

Options:
(a) `session close` runs `hk run close` itself, first, unless `--no-housekeeping`; then the ledger entry; then the banner only when given `--banner`/`--banner-file` with `--seen`. All of it is one milestone batch, so one commit. Every refusal the entry or the banner would meet (receipts, named tasks, asked questions, a stale banner hash, banner prose lint, the housekeeping cap) is checked before the first write, so a refused close writes nothing. The entry gains a `housekeeping:` receipt (the run's count line); outside a git history the run is skipped and the receipt says so;
(b) the same, but each part commits on its own (three commits);
(c) housekeeping only when asked for (`--housekeeping`).

Chose (a): one call and one commit is what makes closing after every reply cost seconds (DEC-163); running housekeeping twice is harmless (the second run finds nothing owed), so an adopter whose procedure still runs `hk run close` first loses nothing. The engine-level `Engine.session_close` keeps `housekeeping=False` as its default and the operation (`ops.py::session_close`, which the CLI and MCP call) defaults it on, so library callers and tests that close many sessions are unchanged.

Built in working.py::Engine.session_close, ops.py::session_close and cli.py::build; pinned by AC-185. Cheap to undo.
