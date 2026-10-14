---
type: Task
id: CE-75
title: Orient never cuts batons, pauses, other sessions or questions; its cap counts the bytes delivered
brief: 'Blocks CE-7: a 6 KB banner hides BTN-n entirely; CRLF made a 6000 cap deliver 6110 bytes (adhoc dry run F29, F30)'
pri: NEXT
state: closed
deps: []
source: session 2026-10-14a
created: 2026-10-14
moved: 2026-10-14a
updated: 2026-10-14a
review: [shipped, long-lived]
status: deprecated
closed: 2026-10-14a
---

Orient never cuts batons, pauses, other sessions or questions; its cap counts the bytes delivered.

## Traps

- none yet

## Read first

- none yet

## Log

- 2026-10-14a (claude-code/claude-opus-5-5): closed: done in fb9c1f5: orient never cuts batons, pauses, other sessions or questions

## Design review

affects: every session in every repo, which starts from orient; the owner, who must see batons, pauses, other sessions and questions; a cold session in a repo with a large banner
- eliminated: a large banner pushes batons, pauses, other open sessions and questions out of orient
- reduced: the hook delivers more bytes than the cap on a CRLF console | rung: reduce | control: cli.py::main writes stdout as UTF-8 with LF only; tests/test_working.py::test_a_real_orient_subprocess_delivers_no_more_bytes_than_the_cap
- reduced: a cut lands mid-item, so a pause loses its resume step, or a cut note names nothing that lists the rest | rung: reduce | control: working.py::_cut cuts between items; every cut note names a command (banner show, baton list, task list, task show, register show); test_must_act_lists_past_the_cap_are_cut_between_items_and_name_a_command_that_lists_the_rest
- reduced: text UTF-8 cannot encode crashes orient, so the hook fails silently | rung: reduce | control: working.py::_printable replaces it before counting
- residual: this repo's routine orient cuts its own banner, against orient_max_bytes's provenance | rung: individual | why: the banner is the session's to write | control: banner set says when orient will cut the new banner (CE-76); the cut note points at banner show
- residual: orient displays batons before other open sessions, while the contract and procedures order other sessions first | rung: individual | why: display order is cosmetic and swapping it renumbers shared runbook items | control: the procedure's order governs what the session does
- residual: an orient_max_bytes below about 250 bytes cannot hold the headings | rung: individual | why: no repo sets it that low | control: manual-mode § orient documents the floor
- residual: the questions cut note lists every open question, not which are pending, and no note says N of M shown | rung: individual | why: a precise per-section count needs another read op | control: task list shows each question's state
F: stale when orient gains a section; each section needs a rank in working.py::fit and a cut note naming a list command
A: every section can be read on its own: banner show, baton list, task list, task show, register show (manual-mode § orient)
M: one budget function, working.py::fit, with ranks; one cut function, working.py::_cut
E: reuses the existing read ops and adds one, baton list; reviewed by correctness (20,000-case fuzz), cold-start reader and byte-maths lenses; every finding fixed or filed above
