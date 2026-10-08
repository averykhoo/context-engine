# A context-engineering framework for agent-built repos

**Draft v0.5, 2026-10-08. Status: DRAFT, tracked.** It lives in the `context-engine` repo,
`docs/framework/`, beside the engine that implements it. Until 2026-10-08 it was kept untracked
in the gitignored `PycharmProjects/.scratch/context-framework/` while the goal was to
understand the existing repos; it moved here, with its drafts, source notes and reviews, when
building started (owner, 2026-10-08). v0.1 and v0.4 are kept beside it as `FRAMEWORK-v0.1.md`
and `FRAMEWORK-v0.4.md`; `A-zanzibar.md` to `D-light-and-global.md` are the v0.1 source notes.

**v0.5 adds the record engine** (§8.0): one tool owns every component that is a set of id'd
records (tasks, owner questions, batons, pause blocks, ledger entries, decisions, stories,
deviations), stores them as OKF files, and exposes them to agents through a per-session MCP
server and to housekeeping through a no-model script (§6.11). The driver is context: *"no need
to read and reread every edit"* (owner, 2026-10-08). The OKF v0.2 spec was read for this
revision; its constraints are in §9.3. §12.4 records the owner's answers; §13 lists what changed.

v0.3 records the owner's answers to the v0.2 open questions (§12, 2026-10-07). v0.2 folded in
four reviews, in `review/`:

- `fable-coherence.md`: design coherence;
- `opus-zanzibar.md`: faithfulness to zanzibar;
- `opus-audio-workspace.md`: faithfulness to audio-workspace;
- `opus-citations.md`: 109 citations checked; 1 wrong, 1 not found and 13 imprecise were fixed.

§13 lists what changed and why. Where reviewers disagreed, the resolution is stated in place.

Repo short names:

| short name | path under `PycharmProjects/` | what it contributes most |
|---|---|---|
| **zanzibar** | `graph-reachability-zanzibar-index` | working state as a task tree, ledger receipts, structural claim pins, doc lints |
| **audio-workspace** | `audio-workspace` | PRD → BDD → tests, existence-based freshness, doc shape guards, multi-agent build rounds |
| **intervals** | `intervals` | run ledger, sabotage tooling, property fuzzing |
| **adhoc** | `adhoc-microphone-array` | decision provenance tags, project brief, results docs |
| **peass** | `python-peass` | frozen numerical baseline, "do not reopen" archive |
| **nmd** | `ngram-movers-distance` | negative-results table, parity tests |

---

## 0. What this framework is for

### 0.1 Who does what

The **owner does not write code**. The owner gives **intent**:
- user stories, use cases and interactions;
- the spec;
- goals, principles and non-goals;
- architecture or algorithm direction now and then;
- the decisions only the owner can make.

**Agents do everything else:**
- turn intent into precise criteria, criteria into tests, and tests into code;
- keep the docs, guards and rituals that make the work continuous across sessions.

Agent autonomy is expected to keep rising. The less the owner supervises, the more the repo
itself must carry intent, correctness and continuity.

Four jobs:
1. **Make intent durable.** The owner's words survive sessions, context resets, concurrent
   sessions and model changes: verbatim, attributed to the owner, and dated.
2. **Make correctness checkable.** Every piece of intent traces to something executable that
   has been shown to fail when the behaviour breaks.
3. **Make continuity cheap.** A cold session, even a new model with no memory, can orient in
   minutes from a single query, resume mid-flight, and leave the repo better oriented. This is
   *measured*, not assumed: see the `read:` receipt in §6.3.
4. **Spend owner attention only where it is irreplaceable.** Agents decide what they may
   decide, record it, and ration what they raise.

### 0.2 Stance

- **Plain files and git now.** Markdown with small frontmatter schemas, plus lint scripts that
  run inside each repo's gate. Vector search, source graphs and memory services come later
  (§9.4), as derived indexes, never as the source of truth. SQLite is allowed only on the same
  terms: a disposable index, because it is not friendly to human readers, hand editors, or git.
- **Records are written through a tool; prose is written by hand** (v0.5). Anything that is a set
  of id'd records with a lifecycle is changed by typed operations of the record engine (§8.0),
  so an agent never reads a file in order to change part of it. Hand edits stay legal, for
  humans and agents alike; the gate's lints catch what they break (P7).
- **Mechanical refusal beats a written warning.** audio-workspace guarded its HANDOFF
  mechanically "because three doc warnings lost" (commit `ea214a5`; D-157 §5 *"The guard,
  because this is the fourth prune"*, 2026-09-03). The template-copy repos (Fabric, nmd,
  intervals, adhoc) kept the rules and none of the guards, and all four are drifting
  (`C-midsize.md`).
- **Mechanise a step people keep forgetting.** *"A note in a provenance string is not
  sufficient to cause a step; a tool that has just created the file is"* (zanzibar
  `task.py::ratchet_min_parsed`, written after three sessions forgot the same manual step).
- **One versioned implementation.** The guards ship as one versioned lint package, with a
  per-repo config and a `framework: <version>` pin in each contract (§8.0). Prose rules copied
  between repos diverge; that has already happened four times.
- **Not too simple.** Every component exists because its absence caused a recorded failure.
  "Simple" means no infrastructure, not few concepts.
- **Adopting it in an existing repo: map, don't move.** Existing repos keep their paths, ids
  and check numbers. The routing map records how each framework component maps onto the
  repo's own files (§11.4). zanzibar alone has 428 citations of `session-log.md` and
  `spec-deviations.md` (grep, 2026-10-07); moving those files would break them all.

---

## 1. Principles

**P1. One home per statement; everywhere else points to it.**
- zanzibar `docs/README.md § 1`: *"every statement has exactly one home, and everywhere else is
  a pointer."*
- audio-workspace `CLAUDE.md § Where the authority lives`: *"This table is a POINTER and
  nothing more."*

**P2. Every artifact declares how it changes and how alive it is.** These are two separate
properties.

How it changes:
- **replaced:** rewritten in place; git holds the history;
- **append-only:** entries are never edited; corrections are dated additions;
- **generated:** produced by a tool, and checked against a regeneration **and** for content;
- **stamped:** an entry carries a session key and expires (batons, pause blocks).

How alive it is (zanzibar `docs/README.md § 2`):
- **LIVING:** maintained, true today;
- **ACTIVE-PLAN:** being executed; the body is provenance, corrections are appended at the top
  with dates;
- **FROZEN:** provenance only, with a visible banner.

**For records, the change mode is per-kind config that the engine enforces** (v0.5, §8.0.1):
append-only kinds carry a body hash and accept only `amend`; stamped kinds expire mechanically;
replaced kinds have tool-owned frontmatter and hand-written bodies.

**P3. Stable ids, never reused, and never renumbered.**
- Applies to stories, criteria, decisions, tasks and questions, and also to rule numbers,
  ritual step numbers and guard check numbers.
- Cite stable keys, never line numbers.
- Code is cited as `file::symbol`.
- Source: zanzibar `docs/README.md § 5`. zanzibar check 13 is "never reused".

**P4. Provenance on anything that can go stale:**
- **who:** the actor vocabulary in §6.5, with the model id for agents;
- **when:** a date or session key;
- **how it is known:** READ / REASONED / UNVERIFIED (zanzibar `CLAUDE.md § SCOUTING IS A
  DELIVERABLE`).

**P5. Numbers that can be derived from the tree are generated. Measurements may be typed with
a date.**
- Derivable counts (scenario totals, task counts) live in generated blocks:
  audio-workspace `featureScenarioCounts.test.ts`, zanzibar `check_restated_counts`.
- A measured value from a run may be typed **with its date on the line** (audio-workspace
  D-42), ideally in a single-baseline slot (audio-workspace D-255: one dated baseline per
  suite).
- zanzibar's four allowed forms for a number in prose: a fenced block; a backticked or quoted
  span; a `YYYY-MM-DD` key on the line; or a file whose banner declares its body is provenance
  (`docs/README.md § 1`).
- Re-measure; never difference against a recorded number (global `CLAUDE.md`).

**P6. Cap the dimension that actually grows, target the mechanism of growth, and give every
component a way out.**
- audio-workspace D-221: *"A guard bounds what it measures, and the growth moves to what it
  does not."*
- The growth mechanism behind a regrowing note is **append-layering** against a
  replace rule (zanzibar `docs/history/handoff-redesign-2026-08.md`). So the targeted guard is
  a layer detector: the banner carries exactly one session key. A byte cap is only the
  backstop.
- Components with no exit path bloated, every time:
  - session logs kept inside HANDOFF (intervals, adhoc);
  - a 1.77 MB `decisions.md` (audio-workspace);
  - uncapped `CLAUDE.md` files (zanzibar: 45 KB, growing ~4 KB a week; 2026-10-07).

**P7. Every tracked text component has a schema and a cap; every rule that matters has a guard;
every guard has been shown to fail.**
- **A place needs room, and checks on what is inside it** (owner, 2026-10-08: *"a place for
  everything and everything in its place is a good plan, but that place needs to have the space
  for the thing and checks that run on the things inside"*):
  - **room:** a schema, a cap, and a way out (archive or promotion), so it never has to bloat;
  - **a write-time check:** the engine refuses a bad write when it is made, and names the
    remedy (zanzibar `task.py promote` already refuses a budget violation at write time);
  - **a rest-time check:** a lint in the gate. Both are needed, because humans and hand edits
    bypass the tool (§6.10).
- Sabotage what a guard protects and watch it go red (global `CLAUDE.md § Assurance traps`;
  intervals `tools/sabotage.py`).
- Guard the guards:
  - **Floors are raw totals with zero headroom, plus an automatic ratchet.** The zanzibar task
    floor, `tasks/config.json::min_tasks_parsed`, covers the whole corpus; it got zero headroom
    after `rm -rf tasks/closed` still linted clean.
  - **Floors that measure an instrument keep declared headroom**: zanzibar
    `min_read_first_pointers` "HEADROOM ON PURPOSE".
  - **The doc tools are themselves pinned by tests inside the gate:** zanzibar
    `tests/test_tasktool.py`, `test_handoff_lint_*`.
- **Each guard's docstring says what it deliberately does NOT check** (audio-workspace's guard
  headers; `requirementsFreshness.test.ts`: *"It does NOT claim to catch semantic drift"*).

**P8. Owner attention is the scarcest resource.**
- **The "who decides" test** (zanzibar `CLAUDE.md § Who decides`):
  - agents make engineering and architecture calls and record their reasoning;
  - only goals, priorities and genuine preferences go to the owner;
  - a consult with another model is a recommendation, not an order.
- **Ration what is raised:** standing owner questions are bounded by the NEXT cap (§5.3).

**P9. Skip what can be recovered; never skip what would be lost.**
- Rituals may be shortened at an awkward stopping point (§6.4).
- What may never be skipped:
  - unrecorded owner words;
  - evidence still in scratch;
  - an undescribed uncommitted tree;
  - the session's ledger entry.

**P10. Evidence goes into a tracked file the same hour.**
- `.scratch/` is a crash bag. A 2026-10-05 zanzibar sweep found 3 of 285 scratch files were
  the sole copy of something.
- "Scouting is a deliverable" (zanzibar `CLAUDE.md`).

**P11. Delegate reading for context; parallelise building only when file ownership is
disjoint. Judgement stays with the session.**
- Reading: global `CLAUDE.md § Delegation`.
- Building: audio-workspace's multi-agent build rounds (§6.6) show that parallel builders work
  under disjoint file ownership, with no fan-out on a dependency chain.
- *"The agent audits; the session deletes"* (global `CLAUDE.md § Sweeping it`), generalised:
  agents audit, and the session decides.
- **Exception (v0.5): housekeeping writes.** A housekeeping agent may write, but only through
  typed, logged, revertible engine operations (§8.0.2, the `hk_` set), and only to **carry out
  intent that is already recorded** (a commit trailer, a ledger line, an expiry rule). It never
  forms new intent: no ranking, no answering, no judging that work is done. The audit-only rule
  stands for anything that cannot be undone, such as deleting from `.scratch/`.

**P12. Concurrency is normal, and running sessions in parallel is a goal to build toward**
(owner, 2026-10-07).
- Several sessions share one tree; **working-state files must be safe with several writers**
  (§5.5).
- Commit by path; never `git stash` in a shared tree; re-check `git status` right before
  committing (global `CLAUDE.md § Concurrent sessions`).
- Observed 2026-10-07 in zanzibar: another session's commits absorbed 27 uncommitted files, and
  its last commit (`578d5f4`, 8 files, 17:12) landed under three minutes before an unrelated
  doc commit (`e8b340b`, 17:14), which then sat on top of it.

**P13. Behaviour claims are checked against the code, never against the decision log.**
- audio-workspace D-174 §1: *"rewriting a requirement against the decision log is not the same
  as checking it against the code"*.
- Decisions say what was *meant*; only the code says what *is*.

**P14. Honesty norm: criteria, goldens and oracles are never edited to make a test pass.**
- When a test and a criterion disagree, the default assumption is that the code is wrong
  (zanzibar `CLAUDE.md § Who decides`; `formal/HANDOFF.md § House rules` 1).
- Changing a criterion is a decision, with an actor.

---

## 2. The components at a glance

| # | Layer | Component | Question it answers | Changes by (P2) | Who supplies the content |
|---|---|---|---|---|---|
| 1 | Intent | **Charter** | What are we building, why, what is out of scope, which principle wins a tradeoff? | replaced (rarely), LIVING | owner; the agent proposes |
| 2 | Intent | **Stories** (incl. use cases, interactions) | What does the owner want to happen, in the owner's words? | **record**, append-only (amendments are dated additions; body hash pins the owner's words) | owner |
| 3 | Intent | **Criteria (the spec)** | Exactly what behaviour counts as correct? | replaced, with ids and statuses | agent drafts; owner may veto |
| 4 | Intent | **Law / NFRs** (optional) | Cross-cutting invariants: data model, performance, security | replaced, LIVING, with its own invariant → test map | agent, from owner intent |
| 5 | Intent | **Deviation register** | Where the system deliberately differs from the spec | **record**, append-only | agent; owner approves material ones |
| 6 | Rules | **Contract** | How do I work here? Gate, mandates, footguns | replaced, capped | promotion only |
| 7 | Rules | **Routing map** | Where does each kind of statement live, and how do framework components map onto this repo? | replaced, small | agent |
| 8 | Rules | **Invariants** (durable traps) | What is load-bearing, and must not be rediscovered the hard way? | replaced; changes only when the code does | agent |
| 9 | Rules | **Runbooks** (method) | How do we run the gate, sabotage, fan-out, release? | replaced. *"Archive the status, keep the method"* | agent |
| 10 | Working state | **Orientation note** | What is true now; what must the next session not miss? | replaced at every clean close; banner = one session key, stamped by the engine, written only if unchanged since read (§5.5) | agent |
| 11 | Working state + Record | **Tasks and the board** (tasks **and** owner questions) | What is next, in what order, what is waiting on the owner, and what happened on each item? | each task is a **durable record** (body, comments, op log, links to decisions; it stays when closed, **in place**, with `state: closed`). Only the ranking fields and the board *view* are volatile | agent ranks; owner assignment overrides |
| 12 | Working state | **Batons and pause blocks** | What did a session skip, or leave mid-flight? | **record**, stamped, one file each; cleared by a clean close, or expired after two sessions by housekeeping | agent |
| 13 | Working state | **Unverified hazards** | What is suspected dangerous right now, do not fix blind? | replaced | agent |
| 14 | Record | **Decisions** (with negative results) | Why is it this way, and what was rejected? | **record**, one file per decision, append-only (§6.5) | stamped with actor |
| 15 | Record | **Session ledger** | What happened in each session, with receipts? | **record**, append-only, one entry per session, written by `session.*` operations | agent |
| 16 | Record | **Evidence and plan docs** | What did we measure; what is the plan for item X? | ACTIVE-PLAN → FROZEN | agent |
| 17 | Record | **Archive** | Where did X go? | moved verbatim; redirect table | agent |
| 18 | Verification | **Tests and proofs** | Does the behaviour hold? | code | agent |
| 19 | Verification | **Trace and existence guards** | Is intent ↔ criteria ↔ tests complete, and does the prose still name live code? | code | agent |
| 20 | Verification | **Doc and working-state guards** | Is every component within its schema and caps? | code (versioned package) | agent |
| 21 | Verification | **Verification state** | What has been proven on *this* tree? | generated | tooling |
| 22 | Ephemeral | **Scratch** | Somewhere to put things before they are judged | throwaway | — |
| 23 | Ephemeral | **Memory** | What has the owner taught agents that isn't a rule yet? | accretes; promoted or pruned | agent records the owner's feedback |

**Terms:**
- A **baton** is a stamped note of a step a session skipped.
- A **pause block** is a stamped note of work left mid-flight (§6.4).
- A **session key** is `YYYY-MM-DD` plus a letter, minted by `session.start` under a lock
  (§5.5; v0.4 minted it at write-back).
- A **record** is one OKF file of a **record kind** the engine owns (§8.0.1). The engine owns
  its frontmatter and lifecycle; its body is prose. Components marked **record** in the table
  above are record kinds; the rest are hand-written documents checked by the doc guards.
- **Housekeeping** is the repair pass the engine runs at session start and before close
  (§6.11): a no-model script first, small tool-restricted agents only where reading is needed.

### 2.1 Separations that are load-bearing, and what happened without them

| Kept apart | What happened |
|---|---|
| Orientation note vs session ledger | The banner became a second log: intervals' banner is ~124 lines; audio-workspace has ~650 lines of banners and session sections above its board (2026-10-07). zanzibar's diagnosis: append-layering. |
| Owner-question **row** vs free-floating **badge** | zanzibar's 🧭 badge, unbounded and unchecked, drifted into meaning "see also". The cure (2026-09-22) was to make each owner question a **board row** in its own id series (`ASK-n`), ranked under the same caps, with the badge reduced to a pointer (`docs/README.md § 4` "Signals rank only if they are bounded"; `tasks/README.md § ASK-*`). *A separate question queue would be a second list beside the board, the rot zanzibar removed.* |
| Board vs baton | Batons that never expire become a second backlog. zanzibar: *"A bullet that survives two sessions is not a baton, it is backlog."* |
| Contract vs decision log | audio-workspace `CLAUDE.md` reached 288 KB as a table of contents for the log, cut to ~28 KB with a guard (D-163). |
| Contract vs invariants | audio-workspace `docs/invariants.md`: *"This is not a second contract."* |
| Invariants (durable) vs unverified hazards (volatile) | audio-workspace keeps durable traps in `invariants.md` ("changes only when the code does") and volatile ones as HANDOFF `UNVERIFIED HAZARD (do NOT fix blind)` sections. Merging them would delete durable lessons whenever a hazard is "fixed". |
| Status vs method | zanzibar *"Archive the status, keep the method"* (`docs/README.md § 2`): runbooks survive when the status around them is archived. |
| Stories vs criteria | The owner speaks in stories, not test-grade prose; criteria must be precise. The seam is accepted, and guarded (G-T1, G-T6) and synced (§6.1). |
| Ledger vs archive | The ledger records events; the archive receives pruned material verbatim and never repairs it (audio-workspace `docs/archive/README.md`). |

---

## 3. The intent layer and the correctness chain

### 3.1 Charter

**Contents:**
- goals, each with how it is measured;
- non-goals;
- ranked principles, so tradeoffs have a known answer;
- owner mandates.

**Today:**
- audio-workspace: "9 owner mandates" in `CLAUDE.md § Hard constraints`, and a charter-like §1
  in `docs/requirements.md`;
- adhoc: `docs/project-brief.txt`, and the goal stored as D-18, which also parks localization
  on D-17's evidence.

**Rule:** one charter per repo, owner-stamped. Agents change it only through an owner question,
then a decision, then the edit. Every goal is served by at least one story (G-I1).

**Bootstrapping cost to the owner:** about one page, given in chat (§6.9).

### 3.2 Stories: the owner's voice

**The owner's input is always free prose,** or simply a feature or a goal stated outright
(owner, 2026-10-07). No template is ever imposed on the owner, and the agent never rewrites the
owner's prose into one. **Templates belong to criteria:** BDD scenarios follow the Gherkin
template (§3.3). A stated **goal** goes into the charter; a stated **feature** becomes a story.

**Where stories live.** Either is fine, and a repo may use both:
- one story per file (`S-n`); or
- numbered sections of a per-feature **PRD** (`docs/issues/<slug>/PRD.md § N`). This is
  audio-workspace's working form: `PRD.md § 5.38` carries `(OWNER: "make Ctrl click include the
  cursors row")`, dated and marked provisional.

**Each story carries:**
- an id or section ref;
- a date;
- `actor: human:<id>`: **who gave it, recorded explicitly**, or `agent (reconstructed from …)`
  when back-filled (§11.4). **Git blame is not enough:**
  - the agent writes and commits the text, so the git author is whoever's credentials the
    session runs under, not who spoke;
  - two humans using one remote-control setup look identical in blame;
  - blame breaks when text is moved, reformatted or archived.
- `via:` the channel, e.g. `remote-control session <key>`, `issue #n`, `commit <sha>`,
  `direct edit`;
- a status: `live | unspecified | unconfirmed | retired`.

**Owner words are verbatim.** Agent text inside a story is labelled `AGENT:` and becomes owner
intent only once accepted: audio-workspace `(AGENT, § 5.33; accepted § 5.37)`.

**Amendments** are numbered, dated additions, never silent rewrites.

**As records (v0.5):** a story file is an append-only record (§8.0.1). `story.record` writes the
owner's words with `actor` and `via`; `story.amend` appends. The body hash (G-D10) makes
"verbatim" mechanical: rewriting the owner's words goes red. PRD sections are not separate
files, so a PRD-form repo maps stories onto PRD sections through `context.toml` and keeps
G-D10 off for them until it adopts story files.

**Intake classification (§6.2):**
- **behaviour-shaped intent** ("the user can…", "when X then Y") becomes a story;
- **choice-shaped intent** ("do it with X", "don't pursue Y", a priority) becomes a
  **decision** with `actor: owner`, or a charter edit if it is a goal or non-goal.

Owner intent therefore has exactly one home per kind (P1). G-T1 applies to stories only.

**PRD lifecycle:** a PRD is archived only when the PRD **and every issue under it** are done,
in the same change (audio-workspace `docs/agents/issue-tracker.md`). Origin
(`docs/issues/README.md`): an issue shipped on 2026-09-10 under D-184 stayed listed as
`ready-for-agent` for nine days, so a later session believed it was still open.

### 3.3 Criteria: the definition of correct

Each criterion has:
- an id, or a scenario tag;
- the story section or decision it derives from, **with its actor carried along**, e.g.
  audio-workspace `# PRD § 5.13 A (OWNER, § 5.34-§ 5.35)`;
- a status:

| status | meaning | requirement |
|---|---|---|
| `tested` | a test checks it | the claiming test exists (G-T2) |
| `planned` | no test yet | counted in a generated block |
| `manual` | checked by a hand-run driver | the **driver** declares which criterion or decision it checks (audio-workspace `liveDriverCoverage.test.ts`: each driver carries `@scenario`, `@decision: D-N`, or `@ties: none - <reason>`) |
| `deviates` | deliberately not met | references a deviation-register entry (G-T7) |
| `retired` | no longer intended | references the decision that retired it |

**Owner sign-off** is separate from test status:
- `verified: [{by: human:owner, at}]` in OKF terms;
- **decided: inform and proceed.** Agent-drafted criteria are live as soon as they are
  created. The owner is informed through the digest and pushes back if something is wrong.
  The owner delegated this choice to the agent on 2026-10-07, on the assumption "I'll push
  back if not";
- a story the owner tags `sign-off: required` holds its criteria at `planned` until the owner
  stamps them. This is opt-in.

So the owner's silence never blocks work, and the owner keeps a hard gate where they want one.
**"Inform" must actually reach the owner:** see the digest in §5.6.

**The form depends on the kind of project.** The chain's shape does not:

| Kind of project | Criterion | Its test | Prior art |
|---|---|---|---|
| Product / app | BDD scenario | e2e, component or unit test | audio-workspace `features/*.feature`, `featureCoverage.test.ts` |
| Library / algorithm | property or invariant | property-based or fuzz test | intervals (hypothesis fuzzing) |
| Port | parity with a reference | oracle or parity test | nmd `tests/test_parity_with_nmd.py` |
| Numerical / perf change | moves only within the declared tolerance | frozen baseline plus comparison | peass `TODO.md § process state` (baseline at `e960c5e`) |
| Research | **a direction plus measures** (§3.3.1); thresholds only where real | scored runs that move the frontier on held-out data without regressing guard measures, results in tracked docs | adhoc D-18, D-3, `docs/results/`, the rung table |
| Formal | theorem | proof plus model ↔ code correspondence pin | zanzibar `formal/`, `formal/CORRESPONDENCE.md` |

#### 3.3.1 Research repos

The owner, 2026-10-07: *"bringing the repo closer to the goal is the entire point"*, and the
goal *"does need a definition of success too, which is usually the end goal of the research
(e.g. make speech more intelligible) but this might not have a specific threshold for
success, just a direction."* So a research repo replaces pass/fail criteria with a
**direction, measures and a frontier**:

| Part | What it is | Who | Example (adhoc) |
|---|---|---|---|
| **Direction** | the end goal, as a direction, not a threshold | human (charter) | D-18 "separate each talker from everything else"; D-3 output serves STT **and** human listening |
| **Measures** | proxies for progress, agent-proposed, human-confirmable, each with **its known blind spots** | agent proposes; human may veto | SI-SDR, PESQ, ESTOI, DNSMOS. *"DNSMOS cannot see a dropped turn, so never judge a rung on it alone"* (`HANDOFF.md`) |
| **Ground truth** | the human judgement the proxies stand in for, sampled now and then | human | *"The owner is to listen"* to the scene 107 WAVs (`HANDOFF.md`, D-3) |
| **Frontier** | best-so-far on each measure, dated, on fixed scene sets | generated from results docs | the rung table in the banner: gss_pf 16.8 dB median SI-SDR vs oracle MWF 12.0 dB |
| **Targets** (optional) | a threshold, only where one genuinely exists | human | the DNSMOS OVRL target, 0.28 short (2026-10-05) |

**What counts as progress** (this is the research equivalent of a passing test):
- a change **moves the frontier** on the primary measure;
- on **held-out** data. Score any change to a selection rule on a fresh set, because sets that
  have been looked at are spent (adhoc's "third, fresh scene set" rule);
- **without regressing the guard measures**. A gain on one proxy that the others contradict
  is a suspected proxy failure, not progress;
- and is periodically **checked against ground truth**, because the proxies can drift from the
  direction (Goodhart). When the human's judgement and the proxies disagree, the human wins,
  and the measure set is revised by a decision.

**Success** is not reached; it is approached. A line of work stops when the frontier stops
moving (diminishing returns, recorded as a negative result) or when a human says it is good
enough, which is a decision.

- **All the work is tasks that move the repo toward the direction:**
  - testing new algorithms;
  - literature review and collating references;
  - downloading datasets;
  - building rungs on the ladder.

  These are not criteria, and need no criterion each. Each task names the goal it serves, and
  its outcome is evidence (a results doc, a reference note, a dataset card), or a negative
  result in the decision log.
- **Progress is the ledger of measurements:** dated results docs, each rung scored the same
  way on the same scene sets, with held-out sets kept fresh (adhoc's "score on a third, fresh
  scene set" rule).
- **The harness still gets ordinary tests:** metrics, data loaders, scorers and vendored
  libraries. A wrong metric silently moves you *away* from the goal while looking like
  progress. adhoc already vets research code against its paper under `vetting/<library>/`
  (D-24).

**The D-173 lesson, stated correctly.** audio-workspace's freshness incident hit **both**
layers:
- the FR text, where FR-20/22/24/27 described an orchestrator D-143 had deleted;
- **and** the spec-bdd scenarios: eleven more `@implemented` scenarios described the same
  orchestrator (`docs/spec-bdd/README.md`), and in D-261, 27 of 29 `@planned` tags described
  behaviour that had already shipped, with every guard green.

The cause was **prose criteria that name implementation symbols**, not the number of layers.
Hence:
- **no prose-requirements (FR) layer by default.** audio-workspace is already dropping it on
  its own: 11 of 87 scenarios in its newest feature file cite an FR (2026-10-07);
- an **existence guard against the code** at every prose layer (G-T3);
- **behaviour verified against the code** (P13).

NFRs and data-model law go in the charter, or in a law doc with its own invariant → test map
(audio-workspace `specs/SPEC.md § 13`).

**Unspecified semantics: pin first, then specify.** When existing behaviour nobody specified
must be preserved, write tests that pin it empirically, then write the criterion from the pins
(audio-workspace `AGENTS.md § Working method`).

### 3.4 The chain

```
charter goal ─► story (owner) ─► criterion (agent) ─► test (agent) ─ ─ ─► code (derived)
                     ▲  ▲                                  ▲
   choice-shaped     │  └── criteria census on design change (KEEP / rewrite / retire)
   intent → decision ┘                                     │
                         tests and drivers may also tie to a decision (@decision: D-N)
```

| Link | Written by | Guard |
|---|---|---|
| goal → story | hand (intake) | G-I1 |
| story → criterion | hand (agent) | G-T1: every `live` story has at least one criterion, or is `unspecified` **with a board task to specify it** (an owner question only if the agent cannot tell what the story means). G-T6: every criterion's story ref resolves |
| criterion → test | hand: an annotation in the test or driver | G-T2: every non-`planned`, non-`retired` criterion is claimed by a test or driver, and every annotation resolves. Prior art: audio-workspace `featureCoverage.test.ts` (*"The guard sees annotations, not coverage"*). **Not required:** that every test name a criterion. Tests may be internal |
| test → code | **derived** from coverage or imports | **proven, not declared:** G-T5 mutation per criterion |
| design change → criteria | census (§6.2 step 6) | the census output is an evidence doc. Retirements carry the decision id |

**Rules:**
1. **Stop hand-written links at the test.** A test-to-code map, used for impact analysis, is
   generated and disposable.
2. **A link proves existence, not truth.** D-173 §1: *"traced by a scenario. **That is not the
   same as being TRUE**"*. Hence G-T3 (prose names live code) and G-T5 (mutation).
3. **Structural claims get hash pins.** A claim about *structure* (model ↔ code correspondence,
   "implemented as a sparse bitmap") may cite `file::symbol`. The citation is:
   - resolved (zanzibar `formal/conformance/anchor_check.py`); and
   - pinned by a body hash (zanzibar `formal/conformance/claim_rot.py` →
     `formal/correspondence_anchor_pin.txt`).

   **Calibrate the pin:** zanzibar pins only the *shell* of Python classes, because *"a gate
   that fires on everything gets regenerated without being read."*

### 3.5 Deviation register

- **Append-only:** dated entries, each naming the criterion it affects, the reason, and who
  decided (zanzibar `docs/spec-deviations.md`).
- **A companion, replaced view of what is open today** is allowed (zanzibar
  `docs/latent-gaps.md`). With deviations as records (v0.5, one file each, append-only), that
  view can be a generated query instead.
- **The enforceable check (G-T7):** a `deviates` criterion must reference a register entry.
  No tool detects an *undeclared* deviation in general. A failing test is just a failing test,
  and P14 says the code is presumed wrong.

---

## 4. Drift: kinds and guards

Drift ids are `DR`, to avoid colliding with decision ids `D-n`.

| # | Drift | Guard | Prior art |
|---|---|---|---|
| DR1 | A story with no criterion; a criterion with no test | G-T1, G-T2, G-T6 | audio-workspace `requirementsTraceability.test.ts` (D-172): 17 of 47 FRs cited nowhere (2026-09-06) |
| DR2 | Prose names a file, symbol or route that no longer exists | **G-T3: existence check against the code** | audio-workspace `requirementsFreshness.test.ts` (D-173, D-174); `specBddFreshness.test.ts` |
| DR3 | Prose is semantically false while naming only live symbols | **no guard catches this.** Mitigations: the criteria census on every design change; G-T5 mutation; the trace-sync agent's judgement | `requirementsFreshness.test.ts`: *"It does NOT claim to catch semantic drift"*; D-261 (`@planned` tags describing shipped behaviour) |
| DR4 | Code changed under a structural claim | G-T4 hash pin | zanzibar `claim_rot.py` |
| DR5 | A doc cites a deleted file or symbol | G-D3 | zanzibar `anchor_check.py`; audio-workspace `docLinks.test.ts` |
| DR6 | A typed derivable number goes stale | G-D5 | audio-workspace `featureScenarioCounts.test.ts`; zanzibar `check_restated_counts` |
| DR7 | A test passes without checking the behaviour | G-T5 mutation; sabotage | intervals `tools/sabotage.py` |
| DR8 | The suite or corpus silently shrinks | G-V2 floors | zanzibar `min_tasks_parsed`, `MIN_TESTS_ALL`; audio-workspace runbook baselines (D-255) |
| DR9 | Working docs drift from reality | G-W rows, G-D8 | zanzibar banner "cap of 3" when the cap was 5 (2026-10-07); nmd's stale "What changed recently" table |
| DR10 | A generated index that is wrong but byte-identical to its regeneration | G-D6 content assertions from a cutoff id; **v0.5: generate indexes from record frontmatter, not from parsed prose**, so the misparse cannot happen for new records | audio-workspace `decisionsIndex.test.ts`: 7 recent rows misparsed while green; 141 of 289 historical rows predate the actor suffix (2026-10-07) |
| DR11 | A guard bounds one dimension and growth moves to another | target the growth mechanism (layer detector) plus a byte backstop | D-221; zanzibar banner at 14/14 lines with lines of up to 3,762 chars |

---

## 5. Working state

### 5.1 Orientation note (`HANDOFF.md`)

**Contents:**
- a **banner** with exactly **one session key** (the layer detector, G-D8), stating what is
  true now;
- **open baton and pause blocks** (§5.4);
- **next session**: the start sequence.

**No session history.** In small repos an inline board is allowed (§5.2).

**Read on demand.** The board query prints the banner, so a cold session often needs nothing
else; in v0.5, `orient()` prints it (§6.1). The `read:` receipt records whether the note was
read (§6.3).

**Replaced on clean close**, safely for several writers (§5.5). In v0.5 the batons and pause
blocks leave the note and become records (§5.4); the note keeps a generated pointer to the
open ones, so its replaced part is only the banner and "next session". The banner is written
with `banner.set(text, seen_hash)`, which refuses if the banner changed since this session
last saw it.

**Caps:**
- the layer detector first;
- then lines, bytes and line width as backstops. zanzibar caps at ≤60 lines
  (`handoff_lint.py::MAX_LINES`) and 14 banner lines (`task.py::BANNER_MAX_LINES`), and its
  byte size still regrew from about 4 KB to 18 KB through layering.

**Subtree notes are allowed** for a large subsystem, e.g. zanzibar `formal/HANDOFF.md`
*"It does not rank anything"*.

### 5.2 Board: tasks and owner questions together

**Three sizes:**
1. **Inline table** in the note: `# | id | what | status / blocker | spec`. Only for a
   single-session repo with few items.
2. **One file per item, no CLI.** The cheap step up; it removes most concurrent-edit
   collisions.
3. **Task tree plus CLI**, where the board is a query and nothing is committed as a board
   (zanzibar `tasks/`, `scripts/task.py`; *"There is deliberately no `BOARD.md`"*).

**When to move up a size:**
- the first trigger is **more than one session working the board** (P12);
- then: the note shows append-layering, or sessions still read the note for item detail.

**Adopt the next size by trial:** run it in parallel first, with a pre-registered rubric and
a single revertible cutover commit (zanzibar `docs/tasktool-trial-protocol.md`). zanzibar's
cutover was driven by a 979-line note and a duplicated banner serving stale instructions, not
by an item count.

**Item schema** (files or CLI):
- frontmatter: `id, title, brief, pri, deps, moved, updated, closed, source`, plus in v0.5
  `type: Task` (OKF) and **`state: open | closed`**;
- `brief`: ≤120 characters, **a constraint, not a summary**;
- body: summary, `## Traps`, and `## Read first`, whose pointers are lint-resolved with a
  floor.

zanzibar's trial found sessions still read the note "ten times out of eleven" until the tree
carried these sections (`docs/tasktool-trial-protocol.md`, 2026-08-30).

**Edit rules (task tree):**
- frontmatter changes only through CLI operations carrying `--session <key>`;
- `moved`, which drives staleness warnings, is never hand-edited;
- bodies are rewritten by hand under replace semantics (zanzibar `tasks/README.md`;
  `docs/README.md § 7` step 3).

**Ranking:** NOW (exactly 1), NEXT (≤5), LATER, HOLD, SOMEDAY (zanzibar
`tasks/config.json::budgets`). An owner assignment overrides the ranking. Do not re-rank at
session start; re-rank at clean close.

**Closing:** a closed item leaves the board, with a one-line ledger entry. Nothing is open and
done at once.

**Closing does not move the file** (v0.5; owner, 2026-10-08). Close sets `state: closed`, and
the engine derives OKF `status: deprecated` from it (§9.3). zanzibar moved closed items to
`tasks/closed/` so that `ls` showed open and closed apart; `task.py list --closed` and
`grep -l '^state: closed'` do the same job, and a path that never changes is a stable OKF
concept id. Existing `closed/` directories may be migrated into the flat directory once the
schema carries `state` (owner, 2026-10-08: *"one place for everything feels cleaner"*); the
migration is deferred while the framework is being written (§11.4).

### 5.3 Owner questions are board rows

- **Own id series** (`ASK-n` or `Q-n`), ranked in the same tiers as tasks.
- **Each question states:**
  - the question, answerable in one line;
  - why it is owner-only (the "who decides" test, P8);
  - the options, with the agent's recommendation;
  - what it blocks: the blocked tasks declare `deps: [ASK-n]`, and closing the question
    unblocks them.
- **Rationing:**
  - promoting a question to NEXT obliges the session to **raise it in chat**, one line each,
    in that session;
  - an `asked:` receipt in the ledger proves it, and a missing receipt is red (zanzibar TK96;
    `check_session_receipt`);
  - the NEXT cap bounds how many questions are being pressed at once.
- **The board is the owner's only tracker for questions** (owner, 2026-10-07: questions and
  tasks may share one system, *"just remember to ask me the questions at some point, or nag
  about them since I otherwise won't have a way to track them"*). So:
  - every open question carries `last_asked: <session key>`;
  - **at session start**, the session raises, in chat, one line each, every NEXT-tier
    question plus any question that is **overdue**: not asked in the last 5 sessions or 7
    days, whichever comes first;
  - if the owner says "later", that is recorded and `last_asked` is re-stamped. The question
    stays open, and **"later" is never treated as an answer**;
  - **G-W8** refuses a close while an overdue question has not been raised this session.
- **Closed only by an owner answer**, which becomes a decision with `actor: owner` and is
  recorded **immediately** (§6.4 item 0).
- **Engine operations (v0.5):** `ask.new`; `ask.raised([ids])` stamps `last_asked` and writes the
  `asked:` receipt; `ask.later(id)` re-stamps without answering; `ask.answer(id, owner_words)`
  records the words verbatim as a decision with `actor: owner`, closes the question, and reports
  which tasks it unblocked.
- **The agent never answers its own question.** If the agent can decide, it was not an owner
  question.

### 5.4 Baton and pause blocks

- **Baton:** a skipped step, stamped with its session key. The next session executes it
  **before its own work**. If one survives two sessions, it becomes a board task (G-W3;
  zanzibar `TK97`, not built yet).
- **Pause block** (§6.4), stamped, containing:
  - what was in flight;
  - the exact resume step;
  - the uncommitted paths and the branch;
  - where the evidence is;
  - which steps were deferred.
- Both kinds are **stamped blocks that accumulate per session**, never a single replaced field
  (§5.5).

**As records (v0.5).** Each baton and each pause block is its own record file (stamped kind,
§8.0.1), not a block inside `HANDOFF.md`. This is the largest single win of the engine:
- **nothing is carried forward at close,** so a concurrent session cannot drop another's block
  (v0.4 §5.5 rule 2 needed a verbatim copy-forward);
- `orient()` hands open batons and pause blocks to the next session before anything else;
- **expiry is mechanical:** housekeeping turns a baton older than two sessions into a task
  (G-W3 becomes a one-line check);
- `pause.open` **fills in the branch and uncommitted paths itself** from `git status`, and
  **commits its own record by path** immediately (§5.5 rule 4).

Operations: `baton.add(step, why)`, `baton.done(id, evidence)`,
`pause.open(in_flight, resume_step, evidence, deferred)`, `pause.resume(id)`.

These records are not ephemeral: they are tracked and committed, and they *expire*.

### 5.5 Rules for several writers

*(fable review finding 1, reconciled with zanzibar's real practice.)*

1. **Mint the session key at start, under a lock** (v0.5): `session.start` computes
   `max(newest ledger key, banner key) + 1 letter` while holding the engine lock, and
   immediately writes a **`kind: open` ledger stub** that reserves it. Two concurrent sessions
   therefore never share a key. *(v0.4 minted at write-back, because two sessions computing the
   key by hand at start could collide; the lock removes that race.)* The stubs buy two more
   things:
   - **live sessions are visible:** open stubs are the sessions in flight, and `orient()` lists
     them;
   - **crashes are detectable:** a stub never closed within the configured window is a session
     that died; housekeeping marks it `kind: abandoned` and files a baton (G-W11).
2. **Write the banner only if it is unchanged since you read it.** `banner.set(text, seen_hash)`
   refuses when the banner's hash differs from the one this session last saw; re-read and
   retry. *(v0.4: re-read `HANDOFF.md` and carry every baton and pause block forward verbatim.
   With batons and pause blocks as records, there is nothing to carry.)*
3. **Baton and pause records are keyed by session.** Only the owning session's clean close, or
   the session that completes the work, closes one; housekeeping expires them.
4. **Commit working-state records by path, promptly.** A pause record left uncommitted in a
   shared tree can be lost to another session's close. The engine commits its own working-state
   writes by path as it makes them: a docs-only commit, which is cheap.
5. **Background agents, gates and engine writes use locks** (G-V3 pattern) keyed on the tree
   hash. Each concurrent session runs its own MCP server process (§8.0.2), so the engine's lock
   must be a file lock, which the CLI needs anyway.

Running sessions in parallel is a goal (P12). **Most sessions will run however Claude Code
runs by default** (owner, 2026-10-07): in the shared checkout, with a worktree only when
opted into. So:
- **these rules are mandatory in the shared checkout;**
- **a worktree is recommended for building:** it removes most collisions at the source, at the
  cost of merging back;
- **a worktree session still writes its working state through the same rules on merge**:
  ledger entry, pause blocks carried forward, banner re-read before replacing.

### 5.6 The owner digest: how "inform and proceed" reaches the owner

Inform-and-proceed (§3.3) only works if the owner actually sees what was decided on their
behalf. Each session's chat close-out includes a digest of **at most 7 lines**:

- agent decisions of consequence, by id and one line each;
- criteria created, rewritten or retired, as counts plus anything surprising;
- owner questions raised (§5.3);
- anything the owner might want to push back on, flagged explicitly.

**The digest is also written into the session's ledger entry** as its `summary:` block, so it
is tracked. Anyone using plain git sees what each agent session did and decided, without
access to the chat (owner, 2026-10-07).

**Cross-repo question index, for agents, not for the human.** The owner said they probably
won't read such a page, but agents need one to nag. So:
- at session start, a generated file outside the repos, e.g. `~/.claude/owner-questions.md`
  (T3, generated and disposable), lists every open question across all repos, with
  `last_asked`;
- any session may add **one line** to its start-of-session nag: "also N overdue questions in
  other repos: …";
- the source of truth stays each repo's own board.

---

## 6. Rituals

Rituals are written for agents, and their effects are checked by guards, so a skipped ritual
shows up red. Step numbers are stable (P3).

### 6.1 Session start

**Full orientation** (zanzibar `tasks/README.md § Reading protocol`, *"This is the whole
session-start read"*):
1. The contract loads automatically: global, repo (`AGENTS.md` for workflow, `CLAUDE.md` for
   product, mandates and gate), and subtree.
2. **Open batons and pause blocks: execute or resume them first.**
3. The board query, which prints the banner. **Raise NEXT-tier and overdue owner questions
   in chat now,** one line each (§5.3), together with any tier-2 flags from the background
   pass.
4. `show` the top item, or the one the owner assigned.
5. Read that item's `## Read first` list.
6. Read the rest of the note **only if needed**, and record which in the `read:` receipt.

**With the engine (v0.5), steps 2–5 are one call.** `session.start` mints the key (§5.5), then
`orient()` returns, in one size-capped response: the banner; this session's open batons and
pause blocks, then other sessions'; the other sessions still open; the NEXT tier; overdue owner
questions; and the top item's brief, Traps and Read first. Step 1 is unchanged, and step 6 is
still on demand. A **SessionStart hook** could run start-of-session housekeeping (§6.11) and
inject `orient()`'s output, so orientation costs no tool call (UNVERIFIED: that hook output is
added to the model's context; check before relying on it).

**Resume** (an open pause block of your own, or the owner says "continue"): re-check the tree
against the block, then continue.

**Background housekeeping agents: cheap checks first, escalation on a flag** (owner,
2026-10-07). Fired at session start, read-only.

**Tier 1, the check pass, uses cheap models.** Most of the work is checking, so it runs on the
cheapest model that can do it (set in config; e.g. haiku or sonnet):

| Check | Looks for |
|---|---|
| **trace-check** | new or amended stories without criteria; criteria whose prose looks wrong against current code (DR3 candidates); census candidates after a design change |
| **inbox-check** | owner words not yet recorded: answers, stories or vetoes in recent chat summaries, commit messages, or edits to intent files |
| **question-check** | open questions overdue to be raised (§5.3) |

**Tier 2, escalation, happens only on a flag.** Each flag is routed to exactly one of:
- **a bigger agent** (e.g. opus), for judgement or drafting: write the missing criteria,
  adjudicate a suspected semantic drift, run a census. It reports; it does not edit;
- **the main session**, when the flag needs action in the tree: it is put in front of the
  session at start and becomes a task or a baton;
- **the owner**, only when the "who decides" test (P8) says it is owner-only. It becomes an
  `ASK-n` row and is raised in chat (§5.3).

A tier-1 agent never escalates straight to the owner. The main session does that, so it can
check whether the question is truly owner-only.

Rules for all background agents:
- **Keyed on the tree hash, with a lock file** (G-V3 pattern).
- **Skip** if a report for an ancestor hash is under a day old and no intent file changed.
- **Discard** any report whose hash is not an ancestor of `HEAD`.
- **Budget:** the tier-1 pass is one cheap agent, or a few; tier 2 runs only on flags, at most
  two escalations per session start, and the rest are queued as tasks.
- **Models:** set per repo, per tier, in the framework config, not hard-coded here.
- **Persistence:** reports go to `.scratch/sync/<hash>/<agent>.md`.
- **The session triages and edits.** The agents only report (P11). The exception is
  housekeeping (§6.11), which writes only through the engine's `hk_` operations.

Hygiene (caps, stale banner, expired batons) is **detected by the gate**. In v0.5 the mechanical
**repairs** (stamps, ratchets, regenerated indexes, expiring batons) are housekeeping's job
(§6.11), not the session's and not a checking agent's.

### 6.2 Intake: the owner gives intent

1. **Record it verbatim, now.** Behaviour-shaped intent goes into a story (a new story, an
   amendment, or a PRD section). Choice-shaped intent goes into a decision with
   `actor: owner`, or a charter edit. Tell the owner, in one line, which it became. Engine
   operations: `story.record` / `story.amend`, or `decision.new` with `actor: owner`.
2. Link it to the charter goal(s). If none fits, ask: it may be a new goal.
3. Draft the criteria. They are **live by default** (§3.3). Show the owner **a digest of three
   to seven lines**, never files. If the story is `sign-off: required`, the criteria stay
   `planned` until the owner stamps them.
4. Owner-only uncertainties become `ASK-n` rows (§5.3); never guess at them.
5. If the new intent contradicts an existing decision or criterion, say so at once, and record
   the outcome as a decision that supersedes or amends the old one.
6. **On a design change, run a criteria census:** every existing criterion in scope is
   classified KEEP / rewrite / retire, with the work assigned to tasks or slices. The census
   is an evidence doc. audio-workspace censused 318 scenarios against PRD § 5.13; 28 were not
   kept.

### 6.3 Clean close (a natural stopping point)

Order generalised from zanzibar `docs/README.md § 7` (*"Write the records FIRST, then run the
gate, then commit"*):

0. **Every owner word given this session is recorded** (story, decision, or question answer).
1. **Run the doc guards first, to see what earlier sessions left red,** before adding to it.
2. Write the ledger entry:
   - the session key, minted now (§5.5);
   - a `rows:` line naming the items touched;
   - receipts:
     - the guard results;
     - `read:` (`board only` / `board + note`), which **measures how cheap orientation is
       (job 3)**;
     - `asked:` when a NEXT question is pending;
   - `Still owed:`.
3. **Replace** the banner, safely for several writers (§5.5).
4. Board operations: close, rank, mint (with `--session`). Hand-rewrite the
   summary / Traps / Read first of every NOW and NEXT item you touched.
5. Promote durable rules into the contract; file method lessons into runbooks (§6.7).
6. Anything skipped becomes a baton block.
   - **6a. Pre-close housekeeping** (v0.5, §6.11): carry out what this session recorded but
     did not finish (closes named by `Closes:` trailers, floor ratchets, stamps, regenerated
     indexes). Its operation list goes into the digest.
7. **Run the gate again, to prove this close,** then commit by path. Push only with permission,
   then watch CI (§6.8).
8. **Owner digest in chat** (§5.6, at most 7 lines). A pause gives the same digest, shorter.

**With the engine (v0.5):** steps 2–4 and 6 are operations: `session.close(summary, rows,
receipts)` writes the ledger entry and refuses a malformed receipt; `banner.set`; the board
operations; `baton.add`. Step numbers are unchanged (P3); 6a is inserted, not renumbered.

### 6.4 Pause (an awkward stopping point; the work continues next session)

Rituals may be shortened. **What is mandatory** (P9) is cheap, and protects everything that
cannot be recovered:

0. **Owner words given this session are recorded.** The most easily lost thing of all: they
   exist only in one session's transcript.
1. **Evidence is out of scratch**, in a tracked doc. It may be rough, dated and ACTIVE-PLAN.
2. **A ledger entry, `kind: pause`.** Three lines are enough: key, rows, `deferred:`. The
   ledger is one entry per session without exception (zanzibar `session-log.md` header: *"One
   entry EVERY session, without exception"*), because staleness tracking depends on it.
3. **A pause block in the note**: in flight, resume step, uncommitted paths and branch, and the
   deferred steps. **Committed by path.**

**Deferred, not dropped:** the gate, the commit of the work itself, re-ranking, banner
replacement, runbook filing.

**With the engine (v0.5):** items 2 and 3 are `session.pause(rows, deferred)` plus
`pause.open(...)`, which captures the branch and uncommitted paths itself and commits its record
by path.

zanzibar's real pause on 2026-10-07c (the owner cleared context rather than wait for the gate)
did exactly this: ledger plus banner key written, gate and commit deferred as a stamped
Still-owed bullet listing exact paths.

**Enforcement:**
- **G-W2:** at most N consecutive `kind: pause` ledger entries without a `kind: close`.
  N = 2 (owner, 2026-10-07).
- **G-W3** is separate: no baton or pause block older than two sessions.

### 6.5 Decision recording

**Heading:** `### D-n — title *(actor, date)*`.
- **Actor vocabulary:** `owner` · `agent (<model-id>)` · `owner + agent` · `owner asked`
  (the owner requested it and the agent chose how) · `owner reported + agent` (the owner
  reported a problem and the agent decided the fix).
- **With more than one human,** `owner` becomes `human:<id>`, e.g. `human:alice asked`.
  The charter lists the humans and their **roles**: who may decide what (goals, priorities, a
  feature area). The "who decides" test (P8) then routes a question to the right human, not
  just to "the owner". A single-owner repo may keep the bare word `owner` as an alias.
- The model id matters: "survives model changes" is otherwise untestable.

**Decisions are records (v0.5): one OKF file per decision**, `docs/decisions/D-n-<slug>.md`,
written only through the engine. This answers both problems v0.4 left open: audio-workspace's
`decisions.md` is 1.77 MB, so "why is X like this?" meant grepping it and reading a large chunk;
and append-only was a doc rule checkable only by reading git diffs.

```yaml
---
type: Decision
id: D-262
title: Batons are one record each, not blocks in HANDOFF
description: one line; this is what the generated index shows
actor: owner asked                # the vocabulary above
decided: 2026-10-08
session: 2026-10-08a
decision_status: BUILT            # BUILT | PROVISIONAL | DEFERRED | SUPERSEDED | REJECTED
status: deprecated                # OKF; derived by the engine, present only when SUPERSEDED
supersedes: [D-157]
superseded_by: []                 # backlink, maintained by the engine
relaxes: []                       # narrowed_by likewise
creates: [S-4]                    # amends: / retires: likewise
tasks: [TK96]
tags: [working-state]
reopen_if:                        # REJECTED only: what would justify reopening it
generated: { by: claude-code/<model-id>, at: 2026-10-08T14:02:00Z }
verified: { by: human:owner, at: ... }   # optional: the owner explicitly endorsed it
sources: [{ id: ev1, resource: /docs/evidence/<file>.md }]
body_sha: <hash>                  # covers everything above "## Amendments"
---
<the decision text, written once>

## Amendments
> **AMENDED 2026-10-09 (agent (<model-id>))** ...
```

**Operations:** `decision.new`, `decision.amend` (appends a dated blockquote; the only allowed
body change), `decision.supersede(old, new)` (sets both directions and derives OKF `status`),
`decision.link(id, task | story | criterion)`, `decision.find(text, tag, status, links_to)`
(one-line rows), `decision.show(id, section)`, and **`why(target)`**: given a task, criterion
or `file::symbol`, the decisions that link it. Writing a decision costs only its own text; no
session opens the log to append to it.

**Typos.** A strict body hash forbids fixing them. `decision.correct(id, ...)` is allowed: it
updates `body_sha` and logs a `corrected:` line under Amendments, so every edit stays visible
(agent proposal; open question Q-I).

**Organisation: the by-id versus by-topic choice is gone.** Records are stored by id; topic is
a tag, and the generated index groups by tag. zanzibar-style topic narratives ("why is it like
this at all", `docs/architecture/decision-log.md`) stay as prose docs that link decisions.
Small engineering calls may still live as task comments (zanzibar), and can be promoted to a
decision when they turn out to matter.

**Status:** BUILT · PROVISIONAL · DEFERRED · SUPERSEDED · REJECTED (v0.5: rejected approaches
are decisions with `reopen_if:`, so "what was rejected that touches X" is a query).

**Links:**
- `supersedes` / `superseded by`;
- `relaxes` / `narrowed by` (adhoc);
- `creates / amends / retires: S-n, C-n`. These feed the census and trace-sync, **not** a
  freshness guard (P13).

**Amendments** are dated blockquotes (audio-workspace `> **AMENDED …**`), never edits to the
body.

**Negative results** go in their own section: *"Built and rejected … Do not re-derive these."*
(nmd, adhoc). Each entry says what was tried, the evidence, and what would justify reopening
it. peass `ARCHIVE.md` keeps "Closed investigations (do not reopen)". In v0.5 they are
`decision_status: REJECTED` records with `reopen_if:`; the generated index lists them in their
own group, which keeps the "do not re-derive" section as a view.

**A generated index**: in v0.5 an OKF `docs/decisions/index.md` (no frontmatter, list shape,
§9.3) built **from frontmatter**, grouped by status and tag. Because nothing parses prose, its
check is byte equality with a regeneration; the **content-from-a-cutoff-id** check (G-D6) is
needed only for migrated historical entries (audio-workspace `bin/decisionsIndex.mjs` is the
prior art for the v0.4 form).

**No period splits.** One file per decision has no single-file cap to hit. The growing thing is
now the index (DR11); one line per decision keeps it small, and superseded decisions can
collapse into a group.

**Existing single-file logs** keep working through a read adapter until migrated. Migration
keeps every id, so `D-157 §5` citations survive; `decisions.md#anchor` links break (§11.4).

### 6.6 Delegation and build rounds

**Reading and auditing** (global `CLAUDE.md § Delegation`):
- verdicts plus `file::symbol` evidence, never dumps;
- each agent persists incrementally to its own file;
- check the file exists on return, and persist on receipt if it doesn't;
- `Explore` cannot persist;
- agents audit; the session decides.

**Build rounds** (audio-workspace `AGENTS.md`, `.claude/workflows/`, the
`wds-slice.workflow.js` flow):
1. map;
2. plan, with a critic;
3. BDD: criteria first, `planned`;
4. build in waves with **disjoint file ownership**, and **no fan-out on a dependency chain**;
5. integrate, with sabotage;
6. adversarial review through several lenses;
7. flip the statuses.

No `git stash`. Workflows are tracked files.

**Model choice** is per-repo config (§8.0), not prose here.

### 6.7 Promotion and demotion

| From | To | When |
|---|---|---|
| owner words in chat | story, decision, or question answer | immediately (§6.2) |
| scratch | evidence doc | the same hour |
| evidence | decision | when a conclusion is reached |
| decision | contract | when it becomes a durable rule (the contract keeps a pointer) |
| a lesson about method | runbook | at clean close |
| memory | contract (global or repo) | when the lesson proves general |
| baton or pause block | board task | after two sessions, by housekeeping (§6.11) |
| closed board item | ledger line; the item file stays in place with `state: closed` (v0.5; v0.4 moved it to `closed/`) | at close |
| a component over its cap | archive with a redirect table | when the guard warns |
| ACTIVE-PLAN doc | FROZEN | when its item closes (freeze when it lands) |

### 6.8 Push and CI

From global `CLAUDE.md § Git`:
- gate before every push;
- push only with permission;
- a background CI watcher for every push, keyed on the commit hash; the push is not done until
  the watcher reports;
- the watcher only watches.

**A push hold**, when the owner imposes one, is a single line at the top of the contract
naming the hold and where it is recorded (audio-workspace `CLAUDE.md` line 3).

### 6.10 Humans working outside the rituals

The owner works mainly through Claude remote control, but the repo **must not become
dysfunctional for someone using plain git or writing code by hand** (owner, 2026-10-07).
Humans are never required to perform rituals. The agent sessions absorb the cost:

1. **Agent commits carry a trailer** `Session: <key>`. Commits without one are **foreign**.
2. **At session start, reconcile foreign commits** since the newest ledger entry:
   - write a ledger entry `kind: foreign` summarising them (author, what changed);
   - run the tier-1 trace-check over them (criteria or prose they may have staled);
   - inbox-check them for intent: a commit message or doc edit that states a feature or
     decision is recorded as a story or decision, `via: commit <sha>`, attributed to its
     author.
3. **Everything a human needs is readable without an agent:**
   - the banner and board in plain markdown;
   - the per-session `summary:` in the ledger;
   - guards runnable with one command (e.g. `make context-lint`) with readable reds that name
     the remedy (§8.0).
4. **A human's red guard is the agent's job.** A human commit that breaks a doc guard is not
   reverted; the next session fixes or reconciles it and records that in the ledger.

### 6.9 Bootstrap (a new repo)

1. The owner gives, in chat: a charter (about a page), the first stories, and any mandates.
2. The agent scaffolds the layout (§10), installs the record engine (§8.0) at a pinned version, and
   writes the per-repo config, with a provenance note on every cap.
3. The agent drafts criteria and shows a digest, opens questions, and builds the first board.
4. First clean close: the guards are green, and the ledger entry is `kind: close`.

### 6.11 Housekeeping (v0.5)

Housekeeping is the repair pass for things that should happen and keep being forgotten.
zanzibar forgot to raise its task floor three sessions running before `task.py new` did it
itself (`tasks/config.json::_provenance.min_tasks_parsed`). The owner wants it done by tools so
nothing is broken by hand (2026-10-08), and wants a script or MCP tried **before** edit
subagents: *"if a script (or mcp) might work lets try that out first"*.

**Three tiers; most housekeeping needs no model:**

| Tier | Who | Does | Example operations |
|---|---|---|---|
| 0 | **a no-model script** (`process:housekeep`) | deterministic repairs | stamps; floor ratchets; regenerated indexes; flagging and converting expired batons; turning stale `kind: open` stubs into `kind: abandoned` plus a baton; stamping `last_asked` from `asked:` receipts |
| 1 | **small agents restricted to the engine's `hk_` operations** | reading unstructured text, writing through typed operations | commits since the last session → dated task comments; clearing a pause record whose paths are now committed; reconciling foreign commits (§6.10); spotting owner words not yet recorded (reported, not written) |
| 2 | **the main session** | every judgement | ranking, criteria, task bodies, answers, closes without evidence |

**The rule: housekeeping carries out intent that is already recorded somewhere; it never forms
new intent** (P11 exception).

**Closing is the hard case, not a simple one.** zanzibar's tool deliberately offers no
`--mechanical` close: *"no tool is allowed to auto-close, so a --mechanical close would only
ever be a human quietly declining to record that they closed something"* (`scripts/task.py`,
`write_op`). Under the rule, `hk.close(id, commit)` closes only when that commit **really
carries** `Closes: <id>` (the engine checks git, not the agent's word) or the session's ledger
entry names the item as closed, and it cites that evidence in the close message (G-W9).
Otherwise housekeeping proposes the close and the session approves the batch.

**When:**
- **At session start: reconcile** what happened since the last session: foreign commits,
  other sessions' leftovers, stale open stubs, overdue questions. A SessionStart hook can run
  tier 0 (§6.1).
- **Just before close: carry out** what this session recorded but did not finish (§6.3 step
  6a).

**Safety:**
- every `hk_` write is stamped `--mechanical` with its actor, is logged, and lands in its own
  commit by path with a `Session:` trailer, so `git revert` undoes it;
- writes per run are capped (G-W10);
- the run's report **is** its operation list, and it goes into the owner digest (§5.6);
- the run takes the engine lock, because another session may be live in the same tree.

**Tool restriction is what makes "cannot break things by hand" true.** A tier-1 agent gets no
`Edit`, `Write` or `Bash`; its tool allowlist names only the engine's `hk_` MCP tools (§8.0.2).
Fencing `Bash` to one script through permission rules is weaker, because those rules apply to
the whole session.

**Edit subagents** (agents that hand-edit files on the session's behalf) were considered and are
deferred: try the script and MCP first (owner, 2026-10-08).

---

## 7. Record layer details

### 7.1 Session ledger

- **One entry per session, without exception:** `kind: close | pause`, plus `foreign` for
  reconciled human commits (§6.10). v0.5 adds `open` (the stub `session.start` writes, §5.5)
  and `abandoned` (a stub housekeeping found never closed).
- **Written by the engine** (v0.5): `session.start`, `session.close`, `session.pause`. The
  receipts are checked when the entry is written, as well as by the gate.
- Append-only, newest first, **in its own file**, keyed by session key. *Open question Q-H:*
  one file per entry (no two sessions append to one file; a generated rollup for reading)
  versus the existing single file under the engine lock. zanzibar has 428 citations of
  `session-log.md` and `spec-deviations.md` together (grep, 2026-10-07), so an existing single
  file stays readable either way.
- Receipts are machine-checked (zanzibar `check_session_receipt`).
- Rotate by period when it passes its cap; the current file indexes the periods.
- Counter-examples: intervals (38 entries inside a 62 KB HANDOFF); adhoc (session log ≈ half of
  HANDOFF).
- **Not an OKF `log.md`** (§9.3): it is a session journal, not a concept changelog.

### 7.2 Evidence and plan docs

- One per item or investigation, dated, with its liveness declared near the top. While
  ACTIVE-PLAN, corrections are appended at the top with dates. It freezes when the item lands.
- *"The task row is the index, the doc is the body … `show <id>` alone must be enough to
  resume"* (zanzibar).
- An author's-voice TODO in a frozen doc is a declared hole, not an instruction (zanzibar
  `docs/README.md § 2`).

### 7.3 Archive

- `git mv` the material, never repair it.
- First line: `ARCHIVED YYYY-MM-DD`.
- One redirect table per archive directory (adhoc `docs/archive/README.md § Two rules`;
  audio-workspace `docs/archive/README.md`: *"Nothing in here is repaired, extended or kept
  current"*).
- Archive headings act as the index (audio-workspace `docs/archive/HANDOFF_ARCHIVE.md`,
  `## Pruned from HANDOFF.md on <date>`).

### 7.4 Invariants vs unverified hazards

- **Invariants:** durable, load-bearing traps. They change only when the code does
  (audio-workspace `docs/invariants.md`). LIVING, part of the rules layer. They carry
  `stale_after` only if they are about something external.
- **Unverified hazards:** volatile suspicions ("do NOT fix blind"). They live in the note or on
  the board. When resolved, they either become an invariant, a fix plus a ledger line, or are
  dismissed with a ledger line.

### 7.5 Runbooks

Gate, sabotage procedure, fan-out, release, test baselines. They hold **method**, which
survives when the status around it is archived. Examples:
- zanzibar `gate-runbook.md`, `sabotage-procedure.md`, `subagent-fanout-runbook.md`;
- audio-workspace `docs/testing-runbook.md`: one dated baseline per suite, and an
  *unexplained* drop is a blocker (D-255, `runbookShape`).

---

## 8. Tooling and verification: the record engine and the guard catalogue

### 8.0 Packaging: the record engine

- **One versioned package, the record engine** (the dedicated repo, §12 Q5: `context-engine`,
  created 2026-10-08), plus a per-repo
  config, e.g. `context.toml`. v0.4 called it the lint package; in v0.5 the same package also
  owns record writes (§8.0.1–8.0.3). The config holds:
  - enabled guards;
  - paths (the routing map's mapping of components onto files; v0.5 moves this mapping here
    from `docs/index.md`, because OKF fixes `index.md`'s shape, §9.3);
  - the record kinds and their schemas (§8.0.1);
  - caps;
  - cutoff ids;
  - model choices for background agents;
  - the housekeeping write budget and the stale-stub window.
- **Every tuned value carries a provenance note: MEASURED or JUDGEMENT, with the method and
  what would make it wrong.** A test refuses values copied from spec examples (zanzibar
  `tasks/config.json::_provenance`; `test_tasktool.py::test_shipped_config_is_measured_not_an_example`).
- **G-D0:** the contract's `framework: <version>` matches the installed package.
- **Upgrade ritual:** bump the version, run the lint, fix the reds, write a ledger line.
- **Existing repos keep their own check numbers.** The package maps its ids onto them and
  never renumbers them (P3).
- **Tools that refuse name the remedy.** Every red says what to do.
- **Every guard docstring says what it deliberately does not check** (P7).

### 8.0.1 Record kinds and change modes (v0.5)

The engine is **one core with several record kinds, not a bigger task tool.** zanzibar's
`scripts/task.py` is already 4,254 lines (`wc -l`, 2026-10-08). The core does OKF read and write, id
allocation under a lock, the operation log with session stamps, write-time refusal, and the
lint framework. Each kind is a small schema in config, with one of three change modes (P2):

| Change mode | Kinds | The engine enforces |
|---|---|---|
| **append-only** | decisions, stories, deviations, ledger entries | a `body_sha` over the original body; `amend` appends a dated block and is the only body change (`decision.correct` is the logged exception, Q-I); G-D10 recomputes the hash |
| **replaced body, tool-owned frontmatter** | tasks, owner questions (`ASK-n`) | frontmatter changes only through operations carrying the session key; bodies are hand-edited or set one section at a time (`section.set`) |
| **stamped** | batons, pause blocks | a session key on creation; expiry after two sessions; housekeeping converts the expired ones |

**Not record kinds:** criteria (they live in `.feature` files and test annotations, and the
trace guards read them in place); the charter, contract, invariants, runbooks and evidence
docs (prose, checked by the doc guards); verification state (zanzibar `gate_status.py` owns
it). The banner is prose, but the engine stamps its key and guards its write (§5.5).

**Every kind round-trips unknown frontmatter keys,** as OKF asks (§9.3), so a key a human adds
by hand survives the next tool write.

### 8.0.2 Three entry points, one library

| Entry point | For | Notes |
|---|---|---|
| **CLI** | humans, Bash, the gate | zanzibar `task.py` today |
| **MCP server** | agents | a thin wrapper: each MCP tool calls the function its CLI subcommand calls |
| **Housekeeping script** | the gate, hooks, §6.11 tier 0 | no model; actor `process:housekeep` |

**The MCP server is local and per session; nothing has to be run by hand.** It uses the
**stdio** transport: a `.mcp.json` committed at the repo root names a command (the repo env's
interpreter and the wrapper script), Claude Code starts it as a child process when a session
opens in the repo and ends it with the session. There are no ports, and each concurrent session
gets its own process. Claude Code asks once before trusting a server defined by a repo.
- **The interpreter path is machine-specific** (bare `python` is broken on this laptop; global
  `CLAUDE.md § Python environments`). Use an environment variable in `.mcp.json` rather than a
  hard-coded path (UNVERIFIED: that `.mcp.json` expands `${VAR}`).
- **A server process is not a framework session.** The process lives as long as the Claude
  Code process, and a `/clear` probably leaves it running (UNVERIFIED). So a session begins
  with an explicit `session.start`, never with the process start.
- **Subagents probably share the parent's server connection** (UNVERIFIED), so the actor is
  recorded per call, chiefly through the `hk_` prefix, not per process.

**Design rules for the MCP surface; the goal is context, not convenience:**
1. **Edits are operations, not text replacement:** set a field, append a comment, replace one
   named section. No read-modify-write.
2. **Every write returns one line:** what changed and the new state.
3. **Every read returns a slice:** one-line rows, one section, or the newest N log entries,
   each with a hard size cap and a pointer to the rest.
4. **Every refusal names its remedy** (§8.0).

**Tools:**

| Group | Tools |
|---|---|
| Session | `session.start`; `session.close(summary, rows, receipts)`; `session.pause(rows, deferred)` |
| Orientation | `orient()`: the §6.1 read in one capped response |
| Batons and pauses | `baton.add`, `baton.done`, `pause.open`, `pause.resume` (§5.4) |
| Banner | `banner.set(text, seen_hash)` (§5.5) |
| Tasks | `find`, `show(id, section, head)`, `new`, `set`, `promote`, `dep`, `comment`, `touch`, `close(msg)`, `reopen` (zanzibar `task.py` today); `section.set(id, name, text)` (new) |
| Owner questions | `ask.new`, `ask.raised`, `ask.later`, `ask.answer` (§5.3) |
| Intent and record | `story.record`, `story.amend`; `decision.new`, `.amend`, `.correct`, `.supersede`, `.link`, `.find`, `.show`; `why(target)` (§6.5) |
| Checks | `lint(scope)`: failures only, each with its remedy |
| **Housekeeping (`hk_`)** | `hk.comment(id, text, commit)`, `hk.stamp`, `hk.ratchet`, `hk.regen_index`, `hk.expire_batons`, `hk.close(id, commit)` (checks the `Closes:` trailer in git, §6.11) |

The `hk_` set has its own prefix so a housekeeping agent's allowlist can name only those tools
(§6.11). zanzibar's `task.py` already has the seed of this: a `--mechanical` flag on `set`,
`dep`, `comment` and `touch` (*"housekeeping write: bump `updated` only … For TOOLS"*), and
none on `close`.

**Out of scope for the MCP:** `.feature` files and code; gate runs; prose documents; and
every judgement: the session makes it by calling an operation, the tool never makes it.

### 8.0.3 Trial before adoption

Following §5.2's adopt-by-trial rule. **Build first:** the MCP wrapper over zanzibar's existing
`task.py` operations; `orient`; `session.start` / `close` / `pause`; baton and pause records;
the tier-0 housekeeping script. **Pre-registered rubric:** context spent on session start and
clean close against the same rituals done by hand (the `read:` receipt is the existing
measure), plus collisions or lost blocks across two concurrent sessions. Decisions as records
follow once the core holds.

### 8.1 Intent guards
- **G-I1:** every charter goal has at least one story; every story names at least one goal.
- **G-I2:** every story has an actor, a date and a status from the vocabulary. `unconfirmed`
  requires `actor: agent (reconstructed from …)`.

### 8.2 Trace and existence guards
- **G-T1:** every `live` story has a criterion, or is `unspecified` with a board task.
- **G-T2:** every `tested` or `manual` criterion is claimed by a test or driver, and every
  annotation resolves (audio-workspace `featureCoverage.test.ts`, `specBddFreshness.test.ts`,
  `liveDriverCoverage.test.ts`).
- **G-T3 (existence, against code):**
  - every file, `file::symbol` and route named in the **normative** text of a story, criterion,
    law doc or invariant exists in the code;
  - history notes (`*HISTORY —*`, blockquotes) are exempt;
  - (audio-workspace `requirementsFreshness.test.ts`, D-173 / D-174).
- **G-T4:** structural-claim anchors resolve and their body hashes match the pins; re-pinning
  is an explicit, reviewed act (zanzibar `anchor_check.py`, `claim_rot.py`).
- **G-T5 (mutation per criterion):**
  - runs as a scheduled routine, or as the one slow background job, keyed on the hash, with
    results in a tracked evidence doc;
  - it does not apply to formal theorems, where G-T4 substitutes;
  - generalises intervals `tools/sabotage.py`.
- **G-T6:** every criterion's story or decision ref resolves, and its actor matches the
  source's.
- **G-T7:** every `deviates` criterion references a deviation-register entry; every `retired`
  one references a decision.

### 8.3 Doc guards
- **G-D1:** per-component caps (lines, bytes, line width), set in config with provenance.
  Prior art:
  - audio-workspace `claudeMdShape.test.ts`: 40,000 total, and each authority-table row ≤600;
  - audio-workspace `handoffShape`, `runbookShape`;
  - zanzibar `MAX_LINES`.
- **G-D2:** ids are unique within their series and never reused. zanzibar `task.py new` scans
  open and closed items, and `tasks/retired-ids.txt` exists, deliberately empty.
- **G-D3:** every link and `file::symbol` resolves, case-exact (audio-workspace
  `docLinks.test.ts`; zanzibar `anchor_check.py`).
- **G-D4:** every doc declares its liveness near the top. zanzibar's
  `check_frozen_banners` uses `LIVENESS_WINDOW = 10` for history directories; which
  always-living docs are exempt is zanzibar's open row `HS-5`.
- **G-D5:** derivable counts appear only in generated blocks. A typed number needs one of
  zanzibar's four allowed forms (P5).
- **G-D6:** generated indexes match a regeneration **and** are content-complete from a
  configured cutoff id. v0.5: an index built from record frontmatter needs only the
  regeneration check; the cutoff check remains for indexes that still parse prose.
- **G-D7:** signal budgets: ⚠ ≤N per file, a bold-caps budget, retired glyphs (zanzibar
  `handoff_lint.py` `WARN_BUDGET`, `check_bold_caps`, `check_no_stars`; `docs/README.md § 4`
  *"Signals rank only if they are bounded"*).
- **G-D8:** the note's banner carries exactly one session key (the layer detector); there is no
  session history in the note; an inline board, if present, starts within the first K lines.
- **G-D9:** tuned config values carry a provenance note, and spec-example values are refused
  (§8.0).
- **G-D10 (v0.5):** every append-only record's `body_sha` matches its body above
  `## Amendments`. This turns "append-only" and "owner words are verbatim" into refusals.
- **G-D11 (v0.5):** each configured OKF bundle directory is conformant: every non-reserved
  `.md` has frontmatter with a `type`; every `index.md` has no frontmatter (except an
  `okf_version` key at the bundle root) and the list shape; `status` uses only `draft`,
  `stable` or `deprecated`, and agrees with the record's own state key (§9.3).

### 8.4 Working-state guards
- **G-W1:** the banner's key is ≥ the newest `kind: close` ledger key.
- **G-W2:** at most N consecutive `kind: pause` entries.
- **G-W3:** no baton or pause block older than two sessions (zanzibar `TK97`, unbuilt). With
  baton and pause records (v0.5) this is a one-line check, and housekeeping repairs it.
- **G-W4:** closed ids do not appear on the open board. v0.5: `state` and the derived OKF
  `status` agree on every task, and the board query reads `state`.
- **G-W5:** tier caps: NOW = 1, NEXT ≤ 5.
- **G-W6:** ledger receipts are present and well-formed, including `asked:` when a NEXT
  question exists (zanzibar `check_session_receipt`).
- **G-W7:** task frontmatter changed only by the tool. `moved` is consistent with the
  `--session` op log. v0.5: extended to every record kind's tool-owned frontmatter.
- **G-W8:** no clean close while an overdue owner question (§5.3) has not been raised this
  session. This is the nag that gives the owner a tracker.
- **G-W9 (v0.5):** every `--mechanical` close cites its evidence: a commit whose message
  carries `Closes: <id>`, or a ledger entry naming the item. `hk.close` checks it at write time;
  the lint re-checks it at rest.
- **G-W10 (v0.5):** housekeeping writes per run stay within the configured budget (the value,
  with provenance, is open question Q-K).
- **G-W11 (v0.5):** no `kind: open` ledger stub older than the configured window without a
  matching `close`, `pause` or `abandoned` entry.

### 8.5 Verification-state guards
- **G-V1 (run ledger):** which gate phases passed on which content tree id. A commit or push
  can require a green row for the current id. Examples:
  - intervals `tools/gate.py status --require commit|push`, pinned by
    `tests/test_gate_ledger.py`;
  - zanzibar `.gate-runs/` plus `gate_status.py`, keyed per phase, so a docs-only edit costs
    only the docs phase.
- **G-V2 (floors):** raw totals with zero headroom plus an automatic ratchet; instrument floors
  keep declared headroom (P7). Examples:
  - zanzibar `min_tasks_parsed`, `ratchet_min_parsed`, `MIN_TESTS_ALL`;
  - audio-workspace one baseline per suite.
- **G-V3:** a lock on gate runs and background-agent runs for the same tree (zanzibar
  `scripts/gate_lock.py`).
- **G-V4:** exit-code hygiene: no piping through `tail`/`tee`, one phase per command, logs from
  `mktemp` (zanzibar `CLAUDE.md § The five standing footguns`).
- **G-M1:** the doc and lint tools are pinned by their own tests inside the gate.

---

## 9. Storage, persistence and OKF

### 9.1 What persists

> **If this were lost, would it cost owner attention or a re-measurement?**
> Yes → it persists, tracked. No (it can be regenerated from tracked state) → it is ephemeral.

### 9.2 Tiers

| Tier | What | Persistence | Format |
|---|---|---|---|
| **T0 ephemeral** | context window, `.scratch/`, sync reports, generated maps (coverage → code) | none | anything |
| **T1 working state** | orientation note, the board *view* and ranking fields, baton and pause records (one file each, v0.5), unverified hazards | tracked, replaced or stamped; git is the history | our own schemas; baton and pause records are OKF files (`type: Baton`, `type: Pause`) so the engine has one reader |
| **T2 durable knowledge** | charter, stories (incl. PRDs), criteria, law, decisions, evidence, invariants, deviations, runbooks, archive, **task records** (open and closed: body, comments and updates, op log, links to decisions) | tracked, append-only / LIVING / FROZEN | **OKF-conformant**, with our stricter profile. Task frontmatter stays **tool-owned**: the tool emits `type: Task` and *maps* its own fields onto OKF keys, rather than an OKF overlay duplicating them |
| **T2′ ledger** | session ledger | tracked, append-only | our own format, with OKF-style date headings |
| **T3 cross-project** | global contract, memory | `~/.claude` | memory files already have OKF's shape: one fact per file, frontmatter with a type, an index file. A redesign is planned |

### 9.3 How OKF is used

OKF v0.2 (`GoogleCloudPlatform/open-knowledge-format`, `SPEC.md`):

| Our need | OKF feature | Our profile adds |
|---|---|---|
| component type | required `type:` (`Story`, `Criterion`, `Decision`, `Evidence`, `Invariant`, `Deviation`, `Runbook`, `Charter`) | — |
| identity | concept id = path minus `.md` | **`id:`** extension: stable series ids that survive moves (P3) |
| routing map / progressive loading | `index.md` per directory | **generated**, and checked by G-D6; v0.5: the component → path mapping lives in `context.toml`, because `index.md`'s shape is fixed (§9.3.1) |
| concept changelog | `log.md` | **generated** from decisions' `creates/amends/retires`; this is *not* the session ledger |
| who and when | `generated: {by, at}`; actors `human:<id>` / `<producer>/<version>` | `actor:` in our vocabulary; the model id goes into `generated.by` |
| owner sign-off | `verified: [{by: human:owner, at}]` → "human-reviewed" tier | distinct from `criterion_status: tested` |
| no longer current | `status: deprecated` | **one mapping:** SUPERSEDED decision, `retired` story or criterion, FROZEN archive item, closed task (v0.5) → all carry `status: deprecated`, derived by the engine from the record's own state |
| freshness | `stale_after:` (the spec defines when a concept is stale; it does not prescribe what a reader does) | **our profile refuses** an expired `stale_after` on a live item. Bound to `manual` criteria (re-run the driver by date) and external invariants |
| provenance | `sources:` with ids, cited as footnotes | evidence docs cite their runs |
| extensions | readers SHOULD preserve unknown keys and MUST NOT reject them | `supersedes`, `relaxes`, `retires`, `criterion_status`, `test`, `liveness`, `sign-off` |
| attested results (later) | `type: Attested Computation`: a deterministic attester checks a receipt | candidate format for G-V1 run-ledger rows |

**What OKF does not cover:** ranking, owner-question rationing, stamped baton and pause blocks,
writes from several sessions, replace-vs-append discipline, rituals, guards. OKF readers are
deliberately permissive; our profile is strict on top of conformant files.

#### 9.3.1 Constraints read from the OKF v0.2 spec (READ, 2026-10-08)

Read from `SPEC.md` at `GoogleCloudPlatform/open-knowledge-format`, version 0.2, as of commit
`0b87c52c6ef999286c745e19998fdfcd03d5dbee` (the newest commit touching `SPEC.md` on
2026-10-08, dated 2026-08-21).

| The spec says | What it means for us |
|---|---|
| **`status` is a defined lifecycle key: `draft` \| `stable` \| `deprecated`; absent means `stable`** (§5.4). `deprecated` = "kept for links and history; no longer current" | Our own states must not go into `status`. Tasks carry **`state: open \| closed`** (an extension key); the engine derives `status`: absent while open, `deprecated` once closed. Superseded decisions, retired stories and criteria, and frozen archive items keep the v0.4 mapping to `deprecated`. G-D11 checks the two keys agree. |
| **Concept id = the file's path minus `.md`** (§2) | Closing in place (§5.2) makes task ids stable as OKF ids. zanzibar never renames a task file on retitle (`scripts/task.py::slugify`: *"Generated ONCE at `new` and never updated"*); the move to `closed/` in `task.py::op_close` was the only path change. The `id:` extension stays, for series ids that survive a migration. |
| **Every non-reserved `.md` in a bundle needs frontmatter with a non-empty `type`** (§11) | **A bundle is a chosen set of directories, not the repo root;** otherwise README, CLAUDE.md and HANDOFF would all need frontmatter. Non-record files inside a bundle directory need a `type` too: zanzibar's `tasks/README.md` and `tasks/BANNER.md` (today excluded by name, `task.py::NON_TASK_MD`) would carry e.g. `type: Readme`, and the exclusion becomes a filter on `type`. |
| **`index.md` and `log.md` are reserved at every level; `index.md` has no frontmatter (except `okf_version` at the bundle root) and a fixed list shape** (§3.1, §8) | v0.4's `docs/index.md` (routing map plus a component → path table) does not fit. The mapping moves to `context.toml` (§8.0); `index.md` is a plain generated listing. |
| **`log.md` headings must be `YYYY-MM-DD`** (§9) | Session keys like `2026-10-07c` cannot be log headings. Confirms §7.1: the ledger is not an OKF `log.md`. |
| **Actors: `<producer>/<version>`, `human:<id>`, `process:<id>`** (§7); trust tiers key off the `human:` prefix (§5.3) | Agent writes carry `claude-code/<model-id>`; the housekeeping script is `process:housekeep`; owner sign-off is `verified: {by: human:<id>}`. |
| **`stale_after` is an absolute instant** (§5.5) | Baton expiry counts sessions, so it is an extension key; `stale_after` may serve as a time backstop. |
| **Producers MAY add keys; consumers SHOULD preserve unknown keys when round-tripping and MUST NOT reject them** (§4.1, §11) | The engine round-trips unknown keys (§8.0.1). |
| Links: bundle-relative `/…` is recommended (§6.1) | Record links use bundle-relative paths, stable when files move within a directory. |

### 9.4 Later

All derived and disposable; the files stay the source of truth:
- vector search over T2 and T3;
- a source graph: the code symbol graph, plus OKF links, plus the generated coverage map, for
  impact analysis;
- a memory architecture for T3, including the path-case split in memory directories, which the
  owner deferred on 2026-10-07.

---

## 10. Layout for a **new** repo

Existing repos map instead of moving (§11.4).

```
AGENTS.md                  # workflow conventions (how agents work), read first
CLAUDE.md                  # product contract: mandates, gate, footguns; push-hold line on top; framework: <version>
HANDOFF.md                 # orientation note: banner (one key), next session, generated pointer to open batons/pauses
context.toml               # framework config: guards, component → path map, record kinds, caps (+ provenance), cutoffs, models
.mcp.json                  # v0.5: starts the engine's stdio MCP server per session (§8.0.2)
docs/
  index.md                 # generated OKF listing (no frontmatter, list shape)
  charter.md
  law.md                   # optional: NFRs / data-model law with invariant → test map
  stories/S-n-<slug>.md or issues/<slug>/PRD.md   # owner's voice (records, or PRD sections mapped in context.toml)
  criteria/ or features/*.feature
  decisions/D-n-<slug>.md  # v0.5: one record per decision; generated index.md
  deviations/              # v0.5: append-only records (+ optional generated open-gaps view)
  invariants.md            # durable traps
  runbooks/                # method
  evidence/<id>-<topic>-<date>.md
  ledger/                  # session ledger (single file or one entry per file: Q-H)
  archive/README.md        # redirect table
tasks/                     # flat; open and closed side by side, `state:` in frontmatter (§5.2)
  batons/                  # v0.5: baton and pause records (§5.4)
.claude/skills/, .claude/workflows/, .claude/agents/   # project skills, tracked build workflows, the hk agent
.scratch/                  # gitignored crash bag
```

---

## 11. Adoption

### 11.1 Minimum set for a new repo

**Components:**
- charter;
- stories;
- criteria with statuses;
- contract;
- orientation note with an inline board (including question rows);
- baton and pause blocks;
- decision log with negative results;
- ledger in its own file;
- the scratch rule.

**Rituals:** intake, start/resume, clean close, pause, bootstrap.

**Tooling (v0.5):** the record engine's CLI and the tier-0 housekeeping script. The MCP
server is not in the minimum set until the §8.0.3 trial reports.

**Guards:** G-D0, G-D1, G-D2, G-D3, G-D8, G-I2, G-T1, G-T2, G-W1, G-W2, G-W4, G-W6; v0.5 adds
G-D10 (append-only hashes), which is free once records exist.

### 11.2 Add when needed

| Trigger | Add |
|---|---|
| a second concurrent session works the board | board size 2 (one file per item) |
| the note layers, or sessions read it for item detail | board size 3 (tree plus CLI), adopted by trial |
| a baton survives two sessions | G-W3 |
| the repo measures things | evidence docs; runbook baselines; G-D5 |
| traps accumulate | invariants doc; G-T3 over it |
| the code deliberately departs from the spec | deviation register; G-T7 |
| "did the gate pass on this tree?" keeps coming up | G-V1 |
| a component hits its cap | archive plus redirect table |
| the spec makes structural claims | G-T4 |
| the suite is large | G-V2 floors; G-T5 mutation |
| cross-cutting NFRs or data law | law doc with an invariant → test map |
| parallel building | build-round protocol (§6.6), tracked workflows |
| sessions spend context reading files in order to edit them | the engine's MCP server (§8.0.2), after the §8.0.3 trial |
| housekeeping needs reading, not just rules (commit → task comments, foreign commits) | tier-1 housekeeping agents restricted to `hk_` tools (§6.11); G-W9, G-W10 |
| `session.start` stubs are in use | G-W11 |
| a bundle directory is declared OKF | G-D11 |

### 11.3 Where each repo stands (2026-10-07)

| Repo | Strongest | Biggest gaps against this framework |
|---|---|---|
| zanzibar | board as a query with read-first/traps, `ASK-n` rows plus receipts, structural pins, floors with ratchet, doc lints, gate phases | no charter or story layer; CLAUDE.md uncapped; banner layering (14 lines, up to 3,762 chars); TK97 unbuilt; HS-5 undecided |
| audio-workspace | PRD → scenario → test, existence guards, shape guards, build rounds, AGENTS/CLAUDE split | PRD → scenario link unguarded (G-T6); ~650 lines of history above the board; decision index content unchecked; CLAUDE.md and runbook at their caps |
| intervals | run ledger, sabotage, property fuzzing, project skill | no doc guards; banner used as a log; decisions spread over plans and HANDOFF; no charter (`v2-plan.md` has a design and a decision log, but no goals) |
| adhoc | decision actor tags and relation links, project brief, results docs | no doc guards; session log inside HANDOFF; method detail in CLAUDE.md |
| peass | frozen baseline, "do not reopen" archive | two stale process-state blocks; no ledger; no guards |
| nmd | negative-results table, parity tests | decisions have no ids; tests cite HANDOFF item numbers unchecked; stale sections |

### 11.4 Migration (existing repos)

- **Charters are reconstructed by an agent and brought to the human for review** (owner,
  2026-10-07), from what exists: adhoc `docs/project-brief.txt` and D-18; audio-workspace's
  mandates and `docs/requirements.md § 1`. Tagged `unconfirmed` until reviewed.

- **Map, don't move.** The routing map and `context.toml` map each component onto the repo's
  existing files. Existing ids and check numbers are never renumbered; the package maps onto
  them.
- **Enable guards incrementally.** Each one starts as a warning, with a dated deadline for
  becoming a refusal.
- **Back-filled stories are reconstructions, never the owner's words:**
  `actor: agent (reconstructed from D-n / PRD § / commit …)`, `status: unconfirmed`. The owner
  confirms them through **one batched digest question**, not one question per story.
- Adopt structural changes (board size, ledger rotation) **by trial**, with a single
  revertible cutover commit.
- **Closed-task directories may migrate** (owner, 2026-10-08): `tasks/closed/*` moves into the
  flat `tasks/` once the schema carries `state` and every moved file has `state: closed`.
  "Map, don't move" yields here because the owner prefers one place, and the cost is bounded:
  in zanzibar, 18 tracked files outside `tasks/closed/` cite paths under it (`git grep -l`,
  2026-10-08), and the store already falls back to finding a task by id when a path is wrong
  (`task.py::Store`). **Deferred:** the framework comes first.
- **Single-file decision logs migrate to records the same way, later:** every id is kept, so
  `D-n §k` citations survive; anchor links into the old file break and get a redirect table.
  Until then the engine reads the old file through an adapter.

---

## 12. Owner answers and remaining questions

### 12.1 Answered (owner, 2026-10-07)

| v0.2 question | Answer | Where it landed |
|---|---|---|
| Story form | The owner's input is always free prose, or a bare feature or goal. Only BDD criteria follow templates | §3.2 |
| Research criteria | The research goal is the criterion; all the work (algorithms, literature, references, datasets) moves the repo toward it | §3.3.1 |
| Background agents | Cheap agents do the checks first; on a flag, hand off to a bigger agent, the main session, or the human | §6.1 |
| Pause tolerance | N = 2 | §6.4, G-W2 |
| Where the framework lives | Here in `.scratch/` for now: the goal is to understand and optimise the existing repos. *Superseded 2026-10-08: moved, tracked, into the `context-engine` repo when building started* | header |
| Tasks: working state or durable? | **Durable**, especially with comments, updates and links to decisions | §2 row 11, §9.2 |
| Sign-off | Delegated to the agent → **inform and proceed**; the owner pushes back if needed | §3.3, §5.6 |
| Questions and tasks in one system | Yes, but the agent must ask or nag, because the owner has no other tracker | §5.3, G-W8 |
| Parallel sessions | A goal to work toward | P12, §5.5 |
| One ledger entry per session | Confirmed | §6.4, §7.1 |

Agent decision recorded here, for push-back: **research harness code (metrics, loaders,
scorers, vendored libraries) still gets ordinary tests** (§3.3.1).

### 12.2 Answered in the second round (owner, 2026-10-07)

| Question | Answer | Where it landed |
|---|---|---|
| Who gave a story, with several humans? | (asked by the owner) → recorded explicitly as `actor: human:<id>` plus `via:`; git blame is insufficient | §3.2, §6.5 |
| Research success | Not a threshold but a **direction**: direction, measures, ground truth, frontier, optional targets | §3.3.1 |
| Q-A worktrees | Whatever Claude Code does by default is what will mostly happen; worktrees are fine | §5.5 |
| Q-B cross-repo view | The owner won't read it, but it helps agents nag → a generated question index for agents | §5.6 |
| Q-C channels | Mainly Claude remote control; plain-git users must not be left out → the digest goes into the ledger; foreign-commit reconciliation | §5.6, §6.10 |
| Q-D charters | Reconstruct, then bring to the human for review | §11.4 |
| Q-E cross-repo work | The task lives where the outcome is needed; a pointer row elsewhere | §12.3 |

### 12.3 Still open

- **Q-F. Roles with several humans:** is there one owner per repo who decides goals and
  priorities, with other humans contributing stories, or several humans with equal say?
  *Default: one owner per repo, named in the charter; other humans' stories are recorded
  under their own id, and conflicts go to the owner.*
- **Q-G. Who gets nagged:** only the owner, or every human with an open question addressed
  to them? *Default: only humans who use the remote-control channel get nagged in chat;
  questions for anyone else are left as board rows for them to find.*
- **Q-H. Ledger storage (v0.5):** one file per entry (no shared append; a generated rollup for
  reading) or the existing single file under the engine lock? *Default: single file under the
  lock until the trial shows append collisions.*
- **Q-I. `decision.correct`:** allow logged typo fixes to append-only records, or forbid every
  body change except `amend`? *Default: allow, logged under Amendments (agent proposal).*
- **Q-J. A combined read-only view of all decisions** for reading in an editor? *Default: no;
  the generated index plus `grep` covers it, and a combined file would be a second copy.*
- **Q-K. Housekeeping write budget per run** (G-W10) and the stale-stub window (G-W11): values
  to be measured in the trial, with provenance (G-D9).

**To verify before building (UNVERIFIED claims in §6.1 and §8.0.2):** that SessionStart hook
output is added to the model's context; that `.mcp.json` expands environment variables; whether
`/clear` restarts a stdio MCP server; whether subagents share the parent's MCP connection.

### 12.4 Answered in the third round (owner, 2026-10-08)

| Question | Answer | Where it landed |
|---|---|---|
| How much goes into the task tool? | Every record-shaped component; the tool reads and writes OKF. Hand-edited files are fine, but **context bloat** is the concern tools should solve: *"no need to read and reread every edit"* | §0.2, §8.0 |
| Containers | *"that place needs to have the space for the thing and checks that run on the things inside"* | P7 |
| Housekeeping | A run at session start or before close, by small agents that use tools so they cannot break things by hand. Edit subagents were considered; **try a script or MCP first** | §6.11 |
| Can the MCP server be local, per repo, per session? | (asked by the owner) → yes: stdio, started by Claude Code from a committed `.mcp.json`, ended with the session | §8.0.2 |
| Moving closed tasks | Not needed; a status plus a tool to list and sort is fine. SQLite is less friendly to humans and git. `closed/` may migrate once the schema carries the state; *"one place for everything feels cleaner"*; framework first, migration later | §5.2, §11.4 |
| OKF `status` | (owner asked the agent to check) → reserved for `draft \| stable \| deprecated`; tasks use `state:` and the engine derives `status` | §9.3.1 |
| Decisions | Handled by the tool, as OKF records | §6.5 |
| Batons | (asked by the owner) → yes, the engine owns baton passing, as records | §5.4 |

---

## 13. Changes from v0.1, and where they came from

| Change | Source |
|---|---|
| Owner questions are board rows (`ASK-n`) with a NEXT nag and an `asked:` receipt, not a separate queue; the 🧭 lesson restated | zanzibar review §1, §5.1 |
| A pause writes a short ledger entry (`kind: pause`) plus a committed pause block; it defers gate, commit and re-rank. G-W2 counts pause entries | zanzibar review §3; fable 1 |
| Several-writer rules: key minted at write-back, re-read before replacing, keyed blocks carried forward, prompt commits | fable 1 |
| Owner words recorded as item 0 of pause and clean close | fable 4 |
| Session start: batons first, board query, `show`, read-first; note on demand; the `read:` receipt measures cost | zanzibar review §5.3 |
| Task schema (brief, Traps, Read first); frontmatter via tool with `--session`, bodies by hand; three board sizes adopted by trial; concurrency is the first trigger | zanzibar review §5.4; fable 17 |
| `tested` (test status) vs `verified` (owner sign-off); criteria live by default; `sign-off: required` opt-in | fable 2 |
| Intake classification: behaviour → story, choice → decision | fable 3 |
| Stories as PRD sections with OWNER/AGENT provenance; G-T6; criteria census; pin-then-specify; tests may tie to decisions | audio-workspace review §5.3 |
| G-T3 is an existence check against the code; P13 (D-174); the D-173 lesson restated (both layers rotted; the cause is prose naming symbols); DR3 semantic drift declared unguarded | audio-workspace review §1, §5.1–2 |
| The `manual` status direction fixed (the driver declares the tie) | audio-workspace review; citations #52 |
| G-T2 relaxed: claimed criteria and resolving annotations; not every test must name a criterion | audio-workspace review §4; zanzibar review §3 |
| P5/G-D5: derivable counts generated; dated measurements allowed; zanzibar's four forms | both repo reviews |
| P7/G-V2: raw-total floors with ratchet; instrument headroom; G-M1 meta-tests; G-D9 config provenance | zanzibar review §5.5 |
| Invariants (durable) split from unverified hazards (volatile); Runbooks component; Law/NFR doc | audio-workspace review §5.5; zanzibar review §2.8 |
| P11 qualified: build rounds with disjoint ownership; AGENTS.md/CLAUDE.md split; skills; tracked workflows; push-hold line | audio-workspace review §3 |
| P14 honesty norm; the "who decides" test | zanzibar review §2.3 |
| One versioned lint package, `context.toml`, G-D0, upgrade ritual; bootstrap (§6.9); migration with reconstructed-story tagging (§11.4) | fable 5, 6 |
| "Map, don't move" for existing repos; keep existing ids and check numbers | zanzibar review §3; audio-workspace review §4 |
| Background agents cut to trace-sync and inbox, with lock, ancestry, skip and budget rules; hygiene goes to the gate | fable 7 |
| Minimum guard set revised; G-W3 moved to add-when-needed | fable 8 |
| Change mode separated from liveness; "stamped" added | fable 14; zanzibar review §1 (P2) |
| OKF: the ledger is not `log.md`; `index.md` and `log.md` generated; deprecation mapping; `stale_after` bound; model id in `generated.by`; corrected SHOULD/MUST wording; no overlay on task files | fable 11, 12; citations #105–106 |
| Decision logs may be organised by topic; split by period only when the cap forces it; content check from a cutoff id | zanzibar review §3; audio-workspace review §4 |
| Drift ids renamed `DR`; terms defined; story statuses defined; double guard run explained | fable 15, 16, 18 |
| Citation fixes: P12 (8 files, `578d5f4`); the "three doc warnings lost" source (commit `ea214a5`); "Signals rank only if they are bounded"; HS-5 is an open decision; floor on the whole corpus; D-173 exact quote; 40,000 total / row ≤600; intervals has no goals doc; D-18 parks localization; the template-copy list; the global "audits/deletes" quote; approximate line numbers for live files | `opus-citations.md` |

### v0.2 → v0.3 (owner answers, 2026-10-07)

| Change | Source |
|---|---|
| Owner input is free prose, or a bare feature or goal; templates are for BDD criteria only; goals go to the charter | owner |
| §3.3.1 research repos: the goal is the criterion; work is tasks toward it; the harness is still tested | owner; harness rule is an agent decision |
| Sign-off decided: inform and proceed; `sign-off: required` opt-in; new §5.6 owner digest | owner delegated |
| Questions nagged: `last_asked`, overdue after 5 sessions or 7 days, raised at session start; "later" re-stamps but never answers; G-W8 | owner |
| Background agents: cheap tier-1 checks, tier-2 escalation on a flag to a bigger agent, the main session, or the owner (owner only via the main session) | owner |
| Task records are durable (T2), with tool-owned frontmatter mapped onto OKF; only ranking and the board view are volatile | owner |
| N = 2 pauses; one ledger entry per session confirmed; parallel sessions a goal | owner |

### v0.3 → v0.4 (owner's second round, 2026-10-07)

| Change | Source |
|---|---|
| Stories record `actor: human:<id>` and `via:` explicitly; git blame is not attribution. Several humans → roles in the charter; the "who decides" test routes to the right human | owner question; agent recommendation |
| Research repos: direction, measures with known blind spots, human ground truth, generated frontier, optional targets. Progress = moves the frontier on held-out data without regressing guard measures | owner |
| Shared checkout is the default reality; worktrees recommended for building | owner |
| Session digest written into the ledger `summary:` block; cross-repo question index for agents | owner |
| §6.10 humans outside the rituals: `Session:` commit trailer; foreign-commit reconciliation; one-command guards; a human's red is the agent's job | owner; agent design |
| Charters reconstructed by agents for human review; cross-repo task ownership | owner |

### v0.4 → v0.5 (owner's third round, 2026-10-08)

| Change | Source |
|---|---|
| **The record engine** (§8.0–8.0.3): one core, record kinds in config, three change modes enforced (P2); CLI, MCP and housekeeping script as three entry points to one library; v0.4's lint package becomes the engine | owner (context bloat; "a place … needs the space … and checks"); agent design |
| P7: a place needs room, a write-time check and a rest-time check | owner |
| P11 exception: housekeeping may write through `hk_` operations to carry out already-recorded intent; it never forms new intent | owner (housekeeping by tool-using agents); agent rule |
| §6.11 housekeeping: tier 0 no-model script, tier 1 `hk_`-restricted agents, tier 2 the session; at start (reconcile) and before close (carry out); `hk.close` only on a verified `Closes:` trailer or ledger line; edit subagents deferred | owner; zanzibar `task.py` "no tool is allowed to auto-close" |
| MCP server: local stdio, per session, from a committed `.mcp.json`; context-first design rules; tool list; `hk_` prefix for allowlisting; a server process is not a session | owner question; agent design; four UNVERIFIED claims listed in §12.3 |
| Batons and pause blocks become records (§5.4): no carry-forward, `orient()` hands them over, mechanical expiry, `pause.open` captures git state and commits itself | owner question; agent design |
| §5.5: session key minted at **start** under a lock, with a `kind: open` stub (live sessions visible, crashes detectable); banner written only if unchanged since read (`seen_hash`) instead of re-read plus copy-forward | agent design, enabled by the engine |
| §6.1 `orient()` replaces steps 2–5; optional SessionStart hook; §6.3 step 6a pre-close housekeeping; §6.4 pause as operations | agent design |
| Tasks close **in place** with `state: open \| closed`; `closed/` may migrate later | owner |
| Decisions become one OKF record per file (§6.5): record shape, operations, `why(target)`, `body_sha`, REJECTED with `reopen_if`, by-id vs by-topic dissolved, no period splits, `decision.correct` proposed | owner; agent design |
| Stories and deviations become append-only records; G-D10 makes "verbatim owner words" mechanical | agent design |
| §9.3.1 OKF v0.2 constraints, read from the spec: `status` reserved; concept id = path; bundles are chosen directories, every `.md` in them needs `type`; `index.md` shape fixed, so the component → path map moves to `context.toml`; log headings are dates; actor forms; round-tripping | OKF `SPEC.md` (READ, 2026-10-08) |
| Guards: G-D6 simplified; new G-D10, G-D11, G-W9, G-W10, G-W11; G-W3, G-W4, G-W7 updated | agent design |
| Ledger kinds `open` and `abandoned`; ledger written by `session.*`; Q-H fragments vs single file | agent design |
| Layout, minimum set and add-when-needed updated; trial plan (§8.0.3); open questions Q-H to Q-K and a to-verify list | agent design |
