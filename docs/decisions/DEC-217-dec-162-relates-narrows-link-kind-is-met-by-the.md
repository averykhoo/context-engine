---
type: Decision
id: DEC-217
title: DEC-162 relates/narrows link kind is met by the existing `refs` and `relaxes`/`narrowed_by` links (CE-5); no new link field or `--rel` alias; `_link_rel` remedy and manual-mode decision link now name `--rel refs`
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
tasks: [CE-189]
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:f1fde7ce2f7ac0ba0919f0c43bef91b9d604b22e219771e1067acfffd905422e
---

DEC-162's relates/narrows link kind is met by links built in CE-5 (4190458): `relaxes`, with its backlink `narrowed_by` (decisions.py::BACKLINK, working.py::Engine.link), is the narrows link, and `refs` links any other record, a decision included. DEC-126 already has `refs: [DEC-112]`, and DEC-125 has `supersedes: [DEC-88]`, so both of the advice's example pairs are links now.

No new `relates` field and no `--rel relates` or `--rel narrows` alias is added: those would be two spellings for links that exist, and lint, `why`, `decision find --links-to` and the site would all have to learn the mapping. What was missing is that `refs` was hard to find: working.py::Engine._link_rel's refusal for a decision target given without `--rel` named only `decision supersede` and `--rel relaxes`, and manual-mode § context-engine decision link said a decision needs `--rel relaxes`. Both now name `--rel refs` too.

Cost to undo: cheap; an alias can be added later if the spelling proves to matter.
