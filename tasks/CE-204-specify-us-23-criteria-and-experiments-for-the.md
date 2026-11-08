---
type: Task
id: CE-204
title: "Specify US-23: criteria and experiments for the planner's model, the agent split and compaction"
pri: LATER
state: open
deps: []
goals: [G-1]
source: session 2026-11-07e
created: 2026-11-08
moved: 2026-11-07e
updated: 2026-11-07e
---

Specify US-23 (owner, 2026-11-08): draft its criteria as `planned` rows of docs/criteria.md, then file the experiments they need.

First results are in docs/evidence/us23-planner-and-cost-2026-11-08.md (agent findings, 2026-11-08):
- Planner model: opus beat sonnet on 10 of 11 replayed plans, but an opus-vs-opus noise arm showed the same gap on its 4 tasks (+2.75 each), so the difference is not separable from bias toward the built plan (p about 0.2). Confidence LOW. Opus's lead was largest on small pinned tasks, not unpinned ones.
- Agent split: cache reads are quadratic in turns; cheapest final context is about 160-170k per agent; 2 x 250k about $3.2, 5 x 100k about $3.7, 1 x 500k about $4.9 per 100k of new work; a split pays until the handoff reaches 70-120k (measured handoff about 15k).
- Compaction never occurred in 168 agents (largest context 307k): untested.

Still open, each needing a design before it runs:
1. A planner trial with no incumbent: every arm planned fresh from the same base, each built by the same builder, scored on outcomes (verifier defects, fix rounds, tokens including the planner's), a noise arm on every task, two blinded judges of different models, 25-30 tasks across size, pinned or not, code/kit/docs.
2. A compaction trial: the same medium task as the usual pipeline and as one long agent with compaction, on 2-3 tasks, scored on cost and the verifier's verdict.

## Traps

- The replay judged plans after one of them was built: judges cited "the build follows X". Do not read 10/11 as sonnet being worse.
- Opus 5.5 cache reads are $0.20 per million (the skill's table), 5% of input, not the 10% the anatomy agent assumed as an alternative.

## Read first

- docs/evidence/us23-planner-and-cost-2026-11-08.md
- US-23
