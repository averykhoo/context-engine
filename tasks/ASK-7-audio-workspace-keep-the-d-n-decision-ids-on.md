---
type: Question
id: ASK-7
title: 'audio-workspace: keep the D-n decision ids on import, or renumber into DEC-n?'
brief: "Recommend: keep D-n (init --prefix decision=D, import keeps each number), so the repo's many D-n citations stay valid"
pri: NEXT
state: open
deps: []
source: session 2026-10-17b
created: 2026-10-17
moved: 2026-10-17b
updated: 2026-10-17b
last_asked: 2026-10-17b
blocks: [CE-43]
---

Full migration (DEC-51) imports docs/decisions.md (D-1..D-304 on 2026-10-17a). D-n is cited across code, tests, docs and CLAUDE.md; renumbering would need every citation rewritten or an alias map. Letter ids like D-159b and amendment headings (D-107 FIX) need a rule either way.
