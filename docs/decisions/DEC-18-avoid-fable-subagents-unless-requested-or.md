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

## Amendments

- **2026-10-13a (claude-code/claude-opus-5-5):** Owner, 2026-10-13a, after the proposed agent roster (coordinator, task owner, builder/fixer, adversarial reviewer, scout/auditor, CI watcher, install trial, hk agent) and three proposed board items (bootloader contract; agent roster; move framework rules out of the global CLAUDE.md):

  "We also need a sort of arbiter agent for making decisions based on the repo's goals and thinking though whatever open questions there are in detail, for this I usually use fable. This is one of the rare situations where I do ask for a fable subagent, the other is for really detailed work like writing the difficult bits of proofs

  Okay to file those.

  Any concern that standing instructions for ultracode might not be respected if it's sent from an mcp? Does that and other permissions related stuff need to go into the Claude md instead?"
