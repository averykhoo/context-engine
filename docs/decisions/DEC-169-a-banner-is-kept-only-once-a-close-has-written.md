---
type: Decision
id: DEC-169
title: A banner is kept only once a close has written it under CE-195
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
decided: 2026-11-06
session: 2026-11-06f
body_sha: sha256:ce96727b6942f7b14d206cb1fb93292dd5226158a87ab142cca0fbcff2b609eb
---

verify-2 D1 (2026-11-06f): G-W1 accepted any close whose receipt said banner: kept <key>, so a banner from before CE-195, still copying NOW, NEXT or push lines that orient now generates, could be kept by every close with lint green. Now session close without --banner refuses, and G-W1 fails a kept receipt, until some close says banner: set, or another close kept this same banner (working.py::Engine._banner_cut). A banner written this session by banner set before the close gives banner: set. So each repo's first close under CE-195 cuts its banner, which makes the upgrade step a refusal rather than a doc instruction. Cheap to undo: drop the check. Wrong if a ledger loses its banner: set entry (none is trimmed today): the next close then has to pass a banner once more.
