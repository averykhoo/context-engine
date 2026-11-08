---
type: Task
id: CE-208
title: "ask comment: record an owner's partial answer verbatim, question left open (audio-workspace item 4)"
brief: Owner words, so a milestone; never closes the question; ask answer later cites them
pri: LATER
state: open
deps: []
goals: [G-2]
source: session 2026-11-07e
created: 2026-11-08
moved: 2026-11-07e
updated: 2026-11-07e
---

`ask comment`: record an owner's partial answer to a question verbatim, as a milestone, leaving the question open (audio-workspace feedback item 4).

**What happened** (audio-workspace `docs/context-engine-feedback.md` entry 4, agent-raised, 2026-11-06): the owner answered ASK-102 there conditionally ("errors should be visible yes, this might be merged with 101 depending on how the above exploration goes") and ASK-104 with a counter-proposal and a question back. Neither words closed the question, and the engine has only `ask answer` (which closes it) and `ask raised`, so those owner words lived only in the chat until the final answers; a lost session would have lost them.

**At HEAD cb362ca:** the `ask` group has only new, raised, later and answer (cli.py, the `("ask", v)` op map). `task comment ASK-n` works on a question (working.py::Engine.comment), but it logs under the agent's actor as a one-line Log entry, rides with the next commit instead of being a milestone (DEC-36), and does not mark the words as the owner's.

**The ask:** `ask comment ASK-n --file words.md` records the owner's words verbatim on the question under a dated owner-words part (multi-line, so not a Log line), is a milestone commit like the other owner-words writes (DEC-36), leaves the question open, refuses a closed question, and `ask answer` later cites those earlier words in the decision it writes. Rule the exact part name and where it sits at build time, and record it.

## Traps

- guards.py::ask_parts (through guards.py::_ask_label) opens a new part at any heading of the part's own level or shallower, so a `## Owner words` heading ends the Recommendation and becomes its own part; but a heading deeper than the part above it (`### Owner words` under a bold or `##` Recommendation) is read as that part's text and inflates G-W4's Recommendation word count. Probed 2026-11-08 at cb362ca. Put the owner-words part at the parts' own level, or after `## Log`, where ask_parts stops.
- Owner words verbatim; agent text never inside the quote (G-I3, CE-113).
- The op is logged under the agent's actor, but the part must say the words are the owner's, as the decision `ask answer` writes does (`actor: owner`).

## Read first

- src/context_engine/working.py::Engine.ask_answer
- src/context_engine/working.py::Engine.comment
- src/context_engine/guards.py::ask_parts
- docs/decisions/DEC-36-the-engine-commits-at-milestones-not-at-every.md
- C:/Users/user/PycharmProjects/audio-workspace/docs/context-engine-feedback.md entry 4

## Log
