---
type: Decision
id: DEC-18
title: Avoid fable subagents unless requested or really necessary; never fan out with fable
actor: owner
decision_status: PROVISIONAL
decided: 2026-10-09
session: 2026-10-09d
body_sha: sha256:0cc169dc74b5777277ecc31c969f79870ab8883d3c01f808973bcf83a7d8062e
---

The owner, 2026-10-09 (session 2026-10-09d), asking for a few notes to be added:

> unless requested or really necessary, avoid using fable subagents, especially fanout with fable, because it wastes tokens. if it's really needed then do whatever minimizes cost

So: do not use `fable` as a subagent or workflow model unless the owner asks for it or it is really necessary; never fan out with it. When it is really necessary, do whatever minimizes its cost (fewest agents, narrowest prompt, capped output). This goes into the framework (FRAMEWORK §6.6), so every repo that runs it inherits it. It tightens the global `CLAUDE.md § Delegation` model line, which allows fable for open-ended design or taste judgement.
