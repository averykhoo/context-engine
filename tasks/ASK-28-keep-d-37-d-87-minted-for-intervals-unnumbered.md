---
type: Question
id: ASK-28
title: Keep D-37..D-87 minted for intervals' unnumbered log entries?
brief: Recommend keep; IV-23 fixes statuses
pri: LATER
state: closed
deps: []
source: session 2026-11-02a
created: 2026-11-02
moved: 2026-11-02a
updated: 2026-11-03a
last_asked: 2026-11-03a
blocks: [CE-11]
status: deprecated
closed: 2026-11-03a
answered: {on: 2026-11-03, session: 2026-11-03a, decision: DEC-149, ruled_by: claude-code/claude-opus-5-5}
---

## Context

intervals' decision log had D1-D36 numbered, plus 49 log entries and 2 decision paragraphs with no
id. The cutover imported all 87 as records: D1-D30 became D-1..D-30, D31-D36 kept their numbers, and
the 51 unnumbered entries were minted D-37..D-87, oldest first. About 20 of those are build or review
records rather than decisions. This replaces the log's own "D37 is next" rule. All 87 carry
`decision_status: BUILT`, including some the text itself marks superseded (IV-23 tracks that review).

## Options

- Keep D-37..D-87 as minted.
- Re-import with only real decisions in the D series, the build and review records kept as evidence
  docs instead.

## Recommendation

Keep them as minted: nothing is lost, the series is in date order, and re-importing costs a second
cutover. IV-23 can set the right status on each.

## Log

- 2026-11-03a (claude-code/claude-opus-5-5): answered on the owner's delegation, ruled by claude-code/claude-opus-5-5: DEC-149
