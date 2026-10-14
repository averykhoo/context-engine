---
type: Question
id: ASK-6
title: AC-42 says decision import writes nothing when a prefix is foreign; DEC-37 now renames it. Reword AC-42?
brief: "Recommend: yes, 'renames a foreign prefix to the kind's, keeping the number, the old id an alias (DEC-37)'"
pri: NEXT
state: closed
deps: []
source: session 2026-10-14a
created: 2026-10-14
moved: 2026-10-14a
updated: 2026-10-14b
last_asked: 2026-10-14b
status: deprecated
closed: 2026-10-14b
answered: {on: 2026-10-14, session: 2026-10-14b, decision: DEC-40}
---

CE-74 built DEC-37: decision import renames D-n to DEC-n and keeps D-n as an alias. AC-42 (US-7, tested) still lists 'a prefix is foreign' among the cases where the import writes nothing. Criteria wording is the owner's. Recommendation: reword that clause to 'renames an id in another prefix to the kind's, keeping the number and the old id as an alias (DEC-37)', and leave the rest of AC-42 as it is. CE-74's import tests already claim AC-42 with the new behaviour.

## Log

- 2026-10-14b (claude-code/claude-opus-5-5): answered by the owner: DEC-40
