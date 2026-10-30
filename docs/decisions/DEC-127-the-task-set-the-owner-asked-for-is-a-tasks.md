---
type: Decision
id: DEC-127
title: "The task set the owner asked for is a tasks: line in the session's ledger stub, written by a new op session tasks"
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:82f13e72b495f6f6ecce94c5335b01bacdffa8e0dfaeaebe2299bd7a310b638b
---

The agent's call on CE-112, made while building it in session 2026-10-30a: where the task set the owner asked for is recorded, and by what operation.

Options:
(a) a new op `session tasks <ids>` that adds the ids to the stub's `- **tasks:**` line, as `ask raised` does for `asked:`;
(b) `session start --tasks <ids>`;
(c) a separate record kind or a field in HANDOFF.

Chose (a). Intake usually happens after session start, and the owner can add tasks during the session, so start-time only (b) is too early. The stub is already the per-session record that close reads, so the check needs no new kind (c). The op is not a milestone and writes only the session's own stub. With no ids it only reports each named task's state.

The close refuses rows that do not name every named id, whether done or not. It does NOT refuse a close while named tasks are still open: the owner may stop, or a task may wait on the owner, and the rows say how each one ended. A resuming session re-names the paused entry's tasks with `session tasks` (procedures § Resume), rather than pause resume carrying them automatically, because that is a doc step with no new code. `session tasks` refuses an id that the line's parser (working.py::ID_RE: capital letters, hyphen, digits) would not read back, so an id never drops out of the check silently.

Built in lane commits d6aa802 and f6a5dad, on main as bd95ea1 and ba98530; pinned by AC-155 and AC-156. Cheap to undo: a local commit, one op, two criteria.
