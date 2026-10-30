---
type: Decision
id: DEC-92
title: Linked batches reserve their ids with an id-reserve op, not a batch task new
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:1dc1d2636821e7e8742403e231e035adb715b5ac4c731039204e77487a4739e7
---

The agent's call on CE-105 (with CE-119), made while building it in session 2026-10-30a: how a batch of linked records gets ids it can cite before they are written.

Options:
(a) a batch `task new` that takes symbolic names in the bodies and resolves them to ids at write time;
(b) an `id reserve <kind> --count n` op that holds the next ids in the op log for the session, after which each record is written with `--id`.

Chose (b). It serves tasks, questions, decisions and stories alike, which covers CE-119's `DEC-<NEW>` case: the coordinator reserves the DEC id and hands it to the drafting agent. It reuses the existing `--id` path (store.py::Store.create_many) and needs no symbolic-name syntax in bodies.

Sub-calls, all cheap to undo:
- an `id.reserve` op line names path "" (it writes no file), so another session's commit never carries it by path;
- at most 20 ids per call (store.py::RESERVE_MAX, a judgement);
- it is not a milestone, so its lines ride along to the next commit;
- only board and append-only kinds can be reserved;
- the floor is the max of the ids files hold, the ids created op lines name, and earlier reservations;
- a reserved id that is never written stays a gap.

Built in 069e198. Known gap at landing: `record new --id` accepts any never-used id, not only one this session reserved, while its help text and manual-mode § context-engine record new say it must be reserved; a series can then jump, but ids never collide.

This replaces DEC-91, which recorded the same call but quoted the placeholder bare in its prose, so lint (G-D2, CE-119) failed on it; an append-only body cannot be edited, so it is superseded.
