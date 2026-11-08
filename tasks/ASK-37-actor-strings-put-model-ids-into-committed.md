---
type: Question
id: ASK-37
title: 'Actor strings put model ids into committed records: keep them, or drop the model (audio-workspace item 8)?'
brief: "Recommend: keep harness/model; the contract says a repo's CLAUDE.md may narrow it"
pri: LATER
state: open
deps: []
source: session 2026-11-07e
created: 2026-11-08
moved: 2026-11-07e
updated: 2026-11-07e
last_asked: 2026-11-07e
---

**Question:** Should an agent's actor stay harness/model-id in committed records?

**Context:** audio-workspace feedback entry 8 (agent-raised, 2026-11-06): the contract sets CE_ACTOR to harness/model, so claude-code plus a model id lands in the committed ledger and every task log line, and the entry says the Claude Code harness tells agents not to put model ids in pushed files, so the two instructions conflict. Here the model id is load-bearing: FRAMEWORK §6.5 says "The model id matters: 'survives model changes' is otherwise untestable"; DEC-171 derives each engine commit's Co-Authored-By line from the actor's model, carrying out DEC-170 (your words); CE-198's sonnet-builder trial told models apart by actor.

**Why owner-only:** it changes what every repo's history records and which of two standing instructions wins; neither is cheap to undo once pushed.

**Options:**

- A. Keep harness/model as now, and add one contract line: a repo's CLAUDE.md may narrow the actor (CLAUDE.md already wins over the contract), so a repo that must not publish model ids sets its own form.
- B. Make the actor harness plus role (claude-code/builder) everywhere; the model goes only to uncommitted session state, and DEC-171's co-author line needs --model or CE_CO_AUTHOR.
- C. A per-repo switch in context.toml that makes the engine drop the model from what it commits, keeping it in the uncommitted session state.

**Recommendation:** A: the framework's own trials and DEC-170's co-author line read the model from the actor, and B or C would lose that in every repo to fix one repo's conflict, which a CLAUDE.md line already settles. Option A changes the contract, so it waits for the next framework version bump.

**Blocks:** none
