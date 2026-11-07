---
type: Decision
id: DEC-207
title: 'Backticks are the foreign-id form; no repo-qualified id notation (CE-183): rejected because backticks already exempt an id at rest and were the zanzibar workaround, and a notation would not stop a writer unaware of it'
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:f59166f4b50fdfff5b6f72d3ca2de56717f7dacd204087353aefa8adc5e7290b
---

An id of another repo is cited in backticks, with the repo named in the words around it; there is no repo-qualified id notation (such as `context-engine:ASK-32`), which was the item's second option. Backticks already exempt an id from G-D3 at rest, and they were the workaround the zanzibar session used when it recorded its decisions again. A new notation is one more form for every writer and for the by-hand G-D3 rules to learn, and it would not stop a writer who does not know it from writing the bare id. A plain-prose qualifier ("context-engine ASK-32") as an exemption was rejected too: it would exempt a real typo of this repo's own id.
