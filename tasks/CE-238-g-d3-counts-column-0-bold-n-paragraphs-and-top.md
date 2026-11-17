---
type: Task
id: CE-238
title: G-D3 counts column-0 bold `**N. ...**` paragraphs and top-level ordered items as numbered sections
brief: nothing indented or inline counts; the 6 true mis-citations in audio-workspace stay red
pri: NOW
state: open
deps: []
goals: [G-6, G-2]
source: session 2026-11-17b
created: 2026-11-17
moved: 2026-11-17b
updated: 2026-11-17b
---

G-D3 counts column-0 bold `**N. ...**` paragraphs and top-level ordered items as numbered sections.

G-D3's `<id> § <n>` check (guards.py::cite_problems through guards.py::_headings and guards.py::_cites_heading, CE-105) reads only markdown `#` headings. audio-workspace's imported decisions number their sections as bold paragraphs (`**5. TWO SILENT-WRONGNESS TRAPS ...**`) or as top-level ordered items (`5. **Title**`), so its lint at engine HEAD is red 137 times, 117 of them inside append-only decision bodies it may not edit (docs/evidence/engine-feedback-2026-11-17.md, F31, corrected by the verifier).

1. Widen guards.py::_headings: besides `#` headings, harvest a column-0 line that is wholly bold and opens with a number, and a column-0 top-level ordered item (`5. **Title**`, `5. Title`). Match them by number and by text exactly as guards.py::_cites_heading does today.
2. Field check: a dry lint in audio-workspace clears 131 of the 137 (120 bold paragraphs, 11 list items). The 6 true mis-citations stay red (`D-152 § 5.3`/`§ 5.6` x3, `D-284 § 2` and `§ 3`, `D-419 § 2`): they go through the waiver (DEC-347's task).
3. Sabotage (DEC-11): drop each new branch and watch its test go red; check a nested item and an inline number still fail.

## Traps

- Nothing indented (nested items), no number inside a prose line, no bold text that is not the whole line: each would turn a real mis-citation green.
- Widen what counts as a section, never the existence test: an id that names no record is still red.
- The 6 true mis-citations must stay red after this task: if the dry lint shows fewer than 6 left, the widening is too loose.
- guards.py::_headings has one caller (guards.py::cite_problems); decisions.py has its own unrelated `_headings`.
- The dry lint in another repo is read-only: `git status --short --ignored` identical before and after.

## Read first

- docs/evidence/engine-feedback-2026-11-17.md: F31 (with the verifier's count by kind), § Second opinion item 2
- guards.py::cite_problems, guards.py::record_refs, guards.py::_cites_heading
- DEC-347 (the exit for what this task leaves red)

## Log

- 2026-11-17b (claude-code/claude-opus-5-5): Builder, round 1: the plan's finding (measured 2026-11-17 on audio-workspace): the task text's 'wholly bold line' rule clears only 21 of the 120 bold citations. The real shape is a paragraph whose first line opens with a bold span starting with a number (the span may wrap or be followed by body). Built as a bold paragraph lead, gated on opening a block; the paragraph-opener and ordered-list gates are pinned by tests T3 (the corpus does not discriminate them).
