---
type: Task
id: CE-242
title: context-engine upgrade --dry-run
brief: specify from CE-241's field evidence; promote to NEXT once CE-241 closes; writes nothing
pri: LATER
state: open
deps: [CE-241]
goals: [G-6, G-3]
source: session 2026-11-17b
created: 2026-11-17
moved: 2026-11-17b
updated: 2026-11-17b
---

context-engine upgrade --dry-run: what an upgrade from the pinned ref will ask, before it is done.

Upgrading is by hand (no `upgrade` parser in cli.py), and a dry lint before the upgrade understates what it surfaces: G-D0's ACCEPTED-enum check runs only once the kit block is current (working.py::Engine._accepted_enum). docs/evidence/engine-feedback-2026-11-17.md, F28 and F40.

Specify it from CE-241's field evidence (both repos' upgrade Logs, and what CE-240's checklist missed), then build it. The end state fable sketched (evidence doc § Second opinion item 6): read the pinned ref (`.context-engine/env/.../direct_url.json`), print the release-note Upgrade lines landed after it (CE-240's stamps), run lint as the new engine would see the repo after the kit block is replaced, with remedies, and add orient's deprecated-config section (working.py::Engine.deprecated_config). Dry only: it writes nothing.

## Traps

- Not before CE-241: the spec comes from two real upgrades, not from guesses.
- Depends on CE-240's stamp form; parse that form, do not re-key on section dates.
- Dry means read-only in the target repo: `git status --short --ignored` identical before and after.
- When CE-241 closes, promote this to NEXT (the coordinator's call, 2026-11-17b).

## Read first

- docs/evidence/engine-feedback-2026-11-17.md: F28, F33, F40, § Second opinion items 6 and 7
- CE-241's Log; CE-240; src/context_engine/kit/README.md § 4

## Log
