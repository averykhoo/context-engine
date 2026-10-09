---
type: Decision
id: DEC-17
title: Ultracode has standing approval when used to minimize token consumption
actor: owner
decision_status: PROVISIONAL
decided: 2026-10-09
session: 2026-10-09c
body_sha: sha256:9640afc92974c7e7ff19bf19e81b74e2e43aac01bc18a3f243e7ade687ab9292
---

The owner, 2026-10-09 (session 2026-10-09c), while asking for a git history rewrite to be run
with ultracode:

> do you think sonnet is sufficient? you can spin up instances using ultracode. oh also
> ultracode usage should have standing approval whenever used to minimize token consumption,
> add that somewhere into the framework

So: using ultracode (the `Workflow` tool, multi-agent orchestration) needs no per-request
opt-in whenever it is used to keep the session's own context and token consumption down,
i.e. to push bulky reading, auditing or verification into agents and keep only their verdicts.
This goes into the framework (FRAMEWORK §6.6), so every repo that runs the framework inherits
it. It matches the global `CLAUDE.md § Delegation` standing approval (2026-09-20), which is
machine-local and so does not reach other repos.
