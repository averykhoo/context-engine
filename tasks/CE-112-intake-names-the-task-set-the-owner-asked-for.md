---
type: Task
id: CE-112
title: Intake names the task set the owner asked for, so close-eagerly knows when it is done
brief: At intake record the named task set; clean close fires when every named task is done
pri: NOW
state: closed
deps: []
goals: [G-7]
source: session 2026-10-21b
created: 2026-10-21
moved: 2026-10-30a
updated: 2026-10-30a
status: deprecated
closed: 2026-10-30a
---

Intake names the task set the owner asked for, so close-eagerly knows when it is done

What went wrong (adhoc AAR entry 17b, docs/evidence/adhoc-feedback-2026-10-21.md) and what to change: The close-eagerly rule is fixed (CE-82), but the session has no recorded list of the tasks the owner asked for, so 'every task asked for is done' is judged from memory (entry 17b). Add an intake step and a field for the named set. Census F12: named-task-set part only is NEW; the rule itself is FIXED by CE-82. Filed 2026-10-21b from the CE-7 census (.scratch/ce7-feedback/census.md, row F12).

## Traps

## Read first

- docs/evidence/adhoc-feedback-2026-10-21.md

## Log

- 2026-10-30a (claude-code/claude-opus-5-5): closed: done in bd95ea1, review fixes in ba98530, decisions cited in 619fb23 (lane intake). `session tasks <ids>` (MCP session_tasks) records the task set the owner asked for as the stub's `tasks:` line (DEC-127). With no ids it reports; orient shows the set. `session close` refuses rows that miss a named task, the close and pause entries keep the line, and G-W6 checks the newest close (DEC-128). A resumer re-names a paused entry's tasks (procedures § Resume, FRAMEWORK §6.4). An id the line cannot read back is refused. AC-155 and AC-156 are tested. FRAMEWORK §6.2 item 7, §6.3, §6.4, §7.1 and the G-W6 guard bullet were updated, and the procedures and manual-mode runbooks are updated (including G-W6 in § lint) with byte-equal kit copies.
