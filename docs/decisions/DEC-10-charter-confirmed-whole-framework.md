---
type: Decision
id: DEC-10
title: "Charter confirmed, widened to the whole framework; a managed server is an anti-goal; dogfood here before any other repo"
actor: owner
decided: 2026-10-08
session: 2026-10-08b
decision_status: BUILT
tags: [charter, scope, adoption]
answers: ASK-1
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-08T17:00:00+08:00 }
body_sha: sha256:f5a19576d9ce6eac52c137fb51180d7078dfbf141765a07c3009f6ae2cdae4b3
---

The owner's answer to ASK-1 (verbatim in US-9):

1. **Scope is the whole of `docs/framework/FRAMEWORK.md`**, deployable across all the owner's
   repos, not only the record engine (§8.0). The engine is the first piece. New goal G7.
2. **A server the owner has to start or manage is an anti-goal**, not merely a non-goal. The
   system is text in a repo that Claude Code manages; Claude Code may start its own server as
   a ritual.
3. **One versioned implementation, built and dogfooded in this repo first**; how other repos
   adopt it is worked out after that. This puts CE-8 (dogfood) ahead of CE-7 (the adhoc trial)
   and amends DEC-6's ordering.
4. The rest of the charter, including the agent's ranking of the principles, stands
   ("not incorrect").

## Amendments
