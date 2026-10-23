---
type: Decision
id: DEC-80
title: Engine internals move from FRAMEWORK.md to docs/engine.md
decision_status: PROVISIONAL
actor: claude-code/claude-opus-5-5
decided: 2026-10-24
session: 2026-10-23f
body_sha: sha256:c50e002d59c0119081e4aa1f25756b3495e7e8abbad41a609b02b03f6e28732f
---

An agent's call under P8 (cheap to undo), made by CE-93's builder in session 2026-10-23f and landed in c5b812f. Recorded afterwards from the builder's report (its PROVISIONAL call P-3). Not owner words.

**Call.** Engine internals cut from FRAMEWORK.md (commit mechanics, the pre-write lint, the engine lock, foreign-commit ranges, the MCP server's op lookup, the run ledger's ids) go to a new `docs/engine.md`, which exists only in the engine repo and so may cite task ids. It is routed (`Engine internals` in `[[routes]]`) and read by G-D3 and G-D4. Where a by-hand form already existed in `docs/runbooks/manual-mode.md`, FRAMEWORK.md now points there instead.

**Why.** A user of the framework needs the rules, operations and refusals, not how the engine implements them; the implementation detail still has a guarded home where the engine's maintainers will look.

Task: CE-93. Commit: c5b812f.
