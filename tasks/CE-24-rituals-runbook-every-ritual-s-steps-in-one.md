---
type: Task
id: CE-24
title: "Rituals runbook: every ritual's steps in one file, engine command and by-hand step side by side"
brief: Single source of truth for ritual order (US-15); FRAMEWORK §6 keeps rules and reasons only; CLAUDE.md points
pri: NOW
state: closed
deps: []
source: session 2026-10-12a
created: 2026-10-12
moved: 2026-10-12d
updated: 2026-10-12d
review: [guard, shipped]
status: deprecated
closed: 2026-10-12d
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
- 2026-10-12d (claude-code/claude-opus-5-5): Built (2026-10-12d). Design: docs/runbooks/rituals.md holds every ritual's order as one table per ritual (§ label | Do | Engine | By hand link into manual-mode | Why), with a map from every FRAMEWORK §6 subsection; FRAMEWORK §6 keeps its numbered items as stable labels (P3) of what each ritual must achieve, and its 'order in practice' text moved to the runbook. manual-mode.md stripped of this repo's ids (kinds table now the kit's D/S/T defaults; context.toml is the authority). Both runbooks ship in the kit (kit/docs/runbooks/, byte-equal to docs/runbooks/), init copies them (docs/runbooks dropped from KEEP), package-data is kit/**/*. CLAUDE.md, the kit contract and README point at the repo's own copies. Guards: AC-36 (tests/test_runbook.py, 3 tests), AC-37 (tests/test_kit.py, 3 tests incl. a wheel build, ~5s). Sabotage: tools/sabotage_ce24.py, 15 rows all red. Register: INV-9 and INV-11 controls updated (now collective).
- 2026-10-12d (claude-code/claude-opus-5-5): closed: done: rituals.md, de-leaked runbooks shipped in the kit, AC-36/AC-37 green and sabotaged (session 2026-10-12d)

## Design review

affects: a session running a ritual by hand (no engine, or an engine that errs), the session adopting a repo, the adopting repo's owner and its plain-git humans, the next session with no context, every repo the engine is pointed at
- reduced: a ritual's order drifts between FRAMEWORK §6, the contract and the runbook | rung: collective | control: the order is written only in docs/runbooks/rituals.md; FRAMEWORK §6 keeps numbered requirements and points there; test_runbook::test_every_framework_ritual_has_a_rituals_section
- reduced: a ritual named in FRAMEWORK §6 has no by-hand section | rung: collective | control: test_runbook::test_every_framework_ritual_has_a_rituals_section
- reduced: a ritual step names an operation the engine does not have, or a by-hand link that resolves to nothing | rung: collective | control: test_runbook::test_every_ritual_step_names_an_existing_operation_and_its_by_hand_section
- reduced: a record citing a §6 step number (§6.3 step 6a, §6.4 item 0) stops resolving when the order moves out | rung: collective | control: FRAMEWORK §6 keeps every numbered item at its number (P3), and test_runbook::test_every_framework_step_a_ritual_cites_exists checks each `§6.n item k` tag in rituals.md
- reduced: the shipped runbooks carry this repo's ids | rung: collective | control: test_kit::test_the_kit_and_framework_carry_none_of_this_repos_ids_or_paths scans every kit file, the runbooks included
- reduced: the kit's runbooks drift from the ones this repo runs on | rung: collective | control: test_kit::test_the_kit_runbooks_are_this_repos_runbooks (byte equality)
- reduced: a kit file is left out of the built wheel | rung: collective | control: test_kit::test_the_wheel_carries_every_kit_file builds a wheel in the gate
- reduced: init overwrites an adopter's own edited runbook | rung: reduce | control: bootstrap.plan is create-only (test_init_never_overwrites_and_a_second_run_is_a_no_op)
- residual: an adopter's copied runbooks go stale against a newer engine, because init never overwrites them | rung: individual | why: the copy in the repo is the adopter's own and may carry its edits, so neither init nor an upgrade may replace it unasked | control: the kit README § Upgrade step to replace each kit runbook the repo has not edited; G-D0 flags a major.minor change
F: rituals.md changes whenever an operation or a ritual changes, by whoever changes it, in the same commit; the parity tests go red when it goes stale
A: rituals.md is plain markdown, followed by hand; every engine step links its manual-mode section
M: one ordered table per ritual in one file; FRAMEWORK §6 holds requirements by stable number; the kit copy is byte-equal to this repo's
E: reuses manual-mode's section names as link targets, FRAMEWORK §6's step numbers, and init's create-only copy
