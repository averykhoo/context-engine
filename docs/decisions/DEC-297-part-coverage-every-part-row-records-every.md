---
type: Decision
id: DEC-297
title: "Part coverage: every part row records every scope's id; a scope is covered when every part's newest row on its id passed with its current command; a part is fresh when it passed on its own scope's id; check_commit checks the require scope only, never freshness (as with readers)"
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:a4da0708c218840bec0be6efb9faa0642fc20f7c6b7aade088015e55ddd832ac
---

Every part's row records the id of every scope (with the per-id moved/kept rule a single run
already has), not only its own scope's. A scope is covered when, for every part, the newest row of
that part on the scope's current id (PASSED or FAILED) passed with the part's command configured
now (gate.py::part_covering, gate.py::covered): the whole gate passed on those files, part by
part, which is what a single-command row means today. A part is fresh when it covers its own
scope. `context-engine commit` checks the require scope's coverage only, never freshness: a part
keyed on every file goes stale on each op-log write, any session's, which is the reason the
readers are not checked at commit either (gate.py::check_commit).

Rejected: recording only a part's own scope id. Then a part keyed on `all` could never count
toward the `code` scope, so the commit check would either ignore it on changed code (fail-open)
or never be satisfiable.
