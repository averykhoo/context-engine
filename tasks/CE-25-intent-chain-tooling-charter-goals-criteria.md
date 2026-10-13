---
type: Task
id: CE-25
title: 'Intent chain tooling: charter goals, criteria with statuses and refs, intake steps, and G-I1, G-I2, G-T1, G-T2, G-T6'
brief: Charter and criteria stay hand-written today; build their checks after CE-14's lint frame, each sabotaged red
pri: NEXT
state: open
deps: [CE-14]
source: session 2026-10-12b
created: 2026-10-12
moved: 2026-10-13b
updated: 2026-10-13b
review: [guard, write-op, shipped]
---

Filed by CE-16 from the coverage map (docs/evidence/framework-coverage-2026-10-12.md): components 1 (charter) and 3 (criteria), ritual §6.2 (intake), guards G-I1, G-I2, G-T1, G-T2, G-T6 (FRAMEWORK §3.1 to §3.4, §6.2, §8.1, §8.2). Stories are already a record kind (record new / amend / stamp); charter goals and the criteria in docs/criteria.md are prose that no tool reads. Intake step 1 (record verbatim) is built; steps 2 to 6 (goal link, criteria drafted planned, ASK rows, contradiction check, criteria census) have no tool support. Most of G-I2 and G-T1 are in the §11.1 minimum set.

## Design review

affects: every later session, since lint runs in the gate (AC-23) and a false red stops all work; the owner, whose charter and stories the guards read and who answers the open questions below; every repo the kit deploys to, since G-I2, G-T1 and G-T2 are in the §11.1 minimum set and ship with `[guards]` defaults; a plain-git human who edits `docs/criteria.md` or a test by hand
- reduced: a guard fails by passing because its extraction finds nothing (the charter's goal table reworded, a criteria table header changed, a claim pattern that does not match the repo's test syntax), so nothing is checked | rung: reduce | control: each guard reds when its configured source yields zero goals, zero criterion rows or zero claims, as G-D12 does; a sabotage row empties each source
- reduced: landing the guards turns this repo's gate red at once, since US-10, US-12 and US-13 are live with no criterion and US-12 has no board item | rung: reduce | control: the build runs the new guards on this tree before committing and lands the fixes the owner picks (planned criteria, or `unspecified` plus a board task) in the same commit, so no commit is red
- reduced: a criterion marked `tested` whose claiming test was deleted or renamed keeps reading as tested | rung: reduce | control: G-T2, sabotaged by deleting one `criterion("AC-n")` marker
- reduced: a claim names a criterion that is not a row (a typo, a renumbered id), so the test looks traced and is not | rung: reduce | control: G-T2's second half (every annotation resolves), sabotaged by a claim of an unused AC id
- reduced: a story names a goal the charter does not have, or a criterion's `from` names a story or decision that does not exist, so the chain looks linked and is not | rung: reduce | control: G-I1 (goal ids resolve against the charter's goal table) and G-T6 (each `from` id resolves to a record); `record new story` refuses an unknown goal at write time
- reduced: a story passes the schema with `goals: []`, or an agent-reconstructed story is marked `unconfirmed` with `actor: owner` and reads as owner words | rung: reduce | control: G-I1 reds an empty goal list; G-I2 reds `unconfirmed` without `actor: agent (reconstructed from ...)`
- reduced: a deployed repo with no charter, no criteria file or a different test language gets reds it cannot fix | rung: reduce | control: each source path and the claim pattern come from `[guards]`; an unset path switches that guard off and a set path that does not exist is red, as CE-14's lists and G-D12 do
- reduced: the criterion write op corrupts a hand-edited markdown table (reorders rows, rewraps lines, drops a column) | rung: reduce | control: it rewrites or appends one row only, under the store lock, with an op-log line; a test that the file is byte-identical outside that row; setting `tested` refuses unless G-T2 finds a claim
- residual: a test that carries the marker but does not check its criterion (a skipped test, an assert that cannot fail) satisfies G-T2 | rung: individual | why: the guard sees annotations, not coverage (FRAMEWORK §3.4); proving a test checks its claim is mutation, which is CE-34 | control: the sabotage rule (DEC-11), under which a criterion moves to tested only after its claiming test was seen red; G-T5 (CE-34) mechanises it later
- residual: G-T1's `unspecified` with a board task is satisfied by any board file that mentions the story id, a passing mention included | rung: individual | why: telling a task that specifies the story from one that mentions it needs judgement, as with G-D12 | control: the session reads the named item at intake; the guard's message names the item it counted
- residual: intake steps 5 (contradiction check) and 6 (criteria census) get no tool, so a session can skip them | rung: individual | why: finding a contradiction or classing a criterion KEEP, rewrite or retire is judgement no lint can make (P8) | control: rituals.md § Intake steps 5 and 6 and the census evidence doc; the next coverage map marks them deliberately prose-only, so G7 counts them
F: goes stale when the charter's goal table, the criteria table's columns or a repo's test annotation syntax change (the empty-extraction red catches each); every intake adds criteria, so the write op and G-T2 run most sessions; the next coverage map must move these rows from NEW to built
A: five functions in `src/context_engine/guards.py`, each done by hand from manual-mode.md § context-engine lint (list the charter's goal ids, the criterion rows and the `criterion("AC-n")` markers, and diff the sets); `[guards] off` silences any one with no code change; the criteria stay one markdown table a human can edit
M: one criterion-row parser (`src/context_engine/working.py::CRITERION_ROW_RE`, already used by `decision link`) shared by the guards and the write op; each write-time refusal is the twin of a rest-time guard and calls the same check; sources scoped through `[guards]` paths as CE-14 and CE-30 did
E: reuses the guards frame, `Failure`, `[guards]` path scoping and the sabotage table; criteria stay rows of `docs/criteria.md`, not a new record kind; one manual-mode section per new op; each remedy names the exact id and the op that fixes it

## Read first

- ASK-3: five owner calls, open; build nothing they decide before they are answered
- `## Design review` above (written 2026-10-13a, review: guard, write-op, shipped)
- `docs/evidence/framework-coverage-2026-10-12.md`; FRAMEWORK §3.1 to §3.4, §6.2, §8.1, §8.2

## Traps

- G-D3 can check a bare file name against a stale `build/` copy (CE-41): cite `src/context_engine/...` paths in full
- Landing G-T1 turns the gate red at once (US-10, US-12, US-13 have no criterion): land the guard and the fixes in one commit

## Log

- 2026-10-13b (claude-code/claude-opus-5-5): Owner, 2026-10-13b: "Let's try to get it ready for first use then trial it on a repo": CE-38 then CE-7 (the trial) lead; CE-25 waits on ASK-3.
