# A context-engineering framework for agent-built repos

**LIVING. Framework 0.5. Status: DRAFT.** This is the specification of what the
`context-engine` repo builds, and the source of truth for how the framework works. It describes
the framework as it is meant to work now and carries no history. Where the engine has not caught
up with the design, the text says *Not built yet* (or *Built so far* for a part) and names the
board task.

**History lives elsewhere.** Why a rule exists is in its decision or story (`docs/decisions/`,
`docs/stories/`). Earlier versions are kept beside this file: `FRAMEWORK-v0.1.md`,
`FRAMEWORK-v0.4.md` and `FRAMEWORK-v0.5.md`, the last copy before history was moved out, which
holds the prior-art citations to the owner's other repos, the owner's answers round by round (its
§12) and the change log from v0.1 (its §13). Git history has the rest.

**Section numbers are stable** (P3): other records cite them. A missing number (§11.3, §12, §13)
is a section that now lives only in `FRAMEWORK-v0.5.md`.

---

## Summary

The owner of a repo does not write code. The owner gives **intent**: stories, goals, decisions.
Agents do everything else, across many sessions, often several at once, with no memory between
them. The framework is what keeps that working. It has four jobs: make the owner's intent
**durable**, make correctness **checkable**, make continuity **cheap** for a session that starts
with no context, and spend the owner's attention **only where it is irreplaceable**.

It does this with plain files in git, organised in layers:

- **Intent:** a charter, the owner's stories in the owner's words, criteria that define correct
  behaviour, and decisions. Every link from goal to story to criterion to test is guarded.
- **Rules:** a short contract, a routing map of where everything lives, a residual-risk register
  and runbooks.
- **Working state:** an orientation note with a one-session banner, a board of tasks and owner
  questions, and session-stamped batons and pause records for work a session skipped or left
  mid-flight.
- **Record:** a session ledger with receipts, evidence docs, and an archive.
- **Verification:** tests, plus guards that fail the gate when a component drifts, bloats or
  loses its links.

Anything that is a set of id'd records (tasks, questions, batons, pauses, decisions, stories,
deviations) is written through **one tool, the record engine** (`context-engine`), which stores
records as OKF files, refuses bad writes and names the remedy, and is reachable as a library, a
CLI and a per-session MCP server. Prose is written by hand. **Procedures** (session start, intake,
clean close, pause) are engine operations, and every one has a by-hand fallback in a runbook.

A `CE-n` in parentheses, as in *Not built yet (CE-n)*, points at the record engine's own board in
the engine repo: it is build status, not part of the framework, and an adopting repo has no such
item.

## What each section covers

| § | Section | What it covers |
|---|---|---|
| 0 | What this framework is for | Who does what (owner intent, agents the rest), the four jobs, and the stance: plain files, records through a tool, mechanical refusal over warnings |
| 1 | Principles | P1 to P18: one home per statement, change modes, stable ids, provenance, caps, guards that have been seen to fail, owner attention, concurrency, design for a context-free agent, fallbacks, design for safety and maintainability |
| 2 | The components at a glance | The components by layer, how each changes and who writes it; terms; which separations are load-bearing |
| 3 | The intent layer and the correctness chain | Charter, stories, criteria (including research repos), the chain from goal to test and its guards, the deviation register |
| 4 | Drift: kinds and guards | Each way records drift from reality, and the guard (or the absence of one) for it |
| 5 | Working state | The orientation note, the board, owner questions as board rows, batons and pause records, rules for several writers, the owner digest |
| 6 | Procedures | Session start, intake, clean close, pause, decision recording, delegation, promotion, push, bootstrap, humans outside the procedures, housekeeping, keeping this document current, rollback |
| 7 | Record layer details | Ledger, evidence docs, archive, the residual-risk register, runbooks |
| 8 | Tooling and verification | The record engine (config, record kinds, CLI / MCP / housekeeping entry points, trial before adoption) and the guard catalogue |
| 9 | Storage, persistence and OKF | What persists, storage tiers, how OKF is used and its constraints, what comes later |
| 10 | Layout for a new repo | The directory tree |
| 11 | Adoption | The minimum set, what to add when, and migrating an existing repo |

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
- keep the docs, guards and procedures that make the work continuous across sessions.

Agent autonomy is expected to keep rising. The less the owner supervises, the more the repo
itself must carry intent, correctness and continuity.

Four jobs:
1. **Make intent durable.** The owner's words survive sessions, context resets, concurrent
   sessions and model changes: verbatim, attributed to the owner, and dated.
2. **Make correctness checkable.** Every piece of intent traces to something executable that
   has been shown to fail when the behaviour breaks.
3. **Make continuity cheap.** A cold session, even a new model with no memory, can orient in
   minutes from a single query, resume mid-flight, and leave the repo easier for the next session
   to orient in. This is
   *measured*, not assumed: see the `read:` receipt in §6.3.
4. **Spend owner attention only where it is irreplaceable.** Agents decide what they may
   decide, record it, and ration what they raise.

### 0.2 Stance

- **Plain files and git now.** Markdown with small frontmatter schemas, plus lint that runs
  inside each repo's gate. Vector search, source graphs and memory services come later (§9.4),
  as derived indexes, never as the source of truth. SQLite is allowed only on the same terms: a
  disposable index, because it is not friendly to human readers, hand editors, or git.
- **Records are written through a tool; prose is written by hand.** Anything that is a set of
  id'd records with a lifecycle is changed by typed operations of the record engine (§8.0), so
  an agent never reads a file in order to change part of it. Hand edits stay legal, for humans
  and agents alike; the gate's lints catch what they break (P7).
- **Mechanical refusal beats a written warning.** Rules kept only as prose drift; rules backed
  by a guard hold.
- **Mechanise a step people keep forgetting.** A note asking for a step does not cause it; a
  tool that has just created the file can do it itself.
- **One versioned implementation.** The engine and its guards ship as one versioned package,
  with a per-repo config and a `framework: <version>` pin in each contract (§8.0). Prose rules
  copied between repos diverge.
- **Not too simple.** Every component exists because its absence caused a recorded failure
  (the evidence is in `FRAMEWORK-v0.5.md`). "Simple" means no infrastructure, not few concepts.
- **Adopting it in an existing repo: map, don't move.** Existing repos keep their paths, ids
  and check numbers. The routing map records how each framework component maps onto the repo's
  own files (§11.4), because moving heavily cited files breaks every citation.

---

## 1. Principles

**P1. One home per statement; everywhere else points to it.** A table of where things live is
a pointer and nothing more.

**P2. Every artifact declares how it changes and whether it is kept current (its liveness).**
These are two separate properties.

How it changes:
- **replaced:** rewritten in place; git holds the history;
- **append-only:** entries are never edited; corrections are dated additions;
- **generated:** produced by a tool, and checked against a regeneration **and** for content;
- **session-stamped** (`mode = "stamped"` in config): an entry carries a session key and
  expires (batons, pause records).

Whether it is kept current (its liveness):
- **LIVING:** maintained, true today;
- **ACTIVE-PLAN:** being executed; the body is provenance, dated corrections are added at the
  top;
- **FROZEN:** provenance only, with a visible banner.

**For records, the change mode is per-kind config that the engine enforces** (§8.0.1):
append-only kinds carry a body hash and accept only `amend`; session-stamped kinds expire mechanically;
replaced kinds have tool-owned frontmatter and hand-written bodies.

**P3. Stable ids, never reused, and never renumbered.**
- Applies to stories, criteria, decisions, tasks and questions, and also to rule numbers,
  procedure step numbers, guard check numbers and the section numbers of this document.
- Cite stable keys, never line numbers.
- Code is cited as `file::symbol`.
- **One standard id form** for every id a repo mints (goals, stories, criteria, decisions, tasks,
  questions, register entries): `[A-Z]+-[1-9][0-9]*`, a prefix of capitals, a dash, and a number
  with no leading zero (`G-3`, `S-12`). The prefixes of record kinds are per-repo config
  (`[kinds.*].prefix`); the form is not. Goals and register entries are not record kinds, so
  their prefixes (`G`, `INV`) are fixed by the engine. *Not built yet (CE-56): the config does
  not check a prefix against the form, and `init` accepts a prefix with digits.* Guard and
  drift names (`G-D3`, `DR1`) belong to this document, not to a repo. A record stamped before a repo took up the form keeps its old ids verbatim (owner words
  are never rewritten), and the guards read a legacy goal id `G3` as `G-3`.

**P4. Provenance on anything that can go stale:**
- **who:** the actor vocabulary in §6.5, with the model id for agents;
- **when:** a date or session key;
- **how it is known:** READ / REASONED / UNVERIFIED. Finding out how a claim is known is part of
  the work, not overhead.

**P5. Numbers that can be derived from the tree are generated. Measurements may be typed with
a date.**
- Derivable counts (scenario totals, task counts) live in generated blocks.
- A measured value from a run may be typed **with its date on the line**, ideally in a
  single-baseline slot (one dated baseline per suite).
- A number in prose takes one of four forms: a fenced block; a backticked or quoted span; a
  `YYYY-MM-DD` key on the line; or a file whose banner declares its body is provenance. A bound
  (`at most 2 entries`) is a rule's value, not a count, and needs none of them.
- Re-measure; never difference against a recorded number.

**P6. Cap the dimension that actually grows, target the mechanism of growth, and give every
component a way out.**
- A guard bounds what it measures, and the growth moves to what it does not.
- A note meant to be replaced, not added to, grows back by **stacking**: each session stacks
  its update on top. So the targeted guard is a stacking check (the banner carries exactly one
  session key), and a byte cap is only the backstop.
- A component with no exit path bloats: session logs kept inside the orientation note, a
  single-file decision log, an uncapped contract.

**P7. Every tracked text component has a schema and a cap; every rule that matters has a guard;
every guard has been shown to fail.**
- **Every component needs room, and checks on what is inside it:**
  - **room:** a schema, a cap, and a way out (archive or promotion), so it never has to bloat;
  - **a write-time check:** the engine refuses a bad write when it is made, and names the
    remedy;
  - **a check on the stored files:** a lint in the gate. Both are needed, because humans and hand edits
    bypass the tool (§6.10).
- Sabotage what a guard protects and watch it go red before believing it.
- Guard the guards:
  - **floors are raw totals with zero headroom, plus an automatic ratchet**, so deleting a
    corpus cannot lint clean;
  - **floors that check what a guard's own extractor finds (G-D12's, for one) keep declared
    headroom;**
  - **the doc tools are themselves pinned by tests inside the gate.**
- **Each guard's docstring says what it deliberately does NOT check.**

**P8. Owner attention is the scarcest resource.**
- **The "who decides" test**, in this order:
  - **reversibility first:** a call that is cheap to undo, in time and tokens, is the agent's,
    whatever kind of call it is. A local commit or a record write is cheap to undo: git reverts
    it. A push, a release, a published tag, deleting untracked files, owner words and anything
    outside the repo are not, and stay the owner's;
  - then the kind of call: agents make engineering and architecture calls and record their
    reasoning; goals, priorities and genuine preferences that are not cheap to undo go to the
    owner;
  - an agent's call where the owner would otherwise decide is recorded PROVISIONAL and flagged
    in the close digest, so the owner can push back (§5.3, §5.6);
  - a consultation with another model is a recommendation, not an order.
- **Ration what is raised:** standing owner questions are bounded by the NEXT cap (§5.3).

**P9. Skip what can be recovered; never skip what would be lost.**
- Procedures may be shortened at an awkward stopping point (§6.4).
- What may never be skipped:
  - unrecorded owner words;
  - evidence still in scratch;
  - uncommitted changes that nobody has described;
  - the session's ledger entry.

**P10. Evidence goes into a tracked file the same hour.** `.scratch/` is throwaway space: anything
recorded only there is already lost.

**P11. Delegate reading to save context; parallelise building only when file ownership is
disjoint. Judgement stays with the session.**
- Reading and auditing go to subagents, which return verdicts, not file dumps (§6.6).
- The top-level session coordinates: every task, even a lone one, goes to a subagent, checks and
  verification go to agents, and the top level only reports (§6.6).
- Building: parallel builders work under disjoint file ownership, with no fan-out on a
  dependency chain (§6.6).
- Agents audit, and the session decides.
- **Exception: housekeeping writes.** A housekeeping agent may write, but only through typed,
  logged, revertible engine operations (§8.0.2, the `hk_` set), and only to **carry out intent
  that is already recorded** (a commit trailer, a ledger line, an expiry rule). It never forms
  new intent: no ranking, no answering, no judging that work is done. The audit-only rule stands
  for anything that cannot be undone, such as deleting from `.scratch/`.

**P12. Concurrency is normal, and running sessions in parallel is a goal to build toward.**
- Several sessions share one tree; **working-state files must be safe with several writers**
  (§5.5).
- Commit by path; never `git stash` in a shared tree; re-check `git status` right before
  committing. Another session's commit can absorb uncommitted files, or land minutes before
  yours.

**P13. Behaviour claims are checked against the code, never against the decision log.**
Restating a requirement from the decision log is not the same as checking it against the
code. Decisions say what was *meant*; only the code says what *is*.

**P14. Honesty norm: criteria, goldens and oracles are never edited to make a test pass.**
- When a test and a criterion disagree, the default assumption is that the code is wrong.
- Changing a criterion is a decision, with an actor.

**P15. Design for an agent that starts with no context.**
- A context clear, a handoff to the next session, a parallel session and a fresh subagent are
  the same case: the reader has none of the current session's memory. Design every record for
  that reader.
- **Anything a later agent needs lives in the repo, stamped with what it is true for** (a
  content hash, a date, a session key), so the agent can trust it without re-deriving it and can
  tell when it has gone stale. "Tests passed" is worth recording only with the hash it passed on.
- The test for any record: **could an agent with no context act on this correctly, or at least
  tell that it cannot?**
- This principle is the reason for P4 (provenance), P5 (generate what is derivable), P9 and P10
  (never lose what cannot be recovered), and P12 (other sessions are such readers too). The
  mechanisms that serve it: `orient()` (§6.1), batons and pause records (§5.4), ledger receipts
  (§7.1), and the run ledger, with parts keyed on their inputs' hash (G-V1, §8.5).

**P16. Every programmatic process has a by-hand fallback,** as a business keeps a
continuity plan for a system it normally runs by machine.
- The engine, its guards, the housekeeping run and the MCP server are conveniences over steps a
  session can do by hand, not replacements for them: for each one, a runbook gives the by-hand
  steps for when the program is missing, broken, or wrong.
- **The fallback is a section of a runbook, named after the process:**
  `docs/runbooks/manual-mode.md` has one per engine operation, and `docs/runbooks/procedures.md`
  one per procedure, the housekeeping run included. A new engine operation is not done until its
  fallback section exists. Both ship in the adoption kit (§6.9), with the method runbooks (§7.5).
- **Using a fallback is something to act on, not a quiet workaround:** do the step by hand, then fix the process
  (runbook § When the engine and this runbook disagree), and note it in the session's review
  (§6.12).
- A refusal with a sensible remedy is not a failure of the process (§8.0); the fallback is for
  an error, or for a refusal the process should not have made.

**P17. Design for safety: foresee whom a design can hurt, and remove the risk before relying on
anyone to avoid it.** Adapted from Singapore's Workplace Safety and Health (Design for Safety)
Regulations 2015 (S 428/2015).
- **The source principles**, paraphrased so the intent can be re-derived if a process here
  breaks:
  - every foreseeable design risk is eliminated, as far as reasonably practicable (regs. 4(1),
    9(1));
  - a risk that cannot be eliminated is reduced as low as reasonably practicable, **at its
    source**, and **collective protective measures come before individual ones** (regs. 4(2),
    9(2));
  - risks are found in design reviews with everyone who designs and builds the work (reg. 6);
  - a **register** of the reviews and of every **residual risk** (one not reasonably
    practicable to eliminate) is kept up to date, open to everyone working on the project,
    and **handed to whoever next takes the structure over** (regs. 7, 11);
  - whoever builds and notices a foreseeable risk reports it (reg. 10(1)); designers and
    builders are given the information they need, and the designer passes on what is needed
    to build and maintain the work (regs. 5(3), 9(3)).
- **Here:** the *structure* is the engine, a record kind, a guard, a procedure or a repo layout.
  The *affected persons* are the session building it, the next session with no context (P15),
  the owner, a human using plain git (§6.10), and every repo the engine is deployed to.
  *Harm* is lost work in a shared checkout, a false green, owner words lost or altered, a git
  operation that destroys work, or a rule that silently stops applying. The *life* of the
  structure is build, operate, maintain, and roll back or remove (§6.13).
- **Hierarchy of controls**, strongest first:
  1. **eliminate:** the design cannot produce the harm (no operation that can do it, a format
     that cannot express it);
  2. **reduce at source:** the operation refuses the harmful write as it is made (P7);
  3. **collective:** a guard in the gate or the lint, which protects every session and every
     human at once;
  4. **individual:** a rule in a contract or runbook that each reader must remember. This is
     the last resort, and choosing it puts an entry in the register saying why the stronger
     controls were not practicable.

  "Prefer a mechanical refusal over a doc warning" is this ladder. Example: a commit-trailer
  rule written only in the contract is individual and often forgotten; the engine writing the
  trailer itself moves it to the top rung.
- **Residual risks go to the register** (§7.4), which travels with the work: from a closed task
  into the repo, and from the engine into every repo it is deployed to (§11).
- **Where it happens:** the design review of a task (§5.2) and a project's architectural design
  stage (§10). Like the regulation, which applies only to projects of S$10 million or more, the
  review has a threshold (§5.2), so small work needs no design review (P8).

**P18. Design for maintainability: F.A.M.E.** Adopted from the Singapore Building and
Construction Authority's Design for Maintainability (DfM), which integrates maintenance
experience into design to make maintenance easy, safe and economical over the whole life of the
work. Its principles, as BCA states them, then what each means here:
- **F, Forecast maintenance:** *"Designers should understand the impact of their designs and
  the expected downstream maintenance works, thereby making necessary upstream design
  provisions."* Here: for each new component, say what will need doing to it later, who does it
  (a session, housekeeping, the owner), how often, and what makes it stale; make the provision
  now (a housekeeping operation, a guard, a `stale_after`).
- **A, Access for maintenance:** *"Designers should give due considerations for all areas
  requiring access for inspection and maintenance, thereby making necessary design
  provisions."* Here: every record is readable and fixable without the engine (§6.10), and
  every process has a fallback done by hand (P16). Nothing is reachable only through a server,
  a cache or a model.
- **M, Minimise maintenance interventions:** *"Designers should give adequate attention to
  materials performance and detailing to minimise common and critical defects."* Here: choose
  the forms that do not drift: one home per statement (P1), derived numbers generated (P5),
  schemas and write-time refusals (P7), owner words append-only with a hash (§3).
- **E, Enable simple maintenance:** *"Designers should consciously consider standardisation
  and prefabricated components to facilitate easy inspection and productive maintenance."*
  Here: one engine and one record format across every repo (§0.2), one name per operation
  across library, CLI and MCP, and one runbook section per process.

BCA turns F.A.M.E. into five design considerations: design strategy and collaboration, access
for maintenance, materials and finishes, design and detailing, and integrating technology.

**Use:** go through F.A.M.E. and P17 as a checklist at a project's architectural design stage (a new
repo, §10, or a new engine subsystem) and in a task's design review (§5.2). **When a process
here breaks or a rule is unclear, re-derive the intent from P17 and P18** and fix the process
from them, not from the broken process.

---

## 2. The components at a glance

| # | Layer | Component | Question it answers | Changes by (P2) | Who supplies the content |
|---|---|---|---|---|---|
| 1 | Intent | **Charter** | What are we building, why, what is out of scope, which principle wins a tradeoff? | replaced (rarely), LIVING | owner; the agent proposes |
| 2 | Intent | **Stories** (incl. use cases, interactions) | What does the owner want to happen, in the owner's words? | **record**, append-only (amendments are dated additions; a body hash pins the owner's words) | owner |
| 3 | Intent | **Criteria (the spec)** | Exactly what behaviour counts as correct? | replaced, with ids and statuses | agent drafts; owner may veto |
| 4 | Intent | **Non-functional requirements (NFRs)** (optional) | Cross-cutting invariants: data model, performance, security | replaced, LIVING, with its own invariant → test map | agent, from owner intent |
| 5 | Intent | **Deviation register** | Where the system deliberately differs from the spec | **record**, append-only | agent; owner approves material ones |
| 6 | Rules | **Contract** | How do I work here? Gate, mandates, traps | replaced, capped | promotion only |
| 7 | Rules | **Routing map** | Where does each kind of statement live, and how do framework components map onto this repo? | replaced, small | agent |
| 8 | Rules | **Residual-risk register** | What is load-bearing, and must not be rediscovered the hard way? | replaced; changes only when the code does | agent |
| 9 | Rules | **Runbooks** (method) | How do we run the gate, sabotage, fan-out, release, and every engine operation by hand? | replaced. Archive the status, keep the method | agent |
| 10 | Working state | **Orientation note** | What is true now; what must the next session not miss? | replaced at every clean close; banner = one session key, stamped by the engine, written only if unchanged since read (§5.5) | agent |
| 11 | Working state + Record | **Tasks and the board** (tasks **and** owner questions) | What is next, in what order, what is waiting on the owner, and what happened on each item? | each task is a **durable record** (body, comments, op log, links to decisions; it stays when closed, **in place**, with `state: closed`). Only the ranking fields and the board *view* are volatile | agent ranks; owner assignment overrides |
| 12 | Working state | **Batons and pause records** | What did a session skip, or leave mid-flight? | **record**, session-stamped, one file each; closed by `baton done` with evidence (a pause by `pause resume`), or expired after two sessions by housekeeping | agent |
| 13 | Working state | **Unverified hazards** | What is suspected to be dangerous right now, and must not be fixed without checking first? | replaced | agent |
| 14 | Record | **Decisions** (with negative results) | Why is it this way, and what was rejected? | **record**, one file per decision, append-only (§6.5) | stamped with actor |
| 15 | Record | **Session ledger** | What happened in each session, with receipts? | append-only, one entry per session, written by `session.*` operations (one file under the engine lock, not a record kind, §8.0.1) | agent |
| 16 | Record | **Evidence and plan docs** | What did we measure; what is the plan for item X? | ACTIVE-PLAN → FROZEN | agent |
| 17 | Record | **Archive** | Where did X go? | moved verbatim; redirect table | agent |
| 18 | Verification | **Tests and proofs** | Does the behaviour hold? | code | agent |
| 19 | Verification | **Trace and existence guards** | Is intent ↔ criteria ↔ tests complete, and does the prose still name live code? | code | agent |
| 20 | Verification | **Doc and working-state guards** | Is every component within its schema and caps? | code (versioned package) | agent |
| 21 | Verification | **Verification state** | What has been proven on *this* tree? | generated | tooling |
| 22 | Ephemeral | **Scratch** | Somewhere to put things before they are judged | throwaway | — |
| 23 | Ephemeral | **Memory** | What has the owner taught agents that isn't a rule yet? | accretes; promoted or pruned | agent records the owner's feedback |

**Terms:**
- A **baton** is a session-stamped note of a step a session skipped.
- A **pause record** is a session-stamped note of work left mid-flight (§6.4).
- A **session key** is `YYYY-MM-DD` plus a letter, minted by `session.start` under a lock
  (§5.5).
- A **record** is one OKF file of a **record kind** the engine owns (§8.0.1). The engine owns
  its frontmatter and lifecycle; its body is prose. Components marked **record** in the table
  above are record kinds; the rest are hand-written documents checked by the doc guards.
- **Housekeeping** is the repair pass the engine runs at session start and before close
  (§6.11): first a script that calls no model, then small agents with restricted tools only
  where something must be read.

### 2.1 Separations that are load-bearing

| Kept apart | Why |
|---|---|
| Orientation note vs session ledger | Otherwise the banner becomes a second log, stacked session on session (P6). |
| Owner-question **row** vs free-floating **badge** | A marker with no limit on where it may appear drifts into meaning "see also". Each owner question is a **board row** in its own id series (`ASK-n`), ranked under the same caps. A separate question queue would be a second list beside the board. |
| Board vs baton | Batons that never expire become a second backlog: a baton that survives two sessions is not a baton, it is backlog. |
| Contract vs decision log | A contract that indexes the decision log grows without bound; the contract holds rules, decisions hold reasons. |
| Contract vs residual-risk register | The register holds residual risks, the traps a session must know, not a second contract. |
| Residual-risk register (durable) vs unverified hazards (volatile) | Merged, a durable lesson would be deleted whenever a hazard is "fixed". |
| Status vs method | Runbooks survive when the status around them is archived. |
| Stories vs criteria | The owner speaks in stories, not test-grade prose; criteria must be precise. The gap between the two is accepted, guarded (G-T1, G-T6) and kept in step (§6.1). |
| Ledger vs archive | The ledger records events; the archive receives pruned material verbatim and never repairs it. |

---

## 3. The intent layer and the correctness chain

### 3.1 Charter

**Contents:**
- goals, each with how it is measured;
- non-goals;
- ranked principles, so tradeoffs have a known answer;
- owner mandates;
- the humans who give intent, and their roles (§6.5).

**Rule:** one charter per repo, signed off by the owner. Agents change it only through an owner question,
then a decision, then the edit. Every goal is served by at least one story (G-I1).

**Goal ids:** each goal leads a row of the charter's goal table with its id, `G-n` (P3), so the
guards can read it: `| G-1 | <goal> | <how it is measured> |`.

**Bootstrapping cost to the owner:** about one page, given in chat (§6.9).

### 3.2 Stories: the owner's voice

**The owner's input is always free prose,** or simply a feature or a goal stated outright. No
template is ever imposed on the owner, and the agent never rewrites the owner's prose into one.
**Templates belong to criteria:** BDD scenarios follow the Gherkin template (§3.3). A stated
**goal** goes into the charter; a stated **feature** becomes a story.

**Where stories live.** Either is fine, and a repo may use both:
- one story per file (`S-n`; id prefixes are per-repo config, `[kinds.*].prefix` in
  `context.toml`, with the defaults in §10); or
- numbered sections of a per-feature **PRD** (`docs/issues/<slug>/PRD.md § N`), each carrying
  the owner's words with a date, e.g. `(OWNER: "make Ctrl click include the cursors row")`.

**Each story carries:**
- an id or section ref;
- a date;
- `actor:` **who gave it, recorded explicitly**: `owner` in a single-owner repo, `human:<id>`
  when the charter names several humans (§6.5), or `agent (reconstructed from …)` when
  back-filled (§11.4). **Git blame is not enough:**
  - the agent writes and commits the text, so the git author is whoever's credentials the
    session runs under, not who spoke;
  - two humans using one remote-control setup look identical in blame;
  - blame breaks when text is moved, reformatted or archived.
- `via:` the channel, e.g. `remote-control session <key>`, `issue #n`, `commit <sha>`,
  `direct edit`;
- a status, `story_status: live | unspecified | unconfirmed | retired` (OKF reserves `status`,
  §9.3.1);
- `goals:` the charter goal(s) it serves, by id (`[G-1, G-3]`; G-I1).

**Owner words are verbatim.** Agent text inside a story is labelled `AGENT:` and becomes owner
intent only once accepted.

**Amendments** are dated additions, never silent rewrites.

**As records:** a story file is an append-only record (§8.0.1). `record.new` (CLI
`record new story`) writes the owner's words with `actor` and `via`; `record.amend` appends an
entry under `## Amendments`, keyed by session and actor; `record.stamp` freezes `body_sha` once.
The body hash (G-D10) makes "verbatim" mechanical: rewriting the owner's words goes red.

**Retiring a story** is owner intent too, so it is an operation that records who and why:
`record.retire(id, why, by, superseded_by)` (CLI `record retire`).
- **Whose call:** `by: owner` (or `human:<id>`), with their words verbatim as `why`; or `by:
  agent`, only to replace a broken record (the wrong goal, actor or status when it was created)
  with a new story named in `superseded_by`, which must carry the story's words as typed (the
  body above `## Amendments`, logged corrections undone; a correction is redone on the new
  record). An agent never withdraws owner intent on its own.
- **What it writes, in one write:** `story_status: retired` and the derived `status: deprecated`
  (§9.3); `superseded_by` on the story and `supersedes` on its successor, both directions as
  `decision.supersede` writes them; and the reason as an amendment (`retired (by <who>): <why>`,
  or `retired (by <who>; superseded by <id>): <why>`), so the why lives with the story. It writes
  one op log line per record, the successor's first; because setting `supersedes` is idempotent,
  a retry completes a write that failed between the two.
- **It refuses** a successor that is not a story, is the story itself or is retired; a story
  whose hash does not match; and a story that a logged `retire` retired, even when a hand edit
  has since undone it.
- **A retirement is final.** No operation undoes it: to bring the intent back, record a new
  story. A story retired by hand (no logged `retire`) may be retired by the operation, which
  records who and why; stories that an adopting repo retired before it adopted the engine are
  retired the same way, with the owner's words from the one batched answer of §11.4.
  `record.new` refuses a story created as `retired`, with
  `status: deprecated`, or with a story link (`supersedes`, `superseded_by`: lists of story ids,
  written only by `record.retire`).

**Confirming a story** an agent reconstructed is owner intent too, so it is an operation that
records whose words: `record.confirm(id, words, by, status)` (CLI `record confirm`).
- **Whose call:** `by: owner` (the default) or `human:<id>`, with their words verbatim. An agent
  never confirms a story.
- **What it writes, in one write:** `story_status: live`, or `unspecified` (`status`) while no
  criterion comes from the story yet (G-T1), and the words as an amendment (`confirmed (by
  <who>): <words>`); one op log line. The `actor` stays the agent's: the text above
  `## Amendments` is still the reconstruction.
- **It refuses** a story whose actor is not an agent's reconstruction, a retired story, a story
  whose hash does not match, and a story that a logged `confirm` confirmed, even when a hand edit
  has since made it `unconfirmed` again. A reconstruction made `live` or `unspecified` by hand (no logged
  `confirm`) may be confirmed by the operation, which records whose words confirmed it.
  `record.new` refuses a reconstruction created `live` or `unspecified`: it starts `unconfirmed`.
  So a confirmed reconstruction that `record.retire --by agent` replaces leaves a successor that
  is `unconfirmed` until it is confirmed again.
- **Lint (G-I2)** fails a story marked retired that no logged `retire` retired, a story that a
  logged `retire` retired but that is no longer `retired` with `status: deprecated`, and a story
  that is deprecated but not retired. A retired story is history: G-I1, G-I2's provenance checks
  and G-T1 do not read it. When a live story replaced a story some criteria cite as their
  source, G-T1's remedy says to add the new story to those criteria's `from` cells.

PRD sections are not separate files, so a PRD-form repo maps stories onto PRD sections through
`context.toml` and keeps G-D10 off for them until it adopts story files.

**Intake classification (§6.2):**
- **behaviour-shaped intent** ("the user can…", "when X then Y") becomes a story;
- **choice-shaped intent** ("do it with X", "don't pursue Y", a priority) becomes a
  **decision** with `actor: owner`, or a charter edit if it is a goal or non-goal.

Owner intent therefore has exactly one home per kind (P1). G-T1 applies to stories only.

**PRD lifecycle:** a PRD is archived only when the PRD **and every issue under it** are done,
in the same change. An issue left listed as ready after it shipped makes a later session
believe it is still open.

### 3.3 Criteria: the definition of correct

Each criterion has:
- an id, or a scenario tag;
- the story section or decision it derives from (its `from`). **Its actor is its source's:**
  no actor column is kept, and G-T6 checks that the source resolves;
- a status:

| status | meaning | requirement |
|---|---|---|
| `tested` | a test checks it | the claiming test exists (G-T2) |
| `planned` | no test yet | counted in a generated block |
| `manual` | checked by a hand-run driver | the **driver** declares which criterion or decision it checks (`@scenario`, `@decision: D-N`, or `@ties: none - <reason>`) |
| `deviates` | deliberately not met | references a deviation-register entry (G-T7) |
| `retired` | no longer intended | references the decision that retired it |

**Owner sign-off** is separate from test status:
- `verified:` in OKF terms, naming `human:owner` and when (its shape is not settled, §9.3);
- **inform and proceed:** agent-drafted criteria are live as soon as they are created. The
  owner is informed through the digest and pushes back if something is wrong;
- a story the owner tags `sign-off: required` holds its criteria at `planned` until the owner
  signs them off. This is opt-in.

So the owner's silence never blocks work, and the owner can still require approval where they
want it.
**"Inform" must actually reach the owner:** see the digest in §5.6.

**The form depends on the kind of project.** The chain's shape does not:

| Kind of project | Criterion | Its test |
|---|---|---|
| Product / app | BDD scenario | e2e, component or unit test |
| Library / algorithm | property or invariant | property-based or fuzz test |
| Port | parity with a reference | oracle or parity test |
| Numerical / perf change | moves only within the declared tolerance | frozen baseline plus comparison |
| Research | **a direction plus measures** (§3.3.1); thresholds only where real | scored runs that move the frontier on held-out data without regressing guard measures, results in tracked docs |
| Formal | theorem | proof plus model ↔ code correspondence pin |

#### 3.3.1 Research repos

Bringing the repo closer to the goal is the entire point. The goal still needs a definition of
success, which is usually the end goal of the research (e.g. make speech more intelligible), but
it may have no threshold, only a direction. So a research repo replaces pass/fail criteria with a
**direction, measures and a frontier**:

| Part | What it is | Who | Example (speech separation) |
|---|---|---|---|
| **Direction** | the end goal, as a direction, not a threshold | human (charter) | "separate each talker from everything else"; output serves speech-to-text **and** human listening |
| **Measures** | proxies for progress, agent-proposed, human-confirmable, each with **its known blind spots** | agent proposes; human may veto | SI-SDR, PESQ, ESTOI, DNSMOS; "DNSMOS cannot see a dropped turn, so never judge on it alone" |
| **Ground truth** | the human judgement the proxies stand in for, sampled now and then | human | the owner listens to a fixed set of outputs |
| **Frontier** | best-so-far on each measure, dated, on fixed scene sets | generated from results docs | a table of the best median SI-SDR per method |
| **Targets** (optional) | a threshold, only where one genuinely exists | human | a DNSMOS target |

**What counts as progress** (the research equivalent of a passing test):
- a change **moves the frontier** on the primary measure;
- on **held-out** data. Score any change to a selection rule on a fresh set, because a set that
  has been looked at is no longer held out;
- **without regressing the guard measures**. A gain on one proxy that the others contradict
  is a suspected proxy failure, not progress;
- and is periodically **checked against ground truth**, because the proxies can drift from the
  direction (Goodhart). When the human's judgement and the proxies disagree, the human wins,
  and the measure set is revised by a decision.

**Success** is not reached; it is approached. A line of work stops when the frontier stops
moving (diminishing returns, recorded as a negative result) or when a human says it is good
enough, which is a decision.

- **All the work is tasks that move the repo toward the direction:** testing new algorithms;
  literature review and collating references; downloading datasets; building the methods to be
  compared. These are not criteria, and need no criterion each. Each task names the goal it
  serves, and its outcome is evidence (a results doc, a reference note, a dataset card), or a
  negative result in the decision log.
- **Progress is the ledger of measurements:** dated results docs, each method scored the same
  way on the same evaluation sets, with held-out sets kept fresh.
- **The harness still gets ordinary tests:** metrics, data loaders, scorers and vendored
  libraries. A wrong metric silently moves you *away* from the goal while looking like
  progress. Vet research code against its paper.

**No prose-requirements layer by default.** Prose criteria that name implementation symbols rot
silently: they keep describing deleted code, and criteria still tagged `planned` keep
describing behaviour that has shipped, with every guard green. The cause is prose naming symbols, not the number of layers.
Hence:
- no separate prose-requirements (FR) layer between stories and criteria;
- an **existence guard against the code** at every prose layer (G-T3);
- **behaviour verified against the code** (P13).

NFRs and data-model law go in the charter, or in an NFR doc with its own invariant → test map.

**Unspecified semantics: pin first, then specify.** When existing behaviour nobody specified
must be preserved, write tests that pin it empirically, then write the criterion from the pins.

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
| criterion → test | hand: an annotation in the test or driver | G-T2: every `tested` or `manual` criterion is claimed by a test or driver, and every annotation resolves. The guard sees annotations, not coverage. **Not required:** that every test name a criterion. Tests may be internal |
| test → code | **derived** from coverage or imports | **proven, not declared:** G-T5 mutation per criterion |
| design change → criteria | census (§6.2 step 6) | the census output is an evidence doc. Retirements carry the decision id |

**Rules:**
1. **Stop hand-written links at the test.** A test-to-code map, used for impact analysis, is
   generated and disposable.
2. **A link proves existence, not truth.** Being traced by a scenario is not the same as being
   true. Hence G-T3 (prose names live code) and G-T5 (mutation).
3. **Structural claims get hash pins.** A claim about *structure* (model ↔ code correspondence,
   "implemented as a sparse bitmap") may cite `file::symbol`. The citation is resolved, and
   pinned by a body hash. **Calibrate the pin:** pin only what the claim is about (e.g. the
   *shell* of a class), because a pin that trips on every edit gets re-pinned without anyone
   reading the change. *Not built yet: the pins and their guard, G-T4 (§8.2).*

### 3.5 Deviation register

- **Append-only:** one record per deviation, each naming the criterion it affects, the reason,
  and who decided.
- **A companion view of what is open today** is allowed, as a generated query over the records.
- **The enforceable check (G-T7):** a `deviates` criterion must reference a register entry.
  No tool detects an *undeclared* deviation in general. A failing test is just a failing test,
  and P14 says the code is presumed wrong.

*Not built yet: deferred until the code first deliberately departs from the spec (§11.2). No
`[kinds.*]` entry, id prefix or schema is defined for a deviation yet, and G-T7 comes with it.*

---

## 4. Drift: kinds and guards

Drift ids are `DR`, to avoid colliding with decision ids.

| # | Drift | Guard |
|---|---|---|
| DR1 | A story with no criterion; a criterion with no test | G-T1, G-T2, G-T6 |
| DR2 | Prose names a file, symbol or route that no longer exists | **G-T3: existence check against the code** |
| DR3 | Prose is semantically false while naming only live symbols | **no guard catches this.** Mitigations: the criteria census on every design change; G-T5 mutation; the trace-check agent's judgement |
| DR4 | Code changed under a structural claim | G-T4 hash pin |
| DR5 | A doc cites a deleted file or symbol | G-D3 |
| DR6 | A hand-typed number that could be derived goes stale | G-D5 |
| DR7 | A test passes without checking the behaviour | G-T5 mutation; sabotage |
| DR8 | The suite or corpus silently shrinks | G-V2 floors |
| DR9 | Working docs drift from reality | G-W rows, G-D8 |
| DR10 | A generated index that is wrong but byte-identical to its regeneration | generate indexes from record frontmatter, not from parsed prose, so the misparse cannot happen; G-D6 content assertions from a cutoff id onward for indexes still built by parsing prose |
| DR11 | A guard bounds one dimension and growth moves to another | target the growth mechanism (stacking check) plus a byte backstop |

---

## 5. Working state

### 5.1 Orientation note (`HANDOFF.md`)

**Contents:**
- a **banner** with exactly **one session key** (the stacking check, G-D8), stating what is
  true now;
- a generated pointer to **open batons and pause records** (§5.4);
- **next session**: the start sequence.

**No session history.** In small repos an inline board is allowed (§5.2).

**Read on demand.** `orient()` prints the banner (§6.1), so a cold session often needs nothing
else. The `read:` receipt records whether the orientation note was read (§6.3).

**Replaced on clean close**, safely for several writers (§5.5). Batons and pause records are
records of their own (§5.4), so the replaced part is only the banner and "next session". The
banner is written with `banner.set(text, seen)`, which refuses if the banner changed since
this session last saw it.

**Caps:** the stacking check first; then lines, bytes and line width as backstops. A line cap
alone does not hold: the bytes grow back as sessions stack updates.

**Subtree notes are allowed** for a large subsystem. A subtree note does not rank anything.

### 5.2 Board: tasks and owner questions together

**Three sizes:**
1. **Inline table** in the orientation note (`HANDOFF.md`): `# | id | what | status / blocker | spec`. Only for a
   single-session repo with few items.
2. **One file per item, no CLI.** The cheap step up; it removes most concurrent-edit
   collisions.
3. **Task tree plus CLI**, where the board is a query and nothing is committed as a board.

**When to move up a size:**
- the first trigger is **more than one session working the board** (P12);
- then: the orientation note shows stacked updates, or sessions still read it for item detail.

**Adopt the next size by trial:** run it in parallel first, with a pre-registered rubric and
a single revertible cutover commit.

**Item schema** (files or CLI):
- frontmatter: `type: Task` (OKF), `id, title, brief, pri, deps, state, created, moved,
  updated, closed, source, labels`; a question also carries `last_asked`, `blocks` and, once
  answered, `answered`;
- `goals`: the charter goals (`G-n`) a task serves, at least one, set at `task new --goals` and
  changed by `task set`; G-I1 checks every open task's goals against the charter where
  `[guards] task_goals` names the kind, and the write refuses a goal the charter lacks. Closed
  tasks are history and are not read. The re-rank (§6.14) cites them;
- `brief`: ≤120 characters, **a constraint, not a summary**;
- body: summary, `## Traps`, and `## Read first`, whose relative links and `file::symbol`
  pointers G-D3 resolves on an open item when the board directory is among the docs `[guards]
  links` lists (*not built yet: a floor on how many there are*); and `## Log`, which `comment` and `close` append to and which is never replaced.
  Sessions keep reading the orientation note for item detail until items carry these sections.
- **`## Design review`** (P17, P18), required before a task above the threshold is promoted to
  NOW. It names the affected persons; lists each foreseeable risk as *eliminated*, *reduced (how,
  at which rung of the P17 ladder)* or *residual*; and answers F.A.M.E. in one line each.
  **Threshold:** the task adds a record kind, a guard, an operation that writes or commits, a git
  operation that can lose work, a long-lived process, or anything shipped to other repos. Other
  tasks skip it (P8).
  - **The threshold is declared, not computed:** the task's author sets `review: [<trigger>, ...]`
    (`task set`), each value from `[working] review_triggers`, one per clause above:
    `record-kind`, `guard`, `write-op`, `git-loss`, `long-lived`, `shipped`. Any other value is
    refused. No `review` field means below the threshold.
  - **Line format**, one line each: `affects: <who>`; one or more risk lines
    `- <class>: <risk> | rung: <rung> | why: <why> | control: <guard or rule>`, class
    `eliminated`, `reduced` or `residual`, rung from the P17 ladder (`eliminate`, `reduce`,
    `collective`, `individual`); `reduced` needs a rung, `residual` a rung, `why` and `control`; a
    risk controlled only at `individual` is a `residual`, so it reaches the register (P17);
    then `F:`, `A:`, `M:` and `E:` lines. The template is in the runbook (§ task promote); a
    template line left unchanged counts as missing.
  - **The refusal:** `task promote <id> NOW` on an item carrying `review` refuses, naming every
    reason, until the section passes. Lower tiers are not checked. On an item already at NOW,
    `task set review=` and `task section` run the same check on what they would write, and
    `task set` refuses to remove `review` while the section lists a residual. G-W12 re-checks the
    stored files.
  - **What close does:** `task close` appends each `residual` line to the register (§7.4) as
    the next `INV-n`, under the close's lock, and logs a `register.append` op. It is idempotent
    on (task id, risk text), so a reopen and re-close adds nothing. A close refuses an unready
    review, and residuals with no register configured. G-W13 re-checks the stored files.

**Edit rules (task tree):**
- frontmatter changes only through operations carrying the session key;
- `moved`, which drives staleness warnings, is never hand-edited;
- bodies are rewritten whole by hand, or one section at a time
  (`task.section`).

**Ranking:** NOW (exactly 1), NEXT (≤5), LATER, SOMEDAY. An owner assignment overrides the
ranking. Do not re-rank at session start. Ranking runs at two cadences:
- **the standup, at every clean close** (§6.3 item 4): a light reorder of what the session
  touched, with no full read of the board;
- **the sprint, the full re-rank** (§6.14): every open item read against the charter's goals and
  its next milestone, when NEXT holds no task while tasks are open (orient says "rerank due"; NOW
  does not count), or when the owner asks. Orient flags it; it never runs it. Re-ranking every
  session, or every time NOW empties or owner direction lands, would spend that read when the
  order is unlikely to have changed.

**Cross-repo work:** the task lives in the repo where the outcome is needed; other repos carry
a pointer row.

**Closing:** a closed item leaves the board, with a `closed:` line in its own `## Log` and its id
in the session's ledger `rows:`. Nothing is open and done at once. Taking the NOW item off NOW
(closing it, answering it if it is an owner question, or demoting it) while others stay open
leaves G-W5 red: the operation still succeeds, and its reply says so and asks the owner which item
to promote (the engine picks none). When NEXT holds no task, the sprint is over: the re-rank
(§6.14) proposes what comes next.

**Closing does not move the file.** Close sets `state: closed`, and the engine derives OKF
`status: deprecated` from it (§9.3). `list --state closed` shows closed items apart, and a path
that never changes is a stable OKF concept id. A repo with a `closed/` directory may migrate it
into the flat directory once the schema carries `state` (§11.4).

### 5.3 Owner questions are board rows

- **Own id series** (`ASK-n`), ranked in the same tiers as tasks.
- **Each question states:**
  - the question, answerable in one line;
  - why it is owner-only (the "who decides" test, P8);
  - the options, with the agent's **recommendation**: one the agent holds with reasonable
    confidence, and the why in a line. Spend only cheap effort on reaching it: reading, a quick
    probe, a short subagent. Not a long `fable` session, and not building and testing a
    feature to find out. Where no recommendation is cheap, say so and why;
  - what it blocks: the blocked tasks declare `deps: [ASK-n]`, and closing the question
    unblocks them.
- **Rationing:**
  - promoting a question to NEXT obliges the session to **raise it in chat**, one line each,
    in that session;
  - an `asked:` receipt in the ledger proves it, and a missing receipt is red;
  - the NEXT cap bounds how many questions are being pressed at once.
- **The board is the owner's only tracker for questions,** so the agent must ask, and keep reminding:
  - every open question carries `last_asked: <session key>`;
  - **at session start**, the session raises, in chat, one line each, every NEXT-tier
    question plus any question that is **overdue**: not asked in the last 5 sessions or 7
    days, whichever comes first;
  - if the owner says "later", that is recorded and `last_asked` is re-stamped. The question
    stays open, and **"later" is never treated as an answer**;
  - **G-W8** refuses a close while an overdue question has not been raised this session;
  - only humans on the remote-control channel are reminded in chat; questions for anyone else
    stay as board rows.
- **Closed only by an owner answer**, which becomes a decision with `actor: owner` and is
  recorded **immediately** (§6.4 item 0). `task close ASK-n` is refused, and its remedy names
  `ask answer`.
- **An answered question never reopens:** `task reopen` refuses a question carrying `answered:`
  and never clears it; the answer changes through its decision (amend or supersede), and a
  follow-up is a new question citing both. A question closed without an answer may reopen.
  `ask answer` likewise refuses a question that already carries `answered:`, so no question is
  answered by two decisions; the remedies name the decision that stands now, following `superseded_by`.
- **Operations:** `ask.new`; `ask.raised([ids])` stamps `last_asked` and writes the `asked:`
  receipt; `ask.later(id)` re-stamps without answering; `ask.answer(id, words, title)` records
  the words verbatim as a decision with `actor: owner` under the given title, closes the question, and reports which
  tasks it unblocked.
- **The agent never answers its own question.** If the agent can decide, it was not an owner
  question.
- **A reversible recommendation is the agent's decision, not a question.** Where the
  recommendation is cheap to undo (P8), the agent makes the call: a decision with the agent's own
  actor and `decision_status: PROVISIONAL`, carrying the options and the why, and flagged in the
  close digest (§5.6) so the owner can push back. No `ASK-n` row is opened.

### 5.4 Batons and pause records

- **Baton:** a skipped step, stamped with its session key. The next session executes it
  **before its own work**. If one survives two sessions, it becomes a board task (G-W3).
- **Pause record** (§6.4), session-stamped, containing:
  - what was in flight;
  - the exact resume step;
  - the uncommitted paths and the branch;
  - where the evidence is;
  - which steps were deferred.

**Each baton and each pause record is its own record file** (session-stamped kind, §8.0.1), not a block
inside `HANDOFF.md`. So:
- **nothing is carried forward at close,** and a concurrent session cannot drop another's;
- `orient()` hands open batons and pause records to the next session before anything else;
- **expiry is mechanical:** housekeeping turns a baton older than two sessions into a task;
- `pause.open` **fills in the branch and uncommitted paths itself** from `git status`, and
  **commits its own record by path** immediately, with the op log, whatever the repo's commit
  policy; it refuses, keeping the record, when it cannot (§5.5 rule 4). Its list leaves out what
  that commit carries (the op log and the files its uncommitted lines name), so it names only
  what stays uncommitted.

Operations: `baton.add(step, why)`, `baton.done(id, evidence)`,
`pause.open(in_flight, resume, evidence, deferred)`, `pause.resume(id)`.

These records are not ephemeral: they are tracked and committed, and they *expire*.

### 5.5 Rules for several writers

1. **Mint the session key at start, under a lock:** `session.start` computes
   `max(newest ledger key, banner key) + 1 letter` while holding the engine lock (a newest key
   from an earlier day gives today's date plus `a`), and
   immediately writes a **`kind: open` ledger stub** that reserves it. Two concurrent sessions
   therefore never share a key. The stubs also make:
   - **live sessions visible:** open stubs are the sessions in flight, and `orient()` lists
     them;
   - **crashes detectable:** a stub never closed within the configured window is a session
     that died; housekeeping marks it `kind: abandoned` and files a baton (G-W11);
   - **a baseline for foreign commits:** the stub records HEAD as its `start head`, read under
     the same lock, and the close or pause keeps it; the session reconciles foreign commits up
     to it (§6.10 item 2).
2. **Write the banner only if it is unchanged since you read it.** `banner.set(text, seen)`
   refuses when the banner's hash differs from the one this session last saw; re-read, merge
   and retry.
3. **Baton and pause records are keyed by session.** Any session closes a baton by
   `baton.done` with evidence of the step done; a pause is closed by `pause.resume`;
   housekeeping expires them.
4. **The engine commits its writes by path, at milestones.** A milestone is a write that must
   reach HEAD at once:
   - **a task's close** (`task.close`): its commit is titled `<id>: close; <message>` and
     carries `Closes: <id>` (§6.10) and the close's optional message body, which holds the
     `Sabotage:` and receipt lines a finished task's commit carries;
   - **owner words:** a story or decision recorded (`record.new`), amended, retired or
     superseded, a story confirmed (`record.confirm`), and a question answered (`ask.answer`): until committed they exist in one
     working tree and one transcript (§6.2);
   - **a hand-off:** a baton (`baton.add`) or a pause (`pause.open`), which the next session
     must find whatever happens to this one;
   - **the session's end:** `session.close` or `session.pause`, and `banner.set`, which a
     clean close writes after its ledger entry (§6.3), so nothing of the close is left uncommitted.

   Every other write (a task's new, set, comment, touch, section, dep, promote and reopen; a
   question's new, raised and later; baton done, pause resume; decision set, link, relink and
   import; record stamp and correct; session start; housekeeping) **is still uncommitted and
   goes into the next commit**: it stays in the working tree until then. That commit is made
   while the engine lock is held, and carries **the committing session's op log lines that HEAD
   lacks, every file those lines name, and the op log itself**, so it takes every write of that
   session still uncommitted before it; another session's lines stay out unless they name a
   file it carries (below). (`init` writes the kit's files, not records:
   it logs nothing and commits nothing, and the session commits what it wrote.)
   - **Why milestones, not every write:** a commit per write grew history by a commit per board
     edit and cost every write a git process under the lock (about half a second on Windows,
     2026-10-13), for writes that cost little to lose: the next commit carries them, whoever
     makes it. What a
     milestone commits is what is costly to lose or must be at HEAD now.
   - **The policy is `[engine] commit`:** `"milestones"` (the default), `"every-write"` (each
     write operation commits), or `"off"` (the session commits by path, through `context-engine
     commit` or by hand, no later than its close or pause; no line reminds it). A pause record is
     committed at once whatever the policy, and a pause that cannot be committed refuses,
     keeping its record: a pause left uncommitted in a shared tree can be lost to another
     session's close. The older spelling still reads: `true` is `"milestones"`, `false` is
     `"off"`.
   - **The session's own commits take its uncommitted op lines too:** `context-engine commit
     <paths> -m <message>` commits those paths by path (`git commit --only`) together with the
     session's uncommitted op lines and the records they name, under the same lock, whatever the policy,
     and adds the `Session:` trailer. A plain `git commit -o` naming a record whose op line is still
     uncommitted commits the record without its line, which fails G-W7 on a clean checkout of
     that commit; `commit` never makes one. It runs no gate:
     the session runs the gate before it, as before every commit of its own (§6.3 item 7). Where
     `[gate] require` names a scope, it refuses a path in that scope that no green gate run
     covers (§8.5 G-V1).
   - **Why the op log goes with every record:** lint reads the two together. G-W7 checks a
     board item's session keys against the newest line that wrote them, so a record committed
     without its line fails lint on a clean checkout of that commit, even though the shared tree
     passes. An op line committed without its record claims a write that the commit does not
     contain, and no guard sees it
     (G-W7 walks the records that exist), so the engine never makes one.
   - **Why the session's lines, not every uncommitted line (this supersedes the earlier sweep
     for the default; CE-125):** the commit is derived from the op log against HEAD, not from what this
     process remembers, so every write of this session still uncommitted goes in. The earlier
     design took every other session's lines too (CE-45), as the commit their owner's milestone would have made. With
     two live sessions on one tree that commits one session's half-done work under the other's
     name, and a dead session's lines went into the next session's first commit unasked (adhoc
     AAR entry 22). So by default another session's lines stay in the tree, uncommitted, and the
     reply names them: `left uncommitted: <n> op lines of <key>`. Two kinds go in anyway, and
     the message and reply name whose they were (`including op lines that <key> left
     uncommitted`): another session's line naming a file the commit carries, since that file
     holds its write and G-W7 fails at HEAD without the line (a generated file, the decision
     index, holds every decision's state, so carrying it carries every decision's line, or G-D6
     fails); and a line that does not parse,
     which names no session. `context-engine commit --sweep` takes every line, the earlier way, for a
     session the owner or housekeeping knows is dead (it may also fit a repo run by one session
     at a time).
   - **The partial op log:** when lines stay out, the op log at HEAD is HEAD's own lines plus the
     lines taken, in working order. The commit builds it in a temporary index (`GIT_INDEX_FILE`:
     HEAD's tree, the paths as they are in the tree, that op log as a blob), runs `git commit` on
     that index, so hooks run, then sets the real index's entries for those paths to what was
     committed, as `git commit --only` does. The working op log is never rewritten. The order on
     disk and at HEAD can differ while lines stay out; once none does, a commit carries the
     working file whole and the two converge. Before the first commit every line goes in: there
     is no op log at HEAD to build on.
   - **Why by path and under the lock:** `git commit --only` on those paths leaves what another
     session staged or left untracked exactly as it was: nothing is unstaged, reset or stashed,
     and a `git add` of a new file is taken back if the commit fails. The lock is held from an
     operation's first write to its commit, so no other write lands between them, and the
     commit never reads a half-finished operation. Hooks run; a hook's refusal is reported, never
     bypassed. A slow hook holds the lock for as long as it runs, so another session's write
     can time out on the lock meanwhile; it refuses before it writes anything.
   - **One operation, one commit:** an operation that writes several files (an answer writes a
     decision and closes its question) commits them together, titled `engine: <op> <id>, ...`,
     this operation's first (a pause and a task close keep their own titles, with an `Ops:` line
     naming what the commit carries), and ending in the `Session: <key>` trailer. **No gate runs
     before the engine's own commits of its writes,** the gate's one exception (§11): the
     operation has already
     refused any write its schema forbids, and the gate still runs before the session's own
     commits (`context-engine commit` among them) and before every push.
   - **It never undoes the write.** Where it cannot commit, the write stands and the
     operation's reply says why (`not committed: <why>`), naming the by-hand commit. That covers:
     a merge, rebase, cherry-pick, revert or bisect in progress; a detached HEAD; `GIT_DIR`,
     `GIT_INDEX_FILE` or a similar variable set (inside a git hook, where a commit would go to that
     repo or index); `context.toml` not tracked by the enclosing repo (a target inside an
     unrelated repo, or a new repo before its kit is committed); the op log gitignored, or
     missing lines HEAD has; a record it would carry whose frontmatter does not parse (a hand
     edit in progress, which it would commit as it stands); a refusing hook; git refusing the
     repo; a `.git` directory present but no git executable. Only a target in no git work tree at all commits nothing
     and says nothing (the session's own `commit` refuses there). A named file that git ignores
     is left out, and the reply names it.
   - **A milestone that refuses after a write commits that write too,** since the op log at
     HEAD must not lag the files it names, and the refusal says what became of it; a close's
     `Closes:` is added only once its write is made, so a refused close never claims the item
     closed. A write that is not a milestone stays uncommitted until the next commit, refused or
     not. An operation that fails with an error other than a refusal can leave a partial change, which the next commit
     carries as it stands, named nowhere: lint then reports what is wrong with it.
   - **Branches merge the op log line by line:** two branches that both wrote op lines would
     conflict in it at every merge, so a repo keeps the op log on git's union merge driver
     (`<op log> merge=union` in `.gitattributes`).
5. **Background agents, gates and engine writes use locks** (G-V3) keyed on the tree hash. Each
   concurrent session runs its own MCP server process (§8.0.2), so the engine's lock is a file
   lock. *Built so far: the engine's write lock, one per repo rather than keyed on the tree
   hash; the lock on gate and background-agent runs is not built yet (CE-17).*

Most sessions run however Claude Code runs by default: in the shared checkout, with a worktree
only when opted into. So:
- **these rules are mandatory in the shared checkout;**
- **a worktree is recommended for building:** it removes most collisions at the source, at the
  cost of merging back;
- **a worktree session still writes its working state through the same rules on merge**:
  ledger entry, pause records committed, banner written only if unchanged.

### 5.6 The owner digest: how "inform and proceed" reaches the owner

Inform-and-proceed (§3.3) only works if the owner actually sees what was decided on their
behalf. Each session's chat close-out includes a digest of **at most 7 lines**:

- agent decisions of consequence, by id and one line each;
- criteria created, rewritten or retired, as counts plus anything surprising;
- owner questions raised (§5.3);
- anything the owner might want to push back on, flagged explicitly, including every PROVISIONAL
  call an agent made where the owner would otherwise have decided (§5.3).

**The digest is also written into the session's ledger entry** as its `summary:` block, so it
is tracked. Anyone using plain git sees what each agent session did and decided, without access
to the chat.

**Cross-repo question index, for agents, not for the human:**
- at session start, a generated file outside the repos, e.g. `~/.claude/owner-questions.md`
  (T3, generated and disposable), lists every open question across all repos, with
  `last_asked`;
- any session may add **one line** to its start-of-session reminder: "also N overdue questions in
  other repos: …";
- the source of truth stays each repo's own board.

**Deferred: an answer-in-place question file** for the owner: the engine generates a file of
open questions on request, a human answers in place, and the answers are read back and filed
against the questions. Until such a file is needed, the channel stays Claude remote
control.

---

## 6. Procedures

Procedures are written for agents, and their effects are checked by guards, so a skipped
procedure shows up red. This section says what each procedure must achieve, with its guards and
reasons. **The order of each procedure's steps lives in one place,
`docs/runbooks/procedures.md`:** each step with its engine command, its by-hand step (a section
of `docs/runbooks/manual-mode.md`, P16) and why it is done. A contract points there rather than restating an order.

**Item numbers are stable (P3)** and are labels, not an order: records cite them ("§6.3 item
6a"), and the runbook tags each step with its number here. A new item takes a new number (or a
letter suffix); none is renumbered.

### 6.1 Session start

**Full orientation:**
1. The contract loads automatically: global, repo (`AGENTS.md` for workflow, `CLAUDE.md` for
   product, mandates and gate, which imports the framework's own contract, §6.9), and subtree.
   In an adopted repo a `SessionStart` hook prints `orient` (the read in item 3) into the context at
   startup, resume, `/clear` and compaction. A failing hook is silent, so the contract keeps
   the by-hand `orient` as the fallback.
2. **Open batons and pause records: execute or resume them first.**
3. The board query, which prints the banner. **Raise NEXT-tier and overdue owner questions
   in chat now,** one line each (§5.3), together with any tier-2 flags from the background
   pass. **Show the owner the other open sessions too,** one line each, or say there are none:
   only the owner knows whether one is live in another window or died, and what to stop.
   Orient gives each one's last activity (its newest op log line or `Session:`-trailered commit)
   beside when it opened, so a dead session does not look as live as a working one (CE-104).
   The session stops or closes none of them on its own.
4. `show` the top item, or the one the owner assigned.
5. Read that item's `## Read first` list.
6. Read the rest of the orientation note (`HANDOFF.md`) **only if needed**, and record which in the `read:` receipt.

**With the engine, items 2–5 are one call.** `session.start` mints the key (§5.5), then
`orient()` returns, in one size-capped response: the banner; this session's open batons and
pause records, then other sessions'; the other sessions still open; the NEXT tier; owner
questions to raise; and the top item's brief, Traps and Read first. Step 1 is unchanged, and
item 6 is still on demand (the order: `procedures.md` § Session start). A **SessionStart hook** can run start-of-session housekeeping (§6.11)
and inject `orient()`'s output, so orientation costs no tool call (hook stdout reaches the
model's context; verified by a probe in the engine repo).

**Resume** (an open pause record of your own, or the owner says "continue"): re-check the tree
against the record, then continue.

**Background housekeeping agents: cheap checks first, escalation on a flag.** Fired at session
start, read-only.

**Tier 1, the check pass, uses cheap models.** Most of the work is checking, so it runs on the
cheapest model that can do it (set in config):

| Check | Looks for |
|---|---|
| **trace-check** | new or amended stories without criteria; criteria whose prose looks wrong against current code (DR3 candidates); census candidates after a design change |
| **inbox-check** | owner words not yet recorded: answers, stories or vetoes in recent chat summaries, commit messages, or edits to intent files |
| **question-check** | open questions overdue to be raised (§5.3) |

**Tier 2, escalation, happens only on a flag.** Each flag is routed to exactly one of:
- **a bigger agent**, for judgement or drafting: write the missing criteria, adjudicate a
  suspected semantic drift, run a census. It reports; it does not edit;
- **the main session**, when the flag needs action in the tree: it is put in front of the
  session at start and becomes a task or a baton;
- **the owner**, only when the "who decides" test (P8) says it is owner-only. It becomes an
  `ASK-n` row and is raised in chat (§5.3).

A tier-1 agent never escalates straight to the owner. The main session does that, so it can
check whether the question is truly owner-only.

Rules for all background agents:
- **Keyed on the tree hash, with a lock file** (G-V3).
- **Skip** if a report for an ancestor hash is under a day old and no intent file changed.
- **Discard** any report whose hash is not an ancestor of `HEAD`.
- **Budget:** the tier-1 pass is one cheap agent, or a few; tier 2 runs only on flags, at most
  two escalations per session start, and the rest are queued as tasks.
- **Models:** set per repo, per tier, in the framework config.
- **Persistence:** reports go to `.scratch/sync/<hash>/<agent>.md`.
- **The session triages and edits.** The agents only report (P11). The exception is
  housekeeping (§6.11), which writes only through the engine's `hk.*` operations.

Hygiene (caps, stale banner, expired batons) is **detected by the gate**. The mechanical
**repairs** (stamps, ratchets, regenerated indexes, expiring batons) are housekeeping's job
(§6.11), not the session's and not a checking agent's.

### 6.2 Intake: the owner gives intent

1. **Record it verbatim, now.** Behaviour-shaped intent goes into a story (a new story, an
   amendment, or a PRD section). Choice-shaped intent goes into a decision with
   `actor: owner`, or a charter edit. Tell the owner, in one line, which it became. Engine
   operations: `record new story` / `record amend`, or `record new decision` (or `ask answer`
   for an answer to an `ASK-n`), with `actor: owner`.
2. Link it to the charter goal(s). If none fits, ask: it may be a new goal.
3. Draft the criteria. They are **live by default** (§3.3). Show the owner **a digest of three
   to seven lines**, never files. If the story is `sign-off: required`, the criteria stay
   `planned` until the owner signs them off.
4. Owner-only uncertainties become `ASK-n` rows (§5.3); never guess at them. One whose
   recommendation is cheap to undo is not owner-only (P8): the agent decides it, PROVISIONAL,
   and flags it in the digest.
5. If the new intent contradicts an existing decision or criterion, say so at once, and record
   the outcome as a decision that supersedes or amends the old one. A story the owner withdraws,
   or one a new story replaces, is retired with the owner's words (`record retire`, §3.2). A
   story an agent reconstructed that the owner confirms is confirmed with their words (`record
   confirm`, §3.2).
6. **On a design change, run a criteria census:** every existing criterion in scope is
   classified KEEP / rewrite / retire, with the work assigned to tasks or slices. The census
   is an evidence doc.

### 6.3 Clean close (a natural stopping point)

**A session closes eagerly: as soon as every task it was asked for is done, in that same turn,
before its final reply.** It never asks whether to close and never sits open waiting for
instructions; what is left for the owner goes in the close's digest. It stays open only when the
owner says so; an awkward stopping point is a pause (§6.4), not an open stub. More work asked for
after a close starts a new session. The rule is in the contract, which every session loads, not
only in the procedures runbook, which a session reads on demand.

Write the records first, then run the gate, then commit what the engine has not (it commits at
milestones, and a task's close or the session's is one, §5.5 rule 4). What a clean close does,
numbered for citation (the order is below):

0. **Every owner word given this session is recorded** (story, decision, or question answer).
1. **Run the doc guards first, to see which failures earlier sessions left,** before adding any
   of this session's own.
2. Write the ledger entry:
   - the session key minted at start (§5.5); `session.close` writes over its `kind: open` stub;
   - a `rows:` line naming the items touched;
   - receipts:
     - the guard results;
     - `read:` what was read to start work (e.g. `board only` / `board + note`), which
       **measures how cheap orientation is (job 3)**;
     - `asked:` naming every open question at NOW or NEXT and every overdue one (the engine
       refuses the close otherwise);
   - `Still owed:`.
3. **Replace** the banner, in the way that is safe when several sessions write at once (§5.5).
4. Board operations: close (once the task's work is committed: the close's commit carries its
   `Closes:` and `Sabotage:` lines, §5.5 rule 4), a light reorder (the standup; the full
   re-rank is §6.14), mint (with the session key; a task names its `goals`, §5.2). Before a
   close, freeze each ACTIVE-PLAN doc whose items all close with it (`doc.freeze`, §6.7);
   `task.close` refuses until then.
   Hand-rewrite the summary / Traps / Read first of every NOW and NEXT item you touched.
5. Promotion (§6.7):
   - **5a. Rules and lessons:** promote durable rules into the contract; file method lessons
     into runbooks; change this document in place (§6.12).
   - **5b. The rest of §6.7's table:** an evidence doc for scratch worth keeping, a decision for
     a conclusion reached, `doc.archive` for a doc over its cap.
6. Anything skipped becomes a baton.
   - **6a. Pre-close housekeeping** (§6.11): carry out what this session recorded but did not
     finish (closes named by `Closes:` trailers, floor ratchets, stamps, regenerated indexes).
     Its operation list goes into the digest.
7. **Prove this close with lint and the gate's status,** then commit by path whatever the engine
   did not (`context-engine commit <paths> -m ...`, which takes any write still uncommitted, with
   its op line, §5.5 rule 4). Since the gate run in item 2's receipt, the close has written only
   records, which lie outside the code scope, so that run still covers the code (§8.5 G-V1): a
   second test run is needed only when `gate status` says the scope's id moved, and a repo
   without `[gate] require` runs the gate again. The scope's readers read those records, so where
   the scope names readers the close requires `<scope>+readers` and re-runs just the readers
   (`gate run --readers`) when the close's writes left them uncovered. Push only with
   permission, then watch CI (§6.8).
8. **Owner digest in chat** (§5.6, at most 7 lines). A pause gives the same digest, shorter.

**The order is not the numbering.** Items 2–4 and 6 are engine operations (`session.close`,
which refuses a malformed receipt; `banner.set`; the board operations; `baton.add`). The ledger
entry (2) comes after the gate because the close receipt carries the gate result, and after the
board operations (4) because `rows:` names what they touched. The steps in order, each with its
command and by-hand step: `procedures.md` § Clean close.

### 6.4 Pause (an awkward stopping point; the work continues next session)

Procedures may be shortened. **What is mandatory** (P9) is cheap, and protects everything that
cannot be recovered:

0. **Owner words given this session are recorded.** The most easily lost thing of all: they
   exist only in one session's transcript.
1. **Evidence has been moved out of `.scratch/`** into a tracked doc. It may be rough, dated and ACTIVE-PLAN.
2. **A ledger entry, `kind: pause`.** Three lines are enough: key, rows, `deferred:`. The
   ledger has one entry per session without exception, because staleness tracking depends on
   it.
3. **A pause record** (§5.4): in flight, resume step, uncommitted paths and branch, and the
   deferred steps. **Committed by path.**

**Deferred, not dropped:** the gate, the commit of the work itself, re-ranking, banner
replacement, runbook filing.

**With the engine:** items 2 and 3 are `session.pause(rows, deferred)` plus `pause.open(...)`,
which captures the branch and uncommitted paths itself. Both are milestones, so each commits
its writes by path, with any earlier writes still uncommitted (§5.5 rule 4); the pause commits
whatever the commit policy. The steps in order: `procedures.md` § Pause; picking the work up again: § Resume.

**Enforcement:**
- **G-W2:** at most N consecutive `kind: pause` ledger entries without a `kind: close`; N = 2.
- **G-W3** is separate: no baton or pause record older than two sessions.

### 6.5 Decision recording

**Actor vocabulary:** `owner` · `agent (<model-id>)` · `owner + agent` · `owner asked`
(the owner requested it and the agent chose how) · `owner reported + agent` (the owner
reported a problem and the agent decided the fix).
- **`unrecorded`**, only on an imported entry whose log names no one (CE-98): explicit and
  visible in the index, never a guessed actor.
- **With more than one human,** `owner` becomes `human:<id>`, e.g. `human:alice asked`. The
  charter names one owner per repo and lists the other humans and their **roles**: who may
  decide what (goals, priorities, a feature area). Other humans' stories are recorded under
  their own id; conflicts go to the owner. The "who decides" test (P8) routes a question to the
  right human. A single-owner repo may keep the bare word `owner`.
- The model id matters: "survives model changes" is otherwise untestable.

**Decisions are records: one OKF file per decision**, `docs/decisions/<prefix>-n-<slug>.md`
(`DEC-n` here), written only through the engine. "Why is X like this?" is answered by one small
file, not by grepping a large log, and append-only is enforced by a refusal, not by someone
reading diffs.

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
tasks: [T-96]
tags: [working-state]
answers: ASK-12                   # set by `ask answer` when the decision answers a question
reopen_if:                        # REJECTED only: what would justify reopening it
generated: { by: claude-code/<model-id>, at: 2026-10-08T14:02:00Z }
verified: ...                     # optional: the owner explicitly endorsed it; shape not settled (§9.3)
sources: [{ id: ev1, resource: /docs/evidence/<file>.md }]
body_sha: <hash>                  # covers everything above "## Amendments"
---
<the decision text, written once>

## Amendments
- **2026-10-09a (claude-code/<model-id>):** ...
```

**Operations:** `record.new` (CLI `record new decision`), `record.amend` (appends an entry under
`## Amendments`, keyed by session and actor; the only allowed body change), `record.stamp`
(freezes `body_sha` once and refuses a re-stamp; nothing ever replaces it, not even
`record.correct`); these three work on every append-only kind,
and so does `record.correct` (below). Then: `decision.supersede(old, new)` (sets both
directions under one lock and derives OKF `status`), `decision.set(id, fields, unset)` (a
decision's own keys: `decision_status`, `reopen_if`, `tags`, `title`, `description`; it refuses
`SUPERSEDED`, any status change on a superseded decision, `reopen_if` on a decision that is not
REJECTED, the link fields, `status`, `answers`, the provenance `actor`, `decided`, `session`,
`attribution`, `imported_from` and `generated`, and `verified` (an endorsement is owner words), so
it never writes half a link or re-attributes a decision), `decision.link(id, target, rel)` (a task,
story, criterion, decision or `file::symbol`, checked to exist when linked; `relaxes` writes its
backlink too), `decision.relink(id, old, new)` (moves one `code:` link of a current decision when
the code moves, the new one checked as `link` checks it, so it must name a repo file and symbol, never a blank, a directory or a path outside the repo; id links never move and a superseded
decision's links are history), `decision.find(text, tag, status, links_to)` (one-line rows),
`decision.show(id, section)`, `decision.import(path)` (below), and **`why(target)`**: given a
task, criterion, decision or `file::symbol`, the decisions that link it, each with the field
that does. Writing a decision costs only its own text; no session opens the log to append to it.

**Corrections are bracketed insertions.** A strict body hash forbids fixing a typo in place.
`correct(id, after, text)` inserts `[text]` right after the one place `after` occurs and logs
a `corrected:` line under Amendments that says where it inserted what. It can only insert:
removing every bracket it added gives back the original body exactly, so the words as typed
always survive. `body_sha` is not re-stamped: it keeps pinning the words as typed, and G-D10
hashes the body with the logged insertions undone, so a record whose `corrected:` lines do not
match fails, and so does a bracket whose `corrected:` line was deleted.
The aim is what was meant, not an exact copy of every slip in what was typed; verbatim quotes keep the
flavour and let a later reader check whether they were misread. A change of meaning is an
`amend`, never a correction. Applies to every append-only kind.

**Organisation:** records are stored by id; topic is a tag, and the generated index groups by
tag. Topic narratives ("why is it like this at all") stay as prose docs that link decisions.
Small engineering calls may live as task comments, and are promoted to a decision when they
turn out to matter.

**Status:** BUILT · PROVISIONAL · DEFERRED · SUPERSEDED · REJECTED. Rejected approaches are
decisions with `reopen_if:`, so "what was rejected that touches X" is a query.

**Links:**
- `supersedes` / `superseded by`;
- `relaxes` / `narrowed by`;
- `creates / amends / retires: S-n, C-n`. These feed the census and trace-check, **not** a
  freshness guard (P13);
- `tasks`, `code` (`file` or `file::symbol`) and `refs` (any other record), which `why()` reads.

**Amendments** are dated entries under `## Amendments`, keyed by session and actor, never edits
to the body.

**Negative results** ("built and rejected; do not re-derive these") are `decision_status:
REJECTED` records. Each says what was tried, the evidence, and in `reopen_if:` what would justify
reopening it. The generated index lists them in their own group.

**A generated index:** an OKF `docs/decisions/index.md` (no frontmatter, list shape, §9.3)
built **from frontmatter**, grouped by status (in the kind's enum order) and then by each
decision's first tag, one line per decision: id, link, description or title, actor and date, and
`superseded by` where set. Every engine write to a decision regenerates it under the same lock
(`[working] decision_index`), and `hk.regen_index` regenerates it on demand. Because nothing
parses prose, its check (G-D6) is byte equality with a regeneration; the check of content from a cutoff
id onward is needed only for indexes still built by parsing prose.

**No splitting by period.** One file per decision has no single-file cap to hit. The growing thing is
the index (DR11); one line per decision keeps it small, and superseded decisions can collapse
into a group.

**Existing single-file logs** (heading form `### D-n — title *(actor, date)*`, or `--` for the
dash) migrate with `decision.import` (§11.4): every entry keeps its number and its text verbatim,
stamped, and an id in another prefix takes the kind's with its old id as an alias; a heading's trailing note (`SUPERSEDED by D-n`, `relaxes D-n`, ...) becomes links in
both directions plus an amendment; and a "built and rejected" table becomes one REJECTED record
per row, with new ids and `refs` to the entries that hold the reasoning. It writes all or
nothing, and **never loses text silently** (CE-98): an entry runs to the next entry heading (the
last to the end of the log), and a `#`/`## ` heading inside it stays in its text; whatever no
record holds (before the first entry, an empty group heading) is named by line in its output;
and a line it cannot read refuses, naming every such line: an id-like `### ` heading that is not
an entry (`D-107 FIX`, a letter id such as `D-159b`, an indented or dressed entry heading), which
goes under its parent's `## Amendments` (an entry's own `## Amendments` becomes its record's
first amendments, and a `## ` heading after it refuses), an attribution with no actor or a date
for one, and a fence or comment never closed. Headings in fences and HTML comments are text. Until a repo migrates, its log is read as it is; the read adapter is not built.

### 6.6 Delegation and build rounds

**Reading and auditing:**
- verdicts plus `file::symbol` evidence, never dumps;
- each agent persists incrementally to its own file;
- check the file exists on return, and persist on receipt if it doesn't;
- `Explore` cannot persist;
- agents audit; the session decides.

**Ultracode** (the `Workflow` tool, multi-agent orchestration) needs no per-request opt-in when
it keeps the session's own context and tokens down: bulky reading, auditing or verification
pushed into agents, only verdicts kept.
- What decides how work is split is its shape, not permission: a real fan-out with a reconcile
  step;
- one check goes to one agent, not a fan-out, and coupled work is not split up to go "faster".

**The coordinator:** the top-level session coordinates and does not do the work itself. It takes
this role for every request, one task or several, and by default whenever the board is worked.
- each task, even a lone one, goes to its own subagent through ultracode; that agent owns the
  task end to end, can persist (not `Explore`), and pushes the work down again, to its own
  subagents or a workflow;
- told to check something, the coordinator sends an agent; to verify, it sends another agent,
  never the one that did the work, and the work a commit, a push or a record write carries is
  verified that way first;
- every subagent persists its output to its own file as it goes, so a session that dies loses
  nothing;
- the top-level conversation stays clear: progress, blockers and delays, then the digest;
- tasks that touch the same files go to one agent or run in sequence (disjoint ownership,
  below);
- three things stay with the coordinator: it records owner words verbatim (§6.2), since only it
  holds the transcript; it makes the final call on a verifier's verdict, reading the report, not
  the files; and trivial bookkeeping (one engine op, `git status`) is done inline.

**The full re-rank** (§6.14) has the same shape: one ranking agent proposes and persists, a
second, different agent verifies, and the coordinator applies the moves that are its call and
raises the rest to the owner.

**Build rounds:**
1. map;
2. plan, with a critic;
3. BDD: criteria first, `planned`;
4. build in waves with **disjoint file ownership**, and **no fan-out on a dependency chain**;
5. integrate, with sabotage;
6. adversarial review through several lenses;
7. flip the statuses.

No `git stash`. Workflows are tracked files. How to run each step, and how to delegate,
persist and watch: `docs/runbooks/fan-out.md` (§7.5).

**Model choice** is per-repo config (§8.0), with one rule that applies everywhere:
- **Do not use `fable` subagents unless the owner asks for them or they are really necessary.**
  Never fan out with fable: it wastes tokens.
- When it really is necessary, do whatever minimizes its cost: one agent, the narrowest prompt,
  a capped output, verdicts back rather than prose. Say why in the session summary.
- The default for delegated work is the cheapest model that can do it: a watcher needs the
  least, bulk reading and a census a little more, code and review the most. The repo's
  contract names the models.

### 6.7 Promotion and demotion

| From | To | When |
|---|---|---|
| owner words in chat | story, decision, or question answer | immediately (§6.2) |
| scratch | evidence doc | the same hour |
| evidence | decision | when a conclusion is reached |
| decision | contract | when it becomes a durable rule (the contract keeps a pointer) |
| a lesson about method | runbook | at clean close |
| memory | contract (global or repo) | when the lesson proves general |
| baton or pause record | board task | after two sessions, by housekeeping (§6.11) |
| closed board item | a `closed:` line in its `## Log` and its id in the ledger `rows:`; the file stays in place with `state: closed` | at close |
| a component over its cap | archive with a redirect table | when the guard warns |
| ACTIVE-PLAN doc | FROZEN | when its item closes |

Two rows are engine operations. **ACTIVE-PLAN to FROZEN** is `doc.freeze`, which writes the
FROZEN line G-D4 reads (§7.2), and `task.close` refuses to close the last open item an
ACTIVE-PLAN doc names until that doc is frozen, so the close and the freeze land in one commit
and G-D4 is never red between them. **Archive** is `doc.archive`, for a whole doc (§7.3). The
other rows are the session's judgement: a clean close walks them (§6.3 items 4 and 5), and
housekeeping turns old batons into tasks (§6.11).

### 6.8 Push and CI

- gate before every push; where CI runs on a different platform from the session's machine,
  also run CI's job for that platform locally, in a container set up like CI's runner
  (`gate.md`);
- push only with permission;
- a background CI watcher for every push, keyed on the commit hash; the push is not done until
  the watcher reports;
- the watcher only watches.

The steps in order: `procedures.md` § Push and CI.

**A push hold**, when the owner imposes one, is a single line at the top of the contract naming
the hold and where it is recorded.

### 6.9 Bootstrap (a new repo)

The engine ships an **adoption kit**: text only, as package data beside the engine's code
(`kit/`), readable in the engine repo too. It holds the config template (`context.toml.template`,
which is the config schema), the kit block for `CLAUDE.md` and the contract it imports, the
`SessionStart` hook, skeletons for the orientation note, charter, criteria and ledger, the runbooks (`procedures.md` and `manual-mode.md`, so the
repo can run every procedure by hand from its own tree, P16; and the method runbooks of §7.5), and a README with the install,
bootstrap and upgrade steps. The steps in order: `procedures.md` § Bootstrap.

**The kit block:** an adopted framework must not depend on the owner leaving
`CLAUDE.md` alone, so `CLAUDE.md` carries only a short block between the kit markers: the
`framework:` line and an `@`-import of `docs/framework/contract.md`. The framework owns that
file: an upgrade replaces it whole, G-D0 fails when it differs from the installed engine's copy,
and the repo's own rules (its gate command among them) live in `CLAUDE.md` outside the markers.
A `SessionStart` hook runs `orient`, so the session-start read does not rest on the agent
obeying a rule; its command names the machine's engine interpreter, so it lives in the
machine-local `.claude/settings.local.json`. That file holds the owner's permission grants, so
an existing one gains the hook only with the owner's yes (`init --merge-settings`), and nothing
else in it changes. **Standing permissions stay in owner-loaded files**
(`CLAUDE.md` and what it imports; harness permissions in the settings files), never in MCP
instructions or `orient` output: an agent rightly discounts a grant that arrives as tool output.
Working instructions may come from any of these three sources; a grant may not.

1. The owner gives, in chat: a charter (about a page), the first stories, and any mandates.
2. The agent installs the engine into its own environment, pinned to a release tag or commit:
   a non-editable install in `.context-engine/env/` in the repo's root, gitignored (the
   kit README § 1 gives the lines and where the interpreter sits in it). The engine runs from that
   environment and is never installed into the repo's own, so the repo never imports it; it lives
   inside the repo's folder, so everything the repo runs is there, and a clone rebuilds it at the
   ref the ledger names. A kit change made in the engine repo reaches the repo only when its pin
   moves (the upgrade procedure, §8.0). The MCP
   server (§8.0.2) is optional until the §8.0.3 trial reports (§11.1): the CLI carries every
   operation, and a repo that wants the server registers it here.
3. `context-engine init` writes the kit into the repo: the layout (§10), `context.toml`, the
   runbooks, the kit block appended to `CLAUDE.md`, the contract it imports, the hook, and
   `.context-engine/` appended to the repo's `.gitignore` when nothing there ignores it. It
   only creates files and never overwrites one; by
   hand, copy the kit's files as its README says. The agent then fills the charter and the
   config, with a provenance note on every cap, and checks the id prefixes against ids the
   repo already uses, then commits the kit's files by path before the first session starts:
   the engine commits (§5.5 rule 4) only where `context.toml` is tracked.
4. The agent drafts criteria and shows a digest, opens questions, and builds the first board.
   Then it sets the correctness chain's sources in `[guards]` (§8.1): if they were set before
   the first stories and criteria were recorded, the guards would be red on a source that is
   still empty, and the first session could not open on a green lint.
5. First clean close: the guards are green, the ledger entry is `kind: close`, and the first
   `banner set` (with `--seen none`) writes the banner heading.

### 6.10 Humans working outside the procedures

The owner works mainly through Claude remote control, but the repo **must keep working for
someone using plain git or writing code by hand**. Humans are never required to follow the
procedures. The agent sessions absorb the cost:

1. **Agent commits carry a trailer** `Session: <key>`. Commits without one are **foreign**.
   It sits in the message's last paragraph, the only one git reads as trailers, with every
   other trailer (`Co-Authored-By:`, `Closes:`) and no blank line among them: a `Session:` line
   followed by a blank line and another trailer is no trailer to git, so the commit reads as
   foreign (seen 2026-10-13, three commits; the template is manual-mode § context-engine commit,
   and a test reads it back with git). One task per commit, its id leading the title (`CE-n: what changed`; the prefix is the
   repo's own, `[kinds.task] prefix`). The task's close carries `Closes: <id>` in its own commit
   (§5.5 rule 4), not its work commits; a commit made outside the engine that finishes a task
   carries it instead, and housekeeping closes the item (§6.11). Small tasks may share a session: the gate goes green over all of
   them, then each is committed by path (`context-engine commit`, §5.5 rule 4). The engine's
   own commits carry the trailer too; a task's close leads its title with the id, and every
   other engine commit has no task id: it records working state, not a task's work. An engine
   commit also carries whatever was still uncommitted before it, other tasks' board writes included, and
   its `Ops:` line names them: the one exception to one task per commit.
2. **At session start, reconcile foreign commits** made after the newest `start head` (§5.5
   rule 1) recorded by a session keyed before this one, up to and including this session's own
   start head, leaving out those a `kind: foreign` entry already names. These ranges partition
   HEAD's history: every foreign commit is exactly one session's, the first session whose start
   head it is at or before, however many are open at once; a commit made after the newest start
   head is the next session's. A later key's start head is no baseline (that session may not
   have reconciled yet), and neither is the newest commit touching the ledger: another live
   session's milestone commits the ledger and would move it past foreign commits nobody has
   reconciled (CE-65). A start head no longer in HEAD's history (rebased away) is dropped, and
   a session whose own start head is dropped reconciles up to HEAD. Two cases can then report a
   commit twice, though none is skipped: a session's own start head rebased away (its range
   and the next one's overlap), and a merged side branch (a start head on the branch is not on
   the first-parent line the next baseline is taken from); the `kind: foreign` entry, once
   written, keeps a named commit out.
   Before any earlier entry records a start head, the baseline is the newest commit touching the
   ledger that this session did not make; at that switch-over a foreign commit can be skipped
   once, the bug the start heads remove. A session that records its start head and dies before
   reconciling leaves its range unreconciled. The engine's ledger module computes the list
   (`foreign_commits`; no command runs it yet). The steps and the entry's format:
   `procedures.md` § Reconciling foreign commits:
   - write a ledger entry `kind: foreign` summarising them (author, what changed);
   - run the tier-1 trace-check over them, to check what criteria or prose they may have made
     stale;
   - check them for stated intent (the inbox-check): a commit message or doc edit that states a feature or
     decision is recorded as a story or decision, `via: commit <sha>`, attributed to its
     author.
3. **Everything a human needs is readable without an agent:**
   - the banner and board in plain markdown;
   - the per-session `summary:` in the ledger;
   - guards runnable with one command, with readable failures that name the remedy (§8.0).
4. **Fixing a guard that a human's commit turned red is the agent's job.** A human commit that breaks a doc guard is not
   reverted; the next session fixes or reconciles it and records that in the ledger.

### 6.11 Housekeeping

Housekeeping is the repair pass for things that should happen and keep being forgotten. It is
done by tools, so nothing is broken by hand, and a script or MCP operation is tried **before**
any edit agent.

**Three tiers; most housekeeping needs no model:**

| Tier | Who | Does | Example operations |
|---|---|---|---|
| 0 | **a script that calls no model** (`process:housekeep`) | deterministic repairs | stamps; floor ratchets; regenerated indexes; flagging and converting expired batons; turning stale `kind: open` stubs into `kind: abandoned` plus a baton; stamping `last_asked` from `asked:` receipts written by hand |
| 1 | **small agents restricted to the engine's `hk.*` operations (MCP tools `hk_*`)** | reading unstructured text, writing through typed operations | commits since the last session → dated task comments; clearing a pause record whose paths are now committed; reconciling foreign commits (§6.10); spotting owner words not yet recorded (reported, not written) |
| 2 | **the main session** | every judgement | ranking, criteria, task bodies, answers, closes without evidence |

**The rule: housekeeping carries out intent that is already recorded somewhere; it never forms
new intent** (P11 exception).

**By hand** (no engine, or no housekeeping agents), the main session does every tier's
mechanical part itself, in the order `procedures.md` § Housekeeping gives, marking each write
`mechanical` in the op log.

**Closing is the hard case.** No tool auto-closes on its own judgement: calling a close
"mechanical" would only hide that someone decided to close it.
`hk.close(id, commit)` closes only when that commit **really carries** `Closes: <id>` (the engine
checks git, not the agent's word) or the session's ledger entry names the item as closed, and it
cites that evidence in the close message (G-W9). Otherwise housekeeping proposes the close and
the session approves the batch.

**When:**
- **At session start: reconcile** what happened since the last session: foreign commits,
  other sessions' leftovers, stale open stubs, overdue questions. A SessionStart hook can run
  tier 0 (§6.1).
- **Just before close: carry out** what this session recorded but did not finish (§6.3 step
  6a).

**Safety:**
- every `hk.*` write is stamped `--mechanical` with its actor, is logged, and lands in a
  commit by path with a `Session:` trailer (it stays uncommitted until the next one, §5.5 rule
  4), so
  `git revert` undoes it. A
  commit whose message says it also carried another session's leftover lines reverts those
  too: revert such a commit by path instead.
- writes per run are counted and measured; a cap is optional and off by default (G-W10);
- the run's report **is** its operation list, and it goes into the owner digest (§5.6);
- the run takes the engine lock, because another session may be live in the same tree.

**Tool restriction is what makes "cannot break things by hand" true.** A tier-1 agent gets no
`Edit`, `Write` or `Bash`; its tool allowlist names only the engine's `hk_` MCP tools (§8.0.2).
Fencing `Bash` to one script through permission rules is weaker, because those rules apply to
the whole session.

**Edit agents** (agents that hand-edit files on the session's behalf) are deferred until the
script and MCP prove insufficient.

### 6.12 Keeping this document current, and the after-action review

**This document is updated as we build.**
- A change to how the framework works is made here, in place, in the same session as the work.
  This document keeps no change log: the reason for a change is its decision or story, and git
  holds the old text.
- **A huge change that the future may need to reference** (a rewrite that changes the shape, or
  a design that was tried and dropped) first copies the current file to
  `docs/framework/FRAMEWORK-v<version>.md` and opens the copy with `ARCHIVED <date>` (§7.3), so its
  old LIVING line no longer counts (G-D4). Archived copies are frozen once written.
- If the old text will never be needed, do not archive it.
- What belongs here is the framework: what it is for, its rules, components, procedures, tools and
  guards. Origin stories, prior art, owner Q&A and change history go to decisions, stories,
  evidence docs or an archived copy.

**After-action review (AAR): a first note, not a design.**
- Intent: each session leaves a short record of **what worked well** and **what could be
  improved**, so that the framework can later be assessed and improved from evidence instead of
  from memory. Using a fallback (P16) and any procedure step that cost more than it was worth belong
  in it.
- **Open, to be designed when the owner takes stock:** where it lives (a field of the ledger
  entry, or its own record kind); its shape and cap; whether `session.close` asks for it;
  who reads it, when, and what turns a recurring note into a task or a framework change.
- Not built, and no guard checks it. Until then a session that has a note can put it in its
  ledger `summary:`.

### 6.13 Rollback and close (not designed)

A session can end by undoing what it changed instead of saving it, without breaking other
humans or agents in the same checkout (a shared directory, not a worktree). Design notes: the
shared-tree rules (§5.5) rule out `git stash`, `git reset` and checking out whole files another
writer may also have touched; candidates are `git revert` of the session's own commits (found by
`Session:` trailer; one that carried another session's leftover lines, §5.5 rule 4, is reverted by
path) plus restoring only the paths the session's op log says it wrote, recorded as
a ledger entry of its own kind. Owner words recorded this session stay (§6.3 item 0). Its by-hand
fallback is a runbook section (P16). Not built yet (CE-18).

### 6.14 Rerank (the sprint)

The full re-rank of the open board against the charter's goals and its **next milestone**: one
named milestone with its exit criteria, in the charter's § Next milestone. Clean close keeps only a
light reorder (§6.3 item 4, the standup); this is the sprint, which reads every open item and so
runs once a sprint, not once a session. It forms new intent (an order), so it is not housekeeping
(§6.11).

**When:** NEXT holds no task while tasks are open (whatever NOW holds; an owner question is not
a task), or the owner asks. Orient says "rerank due" only in the first case; the
charter's `Last rerank:` line records when the last re-rank ran and is quoted
beside it, never a trigger. It flags; it never runs the re-rank. Every open task names, in `goals`, the
charter goals it serves (G-I1, where `[guards] task_goals` is set), so the re-rank has a goal to
cite for each item.

1. **Propose:** the coordinator sends a ranking agent (judgement, so the strongest model the
   contract names) to read the goals, the milestone, and every open item's brief and deps. It
   persists its proposal to its own file and returns, per item, keep, promote, demote or drop,
   each with a one-line reason citing a `G-n` or an exit criterion; an item serving no goal is
   flagged for SOMEDAY or retirement.
2. **Verify:** a second, different agent checks the proposal: no item above an open item it
   depends on, NOW holds one, NEXT at most five, every move cites a goal or criterion (§6.6).
3. **Apply:** the coordinator applies the promotes and demotes (cheap to undo, so the agent's call,
   P8), one task comment per move carrying its reason, and flags every move in the close digest.
4. **Owner calls:** drops, retirements and a change of milestone wait for the owner, raised as
   owner questions with the proposal's reason as the recommendation.
5. **Record it:** the session's key replaces the charter's `Last rerank:` value (the one charter
   edit that needs no owner), committed by path.

---

## 7. Record layer details

### 7.1 Session ledger

- **One entry per session, without exception:** `kind: open` (the stub `session.start` writes,
  §5.5), then `close` or `pause`; `abandoned` for a stub that housekeeping found was never closed; and
  `foreign` for reconciled human commits (§6.10), which the session writes by hand from the runbook. *Not built
  yet (CE-6): housekeeping does not write `abandoned`; until it does, a stale stub is marked by
  hand (the runbook's housekeeping step).*
- **Written by the engine:** `session.start`, `session.close`, `session.pause`. The receipts
  are checked when the entry is written, as well as by the gate (G-W6).
- Append-only, newest first, **in its own file**, keyed by session key: **one file under the
  engine lock**, not one file per entry, until a trial shows append collisions.
- Rotate by period when it passes its cap; the current file indexes the periods. *Not built
  yet (CE-6): adopted by trial (§11.4) once a ledger cap is set.*
- **Not an OKF `log.md`** (§9.3): it is a session journal, not a concept changelog.

### 7.2 Evidence and plan docs

- One per item or investigation, dated, with its liveness declared near the top (G-D4). While
  ACTIVE-PLAN it names its board item there, and dated corrections are added at the top.
  It freezes when the item closes: a FROZEN line with the date goes above the old declaration
  (`doc.freeze` writes `FROZEN <date> (session <key>): <why>`), before the item's close.
- The task row is the index and the doc is the body: `show <id>` alone must be enough to
  resume.
- A TODO the author left in a frozen doc marks a known gap; it is not an instruction to whoever
  reads it now.

### 7.3 Archive

- `git mv` the material, never repair it.
- First line: `ARCHIVED YYYY-MM-DD`.
- One redirect table per archive directory: its `README.md`, one row per archived doc (old path,
  new link, date, why). Nothing else in an archive is repaired, extended or kept current.
- Archive headings act as the index (`## Pruned from HANDOFF.md on <date>`).
- **The engine's operation is `doc.archive`** (CLI `doc archive <doc> [--to <dir>] [--why]`): a
  whole `.md` doc, tracked and committed, without frontmatter, moved into `--to` or `[working]
  archive`, first line `ARCHIVED <date> (session <key>), from <old path>.`, its row added to the
  directory's `README.md` (created LIVING by the first archive there). It is not a milestone: the
  next commit carries the move, which git shows as a rename. Pruning part of a file under a dated
  heading needs a judgement of what goes, so it is done by hand (`manual-mode.md`).

### 7.4 Residual-risk register vs unverified hazards

- **Residual-risk register:** the risks left after their controls, the traps a session must
  know; not a second set of rules. Its entries change only when the code does. LIVING, part of
  the rules layer. An entry carries `stale_after` only if it is about something external.
- **It is P17's register of residual risks.** Each entry says what the risk is and whom it
  affects, why it was not eliminated, how it is controlled (the P17 rung, and the guard or rule
  by name), and where it came from (task, decision or incident). Entries arrive
  from a task's design review when it closes (§5.2), and from any session that notices a risk
  and confirms it (an unverified hazard, once confirmed, below).
- **Where it lives:** one markdown file named by `[working] register` (a target repo:
  `docs/invariants.md`, §10). It is not a record kind, so it is read and fixed by hand (P18 A).
  Each entry is `## INV-n: <risk>` followed by four lines: `- **affects:**`, `- **why not
  eliminated:**`, `- **control:** <rung>: <guard or rule>` and `- **from:** <task>, session
  <key>`. `INV-n` ids are never reused: the next is one above the highest in the file and in
  any `register.append` op, so an entry deleted by hand does not give its id to another risk. `context-engine register show` prints it; G-W13 checks
  that every closed reviewed task's residuals are in it and that every entry is whole.
- **The register is handed over with the work:** the engine's own register is
  `src/context_engine/REGISTER.md`, shipped as package data, so it travels with the engine to
  every repo it is pointed at (§11), as the Design for Safety regulations (P17) hand the register
  to whoever next takes the structure over. There, `context-engine register show --engine` reads the installed copy,
  and `orient` adds one line pointing at it whenever the repo's own register is another file.
- **Unverified hazards:** volatile suspicions ("do NOT fix blind"). They live in the orientation note
  or on the board. When resolved, each becomes a register entry, becomes a fix plus a ledger
  line, or is dismissed with a ledger line.

### 7.5 Runbooks

Runbooks hold **method**, which survives when the status around it is archived. Each is one file
under `docs/runbooks/`, short, and routed (§2). Each method runbook declares in its frontmatter
how it changes (`mode: replaced`) and its liveness, whether it is kept current (`liveness:
LIVING`; P2), which G-D4 checks.
- `docs/runbooks/procedures.md`: every procedure's steps in order, each with its engine command,
  its by-hand step and why it is done; the only place a procedure's order is written (§6). A test in the engine
  repo checks that every §6 subsection has its steps or says why it has none, and that every
  step names an operation that exists;
- `docs/runbooks/manual-mode.md`: every engine operation done by hand, each step with why it is
  done (P16); a test in the engine repo keeps it in step with the CLI;
- `docs/runbooks/gate.md`: running the gate so its result is true (the exit code, a worktree's
  code, a red gate), and the **test baselines**: one dated baseline per suite, and an
  *unexplained* regression is a blocker. The gate's own suite takes its baseline from the newest
  ledger entry's `guards:` receipt; a suite outside the gate keeps a dated line where the
  repo's contract names it;
- `docs/runbooks/sabotage.md`: seeing every new test, guard or refusal fail before believing it
  (P7), and the traps that make a sabotage pass falsely; the fallback for G-T5;
- `docs/runbooks/fan-out.md`: delegation, persistence, watchers, worktrees and workflows, and the
  build rounds of §6.6 step by step, with the same numbers;
- `docs/runbooks/release.md`: tag, publish, confirm the version is live, and the fresh-user
  install trial of every published release.

**Generic method, repo values:** every runbook here is the framework's. They ship in the
adoption kit (§6.9) and `init` copies them, so they carry no repo values and no repo ids, and a
test in the engine repo fails on the engine repo's own ids and machine paths. A repo's own values stay in its contract
(`CLAUDE.md`), which the runbooks point at: its test command and interpreter, its CI workflow,
its suites and their baselines outside the gate, its models, where its sabotage probes are kept,
and its release steps, index and declared floor. In the engine repo each runbook is byte-equal
to its kit copy, so a fix lands in both; in an adopted repo they are the repo's own from `init`
on, and move only on upgrade.

**Skills point, runbooks hold.** The engine's Claude Code plugin (§11.2) has a skill per
procedure. A skill is what makes the procedure come to mind when it starts; it names its section
of `procedures.md` and holds no steps of its own. The few lines it adds, the traps sessions miss,
are quoted from the sections it names word for word, and the engine's gate fails when a quote no
longer matches them, so a changed runbook cannot leave a stale copy behind; the runbook stays the
source and the by-hand fallback (P16). The contract is never a skill: a skill
that does not trigger fails silently (P7), and the contract must hold in every session.

---

## 8. Tooling and verification: the record engine and the guard catalogue

### 8.0 Packaging: the record engine

- **One versioned package, the record engine** (`context-engine`), plus a per-repo
  config, `context.toml`. The same package owns record writes (§8.0.1–8.0.3) and the lint. The
  kit's `context.toml.template` (§6.9) is the config's schema: every key the engine reads, with
  its default, and the engine refuses a table or key it does not know, a `[working.caps]` tier
  no board kind's `pri` names, and a value of the wrong type. The config holds:
  - enabled guards;
  - paths: the routing map of components onto files (`[[routes]]`; not `docs/index.md`,
    because OKF fixes `index.md`'s shape, §9.3.1);
  - the record kinds and their schemas (`[kinds.*]`, §8.0.1);
  - caps;
  - cutoff ids;
  - model choices for background agents;
  - an optional housekeeping write cap (none by default) and the stale-stub window.

  Guard switches are `[guards] off`, and `[guards]` also lists what the doc guards read.
  *Not built yet: cutoff ids (only an index that parses prose needs them, and none does),
  model choices (CE-12), the housekeeping cap (G-W10, CE-6) and the stale-stub window (G-W11,
  CE-6) are not config keys yet.*
- **Every tuned value carries a provenance note: MEASURED or JUDGEMENT, with the method and
  what would make it wrong.** A test refuses values copied from spec examples (G-D9).
- **G-D0:** the contract's `framework: <major.minor>` equals the installed engine's
  major.minor. The framework is versioned `major.minor`; the engine is `major.minor.patch`, and
  its major.minor is the framework version it implements. An engine fix moves only the patch; a
  framework change the engine must follow moves the minor of both. Below 1.0 is draft; there is
  no `-draft` suffix. `0.5.*` is accepted as a synonym of `0.5`. `context-engine lint` checks
  every `framework:` line of the contract (`contract` in `[engine]`, `CLAUDE.md` by default),
  and the version in its kit block's begin marker. A missing contract, a missing line, or a value
  that is not `major.minor` fails it too, and each failure names the remedy. A kit block
  of the engine's version must be the kit's block text (`kit/bootloader.md`), and the file it
  imports must exist and equal the installed engine's `kit/contract.md`, line endings aside;
  `orient` opens with these failures, so a session whose contract did not load is told
  at once.
- **Upgrade procedure:** bump the engine's pinned ref (rebuild its environment,
  `.context-engine/env/`, at the new ref, §6.9 step 2) and the contract's `framework:` line, run the lint, fix the failures, and write a ledger line
  naming the new ref. The kit's contract replaces `docs/framework/contract.md` whole, and the
  new kit block replaces the old one between its markers.
- **Existing repos keep their own check numbers.** The package maps its ids onto them and
  never renumbers them (P3).
- **A tool that refuses something names the remedy.** Every failure says what to do.
- **Every guard docstring says what it deliberately does not check** (P7).

### 8.0.1 Record kinds and change modes

The engine is **one core with several record kinds, not a bigger task tool.** The core does OKF
read and write, id allocation under a lock, the operation log with session stamps, write-time
refusal, and the lint framework. Each kind is a small schema in config, with one of three change
modes (P2):

| Change mode | Kinds | The engine enforces |
|---|---|---|
| **append-only** | decisions, stories, deviations (*not built yet*, §3.5) | a `body_sha` over the original body; `amend` appends a dated entry and is the only body change (`correct` is the logged exception for every append-only kind, §6.5, and keeps the stamp); G-D10 recomputes the hash with logged corrections undone |
| **replaced body, tool-owned frontmatter** | tasks, owner questions (`ASK-n`) | frontmatter changes only through operations carrying the session key; bodies are hand-edited or set one section at a time (`task.section`) |
| **session-stamped** (`mode = "stamped"`) | batons, pause records | a session key on creation; expiry after two sessions; housekeeping converts the expired ones |

**Not record kinds:** criteria (they live in `.feature` files or a criteria doc, plus test
annotations such as `@pytest.mark.criterion`, and the trace guards read them in place); ledger
entries (one file written only through `session.*` under the lock, receipts checked by G-W6;
append-only by rule, with no `body_sha`); the charter, contract, residual-risk register,
runbooks and evidence docs (prose, checked by the doc guards); verification state (owned by the gate's run
ledger, G-V1). The banner is prose, but the engine stamps its key and guards its write (§5.5).

**Every kind round-trips unknown frontmatter keys,** as OKF asks (§9.3), so a key a human adds
by hand survives the next tool write.

**`aliases`** (every kind) lists a record's earlier ids from before an import (§11.4); `show`, `why`,
`find`, `link` and `supersede` resolve one to its record and say so, and G-D2 refuses one that
reads as a series' or a criterion's id, or is another record's alias.

### 8.0.2 Three entry points, one library

| Entry point | For | Notes |
|---|---|---|
| **CLI** | humans, Bash, the gate | `context-engine <noun> <verb>` |
| **MCP server** | agents | a thin wrapper: each MCP tool calls the function its CLI subcommand calls; both look the operation up in `ops.OPS` (`python -m context_engine.mcp`) |
| **Housekeeping script** | the gate, hooks, §6.11 tier 0 | no model; actor `process:housekeep`. *Not built yet (CE-6)* |

**The MCP server is local and per session; nothing has to be run by hand.** It uses the
**stdio** transport: Claude Code starts it as a child process when a session opens in the repo,
from the engine's own interpreter (never the target repo's environment), and ends it with the
session. There are no ports, and each concurrent session gets its own process.
- **Set-up is a local-scope registration, once per machine:** `claude mcp add --scope local
  context-engine -- <interpreter> -m context_engine.mcp`, stored in the user's `~/.claude.json`
  for that project. The interpreter path is machine-specific, so it never goes into a committed
  file. A committed `.mcp.json` may name it through `${VAR}`, which Claude Code expands only from
  the environment it was started in: an `env` block in `.claude/settings.local.json` does not
  reach it (verified by a probe in the engine repo).
- **Missing tools call for a set-up step, not a stop.** Claude Code starts MCP servers only at
  launch, so a session that finds the tools missing registers the server as above, runs every
  operation through the CLI for the rest of the session (same functions, nothing lost), and asks
  the owner to restart Claude Code. Fallback text: `manual-mode.md` § When the MCP tools are
  missing.
- **A server process is not a framework session.** The process lives as long as the Claude Code
  process, and a `/clear` probably leaves it running (UNVERIFIED: not testable headless, as the engine repo's spike findings record). So a session begins
  with an explicit `session.start`, never with the process start; the server remembers the key
  and actor from it.
- **Subagents share the parent's server process,** so the actor is recorded per call, not per
  process: a tool may pass its own `session` and `actor`, so a subagent names itself, and
  housekeeping calls are told apart chiefly by the `hk_` prefix.
- **The server's working directory is the directory Claude Code started in**, so the engine
  takes the repo root from its cwd.

**Design rules for the MCP surface; the goal is to save context, not convenience:**
1. **Edits are operations, not text replacement:** set a field, append a comment, replace one
   named section. No read-modify-write.
2. **Every write returns one line:** what changed and the new state.
3. **Every read returns a slice:** one-line rows, one section, or the newest N log entries,
   each with a hard size cap (`read_max_bytes`) and a pointer to the rest.
4. **Every refusal names its remedy** (§8.0); it reaches the agent as a tool error.

**Names:** the dotted names in this document (`session.start`, `record.new`, `hk.expire_batons`)
are the library operations. The CLI spells them `context-engine <noun> <verb>` (`session start`,
`task list`, `record new`), and MCP tool names use underscores (`session_start`, `task_close`,
`hk_expire_batons`), which agents see as `mcp__context-engine__<tool>`.

| Group | Tools |
|---|---|
| Session | `session.start`; `session.close(rows, summary, guards, read, asked, owed)` (the last four are its receipts and owed list); `session.pause(rows, deferred)` |
| Orientation | `orient()`: the §6.1 read in one capped response; `routes()`: where each component lives |
| Batons and pauses | `baton.add`, `baton.done`, `pause.open`, `pause.resume` (§5.4) |
| Banner | `banner.show`; `banner.set(text, seen)` (§5.5) |
| Tasks | `list(state, pri, label)`, `show(id, section, head)`, `new`, `set`, `promote`, `dep`, `comment`, `touch`, `close(msg, body)`, `reopen`, `section(id, name, text)` |
| Owner questions | `ask.new`, `ask.raised`, `ask.later`, `ask.answer` (§5.3) |
| Intent and record | `record.new(kind, ...)`, `record.amend`, `record.stamp`, `record.correct` (for every append-only kind); `record.retire`, `record.confirm` (stories, §3.2); `decision.supersede`, `.set`, `.link`, `.relink`, `.find`, `.show`, `.import`; `why(target)` (§6.5) |
| Checks | `lint(working)`: failures only, each with its remedy; `working` runs only the working-state guards (CLI `lint [--working]`) |
| Register | `register.show(engine)`: the residual-risk register, or with `engine` the installed engine's own (§7.4) |
| Docs | `doc.freeze(path, note)`: a FROZEN line above a doc's liveness line (§6.7, §7.2); `doc.archive(path, to, why)`: a whole doc into an archive directory with its redirect row (§7.3) |
| Adoption | `init(prefix, dry_run, merge_settings, skip_settings)`: writes the kit into the repo (§6.9) |
| Commits | `commit(paths, message)`: the session's own commit by path, with the op log lines HEAD lacks and the files they name; runs no gate (§5.5 rule 4) |
| Gate | `gate.status(require)`: each gate scope's content id and whether a green run covers it (§8.5 G-V1); the run itself is CLI only (`gate run`), out of the MCP's scope |
| **Housekeeping (`hk_`)** | `hk.expire_batons` (CLI `baton expire`); `hk.regen_index` (CLI `decision index`); `hk.comment(id, text, commit)`, `hk.stamp`, `hk.ratchet`, `hk.close(id, commit)` (checks the `Closes:` trailer in git, §6.11; not built yet, CE-6) |

The `hk_` set has its own prefix so a housekeeping agent's allowlist can name only those tools
(§6.11).

**Out of scope for the MCP:** `.feature` files and code; gate runs; prose documents (beyond the
FROZEN line `doc.freeze` adds and the move `doc.archive` makes); and every
judgement: the session makes it by calling an operation, the tool never makes it.

### 8.0.3 Trial before adoption

Following §5.2's adopt-by-trial rule, a repo adopts the engine only after a trial against its
hand-run procedures. **Build first:** the task operations, then the MCP wrapper; `orient`;
`session.start` / `close` / `pause`; baton and pause records; the tier-0 housekeeping script.
What is built so far is on the board (`context-engine task list --state all`), not here. **Pre-registered
rubric:** context spent on session start and clean close against the same procedures done by hand
(the `read:` receipt is the existing measure), plus collisions or lost records across two
concurrent sessions. The hand-run baseline is an evidence doc measured before the trial starts.
Decisions as records follow once the core holds.

### 8.1 Intent guards
- **G-I1:** every charter goal has at least one story; every story names at least one goal,
  and only goals of the charter. Retired stories are history and are not read. Each goal id
  leads exactly one row, always written in the standard form (P3).
- **G-I2:** every story that is not retired has an actor, a date and a status from the
  vocabulary. `unconfirmed` requires `actor: agent (reconstructed from …)`. `record.new` of a
  story refuses what G-I2 and G-I1 would fail, by the same checks, and a story created with what
  only `record.retire` writes (§3.2), or a reconstruction created `live` or `unspecified`. Every
  retired story was retired by `record.retire` (a
  logged `retire`, so who and why are recorded), and every story it retired is still `retired`
  with `status: deprecated`; only a retired story is deprecated; each id in a story's
  `superseded_by` or `supersedes` is a story, and only a retired story has `superseded_by`.
  Every reconstruction that is `live` or `unspecified` was confirmed by `record.confirm` (a
  logged `confirm`, so whose words confirmed it are recorded), and no story it confirmed is
  `unconfirmed` again. Not checked: a hand edit between `live` and `unspecified` (no operation
  owns that move, and the op log records which keys changed, not their values), an `actor`
  rewritten by hand, a retired story's
  frontmatter after the retirement (history), that the retirement's or a confirmation's amendment is still there, that `supersedes` mirrors
  `superseded_by`, and an op log line written by hand (trusted as written, as G-W7 trusts it).

The correctness chain's guards (G-I1, G-I2, G-T1, G-T2, G-T6) read what config names: `[guards]
charter`, `stories` (the story kind) and `tests`, the claim pattern `[guards] claim` (one group,
the criterion id), and the criteria file. A guard is off while a source it needs is unset, but a
half-set pair is red, as G-D12's is: `charter` without `stories`, or `tests` without a criteria
file, would otherwise switch a guard off under a clean lint. A set path that does not exist is red, and so is a source that yields nothing (no goal row, no
criterion row, no claim), so a reworded table or a claim pattern that does not fit the repo's
test syntax cannot pass by finding nothing. So is a row of a goal or criteria table that is not
led by an id (`G 3`, `**C-4**`), so one reworded row cannot pass unread either. An id in the
stored files is read as written (P3): `C-05` and `ADR-0007` resolve. A cell may hold a GFM-escaped `\|`.

### 8.2 Trace and existence guards
- **G-T1:** every `live` story has a criterion that is not retired, or is `unspecified` and an
  open board item names it. Which item specifies it is judgement; the guard counts any mention.
- **G-T2:** every `tested` or `manual` criterion is claimed by a test or driver, every
  annotation resolves, and every status is from the vocabulary (§3.3).
- **G-T3 (existence, against code):** every file, `file::symbol` and route named in the
  **normative** text of a story, criterion, NFR doc or residual-risk register entry exists in the code; history
  notes (`*HISTORY —*`, blockquotes) are exempt. The lint reads the docs `[guards] existence`
  lists, and the names in backticks there, and the `code:` links of every current decision, by
  the rule `decision.link` applies (a file inside the repo, written with `/`, and each dotted part
  of a non-empty symbol; a link whose code moved is moved with `decision.relink`, never by hand); HTTP routes are not
  checked.
- **G-T4:** structural-claim anchors resolve and their body hashes match the pins; re-pinning
  is an explicit, reviewed act. *Not built yet: deferred until the spec makes structural claims
  (§11.2).*
- **G-T5 (mutation per criterion):** runs as a scheduled routine, or as the one slow background
  job, keyed on the hash, with results in a tracked evidence doc; it does not apply to formal
  theorems, where G-T4 substitutes. It mechanises the by-hand sabotage of P7. *Not built yet
  (CE-34).*
- **G-T6:** every criterion's `from` names a story or decision, and each resolves to a record.
  A criterion's actor is its source's (§3.3), so resolving the source is the whole check.
- **G-T7:** every `deviates` criterion references a deviation-register entry; every `retired`
  one references a decision. *Not built yet: it comes with the deviation register (§3.5).*

### 8.3 Doc guards
- **G-D1:** per-component caps (lines, bytes, line width), set in config with provenance:
  `max_lines`, `max_bytes` and `max_width` on a `[[routes]]` entry, applied to the routed file
  or to each `.md` under a routed directory. Table rows are exempt from the width cap.
- **G-D2:** ids are unique within their series and never reused; a new id is allocated after
  scanning open and closed items. In the stored files, no two files carry one id, and the op log never
  shows an id created twice.
- **G-D3:** every link and `file::symbol` resolves, case-exact. The lint reads the docs
  `[guards] links` lists, and checks relative links with their `#anchor`s and backticked
  `file::symbol` spans; a bare file name resolves to any file of that name, and a record no
  longer current (`status: deprecated`) is history and is skipped.
- **G-D4:** every doc declares its liveness (P2) near the top, within a window of lines
  (`liveness_lines`, 10 by default): a frontmatter `liveness:` key (a value that is not a liveness
  word is red), or a line that opens a block (the first, or one after a blank line, a heading or
  the frontmatter) led, after a blockquote's `>` and emphasis, by LIVING, ACTIVE-PLAN or FROZEN,
  or by an archive's `ARCHIVED <date>` (FROZEN, §7.3). The topmost declaration counts; the word
  in passing (mid-line, on a wrapped line, in fenced code) declares nothing. A doc whose opening
  lines this repo may not edit (frozen provenance, the framework's contract, the engine-written
  ledger, a charter signed off by the owner) is given its liveness in config instead, and a doc that declares one
  must agree. History directories hold provenance: each doc there is FROZEN, or ACTIVE-PLAN
  while its item is open. With a board configured, an ACTIVE-PLAN doc names its board item in
  the window, and is red once every item it names there is closed (§6.7: it freezes when its
  item closes; `task.close` refuses to close the last of them until `doc.freeze` has).
  Config: `[guards] liveness` and `history` (paths; both empty is off),
  `liveness_given` (a repo-relative glob to a liveness; one that matches no file is red) and
  `liveness_lines`. A listed path that is missing, and a `liveness` list holding no doc, are red.
- **G-D5:** derivable counts appear only in generated blocks, so a count of things in the tree
  typed in prose is red: a number (a numeral, or a spelled one from three to twenty) directly before a
  counted noun (`[guards] count_nouns`: tests, checks, criteria, stories, tasks, rows and the
  like, plurals only, case-insensitive; an `open`, `closed` or `new` may stand between). A
  number glued on its left to a letter, digit, `.`, `,`, `-`, `§`, `#` or `/` is part of a
  token (`R6`, `1.5`, `§6`, `G-D5`) and is not a count. P5's four forms pass: fenced code and
  frontmatter, a backticked or double-quoted span, a line with a `YYYY-MM-DD` anywhere on it,
  and a doc whose liveness (G-D4's reading) is FROZEN or ACTIVE-PLAN. A bound (`at most 2
  entries`) is a rule's value, not a count, and passes; another rule value or a label (`Step 3
  checks`) goes in backticks. Config: `[guards] numbers`, the LIVING docs to read (empty is off;
  the kit leaves it empty until the repo measures things, §11.2; list each under `liveness`
  too, so its liveness is checked), and `count_nouns`. A listed path that is missing, and a
  list whose docs are all FROZEN or ACTIVE-PLAN, are red. *Not built: generated blocks inside a
  hand-written doc (no generator writes one yet), and a value check of a rule value restated in
  prose (`NEXT holds 5`).*
- **G-D6:** generated indexes match a regeneration **and** are content-complete from a
  configured cutoff id. An index built from record frontmatter needs only the regeneration
  check; the cutoff check remains for indexes still built by parsing prose. Built for the decision
  index (`[working] decision_index`): a missing index fails while any decision exists.
- **G-D7:** signal budgets: ⚠ ≤N per file, a bold-caps budget, retired glyphs. A signal stands
  out only if its use is capped. Config: `[guards] signals`, `warn_max`, `bold_caps_max`,
  `retired_glyphs`.
- **G-D8:** the orientation note's banner carries exactly one session key (the stacking check); there is no
  session history in the orientation note; an inline board, if present, starts within the first K lines.
  The lint fails a second banner heading, any other heading carrying a session key, and a
  banner bullet led by a session key; dated facts citing a key inside a sentence pass. *The
  inline-board clause is not checked: the board is one file per item.*
- **G-D9:** tuned config values carry a provenance note, and spec-example values are refused
  (§8.0). The lint reads every number `context.toml` assigns: its line needs `provenance:
  MEASURED` or `JUDGEMENT`, and `wrong if` (or `wrong as above`); a note citing an example is
  refused.
- **G-D10:** every append-only record's `body_sha` matches its body above `## Amendments`, with
  its logged `corrected:` insertions undone. This turns "append-only" and "owner words are
  verbatim" into refusals. Line endings are normalised before hashing, because a Windows
  checkout may rewrite LF as CRLF. Undoing a logged insertion must find it where its line says,
  and a bracket whose `corrected:` line is gone fails the hash.
- **G-D11:** each configured OKF bundle directory is conformant: every non-reserved `.md` has
  frontmatter with a `type`; every `index.md` has no frontmatter (except an `okf_version` key at
  the bundle root) and the list shape (*the list shape is not checked yet*). That `status`
  agrees with the record's own state key is G-W4.
- **G-D12:** coverage: every component (§2's table), procedure (§5.6 and the §6 headings) and
  G-id this document names is owned, by a table row of the newest dated coverage map or by a
  board item, open or closed, that names it. A map row owns only its own table's class, in
  that table's key column (`Component`; `§` beside `Procedure`, or beside `Ritual` in older
  maps; `Guard`). A renamed component still counts under its former name (`Invariants`,
  `Law / NFRs`), in a map row or a board item alike. Config: `[guards] coverage_spec` and `coverage_maps`
  (a repo-relative glob; the newest by the date and session letters in its file name, ordered
  as session keys). With neither set, the guard is off; with only one set, a missing spec, a
  glob that is absolute or climbs out with `..`, no matching map, or an undated one, it is red.
  A class whose extraction yields fewer items than its floor is red, so a reworded heading or
  id format cannot pass by finding nothing; the floors and patterns are the engine's and fit
  this document, so a repo whose spec they do not fit switches G-D12 off. The map is frozen: a
  failure clears with a new dated map or a board item, never an edit.
- **Record schema** (reported as `schema`): every record has its kind's required keys, enum
  values and types (`[kinds.*]` in config), and `status` uses only `draft`, `stable` or
  `deprecated` (§9.3.1).
- **G-R1:** every path in the routing table (`[[routes]]` in config) exists; a route marked
  optional is exempt.

### 8.4 Working-state guards
- **G-W1:** the banner's key is ≥ the newest `kind: close` ledger key.
- **G-W2:** at most N consecutive `kind: pause` entries.
- **G-W3:** no baton or pause record older than two sessions: two `close` or `pause` entries
  after the owning session. Housekeeping repairs it.
- **G-W4:** closed ids do not appear on the open board; `state` and the derived OKF `status`
  agree on every task, and the board query reads `state`; no open question carries `answered:`.
- **G-W5:** tier caps: NOW = 1, NEXT ≤ 5.
- **G-W6:** ledger receipts are present and well-formed, including `asked:` when a NOW or NEXT
  question exists. The engine checks `asked:` when the entry is written; the lint re-checks
  `guards:`, `read:` and `rows:` in the stored files.
- **G-W7:** every record kind's tool-owned frontmatter is changed only by the tool; `moved` is
  consistent with the session-stamped op log. The lint checks each board item's `moved`,
  `updated`, `closed` and `last_asked` against the session of the newest logged operation that
  wrote it (a value no operation wrote must predate the log), and that every log line parses.
  The values of `state`, `pri` and `deps` are refused at write time; the log does not record
  values, so the lint cannot recheck them.
- **G-W8:** no clean close while an overdue owner question (§5.3) has not been raised this
  session. This repeated reminder is what makes the board the owner's tracker.
- **G-W9:** every `--mechanical` close cites its evidence: a commit whose message carries
  `Closes: <id>`, or a ledger entry naming the item. `hk.close` checks it at write time; the
  lint re-checks it in the stored files. *Not built yet (CE-6).*
- **G-W10:** housekeeping writes per run are **counted and measured** (writes, token counts),
  and the count goes into the run's report. **No budget by default:** change sizes vary by
  session, so a cap that suits a large session would be unreasonably large for most, and a
  smaller one would most likely be overridden. A repo may still configure a cap, with
  provenance (G-D9); hitting it stops the run and asks, and the owner may tell it to write
  anyway. *Not built yet: it comes with real housekeeping runs (CE-6).*
- **G-W11:** no `kind: open` ledger stub older than the configured window without a matching
  `close`, `pause` or `abandoned` entry. The window is provisionally 3 later sessions, counted
  from the stub's last activity (an owner judgement); the trial measures it (§8.0.3) and gives it
  provenance (G-D9). *Not built yet (CE-6): until then a stale stub is marked
  `abandoned` by hand (the runbook's housekeeping step).*
- **G-W12:** an open NOW item carrying `review` has a design review that passes the promotion
  checks (§5.2). `task promote`, `task set` and `task section` refuse it first, so this catches a
  hand edit.
- **G-W13:** every residual of a closed item carrying `review` is in the register with that task
  in `from:`; every register entry has its four lines; no two entries share an `INV-n` (§7.4).

### 8.5 Verification-state guards
- **G-V1 (run ledger):** every gate run is recorded, in a gitignored run ledger, against the
  content id of each **gate scope**: a set of globs over the repo's files, hashed over the
  tracked and untracked-non-ignored files it matches. No commit id goes into it, so `git add`,
  `git commit` and a committed deletion or rename leave it where it is, and a green run earned
  before a commit still counts after it. A scope whose id has a green run needs no re-run: the
  code gate runs only when the code changed, and a change outside the code scope needs lint and
  its readers. A session's own commit of a path in the required scope is refused until a green
  run covers the scope's id (P7). **An exclusion fails open** (an excluded file can no longer
  make a green run stale), so it is verified by a guard, never a survey alone: a test that reads
  an excluded path fails unless the scope names it as a **reader**. The readers are a part of
  their own, keyed on every file: after a hand edit outside the scope they alone re-run. The
  commit refusal checks the scope, not its readers: their id moves on every engine write, any
  session's, and a commit of a code path does not commit what they re-check. A run records each
  id that did not move while it ran, and counts for nothing only when every id moved, so a
  concurrent write voids only the ids it touched. The ledger is gitignored, or it would sit
  inside the id it records.
  A green run means "passed against these sources", not the environment, so every push runs the
  whole gate. *Built (CE-78): `[gate]` in `context.toml`, `context-engine gate run` and `gate
  status`, the commit refusal. Not built yet (CE-17): a long suite split into parts, each keyed
  on its own inputs, and `orient()` reporting the untested parts.*
- **G-V2 (floors):** raw totals with zero headroom, raised by an automatic ratchet; floors on
  what a guard's extractor finds keep declared headroom (P7); one dated baseline per suite.
  *Built so far: G-D12's floors on what its extractor finds. Not built yet: the raw-total
  floors, their ratchet and the per-suite baselines, deferred until a suite is large (§11.2).*
- **G-V3:** a lock on gate runs and background-agent runs for the same tree. *Not built yet
  (CE-17): it comes with the run ledger.*
- **G-V4:** exit-code hygiene: no piping through `tail`/`tee`, one phase per command, logs from
  `mktemp`.
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
| **T1 working state** | orientation note, the board *view* and ranking fields, baton and pause records (one file each), unverified hazards | tracked, replaced or session-stamped; git is the history | our own schemas; baton and pause records are OKF files (`type: Baton`, `type: Pause`) so the engine has one reader |
| **T2 durable knowledge** | charter, stories (incl. PRDs), criteria, NFRs, decisions, evidence, residual-risk register, deviations, runbooks, archive, **task records** (open and closed: body, comments and updates, op log, links to decisions) | tracked, append-only / LIVING / FROZEN | **OKF-conformant**, with our stricter profile. Task frontmatter stays **tool-owned**: the tool emits `type: Task` and *maps* its own fields onto OKF keys, rather than an OKF overlay duplicating them |
| **T2′ ledger** | session ledger | tracked, append-only | our own format, with OKF-style date headings |
| **T3 cross-project** | global contract, memory | `~/.claude` | memory files already have OKF's shape: one fact per file, frontmatter with a type, an index file. A redesign is planned (§9.4) |

### 9.3 How OKF is used

OKF v0.2 (`GoogleCloudPlatform/open-knowledge-format`, `SPEC.md`):

| Our need | OKF feature | Our profile adds |
|---|---|---|
| component type | required `type:` (`Story`, `Criterion`, `Decision`, `Evidence`, `Invariant`, `Deviation`, `Runbook`, `Charter`) | — |
| identity | concept id = path minus `.md` | **`id:`** extension: stable series ids that survive moves (P3) |
| routing map / progressive loading | `index.md` per directory | **generated**, and checked by G-D6; the component → path mapping lives in `context.toml`, because `index.md`'s shape is fixed (§9.3.1) |
| concept changelog | `log.md` | **generated** from decisions' `creates/amends/retires`; this is *not* the session ledger. *Not built yet: no `log.md` is generated* |
| who and when | `generated: {by, at}`; actors `human:<id>` / `<producer>/<version>` | `actor:` in our vocabulary (§6.5); the writing agent (`claude-code/<model-id>`) goes into the op log per write. *Not built yet: `generated.by` is not written* |
| owner sign-off | `verified:`, by `human:owner` at a time → "human-reviewed" tier | distinct from `criterion_status: tested`. *Not settled: no record carries `verified` yet and no operation owns it (`decision.set` refuses it, §6.5), so whether it is one mapping or a list of them is fixed when the first owner endorsement is recorded* |
| no longer current | `status: deprecated` | **one mapping:** SUPERSEDED decision, `retired` story or criterion, FROZEN archive item, closed task → all carry `status: deprecated`, derived by the engine from the record's own state |
| freshness | `stale_after:` (the spec defines when a concept is stale; it does not prescribe what a reader does) | **our profile refuses** an expired `stale_after` on a live item. Bound to `manual` criteria (re-run the driver by date) and register entries about something external. *Not built yet: the engine does not read `stale_after`* |
| provenance | `sources:` with ids, cited as footnotes | evidence docs cite their runs |
| extensions | readers SHOULD preserve unknown keys and MUST NOT reject them | `supersedes`, `relaxes`, `retires`, `criterion_status`, `test`, `liveness`, `sign-off` |
| attested results (later) | `type: Attested Computation`: a deterministic attester checks a receipt | candidate format for G-V1 run-ledger rows |

**What OKF does not cover:** ranking, owner-question rationing, session-stamped batons and
pause records, writes from several sessions, replace-vs-append discipline, procedures, guards. OKF readers
are deliberately permissive; our profile is strict on top of conformant files.

#### 9.3.1 Constraints from the OKF v0.2 spec

| The spec says | What it means for us |
|---|---|
| **`status` is a defined lifecycle key: `draft` \| `stable` \| `deprecated`; absent means `stable`** (§5.4). `deprecated` = "kept for links and history; no longer current" | Our own states must not go into `status`. Tasks carry **`state: open \| closed`** (an extension key); the engine derives `status`: absent while open, `deprecated` once closed. Decisions use `decision_status`, stories `story_status`, the charter `charter_status`. G-W4 checks the two keys agree for board items, and G-I2 for stories. *Not built yet: no guard checks a decision's (SUPERSEDED exactly when `status: deprecated`), so a hand-set `status: deprecated` on a current decision passes lint and the doc guards skip it as history; and nothing reads `charter_status`.* |
| **Concept id = the file's path minus `.md`** (§2) | Closing in place (§5.2) and never renaming a file on retitle keep record ids stable as OKF ids. The `id:` extension stays, for series ids that survive a migration. |
| **Every non-reserved `.md` in a bundle needs frontmatter with a non-empty `type`** (§11) | **A bundle is a chosen set of directories, not the repo root;** otherwise README, CLAUDE.md and HANDOFF would all need frontmatter. Non-record files inside a bundle directory need a `type` too (e.g. `type: Readme`), and the engine filters on `type` rather than excluding files by name. |
| **`index.md` and `log.md` are reserved at every level; `index.md` has no frontmatter (except `okf_version` at the bundle root) and a fixed list shape** (§3.1, §8) | The component → path mapping lives in `context.toml` (§8.0); `index.md` is a plain generated listing. |
| **`log.md` headings must be `YYYY-MM-DD`** (§9) | Session keys like `2026-10-07c` cannot be log headings, so the ledger is not an OKF `log.md` (§7.1). |
| **Actors: `<producer>/<version>`, `human:<id>`, `process:<id>`** (§7); trust tiers key off the `human:` prefix (§5.3) | Agent writes carry `claude-code/<model-id>`; the housekeeping script is `process:housekeep`; owner sign-off is `verified` by `human:<id>`. |
| **`stale_after` is an absolute instant** (§5.5) | Baton expiry counts sessions, so it is an extension key; `stale_after` may serve as a time backstop. |
| **Producers MAY add keys; consumers SHOULD preserve unknown keys when round-tripping and MUST NOT reject them** (§4.1, §11) | The engine round-trips unknown keys (§8.0.1). |
| Links: bundle-relative `/…` is recommended (§6.1) | Record links use bundle-relative paths, stable when files move within a directory. |

### 9.4 Later

All derived and disposable; the files stay the source of truth:
- vector search over T2 and T3;
- a source graph: the code symbol graph, plus OKF links, plus the generated coverage map, for
  impact analysis;
- a memory architecture for T3, including the path-case split in memory directories.

---

## 10. Layout for a **new** repo

Existing repos map the components onto their own files instead of moving them (§11.4). `context-engine init` (§6.9) writes the entries
marked `*` that the repo does not have yet; the rest are added when needed (§11.2).

```
AGENTS.md                  # workflow conventions (how agents work), read first
CLAUDE.md                * # product contract: the kit block (framework: <version>, imports docs/framework/contract.md), mandates, gate, traps; push-hold line on top
HANDOFF.md               * # orientation note: banner (one key), next session, generated pointer to open batons/pauses
context.toml             * # framework config: guards, routes (component → path), record kinds, caps (+ provenance), cutoffs, models
.gitignore               * # the repo's own; init creates it, or appends `.context-engine/` to it when it does not ignore that yet
.mcp.json                  # optional, not committed by default: the server is registered with `claude mcp add --scope local` (§8.0.2)
docs/
  index.md                 # generated OKF listing (no frontmatter, list shape)
  charter.md             *
  framework/contract.md  * # the framework's rules, imported by CLAUDE.md; replaced whole on upgrade, never edited here (G-D0)
  law.md                   # optional: the NFR doc (NFRs, data-model law) with invariant → test map
  stories/S-n-<slug>.md  * or issues/<slug>/PRD.md   # owner's voice (records, or PRD sections mapped in context.toml)
  criteria.md            * or criteria/ or features/*.feature
  decisions/D-n-<slug>.md * # one record per decision; generated index.md
  deviations/              # append-only records (+ optional generated open-gaps view)
  invariants.md            # the residual-risk register (`[working] register`, §7.4)
  runbooks/              * # method: procedures.md (every procedure in order), manual-mode.md (every engine operation by hand), gate, sabotage, fan-out and release (§7.5), from the kit
  evidence/<id>-<topic>-<date>.md *
  ledger/session-log.md  * # session ledger (one file under the engine lock)
  ledger/ops.jsonl         # engine op log, one JSON line per write
  working/               * # baton (BTN-n) and pause (PAU-n) records (§5.4)
  archive/README.md        # redirect table
tasks/                   * # flat; open and closed side by side, `state:` in frontmatter (§5.2)
.context/                * # engine lock; carries its own .gitignore, never tracked
.context-engine/env/        # the engine's pinned, non-editable env, made before init (§6.9 step 2); gitignored, never the repo's own env
.claude/settings.local.json * # machine-local, gitignored (.claude/.gitignore): the SessionStart hook that runs orient
.claude/skills/, .claude/workflows/, .claude/agents/   # project skills, tracked build workflows, the hk agent; the kit ships none: the procedures' skills come with the engine's Claude Code plugin (§11.2) or are copied from it
.scratch/                * # throwaway and gitignored: anything only there is lost (carries its own .gitignore)
```

---

## 11. Adoption

### 11.1 Minimum set for a new repo

**Components:**
- charter;
- stories;
- criteria with statuses;
- contract;
- orientation note (banner and next steps; the board itself is one file per item in `tasks/`,
  questions included, read with `task list`);
- batons and pause records;
- decision log with negative results;
- ledger in its own file;
- the scratch rule;
- the fallback runbooks (P16): every procedure in order (`procedures.md`) and every engine operation
  by hand (`manual-mode.md`), copied from the kit;
- the method runbooks (§7.5): `gate.md`, `sabotage.md`, `fan-out.md` and `release.md`, copied
  from the kit.

**Procedures:** intake, start/resume, clean close, pause, bootstrap.

**Tooling:** the record engine's CLI, and the tier-0 housekeeping script (*not built yet (CE-6)*:
until it is, `baton expire` is the only housekeeping operation). The MCP server is not in the
minimum set until the §8.0.3 trial reports.

**The gate** of an adopting repo is its own test command followed by `context-engine lint`, run
from the repo root before every commit that touches code, tests or records, and before every
push; the engine's own commits of its writes are the one exception (§5.5 rule 4). The kit's contract
(§6.9) states it; the test command itself is in `CLAUDE.md` § Gate. **The code gate runs only
when its code changed** (G-V1): where `[gate]` names the test command and a code scope,
`context-engine gate run` records each run against the scope's content id, a commit whose code
scope already has a green run needs only lint (and the scope's readers, after a hand edit to a
file the scope leaves out), and the push runs the whole gate. A repo without `[gate]` runs the whole gate before every such commit.

**Guards:** G-D0, G-D1, G-D2, G-D3, G-D8, G-D10, G-I2, G-T1, G-T2, G-W1, G-W2, G-W4, G-W6.
`context-engine lint` runs every one (plus the record schemas, G-D11, G-R1 and the other built
guards of §8). G-I2, G-T1 and G-T2 read the sources `[guards]` names (§8.1), which the kit leaves
unset because a fresh repo has no goals, stories or tests yet; bootstrap sets them once the
first stories and criteria are recorded (§6.9 step 4), and until then they are checked by hand.

### 11.2 Add when needed

| Trigger | Add |
|---|---|
| a second concurrent session works the board | board size 2 (one file per item) |
| sessions stack updates in the orientation note, or read it for item detail | board size 3 (tree plus CLI), adopted by trial |
| a baton survives two sessions | G-W3 |
| the repo measures things | evidence docs; dated baselines (`gate.md`, §7.5); G-D5 |
| traps accumulate | residual-risk register; G-T3 over it |
| the code deliberately departs from the spec | deviation register; G-T7 |
| "did the gate pass on this tree?" keeps coming up | G-V1 |
| a component hits its cap | archive plus redirect table |
| the spec makes structural claims | G-T4 |
| the suite is large | G-V2 floors; G-T5 mutation |
| cross-cutting NFRs or data law | NFR doc with an invariant → test map |
| parallel building | build-round protocol (§6.6), tracked workflows |
| sessions spend context reading files in order to edit them | the engine's MCP server (§8.0.2), after the §8.0.3 trial |
| housekeeping needs judgement from reading, not just fixed rules (commit → task comments, foreign commits) | tier-1 housekeeping agents restricted to `hk_` tools (§6.11); G-W9, G-W10 |
| `session.start` stubs are in use | G-W11 |
| a task is above the design-review threshold (§5.2) | `review_triggers` and `register` in `[working]`; G-W12, G-W13 |
| a bundle directory is declared OKF | G-D11 |
| sessions skip a procedure's steps, or the hook and MCP set-up per machine is friction | the engine's Claude Code plugin: a skill per procedure that points at its runbook section, the `SessionStart` hook and the MCP server, each run with the repo's own pinned engine (kit README § Claude Code plugin) |

### 11.4 Migration (existing repos)

- **Charters are reconstructed by an agent and brought to the human for review**, from what
  exists (a project brief, mandates in the contract, goal-shaped decisions). Tagged
  `unconfirmed` until reviewed.
- **Map, don't move.** The routing map in `context.toml` maps each component onto the repo's
  existing files. Existing ids are not renumbered: they take the framework's form at import,
  keeping each number where there is one (`D-27` becomes number 27 of the decision series, `Q8`
  becomes `ASK-8`; an
  unnumbered board row such as `1h` gets a new task id), and each old id stays in the record's
  `aliases`, which the engine resolves (`why`, `task show`, `decision show`, link targets) and
  G-D2 keeps unique. The id map is saved as an evidence doc; history, commit messages and code
  comments keep the old ids.
- **`init` on an existing repo** writes only what is missing: it skips every file that exists,
  appends the kit block to an existing `CLAUDE.md` only when no kit block (of any version)
  is there, and keeps an existing `context.toml` once it loads. Then edit `context.toml` in
  place: each kind's `dir` and each route's `path` point at what the repo already has, each
  kind's `prefix` is the framework's form, and the skeletons `init` wrote for components the
  repo keeps elsewhere are deleted rather than routed. A re-run of `init` writes only what that
  edited config points at. Lint (G-R1 and the schemas) shows what still disagrees.
- **Enable guards incrementally.** Each one starts as a warning, with a dated deadline for
  becoming a refusal.
- **Back-filled stories are reconstructions, never the owner's words:**
  `actor: agent (reconstructed from D-n / PRD § / commit …)`, `story_status: unconfirmed`. The
  owner confirms them through **one batched digest question**, not one question per story, and
  each confirmed story is moved on by `record.confirm` with the owner's words from that answer
  (§3.2). A story the repo had already retired by hand is red under G-I2 until `record.retire --by owner`
  retires it, with the owner's words from that same batched answer (§3.2).
- Adopt structural changes (board size, ledger rotation) **by trial**, with a single
  revertible cutover commit.
- **Closed-task directories may migrate:** `tasks/closed/*` moves into the flat `tasks/` once
  the schema carries `state` and every moved file has `state: closed`. "Map, don't move" gives way
  here because one place is cleaner, and the cost is bounded because the store can find a task
  by id when its path is wrong. Deferred while the framework is being built.
- **Single-file decision logs migrate to records the same way, by trial:** `decision.import`
  (§6.5) on a copy and a branch first, every number kept and every old id an alias, so `D-n §k`
  citations still resolve; the old file is retired with a line pointing at the records in the
  import's commit, so nobody appends to it by hand; anchor links into it break and get a
  redirect table. Until then the old file is read as it
  is (a read adapter is not built).
