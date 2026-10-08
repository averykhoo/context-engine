# A context-engineering framework for agent-built repos

**Draft v0.1, 2026-10-07. Status: DRAFT under review, untracked.** This file lives in the
gitignored `PycharmProjects/.scratch/context-framework/`, so it is not yet backed up anywhere.
It was distilled from read-only audits of six repos run on 2026-10-07: the four audit reports in
this directory (`A-zanzibar.md`, `B-audio-workspace.md`, `C-midsize.md`,
`D-light-and-global.md`) plus first-hand spot checks. Where a rule exists in a repo, the repo and
the file or symbol are cited, so a reviewer can check that the generalisation is faithful.

Repo short names used throughout:

| short name | path under `PycharmProjects/` | role in this draft |
|---|---|---|
| **zanzibar** | `graph-reachability-zanzibar-index` | most complete working-state and verification design |
| **audio-workspace** | `audio-workspace` | most complete spec→BDD→test chain and doc guards |
| **intervals** | `intervals` | run ledger and sabotage tooling; template-copy HANDOFF |
| **adhoc** | `adhoc-microphone-array` | newest template copy (2026-10-01); decision tagging; project brief |
| **peass** | `python-peass` | TODO/ARCHIVE idiom; frozen numerical baseline |
| **nmd** | `ngram-movers-distance` | negative-results table; parity tests |

---

## 0. What this framework is for

### 0.1 Who does what

The **owner does not write code** in these repos. The owner's work is **intent**:

- user stories and use cases;
- the spec and the interactions;
- goals, principles and non-goals;
- occasional pushes on architecture or algorithms;
- the decisions that only the owner can make.

**Agents do everything below intent:** turning stories into precise criteria, criteria into
tests, tests into code, plus keeping the docs, guards and rituals that make the work continuous
across sessions. The expectation is that agent autonomy keeps rising, and the framework is built
for that: the less the owner has to supervise, the more the repo itself has to carry intent,
correctness and continuity.

So the framework has four jobs:

1. **Make intent durable.** What the owner said survives sessions, context resets, concurrent
   sessions and model changes, in the owner's words and with an owner stamp.
2. **Make correctness checkable.** Every piece of intent traces to something executable that
   has been shown to fail when the behaviour breaks.
3. **Make continuity cheap.** Any session, including a fresh model with no memory, can orient
   in minutes, resume mid-flight, and leave the repo better oriented than it found it.
4. **Spend owner attention only where it is irreplaceable.** Agents decide what they may
   decide, record it, and queue only what truly needs the owner.

### 0.2 Stance

- **Plain files plus git, now.** Markdown with small frontmatter schemas, Python or Node lint
  scripts in the repo's own gate. Vector search, source graphs and memory services come later
  (§9.4), as *derived* indexes over the files, never as the source of truth.
- **Mechanical refusal beats a written warning.** Every rule that matters has a guard in the
  gate. audio-workspace wrote its first doc guard "because three doc warnings lost" (D-157,
  2026-09-03). The four template-copy repos kept the rules but not the guards, and all four are
  drifting (`C-midsize.md` § Common gaps).
- **Not too simple.** Every component below exists because its absence caused a recorded
  failure in one of these repos. "Simple" here means no infrastructure, not few concepts.

---

## 1. Principles

These apply to every component. Each one is a generalisation of a rule that already exists, and
says where.

**P1. One home per statement; everywhere else points to it.**
zanzibar `docs/README.md § 1`: *"every statement has exactly one home, and everywhere else is a
pointer."* audio-workspace `CLAUDE.md § Where the authority lives`: *"This table is a POINTER
and nothing more."*

**P2. Every artifact declares how it changes.** There are four ways:
- **replaced:** rewritten in place; git is its history;
- **append-only:** entries are never edited; corrections are new, dated entries;
- **generated:** produced by a tool and checked against regeneration;
- **frozen:** provenance only, with a visible banner.

zanzibar `docs/README.md § 2` (LIVING / FROZEN / ACTIVE-PLAN) and `§ 6` *"Boards replace;
ledgers accrete."*

**P3. Stable ids, never reused, for anything that is cited.** Tasks, decisions, questions,
stories, criteria. Cite stable keys, never line numbers or positions (zanzibar
`docs/README.md § 5`; `tasks/retired-ids.txt`). Citations to code use `file::symbol`.

**P4. Provenance on anything that can go stale:**
- **who:** owner / agent / owner + agent / owner asked;
- **when:** a date or session key;
- **how it is known:** READ / REASONED / UNVERIFIED (zanzibar's provenance labels).

**P5. Numbers are generated, never typed.** A count in prose is deleted and replaced with a
pointer to the generated block. Examples: zanzibar `handoff_lint.py::check_restated_counts`;
audio-workspace `featureScenarioCounts.test.ts`; global `CLAUDE.md` "Date-stamp every measured
number … re-measure rather than differencing".

**P6. Cap the dimension that actually grows, and give every component a way out.**
audio-workspace D-221: *"A guard bounds what it measures, and the growth moves to what it does
not."* Proven 2026-10-07: zanzibar's banner is at its 14-line cap with lines of up to 3.7k
characters. Every component in the six repos that had no exit path bloated:
- session logs kept inside HANDOFF (intervals, adhoc);
- a 1.77 MB `decisions.md` (audio-workspace);
- uncapped `CLAUDE.md` files (zanzibar, 45 KB and growing ~4 KB a week).

**P7. Every component has a schema and a guard, and every guard has been shown to fail.**
Sabotage the protected thing and watch the guard go red. Then guard the guards: count floors
and tests on the lint tools themselves. Global `CLAUDE.md § Assurance traps` (*"an assurance
step that fails by PASSING is the house failure mode"*); intervals `tools/sabotage.py`; the
zanzibar floor on `tasks/closed/` (it exists because `rm -rf tasks/closed` once still linted
clean).

**P8. Owner attention is the scarcest resource.** Agents decide what they may decide, record
who decided, and queue only questions that need the owner. Those questions are never answered
by an agent. Examples: zanzibar `ASK-n` (2026-09-22); adhoc decision tags
`owner | agent | owner asked + agent`.

**P9. Skip what can be recovered; never skip what would be lost.** Rituals may be shortened at
an awkward stopping point (§6.4). Anything whose loss cannot be undone may not be skipped:
- evidence still sitting in scratch;
- an undescribed uncommitted tree;
- a missing pause marker.

**P10. Evidence goes into a tracked file the same hour.** `.scratch/` is a crash bag, not a
home. Global `CLAUDE.md § .scratch/`. A 2026-10-05 zanzibar sweep found 3 of 285 scratch files
were the only copy of something.

**P11. Delegate for context, not for parallelism, and keep the judgement.** A subagent's report
is evidence, not a finding. Global `CLAUDE.md § Delegation`.

**P12. Concurrency is normal.** Several sessions share one working tree. Commit by path, never
by tree; never `git stash` in a shared tree; re-check `git status` right before committing.
Global `CLAUDE.md § Concurrent sessions`. Observed in zanzibar on 2026-10-07: another session
committed 27 files two minutes before an unrelated doc commit landed on top of them.

---

## 2. The components at a glance

Six layers. The question each component answers is the test for what belongs in it.

| # | Layer | Component | Question it answers | Changes by | Owner of content |
|---|---|---|---|---|---|
| 1 | Intent | **Charter** | What are we building, why, what is out of scope, and which principle wins a tradeoff? | replaced, rarely | owner (the agent proposes) |
| 2 | Intent | **Stories and use cases** | What does the owner want to happen, in the owner's words? | append, with amendments | owner |
| 3 | Intent | **Criteria (the spec)** | Exactly what behaviour counts as correct? | replaced, with ids and statuses | agent drafts, owner may veto |
| 4 | Intent | **Deviation register** | Where does the system deliberately differ from the spec? | append-only | agent; owner approves material ones |
| 5 | Rules | **Contract** | How do I work here? Gate, invariants, footguns | replaced, capped | promotion only |
| 6 | Rules | **Routing map** | Where does each kind of statement live? | replaced, small | agent |
| 7 | Rules | **Hazard register** | What is surprising or dangerous right now? | replaced | agent |
| 8 | Working state | **Orientation note** | What is true now; what must the next session not miss? | **replaced every clean close** | agent |
| 9 | Working state | **Board** | What is next, in what order? | replaced | agent ranks; an owner assignment overrides |
| 10 | Working state | **Owner-question queue** | What can only the owner decide? | opened by the agent, closed by the owner | owner answers |
| 11 | Working state | **Baton and pause marker** | What did the last session skip or leave mid-flight? | stamped; expires | agent |
| 12 | Record | **Decision log** (with negative results) | Why is it this way, and what was rejected? | append-only | stamped with who decided |
| 13 | Record | **Session ledger** | What happened, when, and with what receipts? | append-only | agent |
| 14 | Record | **Evidence and plan docs** | What did we measure; what is the plan for item X? | active plan, then frozen | agent |
| 15 | Record | **Archive** | Where did X go? | moved verbatim; redirect table | agent |
| 16 | Verification | **Tests and proofs** | Does the behaviour hold? | code | agent |
| 17 | Verification | **Trace and freshness guards** | Is intent ↔ criteria ↔ tests complete and true? | code | agent |
| 18 | Verification | **Doc guards** | Is every component within its schema and caps? | code | agent |
| 19 | Verification | **Verification state** | What has been proven on *this* commit? | generated | tooling |
| 20 | Ephemeral | **Scratch** | Somewhere to put things before they are judged | throwaway | — |
| 21 | Ephemeral | **Memory** | What has the owner taught agents that isn't a repo rule yet? | accretes; promoted or pruned | agent records the owner's feedback |

### 2.1 Components that must not be merged, and the merges that already failed

| Kept apart | What happened when they were merged |
|---|---|
| Orientation note vs session ledger | The banner became a second log: intervals' banner is ~124 lines; audio-workspace has ~600 lines of banners and session sections above its board (2026-10-07). |
| Board vs owner questions | zanzibar's 🧭 badge drifted into meaning "see also" until `ASK-n` became its own series (2026-09-22). |
| Board vs baton | Batons that never expire turn into a second, unranked backlog. zanzibar `HANDOFF.md § Still owed`: *"A bullet that survives two sessions is not a baton, it is backlog."* |
| Contract vs decision log | audio-workspace `CLAUDE.md` reached 288 KB as a table of contents for the log, cut to 28.6 KB with a guard (D-163, 2026-09-05). |
| Contract vs hazards | audio-workspace `docs/invariants.md`: *"This is not a second contract."* |
| Decisions vs negative results | Kept as a separate section, not a separate file. nmd and adhoc *"Built and rejected, or decided against evidence … Do not re-derive these."*; peass `ARCHIVE.md` "Closed investigations (do not reopen)". |
| Stories vs criteria | Stories are in the owner's voice and may be loose; criteria are precise and testable. Merging them either makes the owner write test-grade prose or loses the owner's words. See §3.3 for why this seam is accepted. |
| Ledger vs archive | The ledger records events as they happen. The archive receives pruned material verbatim and is never repaired (audio-workspace `docs/archive/README.md`). |

---

## 3. The intent layer and the correctness chain

### 3.1 Charter

- **Contents:**
  - goals with how each is measured;
  - non-goals, e.g. adhoc D-17 "localization is parked";
  - **ranked principles**, so a tradeoff has a known answer;
  - owner mandates.
- **Today:**
  - scattered in audio-workspace ("9 owner mandates" inside `CLAUDE.md`);
  - adhoc has `docs/project-brief.txt`, plus its main goal stored as decision D-18 and restated
    in the banner;
  - intervals keeps its goals in `v2-plan.md`.
- **Rule:** one charter file per repo, owner-stamped. Agents change it only through an
  owner-question → decision → edit chain. Every goal is cited by at least one story or
  criterion (guard G-I1).

### 3.2 Stories and use cases (the owner's voice)

- **Contents:** user stories, use cases, interaction descriptions, and architecture or
  algorithm directions, **recorded in the owner's words**, each with an id (`S-n`), a date and
  `actor: owner`.
- **Intake ritual (§6.2):** when the owner says something that is intent, the agent writes it
  down verbatim (light cleanup only), assigns an id, and links it to the goals it serves. The
  owner never has to learn a file format.
- **Amendments** are dated additions under the story, never silent rewrites. A story the
  owner retracts gets `status: retired` and a pointer to the decision.

### 3.3 Criteria (the spec: what counts as correct)

- **Contents:** precise, testable statements, each with:
  - an id (`C-n`, or the scenario tag);
  - the story or decision it derives from;
  - a **status**: `verified` / `planned` / `manual` / `deviates` / `retired`;
  - for `verified`, the exact test that checks it.
- **The form depends on the kind of project.** The shape of the chain does not:

| Kind of project | Criterion is | Its test is | Prior art |
|---|---|---|---|
| Product / app | BDD scenario (`.feature`) | e2e, component or unit test | audio-workspace `features/*.feature`, `featureCoverage.test.ts` |
| Library / algorithm | property or invariant | property-based or fuzz test | intervals (hypothesis fuzzing, `v2-plan.md`) |
| Port / reimplementation | parity with a reference | oracle or parity test | nmd `tests/test_parity_with_nmd.py`; peass frozen baseline at `e960c5e` |
| Numerical / perf change | "moves only within the declared tolerance" | baseline capture plus comparison | peass `TODO.md § process state` ("ground-rule-2 gate") |
| Research | metric threshold on a ladder against oracle bounds | scored run, result in a tracked file | adhoc `docs/results/2026-10-0*.md`, oracle-MWF rung |
| Formal | theorem | proof plus model↔code correspondence | zanzibar `formal/`, `formal/CORRESPONDENCE.md` |

- **Why stories and criteria are both kept**, despite the earlier advice to keep the number of
  hand-written layers small: the owner speaks in stories, and the owner is not expected to write
  test-grade prose. So the seam between them is accepted, and it is guarded mechanically
  (G-T1/G-T2) and by the sync ritual (§6.1). A separate prose-requirements layer (`FR-n`) is
  **not** part of the default. audio-workspace has both FRs and scenarios, and that is exactly
  where its D-173 drift happened. Add an FR layer only when someone outside the project needs
  one (a contract or a standard), and then guard it like any other link.

### 3.4 The chain

```
charter goal ─► story / use case ─► criterion ─► test ─ ─ ─► code
  (owner)          (owner)          (agent)      (agent)   (derived, never hand-linked)
                       ▲               ▲
                       └─ decisions create, amend or retire stories and criteria ─┘
```

| Link | Written by | Guard |
|---|---|---|
| goal → story | hand (intake) | G-I1: every goal is served by at least one story; every story names a goal |
| story → criterion | hand (agent) | G-T1: every live story has at least one criterion, or `status: unspecified` with an owner question open |
| criterion → test | hand: an annotation in the test naming the criterion id | G-T2, **both directions**: every `verified` criterion names a test that exists; every test names a criterion or is tagged `internal`. Prior art: audio-workspace `featureCoverage.test.ts` (scenario ↔ test) and `specBddFreshness.test.ts` ("a scenario claiming to be verified says WHICH test verifies it") |
| test → code | **derived** from coverage or imports | **proven, not declared**: G-T5 mutation per criterion; break the behaviour, and the linked test must go red |
| decision → story / criterion | hand: the decision lists what it creates, amends or retires | G-T3 freshness: no live criterion or story describes something a decision retired. Prior art: audio-workspace `requirementsFreshness.test.ts` (D-173) |

**Rules for the chain:**

1. **Stop hand-written links at the test.** A test-to-code map is useful for impact analysis
   ("what criteria does this function touch?"), but it is **generated** from coverage and
   thrown away, never maintained by hand.
2. **A link proves only that the test exists, not that it checks anything.** audio-workspace
   D-173 is the canonical case: FR-20/22/24/27 were traced to real scenarios, so the traceability
   guard was green, while their text described an orchestrator deleted five days earlier.
   *"Traced is not the same as true."* Hence G-T3 (freshness) and G-T5 (mutation).
3. **Structural claims are the exception, and get hash pins.** When a criterion or decision
   claims something about *structure* rather than behaviour, it may cite `file::symbol`. That
   citation is pinned by a hash of the symbol's body, so a code change flags the claim for
   review. Examples of structural claims: a formal model's correspondence to code, "implemented
   with a sparse bitmap", a hazard about a specific function. Prior art: zanzibar
   `formal/conformance/anchor_check.py` (the reference resolves) and
   `formal/conformance/claim_rot.py` → `formal/correspondence_anchor_pin.txt` (the body has not
   changed), both in the `lean` phase of `formal/verify.sh`.
4. **Statuses keep the rule usable during real work:**
   - `planned`: allowed, but counted in a generated block (G-D5);
   - `manual`: must name the hand-run driver (audio-workspace `liveDriverCoverage.test.ts`);
   - `deviates`: must point to a deviation-register entry;
   - `retired`: must point to the decision that retired it.

### 3.5 Deviation register

An append-only list of places where the system **deliberately** differs from the spec, each
entry with an id, the criterion it affects, the reason, and who decided. Declared drift is
allowed; **drift that is not declared fails the gate.** Prior art: zanzibar `docs/spec-deviations.md`
(append-only) and `docs/latent-gaps.md` (what is open today).

---

## 4. Drift: kinds and guards

Drift is not one problem. These are the kinds the six repos have actually hit, each with the
guard that catches it.

| # | Drift | Guard | Prior art |
|---|---|---|---|
| D1 | A story with no criterion; a criterion with no test | G-T1, G-T2 (both directions) | audio-workspace `requirementsTraceability.test.ts` (D-172): *"17 of 47 FRs cited nowhere"* (2026-09-06) |
| D2 | Traced, but describing behaviour a decision removed | G-T3 freshness against decision status | audio-workspace `requirementsFreshness.test.ts` (D-173) |
| D3 | Code changed under a structural claim | G-T4 hash pin on the cited symbol body | zanzibar `claim_rot.py` |
| D4 | A doc cites a deleted file or symbol | G-D3 every reference resolves | zanzibar `anchor_check.py`; audio-workspace `docLinks.test.ts`, `specBddFreshness.test.ts`; zanzibar's 2026-10-05 Still-owed bullet (docs naming symbols TK107 deleted) |
| D5 | A typed number goes stale | G-D5 generated count blocks plus a ban on counts in prose | audio-workspace `featureScenarioCounts.test.ts`; zanzibar `check_restated_counts` |
| D6 | A test that passes without checking the behaviour | G-T5 mutation per criterion; sabotage | intervals `tools/sabotage.py`; global "fails by passing" |
| D7 | The suite silently shrinks | G-V2 count floors | zanzibar's floor on `tasks/closed/`; intervals' run ledger notes floors are recorded but not enforced (`intervals/HANDOFF.md § still owed`) |
| D8 | Working docs drift from reality (stale banner, old caps, closed items listed as open) | doc guards §8.3 | zanzibar `HANDOFF.md:21` "cap of 3" when it was 5 (2026-10-07); nmd's stale "What changed recently" table |
| D9 | A generated index that is wrong but byte-identical to its regeneration | content assertions, not just regeneration equality | audio-workspace `decisionsIndex.test.ts` stayed green while 7 rows lost their actor or date (2026-10-07) |
| D10 | A guard bounds one dimension and growth moves to another | cap the dimension that grows (bytes, line width, sections above the board) | D-221; zanzibar banner line widths; audio-workspace `handoffShape` blind to content above the board |

---

## 5. Working state

### 5.1 Orientation note (`HANDOFF.md`)

- **Contents only:**
  - a **banner**: the session key, what is true now, at most a handful of bullets;
  - the **baton** (§5.4);
  - **next session**: the start sequence and pointers.
  
  **No board, no history, no session log.**
- **Changes by being replaced on every clean close.** The old banner's content goes to the
  ledger, if it is worth keeping.
- **Caps:** lines **and** bytes **and** line width. zanzibar uses ≤60 lines
  (`handoff_lint.py::MAX_LINES`), but its bytes regrew 4.3 KB → 18 KB because nothing capped
  them.
- **Guard:** the banner's session key is ≥ the newest clean-close ledger entry (G-W1).
- Prior art: zanzibar `HANDOFF.md` ("the one-hop note"). Counter-examples: intervals' banner,
  and audio-workspace's lines 3–596.

### 5.2 Board

- **Small repos:** a table inside the orientation note is acceptable, **with** a cap.
  Columns (from intervals and adhoc): `# | id | what | status / blocker | spec`, where `spec`
  cites criteria, stories or decisions.
- **When open items exceed ~30**, or more than one session works the board at once: one file
  per task with frontmatter, plus a CLI. The board is then a **query**, not a committed file.
  Tasks change only through CLI commands tagged with a session key; editing the files by hand
  is banned. Closed tasks move to `tasks/closed/` with a floor. Prior art: zanzibar `tasks/`,
  `scripts/task.py` (`new`, `board`, `show`, `promote`, `close`, `lint`), `tasks/config.json`.
- **Ranking tiers with caps:** NOW (exactly 1), NEXT (≤5), LATER, HOLD, SOMEDAY (zanzibar).
- **An owner assignment overrides the ranking.** Do not re-rank at session start; re-rank at
  the clean close (zanzibar `HANDOFF.md`).
- **Leaving the board:** a closed item leaves the board and gets a one-line ledger entry.
  Nothing is listed as open and done at once (intervals and adhoc preamble).

### 5.3 Owner-question queue

- **Contents:** `Q-n` / `ASK-n` entries:
  - the question, phrased so the owner can answer in one line;
  - why only the owner can answer it;
  - the options with the agent's recommendation;
  - what is blocked on it.
- **Closed only by an owner answer.** The answer becomes a decision with `actor: owner`.
- **Visibility:** an open question with something blocked on it surfaces at the top of the
  board output; zanzibar adds an `asked:` receipt line in the ledger.
- **Rule:** the agent never answers its own owner question. If the agent can decide, it was
  not an owner question, so it decides and records `actor: agent`.

### 5.4 Baton and pause marker

- **Baton:** a step the last session skipped, stamped with its session key. **Expires after
  two sessions:** it is either done or turned into a board task (G-W3). Prior art: zanzibar's
  rule, whose check (`TK97`) is not built yet.
- **Pause marker:** a baton of a special kind, written when a session stops at an awkward
  point (§6.4). Contents:
  - what was in flight;
  - the exact resume step;
  - the tree state: what is uncommitted and why, and on which branch;
  - where the evidence is.

---

## 6. Rituals

The rituals are the protocol that keeps the components in sync. They are written for agents,
and their effects are checked by guards, so a missed ritual shows up as a red check, not as
silent rot.

### 6.1 Session start: full orientation, or resume, plus background sync

**Full orientation** (the default after a clean close):

1. Contract (auto-loaded): global, then repo, then subproject.
2. Orientation note: banner, baton, next session.
3. Board: the top item, or the owner's assignment; then that item's read-first list.
4. Open owner questions: anything answered since last time becomes a decision first.

**Resume** (after a pause marker): read the pause marker, check the tree state it describes
against `git status`, and continue. Orientation is deferred to the next natural stopping point.

**Background sync agents** may be launched at session start. They are read-only and **keyed on
`HEAD`**: if nothing has changed since the last sync report for this sha, skip. Each writes its
report incrementally to `.scratch/sync/<sha>/<agent>.md`, and the session triages the reports.
*The agents audit; the session decides and edits* (global `CLAUDE.md § Sweeping it`).

| Agent | Checks | Output |
|---|---|---|
| **trace-sync** | goal ↔ story ↔ criterion ↔ test completeness; drafts missing criteria for new stories | gaps list plus draft criteria (marked `planned`) for the session to accept |
| **freshness** | decisions retired since last sync vs live stories and criteria; hash-pin mismatches; dead references | list of stale items with the decision or commit that made them stale |
| **hygiene** | caps near their limit; stale banner; expired batons; closed ids still on the board; uncommitted tree vs pause marker | checklist |
| **inbox** | owner answers left anywhere (chat log, commit messages, HANDOFF edits) not yet turned into decisions | list of answers to record |

Running the trace and freshness checks *as guards in the gate* stays mandatory. The background
agents add judgement on top (draft criteria, explain why something is stale); they do not
replace the guards.

### 6.2 Intake: the owner gives intent

When the owner gives a story, use case, interaction, spec change or architecture direction:

1. Record it verbatim as a story (`S-n`, `actor: owner`, date), or as an amendment to an
   existing one.
2. Link it to the charter goal(s) it serves. If none fits, ask: it may be a new goal.
3. Draft criteria (`planned`) and show them to the owner **as a short digest**, not as files.
4. Questions only the owner can answer go to the queue, never guessed.
5. If it contradicts an existing decision or criterion, say so immediately, and record the
   outcome as a decision that supersedes or amends the old one.

### 6.3 Clean close (natural stopping point)

In this order (from zanzibar `docs/README.md § 7`, generalised):

1. Run the doc guards.
2. Write a ledger entry with:
   - the session key;
   - a `rows:` line naming the board items touched;
   - receipts: the guard results, and what was read (e.g. `read: board only`), plus `asked:`
     when an owner question is pending;
   - a closing `Still owed:` line.
3. **Replace** the banner.
4. Board edits: close, rank, mint tasks.
5. Promote durable rules into the contract (§6.7).
6. Anything skipped goes into the baton, verbatim and stamped.
7. Run the gate, then commit (by path).

Push only with the owner's permission, and watch CI after every push (global `CLAUDE.md § Git`).

### 6.4 Pause (awkward stopping point; the work continues next session)

The owner is fine with the full ritual being skipped when the work continues next session.
**Only these three are mandatory**, because skipping them loses information (P9):

1. Evidence out of scratch into a tracked file (it may be a rough, dated, ACTIVE-PLAN doc).
2. A description of the tree state: what is uncommitted, why, and on which branch.
3. A pause marker in the baton, stamped with the session key.

Everything else (ledger entry, banner, re-ranking, guards) is **deferred**, not dropped: the
next session to reach a clean close does it.

**Enforcement:** guards do not fail on a pause. They fail when **more than N consecutive
sessions have paused without a clean close** (default N = 2: G-W2/G-W3). This is zanzibar's
two-session baton rule, generalised.

Committing at a pause is optional. A WIP commit on a local branch is fine; never push WIP.

### 6.5 Decision recording

- **Heading format:** `### D-n — title *(actor, date)*`, newest first, append-only. The actor
  is one of `owner`, `agent`, `owner + agent`, `owner asked`. Prior art: audio-workspace
  `docs/decisions.md`; adhoc `docs/decisions.md`.
- **Status:** BUILT, PROVISIONAL, DEFERRED, SUPERSEDED.
- **Links:**
  - `supersedes D-m` / `superseded by D-k`;
  - `relaxes D-m` / `narrowed by D-k` (adhoc);
  - `creates / amends / retires S-n, C-n` (new: this is what G-T3 reads).
- **Amendments** are dated blockquotes under the entry, never edits to the body
  (audio-workspace's `> **AMENDED …**`).
- **Negative results:** a section of rejected options with *"Do not re-derive these."*
  Each entry says what was tried, the evidence, and what would justify reopening it.
- **A generated index at the top** (audio-workspace `bin/decisionsIndex.mjs`). Its test must
  assert **content** (every row has an actor and a date), not just equality with a regeneration
  (D9).
- **Split by period** when the file passes its cap, keeping one generated index across all
  periods. audio-workspace's `decisions.md` is 1.77 MB; whether to split it is an open owner
  question.

### 6.6 Delegation

From global `CLAUDE.md § Delegation`:
- Delegate bulky reading.
- Ask for verdicts plus `file::symbol` evidence, never file dumps.
- Every delegated unit persists its own output incrementally, one file per agent.
- Check that the file exists and has a sensible size on return, and persist on receipt if not.
  `Explore` agents cannot persist.
- Default model is opus. Use fable only for open-ended design or taste judgement, or when the
  owner asks.
- **The agent audits; the session decides.**

### 6.7 Promotion and demotion

These flows are where continuity actually happens:

| From | To | When |
|---|---|---|
| scratch | evidence doc | the same hour (P10) |
| evidence | decision | when a conclusion is reached |
| decision | contract | when it becomes a durable rule; the contract keeps a pointer, not the explanation |
| memory | contract (global or repo) | when the lesson proves general (done for concurrent sessions and subagent model choice, 2026-10-07) |
| baton | board task | after two sessions |
| owner answer | decision (`actor: owner`) | immediately |
| closed board item | ledger line, plus its file archived | at close |
| old banner | ledger | at a clean close, if worth keeping |
| anything over its cap | archive (redirect table) | when the guard warns |

### 6.8 Push and CI

From global `CLAUDE.md § Git`: run the gate before every push; push only with permission; spawn
a background CI watcher for every push, keyed on the commit sha; a push is not done until the
watcher reports. A watcher only watches: it never re-runs, fixes or cancels anything.

---

## 7. Record layer details

### 7.1 Session ledger

- Append-only, newest first, **in its own file**, never inside the orientation note.
- Entry keyed by session key `YYYY-MM-DD[letter]` (zanzibar).
- Receipts are machine-checked (zanzibar `handoff_lint.py::check_session_receipt`).
- Rotation by period once past its cap. The archive is the period file; the ledger stays as
  the index.
- Counter-examples: intervals (38 entries inside a 62 KB HANDOFF); adhoc (the session log is
  about half of HANDOFF).

### 7.2 Evidence and plan docs

- One per item or investigation: `docs/<area>/<id>-<topic>-<date>.md`, declaring
  `ACTIVE-PLAN` while the item is open and `FROZEN` once it closes. Corrections are appended,
  dated, at the top (zanzibar `docs/README.md § 2–3`). Results docs for research repos:
  adhoc `docs/results/`.
- **Scouting is a deliverable:** an investigation's measurements are written down so the next
  session does not redo them (zanzibar CLAUDE.md, 2026-09-13).

### 7.3 Archive

- `git mv` the material, never repair it, first line `ARCHIVED YYYY-MM-DD`, one redirect
  table per archive directory (adhoc `docs/archive/README.md § Two rules`; audio-workspace
  `docs/archive/README.md`: *"Nothing in here is repaired, extended or kept current"*).
- Archive headings act as the index, e.g. audio-workspace's
  `## Pruned from HANDOFF.md on <date>`.

### 7.4 Hazard register

Traps that are true **now**: unverified hazards, fragile areas, "do not fix blind" items.
Edited in place, and removed when fixed (with a ledger line). Prior art: audio-workspace
`docs/invariants.md`; its HANDOFF section `UNVERIFIED HAZARD (do NOT fix blind)`.

---

## 8. Verification layer: guard catalogue

Each guard runs in the repo's gate (and in CI) and **refuses**; anything advisory says so
explicitly. Every guard has a sabotage test proving it can go red (P7).

### 8.1 Intent guards
- **G-I1:** every charter goal has at least one story; every story names at least one goal.
- **G-I2:** every story has an actor, a date and a status. Retired stories point to a decision.

### 8.2 Trace and freshness guards
- **G-T1:** every live story has at least one criterion, or is `unspecified` with an open
  owner question.
- **G-T2:** criterion ↔ test both ways. A `verified` criterion names a test that exists; every
  test names a criterion or is tagged `internal`. (audio-workspace `featureCoverage.test.ts`,
  `specBddFreshness.test.ts`)
- **G-T3:** freshness. No live story or criterion is retired by a decision; nothing describes
  a removed thing. (audio-workspace `requirementsFreshness.test.ts`)
- **G-T4:** structural claims. `file::symbol` resolves and its body hash matches the pin;
  re-pinning is an explicit, reviewed act. (zanzibar `anchor_check.py`, `claim_rot.py`)
- **G-T5:** mutation per criterion, nightly or on demand (too slow for every gate run). Break
  the behaviour; the linked test must fail. (Generalises intervals `tools/sabotage.py`.)

### 8.3 Doc guards
- **G-D1:** caps per component (lines, bytes and line width), configured with a provenance
  note per value: MEASURED or JUDGEMENT (zanzibar `tasks/config.json`). Prior art:
  audio-workspace `claudeMdShape` (40,000 + 600 per table row), `handoffShape`, `runbookShape`;
  zanzibar `MAX_LINES`.
- **G-D2:** ids unique across their series; retired ids never reused
  (zanzibar `tasks/retired-ids.txt`).
- **G-D3:** every link and `file::symbol` reference resolves, case-exact (audio-workspace
  `docLinks.test.ts`).
- **G-D4:** every doc declares its liveness in its first 8 lines (zanzibar `HS-5`, not built
  yet).
- **G-D5:** counts appear only inside generated blocks; prose counts are refused.
- **G-D6:** generated indexes are byte-identical to a regeneration **and** content-complete
  (D9).
- **G-D7:** badge budgets: ⚠ ≤ N per file, bold-caps budget (zanzibar `handoff_lint.py`).
  Badges only rank if they are bounded (zanzibar `docs/README.md § 4`).
- **G-D8:** the orientation note contains no board rows, no session sections and no
  history; the board, if inline, starts within the first K lines (fixes audio-workspace's
  blind spot).

### 8.4 Working-state guards
- **G-W1:** the banner's session key is ≥ the newest clean-close ledger entry.
- **G-W2:** at most N consecutive pause markers without a clean close.
- **G-W3:** batons older than two sessions fail (zanzibar `TK97`, not built yet).
- **G-W4:** closed ids do not appear in the open board.
- **G-W5:** tier caps: NOW = 1, NEXT ≤ 5 (zanzibar `task.py lint`).
- **G-W6:** ledger receipts are present and well-formed (zanzibar `check_session_receipt`).

### 8.5 Verification-state guards
- **G-V1:** a run ledger: which suites passed on which tree hash. A gate for commit or push
  can require a green row for the current hash. (intervals `tools/gate.py status --require
  commit|push`, pinned by `tests/test_gate_ledger.py`)
- **G-V2:** count floors for collected tests and protected files, with **zero headroom** and
  an independent recount (zanzibar).
- **G-V3:** a gate run lock: no two concurrent gate runs on one tree (zanzibar
  `scripts/gate_lock.py`).
- **G-V4:** exit codes are not piped through `tail`/`tee`; one phase per command; temporary
  logs from `mktemp`. These four exit-code lies are recorded in zanzibar.

---

## 9. Storage, persistence and where OKF fits

### 9.1 Choosing what persists

The deciding question for each piece of information:

> **If this were lost, would it cost owner attention or re-measurement?**
> Yes → it persists, tracked. No (it can be regenerated from tracked state) → it is ephemeral.

### 9.2 Tiers

| Tier | What | Persistence | Format |
|---|---|---|---|
| **T0 ephemeral** | context window; `.scratch/`; background-agent reports; generated maps (coverage → code) | none; gitignored or regenerated | anything |
| **T1 working state** | orientation note, board, owner questions, batons and pause markers | tracked, **replaced**; git is its history | plain markdown, or task files with frontmatter; **our own semantics** |
| **T2 durable knowledge** | charter, stories, criteria, decisions with negative results, evidence docs, hazards, deviations, archive, ledger | tracked, **append-only or frozen** | **OKF bundle** |
| **T3 cross-project** | global contract, memory | outside the repos (`~/.claude`) | memory is already close to OKF; redesign later |

### 9.3 OKF's role: the format for T2, not for the framework

Google Cloud's Open Knowledge Format v0.2 (`GoogleCloudPlatform/open-knowledge-format`,
`SPEC.md`) is a vendor-neutral format for a directory of markdown files with YAML frontmatter.
It suits T2 well:

| Our need | OKF feature |
|---|---|
| one concept per file, path as identity | concept id = path minus `.md` |
| component type | required `type:` (e.g. `Decision`, `Story`, `Criterion`, `Evidence`, `Hazard`, `Deviation`) |
| the routing map, progressive loading | `index.md` per directory (no frontmatter; entries carry descriptions) |
| the session ledger | `log.md`: newest first, `YYYY-MM-DD` headings, `**Update**` / `**Creation**` / `**Deprecation**` |
| who and when | `generated: {by, at}`; actors as `human:<id>` / `<producer>/<version>` / `process:<id>` |
| owner sign-off | `verified: [{by: human:owner, at}]` gives the "human-reviewed" trust tier |
| superseded or retired | `status: deprecated` (kept for links and history) |
| freshness | `stale_after:` an absolute timestamp; readers warn or refuse after it |
| evidence sources | `sources:` with ids, cited as footnotes |
| extensions | unknown keys must be preserved, so our extra keys are legal |

**Where we go beyond OKF**, using extension keys, which OKF allows:
- `id:` stable series ids (`D-n`, `S-n`, `C-n`). OKF's path identity breaks when files move;
  our ids must not.
- `supersedes:` / `superseded_by:` / `relaxes:` / `amends:` / `retires:` (OKF only has
  untyped links plus `status: deprecated`).
- `actor:` with our vocabulary (`owner` / `agent` / `owner + agent` / `owner asked`), alongside
  OKF's `generated.by`.
- `criterion_status:` (`verified` / `planned` / `manual` / `deviates` / `retired`) and
  `test:` (the test reference).
- `liveness:` (LIVING / ACTIVE-PLAN / FROZEN), in addition to OKF's `status`.

**What OKF does not cover at all, and the framework must:**
- ranking (NOW/NEXT caps);
- owner-only questions;
- baton expiry and pause semantics;
- replace-versus-append discipline (OKF's `log.md` is newest-first, but OKF never says a log
  may not be rewritten);
- rituals;
- guards.

OKF's conformance is deliberately permissive: readers **must not** reject missing optional
fields, unknown types or broken links. Our guards are deliberately strict. So we write
OKF-conformant files and enforce a stricter profile on top.

**`Attested Computation`** (OKF v0.2 §10) is worth borrowing later for G-V1. It is a
computation plus a deterministic, no-LLM attester that checks a receipt, which matches "what
has been proven on this commit" and the receipt lines in the ledger.

### 9.4 Later: richer memory tools

All of these are **derived and disposable**; the files stay the source of truth:
- **Vector search** over T2 and T3, for recall across large decision logs and evidence.
- **A source graph**: the code symbol graph plus OKF's link graph plus the generated
  coverage-to-code map, for impact analysis ("what criteria and decisions touch this
  symbol?").
- **A memory architecture** for T3 (where per-project memory and the global contract
  meet), including the path-case split in memory directories (`C--users-user-pycharmprojects`
  vs `C--Users-user-PycharmProjects-*`). Deferred by the owner on 2026-10-07.

---

## 10. Layout (default for a new repo)

```
CLAUDE.md                  # contract (capped); AGENTS.md if a cross-tool audience exists
HANDOFF.md                 # orientation note: banner, baton or pause marker, next session (capped)
docs/
  index.md                 # routing map: where each kind of statement lives
  charter.md               # goals, principles, non-goals (owner)
  stories/   index.md, log.md, S-*.md         # owner's voice
  criteria/  index.md, C-*.md or features/*.feature
  decisions/ index.md (generated), log.md, YYYY-Qn.md (D-* entries, negative results section)
  deviations.md            # append-only
  hazards.md               # replaced
  evidence/  <id>-<topic>-<date>.md (ACTIVE-PLAN → FROZEN)
  ledger/    log.md (current period), YYYY-Qn.md
  archive/   README.md (redirect table), *
tasks/                     # only once the board outgrows the note (≈30 open items)
tools/context-lint/        # the guards, plus their sabotage tests
.scratch/                  # gitignored crash bag
```

---

## 11. Adoption

### 11.1 Minimum set for a new repo, from day one
Charter; stories; criteria with statuses; contract; orientation note with an inline board and
owner questions; baton; decision log with negative results; ledger in its own file; scratch
rule; the four rituals (intake, clean close, pause, resume); and guards G-D1, G-D2, G-D3,
G-T2, G-W1, G-W3.

### 11.2 Add when needed
| Trigger | Add |
|---|---|
| the repo starts measuring things | evidence docs, G-D5 count blocks |
| the contract starts filling with traps | hazard register |
| code deliberately departs from the spec | deviation register, criterion status `deviates` |
| "did the gate pass on this commit?" keeps coming up | run ledger G-V1 |
| a component hits its cap | archive plus a redirect table; split the decision log by period |
| more than ~30 open items, or concurrent board work | task tree with a CLI |
| the spec makes structural claims | hash pins G-T4 |
| the suite is big enough to shrink unnoticed | count floors G-V2; mutation G-T5 |

### 11.3 Where each repo stands (2026-10-07)

| Repo | Strongest | Biggest gap against this framework |
|---|---|---|
| zanzibar | working state, ledger receipts, structural claim pins, doc lints | no charter or story layer; CLAUDE.md uncapped; banner bytes uncapped; TK97/HS-5 unbuilt |
| audio-workspace | requirements → BDD → tests, freshness and traceability, doc shape guards | FR and scenario double layer; HANDOFF history above the board; decision index content unchecked; at its caps |
| intervals | run ledger, sabotage, property fuzzing | no doc guards; banner as a log; decisions spread over three places |
| adhoc | decision tagging and links, project brief, results docs | no doc guards; session log inside HANDOFF; method detail in CLAUDE.md |
| peass | frozen baseline, ARCHIVE with "do not reopen" | stale process state; no ledger; no guards |
| nmd | negative-results table, parity tests | no ids on decisions; tests cite HANDOFF item numbers unchecked; stale sections |

Each repo's specific fixes are already recorded in its own handoff (commits of 2026-10-07).

---

## 12. Open questions for the owner

1. **Story format:** free prose per story file, or a light template (role / want / so that,
   plus interactions)? The default here is free prose plus metadata.
2. **Criteria granularity for research repos:** is a metric threshold on a ladder a criterion,
   or is the ladder itself the spec?
3. **Do background sync agents run every session**, or only when `HEAD` changed since the
   last sync (the draft says the latter)? What model: sonnet for hygiene, opus for
   trace-sync?
4. **N for pause tolerance** (the draft says 2).
5. **Where the framework lives:** a dedicated repo, pinned by version from each project (the
   draft's recommendation), or a folder in an existing repo.
6. **OKF adoption depth:** OKF frontmatter on T2 files only (the recommendation), or also on
   task files.
7. **Owner sign-off on criteria:** must every criterion carry `verified: human:owner`, or only
   those derived from stories marked "sign-off required"?

---

## Appendix A: evidence index (to be verified by the reviewers)

| Claim | Where |
|---|---|
| One home per statement | zanzibar `docs/README.md § 1` |
| Liveness is three-valued | zanzibar `docs/README.md § 2` |
| Boards replace; ledgers accrete | zanzibar `docs/README.md § 6` |
| End-of-session Rhythm | zanzibar `docs/README.md § 7` |
| Badges rank only if bounded | zanzibar `docs/README.md § 4` |
| HANDOFF line cap | zanzibar `scripts/handoff_lint.py::MAX_LINES` |
| Receipt check | zanzibar `scripts/handoff_lint.py::check_session_receipt` |
| Restated-count check | zanzibar `scripts/handoff_lint.py::check_restated_counts` |
| Task CLI | zanzibar `scripts/task.py` |
| Retired ids | zanzibar `tasks/retired-ids.txt` |
| Anchor resolution | zanzibar `formal/conformance/anchor_check.py` |
| Claim body hashing | zanzibar `formal/conformance/claim_rot.py`, `formal/correspondence_anchor_pin.txt` |
| Deviations and gaps | zanzibar `docs/spec-deviations.md`, `docs/latent-gaps.md` |
| Gate lock | zanzibar `scripts/gate_lock.py` |
| Pointer-only contract | audio-workspace `CLAUDE.md § Where the authority lives` |
| Contract caps | audio-workspace `src/__tests__/claudeMdShape.test.ts` (`MAX_BYTES = 40_000`, `MAX_ROW_BYTES = 600`) |
| Scenario ↔ test | audio-workspace `src/__tests__/featureCoverage.test.ts` |
| Requirement → scenario | audio-workspace `src/__tests__/requirementsTraceability.test.ts` (D-172) |
| Traced ≠ true | audio-workspace `src/__tests__/requirementsFreshness.test.ts` (D-173) |
| spec-bdd liveness | audio-workspace `src/__tests__/specBddFreshness.test.ts` |
| Generated scenario counts | audio-workspace `src/__tests__/featureScenarioCounts.test.ts` |
| Live driver coverage | audio-workspace `src/__tests__/liveDriverCoverage.test.ts` |
| Decision index | audio-workspace `bin/decisionsIndex.mjs`, `src/__tests__/decisionsIndex.test.ts` |
| Guard bounds what it measures | audio-workspace `docs/decisions.md` D-221 |
| Hazards not a contract | audio-workspace `docs/invariants.md` |
| Archive never repaired | audio-workspace `docs/archive/README.md`; adhoc `docs/archive/README.md` |
| Run ledger | intervals `tools/gate.py`, `tests/test_gate_ledger.py` |
| Sabotage tool | intervals `tools/sabotage.py` |
| Decision actor tags | adhoc `docs/decisions.md` |
| Project brief | adhoc `docs/project-brief.txt` |
| Do not re-derive | nmd `docs/decisions.md`; adhoc `docs/decisions.md` |
| Do not reopen | peass `ARCHIVE.md` |
| Frozen baseline | peass `TODO.md § process state` |
