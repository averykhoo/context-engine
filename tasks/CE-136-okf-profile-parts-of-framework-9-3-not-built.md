---
type: Task
id: CE-136
title: 'OKF profile parts of FRAMEWORK §9.3 not built: generated log.md, generated.by, stale_after refusal, charter_status read'
brief: §9.3 states each as the profile; none exists in src/ (2026-10-24)
pri: NOW
state: closed
deps: []
goals: [G-7, G-5]
source: session 2026-10-23f
created: 2026-10-24
moved: 2026-10-30a
updated: 2026-10-30a
status: deprecated
closed: 2026-10-30a
---

FRAMEWORK §9.3's table states our OKF profile. Four parts of it do not exist (grep of `src/context_engine/`, 2026-10-24). Filed by CE-93's fix round, which dropped the spec's *Not built yet* cells; no open item tracked them.

1. **Concept changelog:** `log.md` generated from decisions' `creates/amends/retires`. No `log.md` is generated.
2. **Who and when:** the writing agent goes into `generated.by`. `generated.by` is not written (the op log carries the actor per write).
3. **Freshness:** the profile refuses an expired `stale_after` on a live item (bound to `manual` criteria and register entries about something external). Nothing reads `stale_after`.
4. **Lifecycle keys:** the charter carries `charter_status`. Nothing reads it.

Each part is built (with a refusal, a lint check and a sabotage) or cut from §9.3 by a decision; either way §9.3 ends true.

## Traps

## Read first

- `docs/framework/FRAMEWORK.md` §9.3, §9.3.1

## Log

- 2026-10-30a (claude-code/claude-opus-5-5): closed: OKF profile of FRAMEWORK §9.3 ends true. Built: G-D4's freshness half (guards.py::stale) refuses an expired stale_after on a live record, criterion or register entry, and a value that is not an absolute instant (AC-150). G-I1 reads the charter's charter_status and status, and orient asks the owner about an unconfirmed charter (AC-151). Cut by PROVISIONAL DEC-120: the generated log.md and generated.by, since the op log is the one record of who wrote what and when. Done in 8b4e799 (lane eb743f1), DEC-120 in 650fe5c, cited in 8c86c6d.
