---
type: Decision
id: DEC-196
title: 'test_ci full-history check requires the integer 0: type(depth) is int and depth == 0; a string "0" or bool false in gate.yml is refused'
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:550ad56a7db2b5ff7ebee1eb0a9b7079303c1ec4ae9555fce4f4a56adff30450
---

tests/test_ci.py::test_the_workflow_checks_out_full_history_for_the_guards_that_read_it checks `type(depth) is int and depth == 0`: the checkout's `fetch-depth` must be the integer 0. A YAML `false` (Python's False == 0, and bool is an int subclass, so isinstance would pass it) or a string "0" is refused, even though actions/checkout may read either as full history. The workflow is ours and writes the integer, so the strict check is the simpler statement and cannot pass by accident. Rejected: accepting "0" or false as equivalents. CE-170.
