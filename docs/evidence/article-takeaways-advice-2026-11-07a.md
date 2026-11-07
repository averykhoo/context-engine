# Article takeaways: fable advice, 2026-11-07a

FROZEN 2026-11-07a. On the owner's "ask fable about the article takeaways" (DEC-170), one fable agent (77k tokens, 2026-11-07a) advised on the two takeaways the 2026-11-06f close drew from an XDA article. This is advice, not owner words: nothing in it is decided until the owner answers.

# Fable advice on the XDA takeaways (DEC-170, session 2026-11-07a)

Read: DEC-45, DEC-44, DEC-60, contract § Rules coordinator bullets, banner Lesson line, ledger 2026-11-06f.
Article found: https://www.xda-developers.com/extend-clause-usage-with-opus-sub-agents/
("My Claude weekly limit lasted longer once I made Opus a project manager").
Sibling XDA piece (same site, different author): delegated runs used 23-34% MORE tokens than Opus alone and
took 7-10x longer; the saving is per-token price, not token count.

## What the article actually evidences
- One user, one project, no token numbers; usage split "can't be certain".
- Opus orchestrated; three Sonnet builders + one Haiku; Opus itself verified (not an independent verifier).
- Author stopped using Opus for small fixes because it kept spawning sub-agents and testing heavily for
  minor changes -- the real lesson is takeaway (2), and it is exactly what DEC-60 mandates here.

(advice follows)

## Advice

**Takeaway 1, Sonnet builders under an Opus verifier: TRIAL, not adopt.** The article is one anecdote with no
numbers, and its Opus did the verifying itself. CE-195's 1.15M was mostly three fix rounds, each a full Opus
verifier pass; a weaker builder can add rounds and erase the per-token saving (the sibling XDA piece measured
delegation costing 23-34% more tokens, not less). Also, CE-195's builder made six design calls (DEC-164..169):
design-bearing builds stay Opus.

Trial shape: the next 6 code tasks whose design is pinned (ACs written, no open ASK, no FRAMEWORK/contract/kit
change). Builder Sonnet, verifier Opus (independence kept, DEC-44). Escalation ladder: a second verifier FAIL
sends the fix round to Opus. Record per task, in a task comment: subagent tokens (builder+verifier+rounds),
FAIL rounds, escalated or not, and whether a trap-class bug (CRLF, kit equality, pycache, Linux divergence)
reached the verifier. Baseline: CE-195 and the 2026-11-02a..06c tasks. Adopt if median tokens/task fall by
30% or more and FAIL rounds rise by at most one; drop it if two tasks escalate.

**Takeaway 2, a size floor: ADOPT.** The article's one real finding is Opus over-delegating minor fixes, which
is what "even a lone task goes to ultracode" (DEC-60) produces here. Floor, all four checkable from `git diff
--numstat` and paths: (a) at most 2 files and 30 changed lines; (b) nothing under `tests/` added or an existing
assertion changed; (c) no path under `docs/framework/`, `src/context_engine/kit/`, the contract, or a workflow;
(d) no new refusal, guard, or record kind. Below it, the coordinator (or one Sonnet agent) edits directly.
Still applies below the floor: the gate (`gate status --require code`), lint, by-path commit, and one read-only
Sonnet diff review with no fix rounds; a FAIL from it promotes the task above the floor. The sabotage rule
cannot be skipped by accident: (b) and (d) put every guard change above the floor.

**What changes.** DEC-45 and DEC-60 are owner words: not edited, but narrowed by one new owner decision.
CLAUDE.md § Rules coordinator line: "opus for code and review" becomes "opus for review and design-bearing
builds; sonnet builders on trial (task id); haiku for watchers", plus the floor. Contract bullet 1 ("each task,
even a lone one") gets the floor as its exception. File one task to run the trial and one to pin the floor.

**Risks.** Verifier independence: never let the Opus verifier become the fixer. Sonnet traps: CRLF and kit
equality are caught mechanically by lint, so the real Sonnet risk is design drift, hence the pinned-design
filter. Floor gaming: a task split into sub-floor edits; rule that a task's edits are summed. Measurement is
the deliverable: without the per-task numbers the trial is just another anecdote.
