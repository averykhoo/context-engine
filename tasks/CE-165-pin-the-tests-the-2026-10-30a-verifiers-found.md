---
type: Task
id: CE-165
title: Pin the tests the 2026-10-30a verifiers found loose
brief: Each pin is sabotaged before it is believed (DEC-11)
pri: NEXT
state: open
deps: []
goals: [G-2]
source: session 2026-10-30a
created: 2026-10-31
moved: 2026-10-30a
updated: 2026-10-30a
---

Pin the tests the 2026-10-30a verifiers found loose.

Source: verifier residuals in the close commits named per line. Each is a claimed check that stays green when what it guards is broken; pin each, then sabotage it (DEC-11).
- AC-150: tests/test_guards.py::test_g_d4_an_expired_stale_after_on_a_live_record_criterion_or_register_entry_is_red does not pin guards.py::stale's `status: deprecated` skip (its fixture is also `state: closed`); a deprecated fixture with no closed state would (CE-136, a7f128b).
- AC-160: removing `with self.store.lock()` from working.py::Engine.criterion_new leaves tests/test_criteria_write.py green (as for doc freeze) (CE-42, f85e632).
- tests/test_coverage_status.py::test_coverage_prints_the_totals_the_rules_and_a_table_per_class_and_stores_nothing compares only file names, so an append to an existing file passes it; and AC-171's refusal on G-D12 map failures (undated map, glob matching nothing, anchored glob) has no test (CE-141, c5d96b0).
- AC-123: the abandoned-key branch and the remedy texts of working.py::Engine._followable are unpinned; the refusal test covers missing, open and paused keys and asserts messages only (CE-84, baeaed9).
- AC-113: tests/test_roster.py's housekeeping Writes regex accepts any trailing clause after 'only through `hk_` operations' (CE-39, 8fa5015).
- Dropping .gitattributes from bootstrap.py::APPENDED is caught only by the refusal text (CE-53, b36c32e).
- Lint runs only against the LF kit; an engine installed from a CRLF checkout linting an LF repo is not exercised (CE-46, 08af172).
- The op-level pytest.raises(match='frontmatter is not valid YAML') passes whichever layer refuses; only the store-direct call pins commit.py's own refusal (CE-134, d6a2fa5).
- That another session's commit never carries an `id.reserve` line (commit.py::select) is checked only by the line's shape; `ask new --id` has no suite test (CE-105, 9e7c1d0).
- AC-110: the claimed sabotage goes red only when every MCP_TIMEOUT is misspelled, and "(milliseconds)" is not checked (CE-85, 75b3748).
- tests/test_docs.py::test_archive_says_nothing_of_pointers_when_g_d3_is_off carries no AC-149 marker (CE-96, 654ea03).

## Traps

- Run every scripted sabotage with a fresh bytecode cache (CLAUDE.md § Sabotage rule).

## Read first

- docs/runbooks/sabotage.md

## Log

- 2026-10-30a (claude-code/claude-opus-5-5): rerank: G-2, DEC-11: ten loose tests, several claiming CE-6's just-landed criteria. Can be fanned out per file.
