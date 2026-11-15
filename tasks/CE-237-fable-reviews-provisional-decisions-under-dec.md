---
type: Task
id: CE-237
title: Fable reviews provisional decisions under DEC-342's list, with a NEEDS CONTEXT outcome
pri: NOW
state: open
deps: []
goals: [G-7, G-3]
source: session 2026-11-13d
created: 2026-11-13
moved: 2026-11-14a
updated: 2026-11-16a
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

- The list itself, and the rules that decide who decides, are ask-the-owner under the list (its condition 4): wording changes beyond what DEC-342 and DEC-343 adopted go to the owner.
- NEEDS CONTEXT carries no options and no recommendation (DEC-343): the body's paragraph above predates that and is wrong on this point; write §6.5 and the runbooks from DEC-343.
- A fable acceptance must never read as owner agreement: that is what `accepted_by` is for.
- Fable shares the maker's priors (evidence doc §1): do not widen silent acceptance beyond implementation detail under a criterion.

## Read first
- DEC-342; docs/evidence/reviewer-accepts-fable-2026-11-13.md; docs/evidence/reviewer-accepts-census-2026-11-13.md §2
- US-24, DEC-48, DEC-34, DEC-18; FRAMEWORK P8 and §6.5

## Log

- 2026-11-14a (claude-code/claude-opus-5-5): DEC-343 (owner, 2026-11-14a) corrects the body's NEEDS CONTEXT paragraph: it is an open-ended question with NO options and NO recommendation (DEC-34's shape does not apply), because what is missing is the owner's story or goal, which an agent cannot supply. The ASK says what is missing, contradictory or shown false, quotes the records involved, and asks for the story, goal or charter text. Promoted to NOW ahead of CE-235 (DEC-343 item 2).
- 2026-11-16a (claude-code/claude-opus-5-5): escalated: steps 1-2 builder went sonnet -> opus in round 3 after two verifier FAILs (DEC-326); verifier-r3 PASS. Workflow wf_f18bca2f-f88, reports in .scratch/ce-237/.
- 2026-11-16a (claude-code/claude-opus-5-5): steps 1-2 committed e9eab4b (gate 2160 passed). Owed to the owner before step 3, from verifier-r3 (.scratch/ce-237/verifier-r3.md): (1) A4: FRAMEWORK P8, the contract's Decision status bullet and the kit README still say a call stays PROVISIONAL until the owner reviews it and prescribe a bare decision accept, which the engine now refuses for agent callers; change them to state DEC-342? (2) is the generic §6.5 transcription faithful (why-tails and ids dropped, fable written as 'the arbiter', the arbiter-input sentence taken from evidence §1)? (3) where does this repo's thin-story list (US-12/13/22; US-16/18/20/21) live durably? (4) was the NEEDS CONTEXT shape in guards.py::ask_problems in scope? (5) how does a NEEDS CONTEXT question close, given that ask answer also mints an owner decision? (6) should the arbiter run decision accept itself, so that accepted_by names it? (7) the C tier's 'a random sample surfaces in the digest' has no procedure step: keep it, or add one? (8) does a built task's decision become BUILT rather than ACCEPTED? Non-blocking: ask_problems matches 'needs context' loosely (N3).
