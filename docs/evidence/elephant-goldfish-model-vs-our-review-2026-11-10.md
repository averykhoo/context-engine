# google/elephant-goldfish-model compared with our review process (2026-11-10)

FROZEN: the comparison as of 2026-11-10; nothing adopted yet (its four candidates wait on the owner).

Session 2026-11-10b. The owner asked how https://github.com/google/elephant-goldfish-model works and how it compares to our review. A sonnet agent read its README, docs/designs/architecture.md, docs/designs/review.md, skills/egm-review/SKILL.md, agents/synthesizer.md, docs/faq.md and TESTING.md. Checked by the session: our wave workflow already records a dead verifier as NO-VERDICT and closes nothing (its recommendation 3).


Source: github.com/google/elephant-goldfish-model (shallow clone, read, deleted): README, docs/designs/architecture.md, docs/designs/review.md, skills/egm-review/SKILL.md, agents/synthesizer.md, docs/faq.md, TESTING.md. Not read: Rensin's Medium essay (linked), resources/document_standards/*.

## 1. What EGM is
A plugin (Claude Code, Codex, Cursor, Gemini, Copilot...) for spec-driven development. It reviews DESIGN DOCUMENTS before code, not code. [docs]
- Elephant = the main agent: holds project context, interviews the human, drafts concepts_brief.md then the design doc, and triages review findings (egm-resolve). Human decides trade-offs and approves via PR.
- Goldfish = fresh, zero-context subagent reviewers that see only the doc plus a reading list (GoldfishContext, linked in-repo files). Personas in agents/: zoom_out (YAGNI/reuse), comprehension (naive reader, reads the doc ALONE), design_critic, implementation_readiness, codebase_details (checks paths/signatures against live source), structural, style, inventive_catalyst (TRIZ), synthesizer.
- Loop (review.md): 5 sequential stages, Zoom Out -> Comprehension -> Critic -> Zoom Out (only the additions) -> Implementation Readiness. A synthesizer subagent fans out reviewers in parallel (optionally two independent instances A/B per reviewer for recall), dedups, ranks Blocker/Major/Nit. A reviewer that fails twice is "not run", never "zero findings".
- Verdicts: the Elephant answers each finding PROPOSE FIX / CONTEST (must cite evidence the reviewer could read) / ESCALATE (only outside knowledge refutes it; human decides) / DECLINE (nit). Comprehension gaps cannot be contested; severity cannot change without a contest. Human triage modes: auto-accept, interactive, artifact comments.
- Stopping rule: a round is clean if no unsettled Blocker/Major; stop after TWO consecutive clean rounds or human halt. At 5 rounds, or when a new finding would revert an earlier fix, ask the human (accept / continue / back to drafting). Contested/declined findings stay settled across rounds; a fixed finding reopens if re-raised.
- Hard rule: no subagent tool = stop; "a review in the same context is not a Goldfish review" (SKILL.md).
- Evidence: none quantitative. FAQ says compare "total time, useful findings, and rework on your own tasks" and that completing the workflow "does not demonstrate a productivity improvement". TESTING.md covers offline schema/link unit tests plus per-skill test_scenarios.yaml "precision and recall" benchmarks (no results published in what I read). Architecture claims (context pollution, confirmation bias) are asserted, not measured.

## 2. Our process (fan-out.md, CLAUDE.md coordinator, contract.md, US-23 evidence)
Coordinator never works; each task goes to an agent. Planner (opus, read-only, with a critic) -> builder in disjoint-ownership waves -> independent verifier, "skeptic by default", tries to refute each claim, never the builder -> up to 3 fix rounds -> gate (pytest + lint) with the sabotage rule -> CI watcher per push. Adversarial review is per-lens (spec fidelity, fresh deploy, checks-that-pass-when-they-should-fail) then a skeptic pass. Reports are evidence, not findings; coordinator makes the final call. US-23 evidence measures verifier cost (opus verify ~$0.53 lifetime, never hits cache) and handoff re-absorption (verifier re-sees 23-35% of tool results already read upstream); it states context rot is "unobserved/not measurable".

## 3. Comparison
| Axis | EGM | Ours |
|---|---|---|
| Object reviewed | Design doc / plan, pre-code | Code + records after build; plan gets a critic |
| Verifier memory | Fresh, deliberately starved: sees doc + reading list only; comprehension persona sees doc alone | Fresh agent but reads task, plan, diff, repo: full evidence access, no builder transcript |
| Independence | Reviewer never saw the drafting chat; author (Elephant) adjudicates findings, but must cite evidence to contest | Verifier never did the work; coordinator reads the verdict, not files |
| Disagreement | Explicit protocol (CONTEST/ESCALATE/settled set) | Implicit: fix rounds, escalate to opus after 2 FAILs |
| Stopping | 2 consecutive clean rounds, cap 5 | Up to 3 fix rounds, then escalate |
| Catches that other misses | Missing background, unstated assumptions, YAGNI/reinvention, hallucinated APIs in the plan, before any code is spent | Real behavioural defects, weak tests (sabotage), cross-platform CI breaks, record/lint integrity |
| Cost | Many parallel reviewers x 5 stages x rounds, each paying a cold start; unmeasured by them | One verifier per task; measured (US-23) |
| Context rot | Argued as the core motive (author/reviewer in one thread validates its own assumptions); no data | Mitigated by agent-per-task and fresh verifier; our own data says unmeasurable |
| Human role | Approves spec, triages every finding | Owner at intake and push; coordinator triages |

Overlap: both reject same-context review, both use fresh subagents, ranked findings, a skeptic stance, one persisted report per agent. Note our planner/critic step is the nearest EGM analogue.

## 4. Recommendations (R = my inference; EGM claims marked [docs])
1. Comprehension-only reader on plans/task bodies [docs: persona reads doc alone]. Cost: one cheap sonnet agent per non-pinned plan, ~$0.2-0.5. Benefit: finds unstated assumptions our critic (which shares planner context norms) misses; builder prompts are exactly "zero-context readers". Trial on 5 plans, count defects found vs later verifier findings (R).
2. Adopt their settled-findings ledger and explicit CONTEST/ESCALATE states for fix rounds [docs]. Cost: a few lines in the verifier/fix prompt. Benefit: stops reopen loops and fix-reverts-earlier-fix; their "new finding would revert an earlier fix -> stop" is a clean extra stop signal for our 3-round cap (R: cheap, no tokens).
3. "Failed reviewer = not run, never zero findings" [docs]. Cost: zero. Benefit: a verifier that times out must not read as PASS; check we enforce this in the workflow script (R).
4. Starved-context second verifier on high-risk tasks only (spec text + diff, no plan or builder summary), run as A/B against the normal verifier [docs mention A/B instances for recall]. Cost: roughly +$0.5 per task (US-23 verify cost, always cache-cold). Benefit: tests whether plan-carried framing biases our verifier; trial 10 tasks, compare defects (R).
5. Hallucinated-API check as a codebase_details-style lens on plans [docs]: verify every cited path/signature exists before build. Cost: small grep agent; we already require grep-before-cite, so mostly mechanical (R: could be a lint, no agent).

Do NOT adopt: the 5-stage x multi-persona pipeline wholesale (no cost or quality evidence; dominated by cold-start cost per US-23; designed for specs, we already have gate+sabotage for code); TRIZ/style/structural personas (our lint covers structure); their "human approves every finding" triage (conflicts with our coordinator model); "two clean rounds" as sole stopping rule (it multiplies verifier cost; keep our cap). Their claims of reduced confirmation bias are untested; treat as hypothesis.
