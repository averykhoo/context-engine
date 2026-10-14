---
type: Task
id: CE-70
title: "init's next: line, settings hints and first-task hint match the bootstrap procedure"
brief: 'Audit 2026-10-14a D3, N2, N3, N4: init output names the gate step and commit, not the optional MCP server'
pri: LATER
state: closed
deps: []
source: session 2026-10-14a
created: 2026-10-14
moved: 2026-10-14a
updated: 2026-10-14a
review: [shipped, write-op]
status: deprecated
closed: 2026-10-14a
---

init's next: line, settings hints and first-task hint match the bootstrap procedure.

## Traps

- none yet

## Read first

- none yet

## Log

- 2026-10-14a (claude-code/claude-opus-5-5): closed: done in 6f8b423: init's next: line, settings hints, dry-run preview and G-W5 remedy

## Design review

affects: the owner and first session in every adopting repo, who follow init's next: line and hints; a person using plain git, whose .claude/settings.local.json may be committed
- reduced: init's next: line skips the gate step and the kit commit and presents MCP registration as a step | rung: reduce | control: bootstrap.py prints the bootstrap procedure's steps in order; tests/test_kit.py::test_inits_next_line_names_the_bootstrap_steps_in_order_and_the_mcp_server_as_optional
- reduced: a machine-specific settings.local.json stays un-ignored after --merge-settings, and only that one run says so | rung: reduce | control: the run that writes the hook writes .claude/.gitignore; every later run warns (bootstrap.py::_ignored); test_a_merge_writes_the_missing_gitignore_and_every_rerun_repeats_a_gitignore_that_misses_the_line
- reduced: --skip-settings asks for the hook by hand when it is there, or crashes on an unreadable file | rung: reduce | control: bootstrap.py::_skip_label; test_skip_settings_says_the_hook_is_there_when_it_is_and_never_refuses
- reduced: a fresh board's empty NOW turns lint red with a remedy that does not say to promote | rung: reduce | control: the G-W5 remedy names `task promote` for an empty NOW and the cap when above one; test_an_empty_now_names_the_promote_step_and_an_overfull_one_the_re_rank
- residual: _ignored does not read .git/info/exclude, the global excludes file or nested ignore files | rung: individual | why: reproducing git's full ignore resolution is not cheap, and erring toward a warning is safe | control: init warns or writes the ignore file; `git check-ignore` is the by-hand check (manual-mode § init)
F: stale when the bootstrap procedure's order changes; the next: line test pins the order to procedures § Bootstrap
A: every step is in procedures § Bootstrap and manual-mode § context-engine init
M: the run, the dry run and the refusal share one plan (writes, skipped, warnings) in bootstrap.py, and bootstrap.py::_ensure_ignore is the one ignore step
E: reuses the DEC-32 refusal and init's label format; reviewed by correctness, deploy/fresh-user and skeptic lenses plus the adhoc dry run's F2, F3 and F11
