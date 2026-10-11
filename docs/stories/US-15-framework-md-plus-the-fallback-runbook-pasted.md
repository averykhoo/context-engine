---
type: Story
id: US-15
title: FRAMEWORK.md plus the fallback runbook, pasted into a repo, are all an agent needs; rituals and housekeeping have one source of truth
actor: owner
story_status: live
goals: [G4, G6, G7]
via: Claude Code chat session 2026-10-11 (after 2026-10-11c) and 2026-10-12a
date: 2026-10-12
body_sha: sha256:989e52b4d73a325da1ffbe0ee1b5fa5e15e6b7237bc7b3c3f3753b336b2aa719
---

## Owner's words (verbatim)

> Check that framework.md is comprehensive. If I paste it into a repo (plus the md file about
> backup rituals) that should include everything that's needed for an agent to start using the
> framework. Are the backup rituals (e.g., when there's no python) are already in there? We should
> probably have a single source of truth for rituals and housekeeping?

The agent answered with a paste test (`docs/evidence/framework-paste-test-2026-10-12.md`) and
proposed: FRAMEWORK.md keeps rules and reasons, one rituals runbook holds the ordered steps
(engine command and by-hand step side by side), manual-mode stays the per-operation reference,
`CLAUDE.md` § Rituals becomes a pointer, and adoption ships a kit. The owner replied:

> Yes go for it

## Notes

AGENT: extends US-11 (rituals without Python) from per-operation fallbacks to whole rituals,
and makes the order of each ritual live in exactly one file. The adoption kit is CE-15's.
