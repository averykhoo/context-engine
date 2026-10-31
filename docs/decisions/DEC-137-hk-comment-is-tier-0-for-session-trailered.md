---
type: Decision
id: DEC-137
title: hk comment is tier 0 for Session-trailered commits whose title leads with ids; the rest stays tier 1
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-11-01
session: 2026-11-01b
body_sha: sha256:6dda5b7b46cac38621189326e27e7873c9e4265e2363310d6d43029f30440f82
---

Agent's call (CE-6 close-out, 2026-11-01b). `hk comment` is tier 0 for one case only: commits that carry a `Session:` trailer and whose title leads with board ids (DEC-22). For those, no model is needed:

- The comment text is derived as `<short sha>: <subject>`. An optional `text` argument is the tier-1 path.
- The window is ledger.py::foreign_range (the CE-65 start heads), deduplicated by the sha the item's log already cites.
- A commit whose `Closes:` trailer names the item is left for `hk close`, so a later `hk close --scan` still closes on it.
- A commit with no trailers stays with foreign-commit reconciliation (tier 1, CE-12).

This amends FRAMEWORK §6.11's tier table, which put the comment row in tier 1. Options weighed: keep the whole row tier 1 (nothing mechanical, so it is forgotten as now), or split it by whether the title parses without a model (chosen). It is cheap to undo: one op and one table row.

Links: CE-6, CE-12, CE-65, DEC-22.
