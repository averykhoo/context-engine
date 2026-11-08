---
type: Decision
id: DEC-275
title: 'CE-126: a lane is any ^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$ token, not checked against the board (the task id is recommended); empty or whitespace means no lane; `*` is reserved as EVERY_LANE'
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:2ec284190b754ad053b2c23be6c1fc21122d2a6d075d9250561ba17c533ff5d9
---

The agent's call on CE-126, building DEC-84's option B in session 2026-11-07e: what a lane value may be.

A lane is any token matching `^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$` (`store.py::LANE_RE`), checked by `store.py::check_lane` before anything is written. It is not checked against the board: a verifier or census agent may work no board item, so the task id is recommended (the fan-out rule says so), not required. An empty or whitespace-only value means no lane, so an unset or blanked `CE_AGENT` is the coordinator. `*` can never match the pattern and is reserved as `commit.EVERY_LANE`, the selector a session close uses to take every lane.

Rejected: checking that the lane names an open board item (it would refuse a verifier's writes).

Cheap to undo: one regex.
