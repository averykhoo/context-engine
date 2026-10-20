---
type: Decision
id: DEC-64
title: 'CE-99 rerank: milestone is the framework fully built; tasks carry required goals; the agent applies moves, the owner approves drops'
actor: owner
decision_status: PROVISIONAL
decided: 2026-10-20
session: 2026-10-20b
body_sha: sha256:1e956c7574e24259874638f87fe25af31e9aef605aa4e7424f9f14201254bdf6
---

Owner, 2026-10-20b, verbatim answers to the session's CE-99 questions (multiple choice; the option labels the owner picked):

- "What is the next milestone the rerank should rank against?" -> "Framework fully built"
- "Should board items carry a `goals` field linking them to charter goals?" -> "Required, backfilled (Recommended)"
- "Who approves a rerank's moves?" -> "Agent; you approve drops (Recommended)"
- "When should the rerank trigger?" -> "why do you recommend now empty over now plus next? would that mean basically running it once per session, since now is usually done once per session? the prioritization is slightly expensive token wise and if the ranking is unlikely to change much i thought it would be more efficient to assume the previous ranking was reasonable and finish off the 1+5 tasks, then run it again, kind of like a sprint prioritization happens biweekly instead of daily in the standups"

Context (the session's words, not the owner's): the options as offered were:
- "Framework fully built": G-7, every FRAMEWORK component built, prose-only by choice, or deferred with a reason; FRAMEWORK.md rewritten for users (CE-93).
- "Required, backfilled": new tasks must name G-n (lint checks it like stories); the first rerank backfills the open items.
- "Agent; you approve drops": per DEC-48, promotes and demotes are applied by the coordinator and flagged in the close digest; dropping or retiring an item, or changing the milestone, waits for the owner.
- The trigger answer is a question, not a pick; the session answers it in chat and the trigger is settled by a later amendment.

## Amendments

- **2026-10-20b (claude-code/claude-opus-5-5):** Owner, 2026-10-20b, verbatim: "agreed for updated q4 answer"

  Context (the session's words, not the owner's), the trigger the owner agreed to:
  - Clean close keeps its light reorder (no full read): the standup.
  - The full rerank runs when NOW and NEXT are both cleared (about six tasks), when orient says "rerank due", and whenever the owner asks: the sprint.
  - A new owner decision or story that changes priorities makes orient say "rerank due" without running the rerank; the owner chooses whether to run it early.
