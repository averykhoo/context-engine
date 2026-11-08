---
type: Decision
id: DEC-318
title: Trimmed global CLAUDE.md keeps machine and harness facts verbatim, adds a framework-repo pointer, re-homes framework-shaped rules the framework lacks, and offers an optional at-most-10-line baseline for non-framework repos (DEC-162)
tasks: [CE-40]
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:493312ddbbb7cc9da3a3bd8f28bdcb358fdf1f8e2de99439332dcc5b6f7355fb
---

An agent's call under P8 (cheap to undo: a proposal in a tracked doc; the owner pastes it or not), made by CE-40's builder in session 2026-11-07e on 2026-11-08, following the planner's design. Not owner words.

The proposed trimmed global `CLAUDE.md` (CE-40's doc, section 4):

1. keeps the machine and harness facts verbatim (two shells, Python environments, Docker, the CI token recipes, facts about other repos, subagent transcripts), so a check can confirm no line was lost;
2. adds a pointer section: a repo whose `CLAUDE.md` has a `framework: <version>` line and imports `@docs/framework/contract.md` follows its contract and runbooks, which win;
3. re-homes the framework-shaped rules no framework text holds yet into a "Not yet in the framework" section;
4. offers an optional baseline of at most 10 lines for repos without the framework, in the owner's current words, which the owner may delete to take DEC-162's gap whole.

Rejected: rewording the machine sections for brevity (risks dropping a fact that bit before; verbatim is cheaper to verify); a lean-only text with no baseline (DEC-162 allows it, but the baseline is about 10 lines and deletes in one stroke).
