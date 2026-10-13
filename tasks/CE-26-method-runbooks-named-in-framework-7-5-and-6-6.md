---
type: Task
id: CE-26
title: 'Method runbooks named in FRAMEWORK §7.5 and §6.6: gate, sabotage, fan-out and build rounds, release, test baselines'
brief: Only manual-mode.md exists; method survives when status is archived; each runbook is short and routed
pri: NEXT
state: closed
deps: []
source: session 2026-10-12b
created: 2026-10-12
moved: 2026-10-13c
updated: 2026-10-13c
review: [shipped]
status: deprecated
closed: 2026-10-13c
---

Filed by CE-16 from the coverage map (docs/evidence/framework-coverage-2026-10-12.md): component 9 (runbooks) and ritual §6.6 (delegation and build rounds). FRAMEWORK §7.5 names a gate, sabotage, fan-out, release and test-baselines runbook; docs/runbooks/ holds only manual-mode.md. The delegation rules themselves are already CLAUDE.md rules (DEC-16, DEC-17, DEC-18); what is missing is the build-round protocol (§6.6 steps 1 to 7) and the other methods, written as runbooks and routed in context.toml. Ritual order is CE-24, not this.

## Log

- 2026-10-13c (claude-code/claude-opus-5-5): 2026-10-13c: building on branch ce-26 in worktree context-engine-wt/ce-26, alongside CE-45. rituals.md, manual-mode.md and FRAMEWORK §5.5 belong to CE-45 for this wave; ritual pointers to the new runbooks get added after the merge.
- 2026-10-13c (claude-code/claude-opus-5-5): Built 2026-10-13c in worktree ce-26 (draft; spec-fidelity, deploy and false-pass lenses; a skeptic; fix): 0e695ce, 929248f, fast-forwarded onto main. Four runbooks (gate.md holds the test baselines; fan-out.md holds delegation, watchers, worktrees, workflows and the §6.6 build rounds), all kit-shipped and routed; AC-71 added (agent-drafted, from US-9 and US-15). Review: 27 findings, 5 overstated and 2 half-rejected by the skeptic, the rest fixed. Gate on main: 504 passed. First-hand sabotage: kit gate.md desynced -> tests/test_kit.py::test_the_kit_runbooks_are_this_repos_runbooks red. Ritual pointers (rituals.md §6.6 row, clean close item 5, push and CI for a tag) and the INV-15 wording in kit manual-mode.md wait for CE-45's merge, which owns those files.
- 2026-10-13c (claude-code/claude-opus-5-5): closed: done in 0e695ce..929248f (four method runbooks, kit-shipped and routed; reviewed by three lenses and a skeptic; gate 504 passed)

## Design review

affects: every repo the kit deploys to, since init copies the four method runbooks and the template routes them; every later session here, which reads gate.md, sabotage.md, fan-out.md and release.md as method; the owner, whose global CLAUDE.md rules (CI watcher, install trial, delegation) the runbooks distil
- reduced: a kit runbook carries this repo's ids or machine paths into a target repo | rung: reduce | control: tests/test_kit.py LEAK (ids, INV-n, tools/sabotage, user paths in every shell form, anaconda3) with a KNOWN_LEAKS ratchet; sabotaged by planting a repo id, an INV-3 and a /c/Users path
- reduced: a runbook copy drifts from the kit, or FRAMEWORK §7.5 names a runbook the kit lacks | rung: reduce | control: byte-equal kit copy tests and the §7.5 set check in tests/test_method_runbooks.py; sabotaged by a desynced copy and by §7.5 dropping or adding a name
- reduced: a runbook is unrouted or outgrows its caps, so lint cannot see it go stale | rung: reduce | control: four [[routes]] with G-D1 caps in context.toml and the kit template, G-R1 for a missing file; sabotaged by a dropped route, a missing file and a lowered cap
- reduced: fan-out.md's build rounds drift from FRAMEWORK §6.6 steps 1 to 7 | rung: reduce | control: tests/test_method_runbooks.py reads the steps inside §6.6, wrapped steps included; sabotaged by a reworded, swapped, wrapped and moved step
- residual: an upgraded repo can lack the method runbooks with lint clean, since init never edits an existing context.toml and the new routes are added by hand while the contract names those files | rung: individual | why: init does not rewrite an owner's config (DEC-1, DEC-32) | control: kit README § 4 upgrade step; a lint check that every runbook the kit ships is routed is the follow-up
- residual: a repo's own file under a method runbook's name takes the framework runbook's place (init skips it, it gains the route's caps and the contract's pointer) | rung: individual | why: init never overwrites | control: kit README § 3 and init's skipped output
- residual: adopted runbook copies drift from the kit after init and nothing compares them | rung: individual | why: they are the repo's own once copied | control: kit README § 4 upgrade step (continues CE-24's residual)
- residual: a runbook's method can be wrong while every check passes, since the tests check shape (set, routes, liveness, step names, leaks), not the method | rung: individual | why: judging a method is review, not lint (P8) | control: design review and the three-lens review at build
- residual: the leak check is a deny-list, so a new repo-specific id prefix or path form passes until someone adds it | rung: individual | why: an allow-list of framework id forms is not built | control: tests/test_kit.py::LEAK, extended when a leak is found
F: goes stale when a ritual, the gate, the push or release order, or §6.6 changes; the tests pin the set, routes, liveness and §6.6 steps, so a rename or a dropped step reds
A: four short markdown files a human reads; delete or replace one and remove its route; each defers to rituals.md for order and to CLAUDE.md for repo values
M: one home per rule: order in rituals.md, repo values in CLAUDE.md, method in the runbook; kit copies byte-equal like rituals.md and manual-mode.md
E: reuses the kit copy pattern, [[routes]] with G-D1 caps, the leak test and the sabotage table (tools/sabotage_ce26.py, 25 rows, all red); review by spec-fidelity, deploy and false-pass lenses plus a skeptic: 27 findings, most confirmed and fixed in 929248f
