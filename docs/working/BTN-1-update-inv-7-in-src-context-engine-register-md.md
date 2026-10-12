---
type: Baton
id: BTN-1
title: 'Update INV-7 in src/context_engine/REGISTER.md: G-D0 is built (CE-21, 3048e85) and checks both the f'
session: 2026-10-12c
state: done
created: 2026-10-12
why: CE-21 agent left the register untouched by instruction; its 'why not eliminated' and 'control' lines are now stale
done: 2026-10-12d
evidence: "INV-7 in src/context_engine/REGISTER.md: why-not-eliminated and control rewritten for G-D0 (collective, working.py::Engine.lint_contract); heading kept so G-W13 still matches CE-15's residual. Probe: a fresh init lints clean at 0.5 and G-D0 red x2 against 0.6.0.dev0, so a version bump leaving bootstrap.BEGIN behind fails test_kit.py::test_an_empty_repo_bootstraps_with_init_alone_and_runs_a_whole_session"
---

Update INV-7 in src/context_engine/REGISTER.md: G-D0 is built (CE-21, 3048e85) and checks both the framework: line and the kit-block marker; only bootstrap.BEGIN being a literal (not tied to __version__) remains

**Why skipped:** CE-21 agent left the register untouched by instruction; its 'why not eliminated' and 'control' lines are now stale
