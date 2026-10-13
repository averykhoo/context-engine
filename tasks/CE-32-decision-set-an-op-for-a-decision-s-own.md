---
type: Task
id: CE-32
title: "decision set: an op for a decision's own frontmatter (decision_status, reopen_if, tags)"
brief: No op changes a decision's status, reopen_if or tags; Engine.set refuses decisions, so they are hand-edited
pri: NEXT
state: closed
deps: []
source: session 2026-10-12d
created: 2026-10-12
moved: 2026-10-13a
updated: 2026-10-13a
review: [write-op, shipped]
status: deprecated
closed: 2026-10-13a
---

Found reviewing CE-5 (2026-10-12d). `working.py::Engine.set` refuses a decision ("not a board item"), and `decision supersede` / `decision link` touch only their own fields. So moving a decision PROVISIONAL -> BUILT, adding `reopen_if:` to a REJECTED one, or fixing `tags` has no operation. In 2026-10-12d DEC-15 and DEC-16 had `tags` fixed by hand, with hand-written op-log lines (docs/ledger/ops.jsonl, op `set`, fields [tags]) recording an op the engine cannot perform for that kind. The op log is append-only, so those lines stay; this row closes the gap. Shape to decide: a `decision set` (or `record set` over append-only kinds) that takes only frontmatter keys, never body_sha/id/type, refuses `decision_status: SUPERSEDED` (that is `decision supersede`), regenerates the index, and has a manual-mode section.

## Design review

affects: the owner, whose decisions (owner words, stamped) carry a status, tags and attribution in frontmatter the body_sha does not cover; the next session, which reads a decision's status and the generated index as current; a plain-git human setting a decision key by hand from manual-mode.md; every deployed repo, which gets the operation and the kit runbook copy
- eliminated: a decision's `tags`, `reopen_if` or `decision_status` can change only by a raw edit plus a hand-written op-log line, as DEC-15 and DEC-16 were in 2026-10-12d (`decision set` writes them under the lock, logs `set` with session and actor, and regenerates the index in the same write)
- eliminated: `decision set` changes `type`, `id` or `body_sha` (Store.set refuses the engine-owned keys before any write; a test runs each through the CLI)
- reduced: `decision set` marks a decision SUPERSEDED, or writes a link field or `status`, without its backlink or derived OKF status, leaving a half-written supersede or link | rung: reduce | control: Engine.decision_set refuses `decision_status: SUPERSEDED`, `status`, `answers` and every link field (DECISION_OWNED), naming `decision supersede`, `decision link` or `ask answer`; sabotaged
- reduced: a superseded decision's status is moved back (SUPERSEDED to BUILT), leaving a current decision that still carries `superseded_by` | rung: reduce | control: Engine.decision_set refuses any `decision_status` change on a SUPERSEDED decision, checked under the lock; sabotaged
- reduced: an agent re-attributes a decision (sets `actor: owner` on its own call, rewrites an imported decision's `attribution` or drops its `imported_from`, moves `decided`, `session` or `generated`, or adds `verified` to claim the owner endorsed it), passing an agent's words off as the owner's | rung: reduce | control: Engine.decision_set refuses `actor`, `decided`, `session`, `attribution`, `imported_from` and `generated` (DECISION_OWNED: provenance is fixed at birth) and `verified` (an endorsement is owner words: `record amend`); sabotaged
- reduced: a refusal's remedy names a command that refuses in turn (`narrowed_by` once pointed at `decision link --rel narrowed_by`) | rung: reduce | control: DECISION_OWNED names `decision link <other> <id> --rel relaxes` for `narrowed_by`; a test follows that remedy through the CLI; sabotaged
- reduced: `reopen_if` is set on a live decision, or survives a move off REJECTED, so the index lists a reopen condition for a rejection that does not stand | rung: reduce | control: Engine.decision_set refuses `reopen_if` unless the decision would be REJECTED, checked under the lock; sabotaged
- reduced: the index goes stale after a set | rung: reduce | control: Store.set regenerates the index under the same lock; G-D6 reds a stale one at rest
- residual: an agent moves an owner's decision PROVISIONAL to BUILT, or to REJECTED or DEFERRED, without the owner having said so | rung: individual | why: whether the owner sanctioned a status move is in the owner's words, which no operation can read; the op log names session and actor and the index diff shows the move in the commit | control: manual-mode.md § decision set: move an owner decision's status only on the owner's words, recorded first (`record amend`)
F: goes stale if the decision kind gains a key another operation owns (it must join DECISION_OWNED) or a link field (LINK_FIELDS feeds the refusal, so it joins by itself); the refusal list and manual-mode § decision set name the same keys
A: by hand, manual-mode.md § decision set: edit the one frontmatter key in place, log one `set` line, regenerate the index; reading is the frontmatter itself
M: one Engine.decision_set over Store.set (lock, validation, op log, reindex already there), one DECISION_OWNED table beside BOARD_OWNED, one ops.decision_set wired to the CLI and MCP by OPS
E: mirrors `task set` (same `--set`/`--unset` shape, same one-line return, op `set` as the hand-written DEC-15/16 lines used); reuses Store.set, coerce and the kind's schema; one runbook section beside § decision link and one clause in FRAMEWORK §6.5's operations list

## Log

- 2026-10-13a (claude-code/claude-opus-5-5): built: `decision set <id> --set k=v --unset k` (working.py::Engine.decision_set over Store.set, refusals in working.py::DECISION_OWNED; ops.py::decision_set; manual-mode § decision set; FRAMEWORK §6.5, §8.0.2; AC-53). Shape: decisions only, not `record set` (the refusals are decision-specific); stories' `story_status` still has no op. Awaiting review.
- 2026-10-13a (claude-code/claude-opus-5-5): closed: decision set built and reviewed: refuses links, provenance, verified, SUPERSEDED moves and reopen_if off REJECTED (9a30916)
