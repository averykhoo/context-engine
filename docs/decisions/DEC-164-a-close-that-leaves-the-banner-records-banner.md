---
type: Decision
id: DEC-164
title: 'A close that leaves the banner records banner: kept <key>, and G-W1 accepts it (CE-195)'
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
refs: [DEC-163, US-21]
decided: 2026-11-06
session: 2026-11-06f
body_sha: sha256:16378380eaa915f1339d1b5d75047e349a972b970ad140ed28edc9bff729e2cd
---

The agent's call on CE-195 (DEC-163, US-21), made while building it in session 2026-11-06f: how a clean close that changed no durable banner line passes G-W1.

Options:
(a) `session close` without a banner records `banner: kept <the banner's key>` as a receipt in its entry, and G-W1 passes when the banner's key is older than the newest close but that close kept this banner; a close in a repo with no banner yet is refused, naming `--banner-file <banner.md> --seen none`, so the first close writes the first banner;
(b) drop G-W1's freshness check altogether: the banner's key only says when it was last edited;
(c) make `session close` require an explicit `--banner-kept` flag or a banner, every time.

Chose (a): the entry says, in the record, what became of the banner, so a close made outside the engine (or by an older one) that left the banner alone is still red, and a hand edit of the banner heading to another key is caught (`that close kept the banner of X, not this one`). (b) loses that; (c) costs a flag at every close and breaks every adopter's existing `session close` call. Not checked by any of them: that a kept line is still true; fewer hand-written lines keep that judgement small.

Built in working.py::Engine.session_close, working.py::Engine._banner_kept and working.py::Engine.lint_working; pinned by AC-185. Cheap to undo.
