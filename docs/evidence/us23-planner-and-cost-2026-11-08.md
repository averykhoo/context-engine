# US-23 experiments: planner model replay and cost anatomy, 2026-11-08

FROZEN 2026-11-08 (session 2026-11-07e). On US-23 (owner, 2026-11-08), one workflow (wf_1d522e9d-002, 44 agents, 4.45M subagent tokens) ran two experiments: a blind replay of sonnet and opus planners on 11 tasks built this session (with an opus-vs-opus noise arm on 4), and a cost anatomy of the session's 168 agent transcripts priced from the claude-api skill's table (cached 2026-10-06). These are agent findings, not owner words; the replay scripts and raw numbers were in .scratch/us23/ and are not kept.

## US-23 planner experiment: synthesis (2026-11-08)

Inputs: 11 opus-vs-sonnet judge results (CE-174, 179, 150, 152, 155, 183, 171, 154, 56, 172, 189), plus 4 opus-vs-opus
noise-arm results (CE-179, 183, 154, 56). "Orig" means the original opus plan, the one that was actually built and verified.
Score = the sum of 5 dimensions, so the maximum is 25. All numbers below come from the judge JSON in the workflow task text,
computed by hand on 2026-11-08.

## 1. Does the planner's model make a difference?

| arm | orig wins | clear / slight | mean score gap (orig minus replan) |
|---|---|---|---|
| opus vs sonnet (n=11) | 10/11 | 8 clear, 2 slight; sonnet won only CE-183 (slight) | +4.4 |
| opus vs opus (n=4) | 3/4 | 2 clear, 1 slight; opus2 won CE-183 (clear) | +2.75 |
| opus vs sonnet, the same 4 tasks | 3/4 | the same pattern (CE-183 is again the loss) | **+2.75** |

- **On the 4 tasks that have both arms, the sonnet gap equals the opus2 gap (+2.75 each).** So most of the original
  plan's lead is **incumbency**, not the model. Judges kept citing "the build follows X almost verbatim" as evidence,
  and that favours whichever plan was built.
- Sign test, 10/11 against a fair coin: p≈0.012. Against the noise arm's 0.75 baseline: P(>=10/11)≈0.20, which is
  **not significant**.
- Judge noise is about 1 point. The same original plan was scored twice: CE-183 got 15 and 16, CE-154 22 and 23,
  CE-56 20 and 21, CE-179 22 and 21.
- Verdict: there is **weak evidence of a small model effect**, concentrated on one task kind (§2). This data cannot
  separate it from incumbency.

Per dimension, mean of opus / sonnet over n=11 (opus2 over n=4 is in brackets):
- builder_ready: 4.9 / 3.5 (opus2 3.75; the original got 5.0 on those same 4 tasks)
- completeness: 4.55 / 3.45
- design: 4.45 / 3.27
- correctness: 4.45 / 3.9
- anticipation: 2.36 / 2.18

The builder_ready gap is about the same against opus2, so it looks like an artifact of the replan's format, not of
the model. Some replans were judged from a compressed summary rather than the full plan (CE-56, CE-171).

## 2. Which kind of task?

| task kind | tasks | opus lead (mean) |
|---|---|---|
| small, well-pinned | CE-174 +5, CE-179 +6, CE-150 +9, CE-155 +8, CE-172 +6 | **+6.8** |
| medium, unpinned or cross-cutting, or a part left open | CE-152 +4, CE-183 -3, CE-171 +2, CE-154 +5, CE-56 +3, CE-189 +3 | **+2.3** |

- This is the opposite of the "sonnet is fine for small items" intuition. Small, pinned tasks reward exact strings,
  fixtures and call sites, and that is where sonnet's false claims turned directly into failing assertions.
- On design-open, cross-cutting work the gap between any two plans dominates. CE-183 lost to *both* sonnet and opus2,
  because the original's central claim ("check text as at rest") was wrong.
- Every task is engine code in this repo. Kit or docs-only work and other repos are untested.

## 3. Which defects each model makes

Wrong claims: opus 12, sonnet 18. Anticipated verifier findings: opus 11/53, sonnet 14/53. That second measure is biased
against the original plan, because the findings come from verifying the build of that plan.

**Sonnet** makes confident claims about runtime behaviour that it never checked:
- what the stored body is (CE-174)
- that G-W4 refuses at task new (CE-174)
- that YAML refuses a backtick (CE-155)
- that Store has no access to config, said **twice** (CE-179, CE-155)
- that a check matches the body "as at rest" (CE-183, in the opus-vs-opus arm that was opus1)

It also misses call sites and fixtures:
- a third fixture and an already-stale sabotage script (CE-150)
- the pruned file and the latin-README test (CE-154)

It leaves runbooks out, adds scope nobody asked for (an unrequested runbook edit, a redundant `relates` field, a
FRAMEWORK clause), and leaves messages and test bytes unpinned.

**Opus** makes errors of counting, naming and staleness:
- wrong census counts (CE-56, CE-189)
- a misnamed symbol, `Working.import_log`, that the builder copied (CE-171)
- repo ids leaking into the kit copy, and a missed G-D12 board step (CE-189)
- incomplete enumerations (CE-179)
- sometimes a wrong central premise on design-open work (CE-183)

Both models missed weak test assertions and the residuals around them.

## 4. Recommended rule (confidence: LOW)

- **Keep opus as the default planner.** No result here supports moving small, pinned items to sonnet: that is where
  sonnet did worst, and the plan is cheap there anyway.
- For medium, cross-cutting or unpinned items, the model matters less than **plan diversity**. A second independent plan
  plus a judge or merge step caught CE-183's wrong premise. Consider that instead of a model switch, but only on such
  items.
- How sure: n=11 with one judge per pair, and the noise arm has n=4. The direction is suggestive; the effect size is
  not established. Do not encode this as a rule yet. Record it as PROVISIONAL.

## 5. What a stronger follow-up needs

1. **No incumbent.** Plan every arm fresh from the same base commit and prompt, and give the judge full plans in the
   same format.
2. **Build each plan** with the same builder model, then measure outcomes rather than judge opinion: verifier defects,
   fix rounds, a green gate, tokens and wall time per task, and planner tokens.
3. **Run the opus-vs-opus noise arm on every task.** Use at least 2 blinded judges per pair, preferably of different
   models, and report agreement between them.
4. **About 25-30 tasks**, stratified by size × pinned × kind (code, kit, docs), with some tasks from another repo.
   Pre-register the primary metric (for example defects plus fix rounds) before running.


## US-23 cost anatomy (2026-11-08)

Data: frozen copy (.scratch/us23/anatomy/snap/) of the 5 workflow runs under subagents/workflows/: wf_486eac17 census, wf_3f99a3fb wave 1, wf_ec686ae4 wave 2, wf_a8a6f427 wave 3 (still running at the copy), wf_1d522e9d (the planner trial: haiku `setup`, sonnet/opus `replan`, opus `judge`; my own agent excluded). 168 agent transcripts with messages, 164 finished per journal `result` entries; the 4 unfinished (3 `replan opus`, `build ce-181 (opus)` at 80 turns) are left out of per-role stats and counted in the grand total. Each assistant message id counted once (max output_tokens over the streamed duplicates). Scripts and raw outputs: .scratch/us23/anatomy/*.py, out_*.txt (gitignored: this file is the record).

Prices ($/M): opus in 4 / write 5.00 / read 0.20 / out 20; sonnet in 2 / write 2.50 / read 0.20 / out 10; haiku in 0.10 / write 0.125 / read 0.01 / out 0.50 (haiku read and write are not in the brief: assumed 0.1x and 1.25x). The brief's opus read price (0.20 = 5% of input) is half the usual 10% ratio (sonnet's 0.20 = 10%): where it matters I give the 0.40 case; grand total is $225.39 at 0.20, $305.73 at 0.40.

TTL: all 26.3M cache-write tokens are `ephemeral_5m`, 0 at 1h. So 1.25x is the right write price, and the 5-minute TTL governs everything below.

## 1. Per role and model (finished agents; turns = distinct message ids)

| role (model) | n | med turns | med $ | mean $ | $ split: uncached in / cache write / cache read / output | role total $ |
|---|---|---|---|---|---|---|
| build (opus) | 23 | 62 | 4.04 | 4.65 | 0 / 58% / 37% / 6% | 107.0 |
| build (sonnet) | 6 | 27.5 | 0.89 | 0.97 | 0 / 51% / 46% / 3% | 5.8 |
| plan (opus) | 36 | 26 | 1.28 | 1.34 | 0 / 40% / 46% / 14% | 48.2 |
| verify (opus) | 31 | 20 | 0.93 | 0.97 | 0 / 56% / 38% / 6% | 30.1 |
| fix (opus) | 2 | 39 | 2.19 | 2.19 | 0 / 55% / 40% / 5% | 4.4 |
| close (sonnet) | 29 | 5 | 0.22 | 0.23 | 0 / 73% / 26% / 1% | 6.6 |
| census (sonnet) | 5 | 23 | 0.67 | 0.70 | 0 / 33% / 59% / 8% | 3.5 |
| replan (sonnet, trial) | 11 | 15 | 0.53 | 0.63 | 0 / 38% / 44% / 18% | 6.9 |
| judge (opus, trial) | 9 | 9 | 0.44 | 0.48 | 0 / 63% / 26% / 11% | 4.3 |
| setup (haiku, trial) | 11 | 7 | 0.013 | 0.013 | 0 / 46% / 37% / 18% | 0.14 |

Split is the dollar-weighted split over the role (not a median of per-agent shares). Uncached input is ~0 because every request carries `input_tokens: 2`: all prompt tokens are either cache write or cache read. Overall: cache write $117.4 (52%), cache read $89.9 (40%), output $18.0 (8%). By role total (all agents incl. unfinished): build 116.9, plan 48.2, verify 30.1, replan 11.3, close 6.6, fix 4.4, judge 4.3, census 3.5. A like-for-like sonnet-vs-opus build comparison is not available: sonnet got the small items (27 vs 62 turns), per-turn $0.033 vs $0.065.

## 2. The fixed start cost

The first request of an agent is ~60k tokens, not 30k. It is two halves:

- ~30k SHARED half (30,180 to 30,825 depending on model/role): read from cache when another agent of the same model and same role-family made a request in the previous 5 minutes. Almost certainly the tool schemas (built-ins plus the per-role `StructuredOutput` tool) and system prompt; the transcript's own system-prompt snapshot is only ~2.2k chars, so most of this half is tool schemas.
- ~30k PER-AGENT half (cache_creation 29.5k to 33.8k even on a hit): CLAUDE.md files, skill listing, deferred-tool names, session context, task prompt. Written fresh by every agent, never shared, because it sits in a first user message that also holds the differing task prompt.

Hit behaviour is exactly predicted by "same model + same role-family request within 300 s" (every first request, no exceptions):

| role | first requests | warm (hit) | cold (miss) |
|---|---|---|---|
| plan (opus) | 36 | 33 | 3 |
| build/fix (opus) | 26 | 12 | 14 |
| build (sonnet) | 6 | 2 | 4 |
| census (sonnet) | 5 | 4 | 1 |
| replan/judge/setup (trial) | 33 | 31 | 2 |
| verify (opus) | 31 | 0 | 31 |
| close (sonnet) | 29 | 0 | 29 |

Why verify and close never hit: each role has a different tool array (its own StructuredOutput schema) and tools come first in the cache key, so the whole 60k misses unless a same-role agent ran <5 min earlier. Verify and close run one per task, serially, 3 to 80 minutes apart. Plans start in bursts, so they hit. A verify starts ~5 s after its builder's last request and still misses entirely (different tool array). The role-to-tool-array link is inferred (the StructuredOutput attachment exists and the hit pattern fits perfectly), not read from the wire.

Start cost, first request only: opus cold $0.30, warm $0.155 (a hit saves $0.145); sonnet cold $0.150, warm $0.080 (saves $0.070); haiku cold $0.0075, warm $0.004. But the prefix is then re-read every turn. Its lifetime cost (60k written once plus (T-1) reads) at median turns is: build opus $1.03 (24% of the agent's cost), plan opus $0.60 (49%), verify opus $0.53 (56%), build sonnet $0.47 (49%), close sonnet $0.20 (91%), haiku setup $0.011 (90%). So the "30k start cost" is really $0.5 to 1.0 per opus agent and most of a close agent.

Prefix composition (attachments in the transcript; 2.6 chars/token is calibrated by regressing first-request tokens on task-prompt length, which gave 2.45 to 2.97 chars/token by role; the requested bytes/4 is shown alongside):

| piece | bytes | tokens @bytes/4 | tokens @2.6 B/tok | $ saved per agent if removed (mean over this mix) | over the 168 agents so far |
|---|---|---|---|---|---|
| ~/.claude/CLAUDE.md (global; not editable per repo) | 24,764 | 6.2k | 9.5k | $0.055 to 0.084 | $9.2 to 14.1 |
| repo CLAUDE.md | 9,987 on disk | 2.5k | 3.8k | $0.022 to 0.034 | $3.7 to 5.6 |
| docs/framework/contract.md (kit copy, gate-pinned) | 9,956 | 2.5k | 3.8k | $0.022 to 0.034 | $3.7 to 5.7 |
| skill listing (data:*, anthropic-skills:*, etc.) | 21,435 | 5.4k | 8.2k | $0.047 to 0.073 | $7.9 to 12.2 |
| deferred-tool names | 5,411 | 1.4k | 2.1k | $0.012 to 0.018 | $2.0 to 3.1 |
| session_context, env, date, model | ~3.4k | 0.9k | 1.3k | ~$0.01 | |

Rule of thumb from the data: every 1,000 tokens in the per-agent prefix costs $0.0088 per agent on this mix ($1.48 over the 168 agents so far; opus carries $1.24 of that). Trimming both repo files (CE-47) saves ~$0.04 to 0.07 per agent, about $7 to 11 over 168 agents: real but small beside the build total ($117). The skill listing is as large as both repo files together and lives outside the repo (disabling unused plugins/skills for subagents is the lever; untested here). The shared 30k tool-schema half cannot be seen or trimmed from the transcript.

## 3. Growth and the quadratic read term

Median context (all tokens in the request) by turn index, opus: build 63k (t0), 81k (t5), 91k (t10), 102k (t20), 117k (t30), 129k (t40), 166k (t60), 197k (t80); verify 64k, 85k, 94k, 112k (t20); plan 59k, 76k, 88k, 112k (t20), 127k (t30), 147k (t40). Median growth per turn: build opus 1.47k, verify 2.1k, plan 2.6k, sonnet planner 4.1k; the largest single-turn jump is 22.6k. Growth regression (n=119): growth(ktok) = 0.48 x tool-result kchars + 0.73 x output ktok + 0.43 x turns (R2 0.98), so results enter at ~2.1 chars/token, ~73% of own output is retained, plus ~0.4k per-turn overhead. Median output is ~190 tokens/turn; builds see ~2k chars of tool result per turn.

Cache-read tokens per agent fit the structural form reads = a*T*P0 + b*g*T^2/2 (T turns, P0 first-request context, g growth/turn) with a=0.91, b=1.13 for opus (R2 0.998, n=102) and a=0.91, b=1.03 for sonnet (R2 0.996, n=51), both ~1 as theory says. So yes, reads are quadratic in turns, but the 60k prefix term (a*T*P0) dominates short agents, so the pooled log-log exponent of reads on T is only 1.28 to 1.34. For a typical opus build (T=62, P0=63k, g=1.5k) the prefix part is 3.9M read tokens and the growth part 2.9M; the quadratic term overtakes the prefix term at T = 2*P0/g, ~85 turns.

Cost fits (finished opus agents, n=102): cost = $0.22 + $0.00032 x (T x final_ctx_k), R2 0.94. With T and final context as separate terms R2 is 0.90, 0.96 with the interaction. Sonnet: $0.15 + $0.00024 x (T x final_ctx_k), R2 0.92. A first-principles model (writes = final ctx x write price, reads from the fit above, output = T x 190 x price) reproduces actual opus agent cost with median ratio 1.001 (p10 0.60, p90 1.23; the low tail is agents that suffered cache misses, which the model omits).

## 3b. Cache misses inside agents (not asked, but large)

Turns split by the gap since the agent's previous message: <60 s: 4,011 turns, 0 cache misses; 60 to 300 s: 95 turns, 0 misses; >300 s: 63 turns, 63 misses (100%). So the TTL is a hard 5 minutes between requests, and a miss re-writes the whole context at the write price. All 63 are builders/fixers waiting 400 to 620 s on the gate (the Bash timeout ceiling is 600 s; a gate run takes ~720 to 890 s). Penalty relative to a hit: $45.23 of $225.39 (20%); single events cost up to $1.46 at 300k context (ce-56). A 1h TTL on opus builder writes would add ~$39 in write price to save ~$44: break-even, not a win. A cheaper candidate (NOT tested): replace one 10-minute wait with polls every 4.5 minutes or less; each poll turn costs a context read ($0.04 at 200k) against ~$1 per miss.

## 4. One agent against several (opus, fitted model, no cache misses)

Setup: first-request context P0=60k; growth g per turn 1.5k (build-like) or 2.1k (verify-like); handoff H = tokens a downstream agent must re-absorb. H measured from 27 tasks with plan+build: matching tool-result lines (>=30 chars, line-number prefixes stripped) between planner and builder, the builder re-sees 37% of its tool-result text that the planner already read: median 10.5k tokens (opus builders 13.5k), 7% of the builder's final context; plus the planner's design text in the builder prompt (median 10.7k chars, ~3.3k tokens), so H is about 15k. The verifier re-sees 23% of its results from the planner alone and 35% from planner+builder (median 4.3k / 6.8k tokens). Within one builder, 4% of tool-result lines are repeats (1.3k tokens).

Literal reading of the question (each agent ends at the stated size; the model is validated up to 307k observed, 500k is extrapolated and T=294 turns is 2x the longest agent seen):

| config | opus total $ (g=1.5k) | opus total $ (g=2.1k) | opus, read $0.40 (g=1.5k) | new-work tokens | $ per 100k new tokens (g=1.5k) |
|---|---|---|---|---|---|
| 1 x 500k | 21.52 | 16.12 | 39.41 | 440k | 4.89 |
| 2 x 250k | 11.78 | 9.16 | 20.10 | 365k | 3.23 |
| 5 x 100k | 5.18 | 4.45 | 7.34 | 140k | 3.70 |

Same 440k of new work split k ways (each downstream agent also carries H=15k): k=1 $21.5, k=2 $15.3, k=3 $13.6, k=5 $12.9, k=8 $13.5 (g=1.5k); k=1 $16.1, k=2 $11.8, k=5 $10.4, k=8 $11.2 (g=2.1k). Sonnet: k=1 $19.7 vs k=5 $10.2 (g=1.5k).

Cost-per-useful-token minimum: with H=15k the cheapest agent size is 100k to 110k of new tokens, i.e. ~160k to 170k final context (H=0: 120k to 140k; H=30k: 200k to 210k), and the curve is within ~5% of flat from 90k to 130k new tokens. Break-even handoff (split cost equals single-agent cost): H of about 120k tokens per downstream agent for 2 agents, 70k to 76k for 5 agents. Measured H is 15k, far inside. Not in the model: a wrong or lossy handoff doc, planner/builder quality differences, context rot (not measurable here), and extra cold starts (+$0.15 to 0.30 each, already in the 60k write).

Recommendation: split work at roughly 150k to 200k final context per agent (about 25 to 60 turns of building), not at 500k, and not into 100k slices unless the pieces are naturally separate. At 1 x 500k the quadratic read term and the cost of each cache miss (~$1.9 at 400k) both grow with size; at 5 x 100k the 60k prefix is a 60% fixed overhead per slice. For a 500k job use 3 to 5 agents; for a 250k job 2 is fine only if H is small (it is).

## 5. Compaction

None. There are zero compaction or summary records in any transcript (record types seen: assistant, user, attachment only; no `compact_boundary`, no `isCompactSummary`), and no turn anywhere shows context dropping by more than 10% from the previous turn. Largest context: 307,378 tokens (build ce-56, turn 147); ce-181 is at 80 turns and still running. The data CANNOT say: what the auto-compaction trigger is (agents reached 307k without it firing, so the trigger is above that or inactive for workflow subagents); what one compaction costs (it should be one summarising request over the full context at read price, then the summary written at write price, and the next request re-writes everything at the write price because the prefix changed: not measured); or whether quality after a compaction is better or worse than after a handoff to a fresh agent (no quality measure here; context rot is unobserved). Compaction does nothing for the 60k start cost and keeps one growing agent, so it competes with splitting only on the quadratic term. A compacting agent carries a ~10 to 20k summary instead of H=15k, so the two may cost about the same; only an experiment can show the quality difference.

## 6. Close step on haiku

29 finished closes, sonnet, all cold (60k written each, 5 turns): $6.60 total. The identical tokens at haiku prices: $0.33, saving $6.27 ($0.216 per close, 96%). Reality check: the 11 haiku `setup` agents (7 turns) cost a median $0.0126 each. Folding the close into the opus verifier instead would cost about $0.11 (+3 turns) to $0.18 (+5 turns) per task on the verifier's ~105k context, so haiku is cheaper than folding. A long-lived haiku agent reused for mechanical tasks gains nothing: a fresh haiku start costs $0.0075 to 0.01, while a reused one wakes after >5 minutes of silence (closes are 3 to 80 minutes apart) and re-writes its whole, growing context at the write price anyway. Over this session so far, $6.3 of $225.4 (2.8%) is the most this saves; each further close saves ~$0.22.

## Answers to the owner's questions

- 100k x 5 vs 250k x 2 vs 500k x 1: per 100k tokens of new work, 2 x 250k ($3.2, g=1.5k) beats 5 x 100k ($3.7) and 1 x 500k ($4.9); the minimum is at ~160k to 170k final context per agent.
- Caching: keyed by prefix, 5-minute TTL refreshed by every request, per model and (here) per tool array; it shared 30k for most plans/builds and nothing for verify/close.
- 30k start cost: it is 60k; half is shared when warm, half is per-agent. Trimming the two repo files is worth ~$0.04 to 0.07 per agent; the skill listing is worth as much again.
- Compaction: never triggered; cannot be assessed from this data.
