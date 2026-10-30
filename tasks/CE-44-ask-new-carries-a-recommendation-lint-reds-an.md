---
type: Task
id: CE-44
title: ask new carries a recommendation; lint fails an open ASK without one
brief: DEC-34's rule made mechanical; a recommendation may say why none was cheap to reach
pri: LATER
state: closed
deps: []
source: session 2026-10-13b
created: 2026-10-13
moved: 2026-10-30a
updated: 2026-10-30a
goals: [G-2]
status: deprecated
closed: 2026-10-30a
---

DEC-34 (owner, 2026-10-13b): every owner question carries a reasonably confident recommendation, when one is cheap to reach (not a long fable session, not building a feature to decide). The text rule goes into FRAMEWORK §5.3 and procedures § Intake now. This item makes it a refusal: ask new requires a recommendation (or an explicit 'none: <why it was not cheap>'), and a lint guard fails an open ASK whose body has none.

## Log

- 2026-10-22a (claude-code/claude-opus-5-5): Scope widened by DEC-34 amendment (owner, 2026-10-22a): every ask records context, several options and a recommendation with reasoning; the exemptions are a recommendation too costly to reach or one that genuinely needs human judgement (the ask then says which). The refusal and lint guard should check all three parts, not just a recommendation.
- 2026-10-30a (claude-code/claude-opus-5-5): closed: Done in 10f8717 (lane 143bb4b), cite in dcc6cd5: ask new refuses an open question whose body lacks context, two or more options, or a recommendation with its reasoning (or none naming its exemption: too costly / human judgement); G-W4 re-checks every open question's stored body; CLI --body-file. AC-121, AC-122 tested; DEC-102, DEC-103, DEC-104.
