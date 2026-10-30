---
type: Task
id: CE-111
title: "ask new --answered: record an owner's chat answer to a question that had no ask record"
brief: 'Recording a chat answer must not need a hand-built decision: ask new --answered'
pri: NOW
state: closed
deps: []
goals: [G-2]
source: session 2026-10-21b
created: 2026-10-21
moved: 2026-10-30a
updated: 2026-10-30a
status: deprecated
closed: 2026-10-30a
---

ask new --answered: record an owner's chat answer to a question that had no ask record

What went wrong (adhoc AAR entry 14, docs/evidence/adhoc-feedback-2026-10-21.md) and what to change: An owner answered a question asked through the chat tool; with no ask record, recording it needed a hand-built decision (entry 14). Add `ask new --answered` (question and words in one op) that writes the ask closed and the decision. Census F9: NEW; related to CE-44. Filed 2026-10-21b from the CE-7 census (.scratch/ce7-feedback/census.md, row F9).

## Traps

## Read first

- docs/evidence/adhoc-feedback-2026-10-21.md

## Log

- 2026-10-30a (claude-code/claude-opus-5-5): closed: Done in 3247ca7 (lane 530bc18), cite in 037aa94: ask new "<question>" --answered <words>|--answered-file <f> --decision-title "<t>" (MCP answered/decision_title, ruling/ruled_by) files the question closed and records the owner's words as the decision ask answer writes, in one milestone commit; refusals write nothing. AC-120 tested; DEC-99, DEC-100, DEC-101.
