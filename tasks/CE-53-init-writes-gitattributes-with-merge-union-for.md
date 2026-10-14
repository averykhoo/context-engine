---
type: Task
id: CE-53
title: init writes .gitattributes with merge=union for the op log
brief: Every adopting repo merges branches that both append op lines; never overwrite an owner's .gitattributes
pri: LATER
state: open
deps: []
source: session 2026-10-13c
created: 2026-10-13
moved: 2026-10-13c
updated: 2026-10-13c
---

From CE-45 (2026-10-13c): this repo's .gitattributes now sets `docs/ledger/ops.jsonl merge=union`, so two branches' op lines merge without conflict, but init does not write it, so adopting repos conflict on every branch merge. Recommendation: init appends the line to an existing .gitattributes (or creates one) only with the same owner yes/no as the settings merge (DEC-32); CE-46's eol=lf lines could be added with it.
