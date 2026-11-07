---
type: Decision
id: DEC-206
title: "Reserved ids pass the write-time twin only when this session holds them (CE-183): another session's reserved id is refused, since this session cannot make it be written"
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:8b730f90a5a060d966f1c76f39e14d64fc1f9ea342c91f194e7c4b7a95422078
---

Beyond what lint accepts, the write-time citation check lets two ids pass: the id the record is being written with (`--id`), and ids this session reserved with `id reserve` (store.py::Store.reserved_ids, the value naming this session). That keeps the reserved-batch flow of procedures § Intake working: a batch of records citing each other is written one by one, and lint stays red on a not-yet-written id until the batch is done, as before.

An id another session reserved is refused: this session can never write it (store.py::Store.create_many refuses it to every other session), so nothing this session does makes the citation true. The writer waits until it is written, or puts it in backticks.
