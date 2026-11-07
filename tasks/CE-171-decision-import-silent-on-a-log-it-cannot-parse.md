---
type: Task
id: CE-171
title: 'decision import: silent on a log it cannot parse, and its dry run and output misreport'
brief: Seen in CE-11 (intervals cutover)
pri: NOW
state: open
deps: []
goals: [G-6]
source: session 2026-11-02a
created: 2026-11-02
moved: 2026-11-07e
updated: 2026-11-07e
---

From the CE-11 intervals cutover (2026-11-02a): (1) decision import on a log whose headings it does not recognise reports 0 entries and 0 problems and exits clean; it should refuse. (2) The dry run lists only # and ## headings kept inside entries and said none where 55 ### and 10 #### lines sat inside entries. (3) The import output gives line numbers of the normalised copy, not the original log. (4) With a prefix equal to the log one, no record gets an alias, so the bare unhyphenated D17 form (about 287 uses in intervals) cannot be aliased at import.

## Log

- 2026-11-07e (claude-code/claude-opus-5-5): Part 4 (bare D17 alias at import) split to CE-202 (DEC-213); parts 1-3 built under CE-171 (DEC-210, DEC-211, DEC-212).
