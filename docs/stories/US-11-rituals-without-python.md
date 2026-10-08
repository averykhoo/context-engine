---
type: Story
id: US-11
title: Everything the engine does can also be done by hand from written rituals, for a repo with no Python
actor: owner
via: Claude Code chat session 2026-10-08 (after 2026-10-08d)
date: 2026-10-08
story_status: live
goals: [G5, G6]
---

## Owner's words (verbatim)

> I think we need to document the working rituals somewhere as a sort of fallback in case the
> place we want to use this context framework doesn't have python
>
> So everything the engine does should be doable (albeit painfully and expensively) with rituals

## Notes

AGENT: this changes CE-8. Its plan was to rewrite `CLAUDE.md` § Rituals as `ce` commands; the
hand procedure must not be lost in that rewrite. It moves into a manual-mode runbook (FRAMEWORK
§7.5) that covers every `ce` operation, and that stays the fallback after cutover. Parity between
the runbook and the CLI wants a guard, not a promise: every `ce` subcommand has a runbook
section, and a missing one fails the gate.
