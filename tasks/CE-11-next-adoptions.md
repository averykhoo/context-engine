---
type: Task
id: CE-11
title: Adopt the engine in intervals; zanzibar follows as CE-167
brief: No 2.0.0 wait (DEC-135); intervals before zanzibar (DEC-134); model on CE-43; no push without the owner
pri: NOW
state: open
deps: [CE-7]
source: session 2026-10-08a
created: 2026-10-08
moved: 2026-11-01b
updated: 2026-11-01b
closed:
goals: [G-6]
---

See `docs/decisions/DEC-6-adhoc-first.md` for why intervals goes second.

## Log

- 2026-11-01a (claude-code/claude-opus-5-5): Owner, 2026-11-01a (DEC-134): intervals goes before zanzibar; zanzibar split out as CE-167 (deps CE-11). audio-workspace already adopted (CE-43).
- 2026-11-01a (claude-code/claude-opus-5-5): Owner, 2026-11-01a (DEC-135): adopt now, the 2.0.0 condition is dropped; promoted SOMEDAY->NEXT.
- 2026-11-01b (claude-code/claude-opus-5-5): Owner, 2026-11-01b: "Finish ce6 now then push up ce11": CE-6 closed this session, CE-11 promoted to NOW.
