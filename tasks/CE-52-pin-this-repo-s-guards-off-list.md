---
type: Task
id: CE-52
title: Pin this repo's [guards] off list
brief: A guard switched off with no decision is a silent false green; a test, not a doc warning
pri: LATER
state: open
deps: []
source: session 2026-10-13c
created: 2026-10-13
moved: 2026-10-13c
updated: 2026-10-13c
---

From CE-26's false-pass review (2026-10-13c, FP#6): nothing stops a commit that adds G-R1, G-D1 or any guard to this repo's [guards] off list, which silences it with lint green. Recommendation: a test pins the off list to its current value and names the decision needed to change it.
