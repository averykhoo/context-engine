---
type: Decision
id: DEC-291
title: "CE-165: AC-160's lock pin asserts the OS lock is held at the read, write and op line, covers criterion_set, and leaves doc_freeze's identical gap"
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:d89082e4b1374f60a63aefc5edd367367672d1dc210862505d708c9d140ec83b
---

The agent's call on CE-165 (session 2026-11-07e): AC-160's lock pin, in tests/test_criteria_write.py, asserts that the OS lock is held (a FileLock probe with a short timeout, the pattern of tests/test_commit.py::test_an_operation_holds_the_lock_from_its_first_write_to_its_commit) at the table's read, its write and the op line, rather than reading the private Store._held flag. It covers criterion_set too.

Rejected: asserting Store._held (a private flag: a refactor renames it and the test dies for the wrong reason); asserting a commit happened (the fixture is not a git repo).

doc_freeze has the same unpinned lock; it is left out of CE-165 (not its bullet) and named in the close digest.

Cheap to undo: one test.
