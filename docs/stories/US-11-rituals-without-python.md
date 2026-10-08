---
type: Story
id: US-11
title: Everything the engine does can also be done by hand from written rituals, for a repo with no Python
actor: owner
via: Claude Code chat session 2026-10-08 (after 2026-10-08d)
date: 2026-10-08
story_status: live
goals: [G5, G6]
body_sha: sha256:4522631f69e03b0224567dc38eaf63cf68111af0eef4e1e1a926d09fb2187b18
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

## Amendments

- **2026-10-08e (claude-code/claude-opus-5-5):** Owner, verbatim:

  > Yup and the rituals can also include short explanations about why they exist, so if the engine
  > fails or errors the agent will know what the correct action or answer was and why, and be able
  > to fix the engine

  AGENT: so each runbook step carries its reason, and the runbook is the engine's reference
  behaviour: when the engine errors or disagrees with it, the runbook says what the right result
  was, and the agent fixes the engine to match (or, if the runbook is wrong, records why).
