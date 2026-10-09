---
type: Decision
id: DEC-23
title: 'Versioning: engine major.minor is the framework version it implements; G-D0 compares major.minor; contract says framework: 0.5'
actor: owner
decision_status: PROVISIONAL
decided: 2026-10-10
session: 2026-10-10a
body_sha: sha256:2072091afa670c34c7902e874235fe33ccf143c1ea232c037502f0f3af383367
---

The owner, 2026-10-09 and 2026-10-10 (session 2026-10-10a), answering the G-D0 version-scheme question (FRAMEWORK §12.3):

> and what do you recommend for versioning? there's the framework version and engine version and they won't always move in sync, although that's feasible and maybe it should since changes to the framework and engine will likely affect each other for sufficiently large changes

The agent recommended sharing major.minor: engine `0.5.N` implements framework `0.5`; a minor bump means the spec changed in a way the engine must follow and moves both; the patch number is the engine's own; G-D0 compares major.minor; drop `-draft` (below 1.0 already means draft); the package moves from `0.0.1.dev0` to `0.5.0.dev0`.

> okay with your recommendation for patch number, but contract can say 0.5.* just to make it obvious? or do you think its implicit and understood even without that, e.g., python 3.8 can be 3.8.1 to 15

So:
- **The framework is versioned `major.minor`; the engine is `major.minor.patch`, and its major.minor is the framework version it implements.** Engine bugfixes move only the patch. A framework change the engine must follow moves the minor of both.
- **G-D0:** the contract's `framework:` must equal the installed engine's major.minor.
- **`-draft` is dropped.** This repo's contract says `framework: 0.5`; the package becomes `0.5.0.dev0`.
- **`0.5`, not `0.5.*`** (agent's call, owner asked for an opinion): the framework itself has no patch number, so `0.5` is exact, like `python 3.8`. The engine accepts `0.5.*` as a synonym so either spelling passes. The owner may overrule.
