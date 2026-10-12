---
type: Task
id: CE-24
title: "Rituals runbook: every ritual's steps in one file, engine command and by-hand step side by side"
brief: Single source of truth for ritual order (US-15); FRAMEWORK §6 keeps rules and reasons only; CLAUDE.md points
pri: NEXT
state: open
deps: []
source: session 2026-10-12a
created: 2026-10-12
moved: 2026-10-12a
updated: 2026-10-12b
---

US-15 (owner, 2026-10-12a): rituals and housekeeping get one source of truth, and FRAMEWORK.md
plus the fallback runbook must be enough for an agent in a pasted-into repo. The paste test
(`docs/evidence/framework-paste-test-2026-10-12.md`) found the order of each ritual written in
three places (FRAMEWORK §6, `CLAUDE.md` § Rituals, and implicitly manual-mode's per-operation
sections), already drifted, and no by-hand section for any whole ritual (P16 asks for one per
process).

Scope:
- `docs/runbooks/rituals.md` (or a ritual part of `manual-mode.md`; decide at design): session
  start, intake, clean close, pause, resume, bootstrap, housekeeping (tier 0 by hand), foreign
  reconcile (§6.10), push and CI. Each step: the engine command, the by-hand step (a link into
  manual-mode's operation section), and its why.
- FRAMEWORK §6 keeps what each ritual must achieve, its guards and reasons; its numbered step
  lists move to the runbook and §6 points there.
- `CLAUDE.md` § Rituals shrinks to a pointer plus this repo's specifics (interpreter, actor).
- A guard: the AC-21 parity test (`tests/test_runbook.py`) extended so every ritual named in
  FRAMEWORK §6 has a runbook section, and every step names an existing operation.
- Strip this repo's specifics out of the runbooks (CE-n/DEC-n/US-n prefixes as fixed values, AC
  ids as reasons) or mark them as this repo's values, so the kit (CE-15) can ship them.
- Ship them (moved here from CE-15 by its review, 2026-10-12b): the stripped runbooks become kit
  package data (`pyproject.toml` package-data), `init` copies them into `docs/runbooks/` instead
  of the bare `.gitkeep` (`bootstrap.py::KEEP`), a test checks a built wheel carries them, and the
  kit contract's Rituals and the kit README's Runbooks section point at the repo's own copy
  rather than the engine repo's. CE-7 depends on this.

Out of scope: the rest of the adoption kit (context.toml schema, install, skeletons) is CE-15.

## Traps

- Moving step lists out of FRAMEWORK §6 must keep step numbers stable (P3): records cite them.
- `CLAUDE.md` loads every session: the pointer must still tell an agent to start with
  `session start` and `orient` without opening another file.

## Read first

- `docs/evidence/framework-paste-test-2026-10-12.md`
- `docs/stories/US-15-framework-md-plus-the-fallback-runbook-pasted.md`, `docs/stories/US-11-rituals-without-python.md`
- `docs/framework/FRAMEWORK.md` §6, P16; `docs/runbooks/manual-mode.md`

## Log

- 2026-10-12a (claude-code/claude-opus-5-5): Drift fixed first (2026-10-12a): FRAMEWORK §5.5 key resets on a new day; §6.3 order in practice and CLAUDE.md § Rituals now carry step 1 (lint first) and 6a (baton expire); manual-mode hashes: lowercase hex, no BOM, banner to EOF. The runbook itself is open.
- 2026-10-12b (claude-code/claude-opus-5-5): Scope gains 'ship the stripped runbooks in the kit' (init copies them into docs/runbooks/, wheel test), moved from CE-15 by its 2026-10-12b review; CE-7 now depends on CE-24.
