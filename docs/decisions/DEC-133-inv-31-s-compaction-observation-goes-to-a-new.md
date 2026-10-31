---
type: Decision
id: DEC-133
title: INV-31's compaction observation goes to a new dated evidence doc, not the frozen 2026-10-23 probe
decision_status: PROVISIONAL
actor: claude-code/claude-opus-5-5
decided: 2026-11-01
session: 2026-10-31a
body_sha: sha256:f4f58d1fad9d89f6fdf82025b4c80ad8ad31941371223785b201c5e7d638ff55
---

Agent call (coordinator, session 2026-10-31a), carrying out DEC-132. It is cheap to undo, so it is recorded PROVISIONAL for the owner to review.

DEC-132's option text said the INV-31 clause names "which evidence file to update", and the research brief proposed appending to the compaction row of `docs/evidence/inv31-adhoc-probe-2026-10-23.md`. That file is FROZEN ("provenance, as written"), and frozen provenance is never edited (CLAUDE.md § Rules). So INV-31's clause tells whoever sees the agent half of the compaction observation to write a new dated evidence doc, `docs/evidence/inv31-compaction-<date>.md`, that cites the 2026-10-23 probe. It does not append to the frozen probe.
