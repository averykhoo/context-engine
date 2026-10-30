---
type: Task
id: CE-134
title: Test that a --sweep commit refuses a record whose frontmatter does not parse
brief: Pin the frontmatter-parse refusal on the sweep path too; see it fail first (DEC-11)
pri: LATER
state: closed
deps: []
goals: [G-2]
source: session 2026-10-23e
created: 2026-10-23
moved: 2026-10-30a
updated: 2026-10-30a
status: deprecated
closed: 2026-10-30a
---

Found by CE-133's verifier (2026-10-23e, .scratch/ce-133/verifier.md): test_commit.py::test_a_milestone_never_commits_a_record_whose_frontmatter_does_not_parse covers a session's own milestone and another session's commit, but no test covers a `commit --sweep` carrying a broken record. The refusal code is session-independent, so it applies today; this pins it.

## Log

- 2026-10-30a (claude-code/claude-opus-5-5): closed: Done in 3fa0554 (lane 0634c5b): tests/test_commit.py::test_a_sweep_never_commits_a_record_whose_frontmatter_does_not_parse (AC-78) pins the frontmatter-parse refusal on commit --sweep: the session commit refuses, store.commit_paths with sweep refuses and names the file, and once the edit is undone the sweep carries the record. Sabotaged red twice.
