---
type: Task
id: CE-49
title: 'Retiring a story: an op and a by-hand step'
brief: G-I1 and G-I2 remedies can only say 'file a task' until a story can be retired
pri: NEXT
state: closed
deps: []
source: session 2026-10-13b
created: 2026-10-13
moved: 2026-10-13c
updated: 2026-10-13c
review: [write-op, guard, shipped]
status: deprecated
closed: 2026-10-13c
---

From CE-25's review (2026-10-13b, false-red-deploy F6, partly fixed in adfc6db): the G-I1 and G-I2 per-story remedies used to say 'record the story again and retire this one', but no op retires a story and manual-mode has no by-hand step; a hand edit of story_status on a stamped story passes lint, and nothing records who retired it or why. Recommendation: a record op that sets story_status (retired, with a superseded_by link where one exists) carrying the session key and an op-log line, its manual-mode section, then point both remedies at it.

## Design review

affects: the owner, whose stories are retired and whose words record why; every agent session, which follows the G-I1 and G-I2 remedies and intake step 5; every repo the kit deploys to, whose stories retired by hand before adoption now go G-I2 red
- eliminated: a story is retired with no record of who retired it or why | rung: eliminate | control: `record retire` (working.py::Engine.retire) is the only write path to story_status retired; the who and why are an amendment on the story and each record changed gets an op log line
- eliminated: the G-I1 and G-I2 remedies can only say "file a task" | rung: eliminate | control: guards.py::retire_hint names `record retire <id> --by agent --superseded-by <new id>`; tests/test_retire.py follows the remedy to green
- reduced: a story is retired, or a retire undone, by a hand edit of story_status | rung: collective | control: G-I2 (guards.py::retire_problems) reds a retired story with no logged retire and a logged retire whose story_status or status changed since; the op refuses a story a logged retire already retired
- reduced: an agent withdraws owner intent by retiring a story | rung: reduce | control: `--by agent` needs a successor whose words as typed equal the story's (working.py::_same_words); any other retire is `--by owner` or `human:<id>` with their verbatim words
- reduced: a retire half-written when its second write fails | rung: reduce | control: the successor's idempotent supersedes link is written first, so a retry completes it; tests/test_retire.py::test_a_retire_whose_second_write_fails_is_completed_by_a_retry
- residual: a hand-forged retire line in the op log, or a deleted retire amendment, passes G-I2 | rung: individual | why: the op log and amendments are trusted as written, as G-W7 trusts them | control: FRAMEWORK §8.1 G-I2 names it under Not checked; review at intake
- residual: a hand edit between live, unspecified and unconfirmed passes lint | rung: individual | why: no op owns those moves, and the op log records keys, not values | control: FRAMEWORK §8.1 G-I2 Not checked; a confirm op is the follow-up
- residual: supersedes and superseded_by not mirrored, a self link or a cycle passes, for stories and decisions both | rung: individual | why: no mirror guard exists | control: record retire writes both directions; a mirror guard is the follow-up
F: goes stale when the story schema, its status vocabulary or the amendment format changes, or when an op learns to write story_status; tests/test_retire.py and the 36-row tools/sabotage_ce49.py red on each
A: by hand, manual-mode § record retire (both copies byte-equal): add the amendment with the retirer's words, set story_status and status, write both links and the op log line; rituals § Intake step 5 says when
M: one op (working.py::Engine.retire) on CLI, MCP and library; G-I2's retire check shares its reading of the op log with the op's refusal
E: reuses Store.update with an amendment, decision supersede's two-way link, the G-I2 frame and the sabotage table with a stricter checker (named tests and reason text only); review by false-pass, false-red/deploy and spec-fidelity lenses and a skeptic; AC-72 and AC-73 added, AC-66 reworded

## Log

- 2026-10-13c (claude-code/claude-opus-5-5): Built 2026-10-13c in worktree ce-49 (build; false-pass, false-red/deploy and spec-fidelity lenses; a skeptic; fix): 2e265ed, ff13174, fast-forwarded onto main. `record retire <id> --by owner|human:<id>|agent [--superseded-by <id>] --file <words>`: the reason is an amendment, superseded_by must name a standing story and both links are written, a retire is final, and an agent may only move a story to one with the same words (stricter than the item asked, from the false-pass review). G-I2 now reds a retire made or undone by hand. Decisions taken in the owner's place are in the agent's report: no undo, born-retired stories refused, adoption retires use --by owner with the batched §11.4 answer. Gate on main: 575 passed. First-hand sabotage: guards.py::retire_problems returning [] -> tests/test_retire.py::test_g_i2_reds_a_retire_made_or_undone_by_hand_and_a_story_link_that_resolves_to_no_story red.
- 2026-10-13c (claude-code/claude-opus-5-5): closed: done in 2e265ed..ff13174 (record retire, its by-hand step, G-I2 reds a hand retire; reviewed by three lenses and a skeptic; gate 575 passed)
