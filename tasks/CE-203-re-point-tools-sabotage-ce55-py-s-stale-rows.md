---
type: Task
id: CE-203
title: Re-point tools/sabotage_ce55.py's stale rows
brief: nine rows match nothing; re-point each, keep its reason line
pri: LATER
state: open
deps: []
goals: [G-2]
source: session 2026-11-07e
created: 2026-11-08
moved: 2026-11-07e
updated: 2026-11-07e
---

Re-point tools/sabotage_ce55.py's stale rows

Nine rows of tools/sabotage_ce55.py::S no longer match the code (found by CE-186, 2026-11-07e, by counting each row's pattern against the files: `text.count(old) == 1` is what tools/sabotage_ce49.py::run asserts, so running the table stops at the first one). The code moved, the guards remain, so each row needs a new pattern whose failing line is still the row's reason. CE-186 dropped the tenth, the `reindex` row, because the method is gone.

Rows by number at 2026-11-07e (after CE-186's edit), and where the code went:

- 19 and 21 (task close, working.py): the close's commit fields (`commit_trailers`, `commit_body`, `commit_title`) are now set in working.py as `st.commit_title, st.commit_body, st.commit_trailers` (store.py::Store holds them).
- 22 and 24 (task close, ops close `body=`, `commit_title` / `commit_trailers`): same move.
- 27 and 28 (commit.py): the trailer paragraph is now `paras.append("\n".join([*trailers, f"Session: {session}", ...]))`, and the `Session:` add is `add = [] if session_trailers(text) else [...]`.
- 40, 41 and 42 (commit.py Outcome lines): "nothing to commit" now has three variants.

Re-check the row numbers with a static count before starting; they shift if a row is added or dropped.

## Traps

- Do not run the whole table to find them: it is about 50 pytest runs and stops at the first stale row. Count each pattern statically.

## Read first

- tools/sabotage_ce55.py
- tools/sabotage_ce49.py::run
- src/context_engine/commit.py
- src/context_engine/working.py
