---
type: Decision
id: DEC-287
title: "coverage map: a new dated map supersedes the 2026-10-12 map, with G-W10 EXISTING CE-6 (built), section 6.11's home refreshed, section 6.12 DEFERRED (US-12, CE-90), and an Operations table holding hk.ratchet DEFERRED with G-V2 (CE-168)"
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:6289d9e5475732e6f8f01ccc115a18d02eb5ca259ef7b4cc1a06d5cea7d87bd2
---

The agent's call on CE-164 (session 2026-11-07e): a new dated coverage map, `docs/evidence/framework-coverage-2026-11-07e.md`, supersedes the frozen 2026-10-12 map, which stays unedited.

It copies the 2026-10-12 tables and changes only:
- G-W10: EXISTING CE-6 (built), home `working.py::Engine.hk_run` (its count line and `[housekeeping] max_writes`, AC-177);
- §6.11 Housekeeping: home `working.py::Engine.hk_run` (tier 0 built); tier 1 is CE-12; `hk.ratchet` waits with G-V2 in CE-168;
- §6.12: DEFERRED, citing US-12 and CE-90 (the owner "does not need them built yet"); un-defer when the owner asks for them built;
- a new Operations table holding one row, `hk.ratchet` DEFERRED (no ratcheting floor until G-V2's; CE-168 holds both); registered operations need no row;
- the Totals section is replaced by a pointer to `context-engine coverage`, which generates them.

Cheap to undo: a later dated map replaces it.
