---
type: Task
id: CE-55
title: "The engine commits at milestones, not every write (DEC-36); task close's commit carries Closes: and the sabotage lines"
brief: Keep CE-45's sweep, change its trigger; build after CE-49 merges, which touches the same op code
pri: NEXT
state: open
deps: [CE-49]
source: session 2026-10-13c
created: 2026-10-13
moved: 2026-10-13c
updated: 2026-10-13c
---

Found 2026-10-13c closing CE-45: commit.py::message titles every engine commit `engine: <op> <id>` with only a Session: trailer. DEC-22 wants `Closes: CE-n` on the commit that finishes a task, and the sabotage rule (DEC-11) puts `Sabotage:` lines in the commit message; once the engine commits the close itself there is no hand commit to carry either. CE-45 itself was closed through the pre-restart MCP server (old code, no commit) and committed by hand. Recommendation: task close adds `Closes: <id>` to its commit, and takes an optional message body (or the close's msg) for the sabotage and receipt lines; rituals § Clean close and manual-mode say so.

## Log

- 2026-10-13c (claude-code/claude-opus-5-5): Widened 2026-10-13c by DEC-36 (owner: "Your recommendation seems fine, yup file and bump it to next"). Scope: [engine] commit becomes a policy, milestones (default) | every-write | off; milestones are task close (Closes: plus sabotage and receipt lines), the owner-words writes (story new, amend, retire; decision; ask answer), pause and baton, session close; everything else rides with the next commit. Add `context-engine commit <paths> -m ...`, which wraps git commit -o with commit.py's sweep so a session's own commits never split records from their op lines. Update FRAMEWORK §5.5 rule 4, the gate exception wording (it now covers milestone commits only), rituals and manual-mode, and the kit README. Review triggers: write-op, git-loss, shipped. Deps: CE-49 merged first.
