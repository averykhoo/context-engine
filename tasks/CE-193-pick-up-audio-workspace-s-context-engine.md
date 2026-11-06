---
type: Task
id: CE-193
title: Pick up audio-workspace's context-engine feedback (entries 1-10 at 2026-11-06, and any since)
brief: Take entries into records here; never edit the entries in audio-workspace
pri: LATER
state: open
deps: []
goals: [G-6]
source: session 2026-11-06e
created: 2026-11-06
moved: 2026-11-06e
updated: 2026-11-06e
---

Pick up audio-workspace's context-engine feedback: `C:/Users/user/PycharmProjects/audio-workspace/docs/context-engine-feedback.md` (one entry per item, newest last). From 2026-11-06e, audio-workspace's `CLAUDE.md` tells its sessions to add entries there, so the file keeps growing. Read it whole, take every entry since the last pick-up into records here (a task, a comment on an existing one, or owner words through intake), and record in this item's Log which entry numbers were taken. Do not edit the entries there: the file's header says fixes are marked here.

State at 2026-11-06d (audit; 10 entries):
1. Setup registers the MCP server: CE-177 (LATER), ASK-33.
2. A green gate is enough to ship, as a framework principle: the owner said yes (US-20, 2026-11-06e); the FRAMEWORK change is its own task.
3. `ask new` accepts empty Options/Recommendation: probably fixed by CE-44 (`guards.py::ASK_PLACEHOLDER_RE`, G-W4); verify, then audio-workspace may only need a re-pin.
4. No way to record a partial owner answer without closing the ask: new.
5. Owner words and the ruling share one field; one `ask answer` over several ids: adjacent to CE-111, CE-113; the multi-id part is new.
6. A clean close can leave the banner stale, so the next gate goes red (G-W1): new; check against the current `session close` first.
7. Close eagerly vs a back-and-forth: the owner's view is US-21 (2026-11-06e): close eagerly fits ephemeral conversations, long-lived sessions fit design, and cheap enough sessions may remove the need.
8. The actor string `claude-code/<model-id>` writes model ids into committed records, against the harness rule on pushed files; conflicts with FRAMEWORK §6.5 and is adjacent to CE-122: needs an owner call.
9. fan-out.md: make "check the file on return, persist on receipt" required: small wording.
10. Every `ask answer` makes its own commit: new; pairs with 5.

The adhoc trial's feedback was taken in already (CE-7; frozen copy `docs/evidence/adhoc-feedback-2026-10-21.md`).

## Traps

- Entries 3 to 10 are agent-raised; only entry 2 (and the owner's view on 7) are owner words. Owner words go through intake verbatim; agent entries become tasks.

## Read first

- C:/Users/user/PycharmProjects/audio-workspace/docs/context-engine-feedback.md

## Log

- 2026-11-06e (claude-code/claude-opus-5-5): audio-workspace ba31e29d (2026-11-06e, local, unpushed; its gate passed): its CLAUDE.md now tells sessions to append context-engine feedback to docs/context-engine-feedback.md. US-21's criterion is AC-185 (planned).
