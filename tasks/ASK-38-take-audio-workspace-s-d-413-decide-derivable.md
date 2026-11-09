---
type: Question
id: ASK-38
title: Take audio-workspace's D-413 (decide derivable or cheap-to-reverse questions; an ask decide path) into the framework (item 12)?
brief: Its words are owner words in audio-workspace only; intake here needs your yes first
pri: LATER
state: closed
deps: []
source: session 2026-11-07e
created: 2026-11-08
moved: 2026-11-07e
updated: 2026-11-10a
last_asked: 2026-11-10a
status: deprecated
closed: 2026-11-10a
answered: {on: 2026-11-10, session: 2026-11-10a, decision: DEC-325}
---

**Question:** Should audio-workspace's D-413 become framework intent here, and with fable?

**Context:** audio-workspace feedback entry 12 quotes your words from its session 2026-11-06d, recorded there as its D-413 ("make recommendations and give context when you ask, and where possible get fables opinion instead of asking me ... Or if it can be reversed without too much cost and doesn't change the project direction then just go ahead ... And note this in the context engine feedback too"). They were said in another repo, so they are not recorded here as owner words. Already in this framework: the contract's Who decides rule (P8) makes a cheap-to-undo call the agent's, PROVISIONAL, not a question; `ask new` refuses a question without a recommendation (CE-44). New: a step that decides a question derivable from the goals and earlier decisions, with fable's opinion (DEC-18 allows fable when you ask for it), and an `ask decide` path that closes a question as answered by an agent decision, which FRAMEWORK §5.3 forbids today (an owner question is closed only by your answer, CE-20).

**Why owner-only:** it would record owner words in this repo and change who may close an owner question, both owner calls.

**Options:**

- A. Yes: intake the quote here verbatim as a story, then file tasks for the triage step (procedures and FRAMEWORK §5.3) and for `ask decide`, with fable as the derivable step's second opinion.
- B. Yes, without fable: as A, but the second opinion is an opus verifier, keeping DEC-18's default.
- C. Keep it local to audio-workspace: its CLAUDE.md carries the rule; the framework only gains `ask decide`, allowed where a repo's own rules delegate such calls.
- D. No change: P8 already covers the cheap-to-undo half, and a delegated question stays open until you answer it.

**Recommendation:** A, flagged as your call: the cheap-to-undo half is already P8, so the new parts are small, and you asked for fable's opinion by name, which DEC-18 permits; one cheap fable call per derivable question, never a fan-out. Any contract wording waits for the next framework version bump.

**Blocks:** none

## Log

- 2026-11-10a (claude-code/claude-opus-5-5): answered by the owner: DEC-325
