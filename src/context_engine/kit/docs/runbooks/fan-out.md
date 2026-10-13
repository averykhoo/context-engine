---
type: Runbook
title: "Fan-out: delegating to agents, workflows, and the build rounds"
source: FRAMEWORK §7.5, §6.6, P10, P11, P12
created: 2026-10-13
mode: replaced
liveness: LIVING
---

# Fan-out

How a session hands work to agents and builds in rounds. The rules are FRAMEWORK §6.6 and the
framework contract § Rules (when to use a workflow, several tasks in one request, model choice);
this file is how to follow them. The repo's values (its default and cheaper models, for one) are
in its `CLAUDE.md`.

## Delegating reading and auditing

- **The test:** would doing it inline flood the session's context with file contents? Then
  delegate it and take back a table. A lookup whose file and symbol are already known is done
  inline: delegating it is pure overhead.
- **The prompt names** the question, the verdict form (`file::symbol` evidence, never file
  dumps), and the one file the agent persists to.
- **Persist incrementally, one file per agent:** each finding is appended as it lands, not
  buffered to the end, so an agent that dies leaves a partial result; two agents on one file lose
  work. Only an agent that can write files can persist (not `Explore`).
- **On return,** check the file exists and is not short; if it is, write the returned report to
  it before doing anything else with it.
- **A report is evidence, not a finding.** What heads for a record, a commit or a golden is
  verified first-hand by the session; reports that contradict each other are reconciled, never
  averaged. Agents audit; the session decides and deletes.
- **A skeptic pass** gives each reviewer's findings to a second agent whose job is to refute
  them, before the session acts on any: it removes false findings cheaply.
- **Clean up:** the session deletes the run's scratch files once their conclusions are in tracked
  files (P10), in the same session.

## Watchers

A background watcher (CI after a push, a release run, a long job) only watches: no fix, no
re-run, no cancel, no push. Its brief names what it watches by commit hash, how to read it, the
verdict to return per run, and its persist file; the CI watcher's brief is in
[rituals.md § Push and CI](rituals.md#push-and-ci-68). A cheap model is enough.

## Build rounds

The steps are FRAMEWORK §6.6's, in its order and with its numbers.

| # | Step | How | Why |
|---|---|---|---|
| 1 | Map | read what exists: the item, its Read first, the code and records it touches; a mapping agent returns the files and who will own each | a plan made without the map rebuilds what is there |
| 2 | Plan, with a critic | the plan names each wave, each builder's files and the order of dependent work; a critic agent attacks it before anything is built | a plan error is cheapest to fix here |
| 3 | BDD: criteria first, `planned` | write the criteria the work must meet, status `planned`, before the code | what "correct" means is fixed before the code it judges |
| 4 | Build in waves with disjoint file ownership, and no fan-out on a dependency chain | in a wave, each builder owns files no other builder touches; work that needs another builder's output waits for the next wave | two writers on one file lose work; a chain split across agents makes each guess the other's interface |
| 5 | Integrate, with sabotage | merge the waves, run the gate, and see every new check fail ([sabotage.md](sabotage.md)) | the waves are proven together, and no new check is believed unseen |
| 6 | Adversarial review through several lenses | one reviewer per lens (for example: fidelity to the spec, a fresh deploy, checks that pass when they should fail), then a skeptic pass on the findings; the findings and residual risks go into the item's `## Design review` (FRAMEWORK §5.2) | one reader misses what a lens built to look for it finds |
| 7 | Flip the statuses | a criterion moves to `tested` only when its claiming test was sabotaged; the item closes with its review, and closing files its residual risks in the register | a status says what is true only once it is |

## Worktrees for parallel builders

- One worktree and one branch per builder; the session merges and verifies first-hand.
- The gate in a worktree imports that worktree's code, and the worktree is checked out with the
  line endings the byte checks expect ([gate.md](gate.md)).
- Board, ledger and other working-state writes stay with the session, in the main tree.
- Commit by path; never `git stash`: in a shared tree it swallows another session's work (P12).

## Workflows

- A workflow script is a tracked file, so a run can be repeated and reviewed (FRAMEWORK §6.6).
- Every agent in it persists its own output, as above; a fan-out that dies at its last agent is
  otherwise paid for twice.
