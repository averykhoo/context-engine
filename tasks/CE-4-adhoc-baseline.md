---
type: Task
id: CE-4
title: "Measure adhoc's session start and close cost today, before any cutover"
brief: "Read-only in adhoc, which may have a live session. Write the rubric down before measuring"
pri: NOW
state: open
deps: []
source: session 2026-10-08a
created: 2026-10-08
moved: 2026-10-10c
updated: 2026-10-10c
closed:
---

The trial's comparison means nothing without a baseline (FRAMEWORK §8.0.3). Measure what a cold
session in `PycharmProjects/adhoc-microphone-array` reads at session start and writes at a
clean close today: the files and their bytes (`CLAUDE.md` 16,196 B and `HANDOFF.md` 28,407 B on
2026-10-08), plus whatever its rituals send it to. Write the rubric first (what is measured, how,
what counts as better), then the dated numbers, into a tracked evidence doc here:
`docs/evidence/adhoc-baseline-<date>.md`.

## Traps

- **Read-only.** Do not edit adhoc. Run `git status` there first: it was being worked on
  2026-10-08 (commits at 10:33 and 12:20).
- Bytes are a proxy for context. If a token count is possible, record both and say which.

## Read first

- `docs/framework/FRAMEWORK.md` §8.0.3, §6.1, §6.3
- `docs/decisions/DEC-6-adhoc-first.md`
- adhoc `CLAUDE.md`, and `HANDOFF.md` § "next session: start here"

## Log
