---
type: Task
id: CE-186
title: Pin the site's group order and body escaping with tests; drop dead sabotage rows
brief: CE-185 verifier nits; each new test sabotaged
pri: NOW
state: closed
deps: []
goals: [G-2]
source: session 2026-11-06a
created: 2026-11-06
moved: 2026-11-07e
updated: 2026-11-07e
status: deprecated
closed: 2026-11-07e
---

Pin the two site-build claims no test holds, and drop dead sabotage rows (CE-185 verifier nits, 2026-11-06a).

- Enum order of the decisions listing on the site is unpinned: with `statuses=()` passed to decisions.py::groups in site.py::Site.decisions_page, groups sort alphabetically and every test still passes; tests/test_site.py's fixture has no REJECTED decision. Add one and assert enum order; sabotage it.
- DEC-159's "bodies are escaped" is unpinned: dropping esc() from the text between links in site.py::Site.link leaves tests green, because no fixture body holds `<` or `&`. The site is public, so an unescaped body is markup injected into the page. Add a body with `<script>` and `&` and assert it is escaped; sabotage it.
- tools/sabotage_ce55.py still patches the removed `reindex` method in working.py and stops there; drop the row as sabotage_ce5.py did.
- CE-170's nit about working.py::Engine._hk_reindex is moot (the method is gone with CE-185): prune it from CE-170.

## Traps

- none yet

## Read first

- site.py::Site.decisions_page
- site.py::Site.link
- tests/test_site.py

## Log

- 2026-11-06a (claude-code/claude-opus-5-5): INV-97 duplicates INV-95: at CE-185's close (031e87a) the coordinator restated the design review's residuals with --residual; the engine skips only an exact repeat of a review residual's text, so a reworded one is filed again. Two things to do: settle INV-97 (the route says an entry is edited only when the code changes, so it was left in place), and have task close refuse or warn on a --residual that rewords one of the review's residuals.
- 2026-11-06c (claude-code/claude-opus-5-5): DEC-162: INV-97 is retired as a duplicate of INV-95 this session (hand edit of the register, which no op writes); this task now carries only the pins and the dead sabotage rows.
- 2026-11-07e (claude-code/claude-sonnet-5-5): CE-170's _hk_reindex nit: settled by CE-170's own close (2026-11-07e, bullet 3 dropped as moot, code removed by CE-185); its closed body is left as is (DEC-241)
- 2026-11-07e (claude-code/claude-sonnet-5-5): closed: pinned the site's decision enum order and escaped record text; dropped sabotage_ce55's dead reindex row (671d7c2; DEC-240..243 records by 32f580b, ade8b49, b6f789f, 9550102)
  residual risk: INV-181
