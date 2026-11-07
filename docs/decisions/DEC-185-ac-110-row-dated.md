---
type: Decision
id: DEC-185
title: AC-110 row dated
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:5ba01da9a140e17ab5f1b5b6615b8ed360c8444fc424fa5ee7f1a8288326c73b
---

AC-110's row in `docs/criteria.md` carries the measurement's date (2026-10-14) and the Claude Code version (2.1.280), as the kit README does, so the "33 to 36 under load" figure no longer reads as current forever. Changed through `criterion set`; its status stays `tested`, since its claiming test (`tests/test_kit.py::test_the_kit_readme_names_the_mcp_connect_timeout_and_its_remedy`) already pins the date and version in the README and needs no change.

Made for CE-200.
