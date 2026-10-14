---
type: Task
id: CE-51
title: 'init appends a second ## Gate to a CLAUDE.md that already has one'
brief: Found by CE-26's deploy lens on main; init never overwrites, so merge or name the clash, not replace
pri: LATER
state: closed
deps: []
source: session 2026-10-13c
created: 2026-10-13
moved: 2026-10-14a
updated: 2026-10-14a
review: [shipped, write-op]
status: deprecated
closed: 2026-10-14a
---

From CE-26's deploy review (2026-10-13c, finding D#7, already on main before CE-26): running init on a repo whose CLAUDE.md already has a ## Gate section appends the kit block's stub next to it, leaving two Gate sections. Recommendation: init detects an existing ## Gate and leaves the stub out, saying so in its output, or lint fails on a duplicate heading in CLAUDE.md.

## Design review

affects: every repo adopting the engine whose CLAUDE.md already has a gate; the owner reading CLAUDE.md after init; the first session there, which runs the gate CLAUDE.md names
- eliminated: init appends the kit's Gate stub beside the repo's own `## Gate`, leaving two gates and a clean lint
- reduced: a heading that is not the repo's gate (`### Gate` under another section, `## Gate-keeping`, one in an HTML comment or a fence) is taken for it, so the stub and the gate step are dropped | rung: reduce | control: bootstrap.py::gate_section counts only a level 1-2 `Gate` heading outside fences and comments; tests/test_kit.py::test_a_gate_heading_that_is_not_the_repos_gate_leaves_the_stub_in
- reduced: a repo's own gate that does not run lint goes unnoticed | rung: reduce | control: the next: line asks to check CLAUDE.md § Gate ends with `&& context-engine lint`; the nudge reads the Gate section only (bootstrap.py::LINT_RE)
- residual: a setext `Gate` heading is not detected, so such a repo still gets a second Gate | rung: individual | why: setext headings in CLAUDE.md are rare and parsing them needs a markdown parser | control: init's output names the CLAUDE.md change, and the kit README and manual-mode say which headings count
- residual: a repo whose real gate is a `### Gate` gets the stub appended beside it | rung: individual | why: a level-3 Gate is usually a subsection, not the repo's gate | control: init's label quotes the heading it took; the kit README and manual-mode say which headings count
F: stale when CLAUDE.md conventions change (a gate under another heading name); the gate_section tests name each case
A: by hand, delete the extra `## Gate` stub from CLAUDE.md (manual-mode § context-engine init)
M: one function, bootstrap.py::gate_section, used by init and the next: line alike
E: reuses init's label and warning format; reviewed by correctness, deploy/fresh-user and skeptic lenses, every finding fixed or filed as residual

## Log

- 2026-10-14a (claude-code/claude-opus-5-5): closed: done in 0940192: init leaves the Gate stub out of a CLAUDE.md with its own Gate
