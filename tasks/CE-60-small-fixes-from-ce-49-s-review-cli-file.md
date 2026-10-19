---
type: Task
id: CE-60
title: "Small fixes from CE-49's review: CLI --file traceback, manual-mode record correct row, older sabotage checkers"
brief: Three small defects found in passing; each needs a test seen red
pri: LATER
state: open
deps: []
source: session 2026-10-13c
created: 2026-10-13
moved: 2026-10-13c
updated: 2026-10-19f
---

From CE-49's review (2026-10-13c): (1) a missing `--file` path on the CLI is a traceback, not a refusal with a remedy; (2) manual-mode's op log table says `record correct` logs `["body_sha","body"]`, but the engine logs `["body"]` (wrong before CE-49); (3) tools/sabotage_ce26.py and older tables count a row red on any match in pytest's stdout, which prints test source, so an unrelated failure can pass as red; tools/sabotage_ce49.py's checker (named tests fail, reason text in the failing line) is the pattern.

## Log

- 2026-10-19f (claude-code/claude-opus-5-5): Items 1 and 3 done (item 1 was already done: cli.py::_read; item 3 in a506054). Left: item 2, frozen kit wording. manual-mode.md op-log row (both copies) reads | record correct | `correct` | the record | `["body_sha", "body"]` |; proposed: `["body"]` (the stamp is untouched: it pins the words with their corrections undone).
