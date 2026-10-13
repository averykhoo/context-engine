---
type: Question
id: ASK-5
title: Rename a repo's existing ids to the framework's form at adoption, or keep them?
brief: 'Recommend: rename, keep the number, old id stays a resolvable alias; same prefix per kind, task prefix per repo'
pri: NEXT
state: closed
deps: []
source: session 2026-10-13b
created: 2026-10-13
moved: 2026-10-13b
updated: 2026-10-13c
last_asked: 2026-10-13c
status: deprecated
closed: 2026-10-13c
answered: {on: 2026-10-13, session: 2026-10-13c, decision: DEC-37}
---

**Question:** When a repo adopts the framework, are its existing ids renamed to the framework's form, or kept as they are?

**Why owner-only:** the owner wants a homogeneous board ("I feel like I would update them all to homogenize the task board"); the contract says never renumber an id. Which wins is the owner's call.

**Facts (adhoc, surveyed 2026-10-13b):** decisions are `D-n` (574 mentions in tracked docs, and in docstrings in `adhoc_loc/` and `adhoc_sep/`); a few `Dn` without the dash (28); questions are `Qn` (47); board items are `1`, `1a` .. `1i`, `2b`; 38 of 69 commit messages cite one of these. Commit messages cannot be rewritten without rewriting history.

**Options:**
(a) keep every imported id exactly as it is;
(b) rename everything to the framework form and rewrite references in docs and code;
(c) rename to the framework form at import, keep the number where there is one, and record each old id as an alias the engine resolves (`why`, `task show`, lint), with the mapping table as an evidence doc; history and code comments are left alone.

**Recommendation:** (c). It gives the homogeneous board without breaking the 600-odd references the repo already has: a commit or a docstring that says `D-27` or `1h` still resolves. For prefixes: a record kind uses the same prefix in every repo (`DEC`, `ASK`, `US`, `AC`), and tasks use a per-repo prefix (`CE` here; e.g. `AD` for adhoc), so a task id says which board it is on. So in adhoc: `D-27` -> `DEC-27`, `Q8` -> `ASK-8`, `1h` -> a new `AD-n`. Cost: an `aliases:` field and its lookup, inside CE-7.

**Blocks:** CE-7 (its import)

## Log

- 2026-10-13c (claude-code/claude-opus-5-5): answered by the owner: DEC-37
