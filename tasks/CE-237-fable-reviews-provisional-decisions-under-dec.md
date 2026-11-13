---
type: Task
id: CE-237
title: Fable reviews provisional decisions under DEC-342's list, with a NEEDS CONTEXT outcome
pri: NEXT
state: open
deps: []
goals: [G-7, G-3]
source: session 2026-11-13d
created: 2026-11-13
moved: 2026-11-13d
updated: 2026-11-13d
---

Build DEC-342: fable reviews and accepts agents' provisional decisions under the three-tier list, with a fourth outcome, NEEDS CONTEXT

DEC-342 adopts the list in docs/evidence/reviewer-accepts-fable-2026-11-13.md §2 and §3, with the two cuts session 2026-11-13c proposed, and asks for an outcome the list did not have.

**NEEDS CONTEXT, the owner's addition.** The ask-the-owner tier asks "approve this call?". NEEDS CONTEXT asks "what do you want here?". It is raised as a dilemma, and its answer lands as a new or amended story, or a charter amendment, not as a decision acceptance. It replaces the list's A6 (a GAP: no covering record, or a thin story) and adds three triggers A6 did not have:
- two owner records contradict each other on the point;
- a story, goal or charter line rests on an assumption the work showed false;
- a goal is too vague to settle the call.

Each one goes to the owner as an ASK whose part one is the dilemma, the options and a recommendation (DEC-34), and whose requested answer is the story or amendment text.

1. Write the list, NEEDS CONTEXT included, into FRAMEWORK.md §6.5 (who decides and decision status) and procedures.md (the review step at each task close: one fable call per batch, never fanned out, DEC-18), with the by-hand fallback in manual-mode.md (DEC-20). Both runbook copies stay byte-equal.
2. Engine: `decision accept` writes `accepted_by` from the caller's actor, and lint reds an ACCEPTED decision without it from the cutover on. A non-owner accept requires `--covered-by <owner record>` or `--gap`, and is refused when the decision's refs name an open ASK. Sabotage each.
3. Then the backlog pass: one fable pass over the PROVISIONAL decisions, batched by task. The silent-accept and flag tiers are accepted with `accepted_by`; the ask and NEEDS CONTEXT ones go to the owner as a handful of grouped ASKs. The owner spot-checks 10 of the silent accepts. Decide first, and ask the owner, whether a built and verified task's decisions become BUILT rather than ACCEPTED.

## Traps
- The list itself, and the rules that decide who decides, are ask-the-owner under the list (its condition 4): wording changes beyond what DEC-342 adopted go to the owner.
- A fable acceptance must never read as owner agreement: that is what `accepted_by` is for.
- Fable shares the maker's priors (evidence doc §1): do not widen silent acceptance beyond implementation detail under a criterion.

## Read first
- DEC-342; docs/evidence/reviewer-accepts-fable-2026-11-13.md; docs/evidence/reviewer-accepts-census-2026-11-13.md §2
- US-24, DEC-48, DEC-34, DEC-18; FRAMEWORK P8 and §6.5

## Log
