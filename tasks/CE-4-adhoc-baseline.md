---
type: Task
id: CE-4
title: "Measure adhoc's session start and close cost today, before any cutover"
brief: "Read-only in adhoc, which may have a live session. Write the rubric down before measuring"
pri: NOW
state: closed
deps: []
source: session 2026-10-08a
created: 2026-10-08
moved: 2026-10-11a
updated: 2026-10-11b
closed: 2026-10-11a
status: deprecated
---

The trial's comparison means nothing without a baseline (FRAMEWORK §8.0.3). Measure what a cold
session in `PycharmProjects/adhoc-microphone-array` reads at session start and writes at a
clean close today: the files and their bytes (`CLAUDE.md` 16,196 B and `HANDOFF.md` 28,407 B on
2026-10-08), plus whatever its rituals send it to. Write the rubric first (what is measured, how,
what counts as better), then the dated numbers, into a tracked evidence doc here:
`docs/evidence/adhoc-baseline-<date>.md`.

## Traps

- **Read-only.** Do not edit adhoc. Run `git status` there first: it was being worked on
  2026-10-08 (commits at 10:33 and 12:20).
- Bytes are a proxy for context. If a token count is possible, record both and say which.

## Read first

- `docs/framework/FRAMEWORK.md` §8.0.3, §6.1, §6.3
- `docs/decisions/DEC-6-adhoc-first.md`
- adhoc `CLAUDE.md`, and `HANDOFF.md` § "next session: start here"

## Log

- 2026-10-11a (claude-code/claude-opus-5-5): closed: Baseline in docs/evidence/adhoc-baseline-2026-10-11.md (adhoc 3e3f442): rubric fixed first, then S = 48,540 B (CLAUDE.md + HANDOFF.md), W-read 48,540 B per close, W-write median 3,352 B over 10 commits, C = 0. Bytes only: no tokenizer or API key available.
- 2026-10-11b (claude-code/claude-opus-5-5): Proxy token counts added (owner asked for a tokenizer): tiktoken o200k_base, installed into the engine env; tools/count_context.py regenerates them. S = 14,095 proxy tokens, W-read 14,095. Not Claude's tokenizer; exact counts need the API and a key.
- 2026-10-11b (claude-code/claude-opus-5-5): Second proxy added at the owner's suggestion: Gemma's tokenizer via vertexai.preview.tokenization (gemini-1.5-pro, local, no key). S = 15,745 gemma tokens (+11.7% on tiktoken). tools/count_context.py prints both.
