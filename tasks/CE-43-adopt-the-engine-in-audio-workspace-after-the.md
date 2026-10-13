---
type: Task
id: CE-43
title: Adopt the engine in audio-workspace after the adhoc trial
brief: The owner's preferred testing ground (DEC-6 amendment); goes before intervals, zanzibar
pri: LATER
state: open
deps: [CE-7]
source: session 2026-10-13b
created: 2026-10-13
moved: 2026-10-13b
updated: 2026-10-13b
---

Owner, 2026-10-13b, on DEC-6: "Adhoc is a good repo yes, we'll do a quick trial there, but I'm hoping to get this into the audio workspace repo soon, since that's a better testing ground". So CE-7 stays a quick trial, and audio-workspace is the next adoption, ahead of the CE-11 order (intervals, then zanzibar and audio-workspace). audio-workspace is a GitLab repo, uses pixi for node only and per-subproject uv venvs (server/.venv); the engine still runs from its own env (DEC-1). Survey the repo (HANDOFF, decision log, board shape, concurrent sessions) before planning the import.
