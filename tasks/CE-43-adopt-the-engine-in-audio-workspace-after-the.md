---
type: Task
id: CE-43
title: Adopt the engine in audio-workspace after the adhoc trial
brief: The owner's preferred testing ground (DEC-6 amendment); goes before intervals, zanzibar
pri: NOW
state: open
deps: [CE-98]
source: session 2026-10-13b
created: 2026-10-13
moved: 2026-10-17b
updated: 2026-10-19e
---

Owner, 2026-10-13b, on DEC-6: "Adhoc is a good repo yes, we'll do a quick trial there, but I'm hoping to get this into the audio workspace repo soon, since that's a better testing ground". So CE-7 stays a quick trial, and audio-workspace is the next adoption, ahead of the CE-11 order (intervals, then zanzibar and audio-workspace). audio-workspace is a GitLab repo, uses pixi for node only and per-subproject uv venvs (server/.venv); the engine still runs from its own env (DEC-1). Survey the repo (HANDOFF, decision log, board shape, concurrent sessions) before planning the import.

## Log

- 2026-10-17b (claude-code/claude-opus-5-5): Owner, 2026-10-17b (DEC-51): onboard audio-workspace now, ahead of the adhoc trial's feedback (which waits till next week), as a full migration, backup first. Its gate: vitest and the live smoke run before push, not on every commit, so the code scope tied to commits stays cheap. Assessment 2026-10-17a: hard, about 5-10x the adhoc trial; open questions on docs/issues/, the caps and the repo's doc-shape tests are with the owner. The aw-owner-1014 worktree (merged) was removed this session.
- 2026-10-17b (claude-code/claude-opus-5-5): Plan review 2026-10-17b (fable, owner asked; the session checked CLAUDE.md at its 40 KB ceiling and D-221's inner ## headings first-hand). Agrees with ASK-7, ASK-8, ASK-10 and the backup. Changes: (1) one commit BEFORE init renames '## Tests - the push gate' to '## Gate', prunes CLAUDE.md, rewrites claudeMdShape and retires handoffShape/decisionsIndex, so the node gate never goes red and init does not append a second Gate stub; (2) rehearse steps 4-10 on a clone of the backup bundle first, measuring lint time over 304 records; (3) after import, a scripted line-conservation check (every non-blank line of the frozen log appears once across record bodies), sabotaged on a fixture before it is believed; (4) ASK-9: a HANDOFF row naming an issue folder IS that folder's task, fresh ids only for rows with no folder, priority from HANDOFF order, the rest LATER; (5) gate: scope 'all' with a cheap command (tsc + lint), since [gate] has one command and readers/scope guard are pytest-only, so a 'code' scope would stay green after a record hand edit; (6) freeze: owner confirms no other audio-workspace session for the cutover; import, decisionsIndex retirement and a FROZEN line atop docs/decisions.md land in one commit; (7) import everything but mark nothing SUPERSEDED at import (CE-80), skip the 304-status review, keep the frozen log routed in place so code citations of docs/decisions.md D-n stay valid; bundle verify the backup, take it inside the quiet window, include untracked .env files.
- 2026-10-19c (claude-code/claude-opus-5-5): Plan change, DEC-61 (owner, 2026-10-19c): push nothing to audio-workspace during the demo hold, neither branch, tag nor cutover commit; the pre-init commit, the import commit and the backup bundle stay local until the owner lifts the hold. Pruning CLAUDE.md and HANDOFF.md must keep the demo-hold notice those files now carry. The push and CI step of the cutover, and the 'vitest + smoke before push' gate (DEC-51), wait for the lift. Start no earlier than Wednesday 2026-10-21 and only after CE-98 is fixed (an audio-workspace session's advice, relayed by the owner). The relayed note's 'pushing a tag (ASK-13)' is stale: DEC-59 already dropped the tag. ASK-7..ASK-14 are all answered; CE-98 is the one blocker.
- 2026-10-19e (claude-code/claude-opus-5-5): 2026-10-17c died in a restart mid-round-1 (abandoned by 2026-10-19e). CE-98 is now committed (a8879f9), so the CE-43 block on it is lifted. 17c's five prep drafts (board, census, charter, config, normalise) are in .scratch/ce-17c/, with a verified copy (218 files) in the audio-workspace backup dir under ce-17c-prep/; they hold private content, so they stay out of this repo. Owner questions they raise, for one digest at cutover: (1) the 41 imported asks are overdue on creation: raise them, `ask later` the lot, or group them into about 12; (2) does docs/issues/README.md keep its live table or point at `task list`; (3) AGENTS.md's 'commit only from the orchestrator after owner sign-off' clashes with engine commits; (4) the charter and 11 candidate stories need one batched confirmation, and G-7 needs a measure; (5) one product-scope call where requirements §7.1 and §7.3 item 5 disagree; (6) whether actors like 'owner asked' and 'owner + agent' stay as they are. Round 2 must first re-run prep/normalise run_e2e.sh and check_conservation.py against the COMMITTED importer (17c's 0-lost result was against an uncommitted tree), and re-run build_board.py and the G-D3/docLinks probes at audio-workspace's HEAD at cutover; import from a tracked copy of the normalised log. 2026-10-19d owns the prep now.

## Traps

- **Never push audio-workspace while its demo hold stands (DEC-61):** no branch, no tag, no cutover commit; everything stays local until the owner lifts the hold.
- **Keep the demo-hold notice** in audio-workspace's CLAUDE.md and HANDOFF.md when pruning them.
- Not before Wednesday 2026-10-21, and not before CE-98 is fixed.
