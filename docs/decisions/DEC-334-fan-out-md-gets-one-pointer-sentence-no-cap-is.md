---
type: Decision
id: DEC-334
title: fan-out.md gets one pointer sentence; no cap is raised
tasks: [CE-219]
actor: claude-code/claude-opus-5-5
decided: 2026-11-11
session: 2026-11-11a
decision_status: PROVISIONAL
body_sha: sha256:c8ce6643f863bea82d95d1c20d232ce928dde5a659e3cebe7e153ca21090cf1b
---

**Decision:** fan-out.md (the kit copy and this repo's byte-equal copy) gets one pointer sentence in § Build rounds, to FRAMEWORK §6.6's size floor and build ladder, within its caps (110 lines, 8000 bytes). Neither fan-out.md's caps nor CLAUDE.md's are raised; CLAUDE.md's Coordinator bullet is rewritten within its caps (140 lines, 10000 bytes, width 125).

**Why:** the kit template carries fan-out.md's caps too, so raising them costs every adopting repo an upgrade step (the 0.5 precedent). The rule fits in FRAMEWORK, which is uncapped, and both rewrites fit.

**Rejected:** a full "how" section in fan-out.md with raised caps; raising CLAUDE.md's caps.

Planner's call for CE-219, session 2026-11-11a.
