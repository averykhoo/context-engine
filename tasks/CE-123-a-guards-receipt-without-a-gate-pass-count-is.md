---
type: Task
id: CE-123
title: A guards receipt without a gate pass count is refused
brief: A close receipt must carry the gate pass count; refuse a guards receipt that omits it
pri: NOW
state: open
deps: []
goals: [G-2]
source: session 2026-10-21b
created: 2026-10-21
moved: 2026-10-30a
updated: 2026-10-30a
---

A guards receipt without a gate pass count is refused

What went wrong (adhoc AAR entry 36, docs/evidence/adhoc-feedback-2026-10-21.md) and what to change: The newest close's receipt had no gate pass count, so the test baseline is unknown (entry 36). Refuse (or lint) a guards receipt that has no gate line. Census F26: NEW, low. Filed 2026-10-21b from the CE-7 census (.scratch/ce7-feedback/census.md, row F26).

## Traps

## Read first

- docs/evidence/adhoc-feedback-2026-10-21.md

## Log

- 2026-10-23a (claude-code/claude-opus-5-5): Built and sabotaged in sweep 2026-10-23a, not committed: needs gate_receipt in kit/context.toml.template (frozen). Plan: template key, config.py Working.gate_receipt with re.compile, refusal in session_close; this repo's value '(?i)\d+ passed|passed \d+|gate not run|gate status'.
