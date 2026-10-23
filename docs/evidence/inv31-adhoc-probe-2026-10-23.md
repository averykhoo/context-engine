# INV-31 live probes in adhoc: startup, resume, /clear, compaction, 2026-10-23 (CE-79)

FROZEN. Session 2026-10-23f, measured 2026-10-23 and verified 2026-10-24 by an independent read-only agent; provenance, as written. Probe scripts and outputs were in `.scratch/ce-79-final/` (gitignored, deleted), so this file is the record.

## What INV-31 asks

`src/context_engine/REGISTER.md` "## INV-31": whether hook output reaches context on resume and after `/clear`
(with the `@`-import-on-missing-target behaviour and the shell a hook runs under on Windows), "not probed on a live
session". The control there is that the owner runs the probes. CE-79 "What to check": did orient appear on startup,
resume, `/clear` and compaction. `docs/evidence/plugin-design-2026-10-14.md` lists the live probes of resume, `/clear`
and compaction as unprobed. `docs/evidence/adhoc-trial-score-2026-10-21.md` ("Forgotten" item 1) says only startup was
evidenced. This file supersedes that for resume and `/clear`.

## Method

- **Source.** Claude Code transcripts of adhoc (`~/.claude/projects/C--Users-user-PycharmProjects-adhoc-microphone-array/*.jsonl`):
  295 files including subagent transcripts, 21 top-level since the cutover. Read-only.
- **The record.** A line with `attachment.type: "hook_success"`, `attachment.hookName: "SessionStart:<startup|resume|clear|compact>"`,
  `exitCode`, `stderr`, `durationMs`, and `content` (the stdout, opening `# orient (no session)`). The command is adhoc's
  `.context-engine/env/python.exe -m context_engine --root <adhoc> orient`.
- **The limit.** A `hook_success` record proves the hook ran and its stdout was captured. It does not prove the text reached
  the model. That was inferred from behaviour: did the agent use an id or phrase that appears only in the orient text
  (not in the user prompt, session_context, git log or an earlier tool result) before it read it anywhere else. No raw API
  request log was available, so this stays an inference.
- **Probe files** (names only): `hooks_census.py`, `after_hook.py`, `first_reply.py`, `uses_orient.py`, `id_leak.py`,
  `show_hook.py`, `ctx_peak.py`; the verifier's `census.py`, `compact_search.py`, `clear_match.py`, `first_use.py`, `dump.py`.

## Census, 2026-10-23 (first hook record 2026-10-14T08:26:45Z, the cutover)

21 `hook_success` records; all exit 0, empty stderr, all open `# orient`. No `hook_non_blocking_error`, `hook_blocking_error`,
`hook_failed` or other `hook_*` type in any file. Startup 7, resume 1, `/clear` 13 records (12 distinct events: the
2026-10-23T05:25:23.645Z event is mirrored into `64c998d9` L19 and `8d66817d` L2, byte-identical), compact 0. The 13 `/clear`
commands before the cutover (2026-10-02 to 10-12) have no hook record, as expected.

## Per-event result

| event | probe verdict | verifier | key evidence | caveats |
|---|---|---|---|---|
| startup | SEEN (7 events) | CONFIRMED | `64c998d9` L1, 2026-10-23T05:24:27.454Z, exit 0, 590 ms. First reply L17 (no tool call before) says orient "lists **Other open sessions: none**" and offers AD-41, ids found only in L1 within L1-L18. First startup `97ab78db`, 2026-10-14T08:26:45Z. | Post-re-pin (adhoc 9f0e8ca): one startup, the one above. |
| resume | SEEN (n = 1) | CONFIRMED, caveat holds | `64c998d9` L145, 2026-10-23T10:17:02.437Z, exit 0, 4538 ms. Output regenerated, not replayed: banner `(2026-10-23e)` against `(2026-10-23c)` at startup; "Other open sessions" lists 2026-10-23f where startup said none. First text L154: "the open session orient lists is this one." | One event only. A restart-recovery resume (container-restart reminder L146), not a typed `claude --resume` or `/resume`. Session key 2026-10-23f was already in history (L136), so only the phrase, the banner stamp and the record together carry it. |
| /clear | SEEN (12 distinct) | CONFIRMED at event level; one example REFUTED | Every post-cutover `/clear` is followed within 0.3 to 0.9 s by a `SessionStart:clear` hook_success (verifier: 13 of 13 typed commands hooked, none missed). Orient-only use: `15f31d7b` L2 (2026-10-15T14:59:42Z) DEC-70, DEC-71 first used in L38; `5dbd5823` L2 (2026-10-17T10:55:53Z) DEC-79; `8d66817d` L2 (2026-10-23T05:25:23Z) AD-41 from `## Top item`. | See below: `fd7ccd98` refuted; the `8d66817d` wording overstated; seven clears have no distinguishing id; `50c6a0c0` is a 5-line stub with no assistant turn. |
| compaction | NO_EVIDENCE | CONFIRMED | Across all 295 files: zero `compact_boundary`, `isCompactSummary`, `compactMetadata`, `SessionStart:compact` or continuation summaries; no `/compact` typed (`/clear` x26, `workflow-authoring` x10 are the only slash commands). | Never occurred, not failed. |

## Caveats and corrections

- **`fd7ccd98` is refuted as an orient-only example** (verifier, 2026-10-24). ASK-9 is in the orient text, but also in
  session_context (L20 git log: "engine: new DEC-69, ask.answer ASK-9") and the owner's prompt said "continuing the session
  on ask ...". The agent's first act used DEC-69, which is not in the orient text and came from the git log. The `/clear`
  verdict rests on the other three examples, which the verifier confirmed independently. (DEC-73 in `15f31d7b` is weaker
  for the same reason: it is also in the git log.)
- **`8d66817d` wording.** The agent did not recite the AD-41 banner; it ran `task show AD-41` at L55 with no prior `task list`,
  and AD-41 occurs before that only in the hook record. The substance holds.
- **Resume n = 1.** One restart-recovery resume is not the typed `/resume` path. Treat resume as evidenced, not as exhaustively
  probed.
- **Compaction has not occurred.** Peak top-level context since the cutover is 339K tokens (`32b73c71`, 2026-10-15T13:58Z); a
  post-cutover subagent reached 515,915 tokens (`64c998d9` subagent `agent-afddaa4a7fcf0176c`, L1183, 2026-10-23T16:08Z) and a
  pre-cutover transcript 574K (2026-10-04), none compacted. Automatic compaction is not to be expected at these sizes. To close
  the probe the owner runs `/compact` once in an adhoc session and looks for a `SessionStart:compact` hook_success line.
- **Not examined.** The `@`-import-on-missing-target behaviour and which shell runs the hook (the other parts of INV-31), and
  whether hook content is injected verbatim into model context (inferred, above).
- **Open call.** INV-31 says the owner runs the probes, so whether to retire its resume and `/clear` parts is the owner's.

## Hook failures

None: 21 of 21 `hook_success`, exit 0, empty stderr (measured 2026-10-23, reproduced 2026-10-24). One extra observation from the
verifier: the `a8f177b6` clear (2026-10-22T07:14Z) opened with `## Contract: fix ...` (contract drift), and was still delivered.

## adhoc push readiness, 2026-10-23

Measured in `adhoc-microphone-array` (origin `github.com/averykhoo/adhoc-microphone-array`), session 2026-10-23f:
- Branch `main`, fetched: behind 0, ahead of `origin/main` by 10 commits (tip `473d7da`, the AD-41 and AD-1 voice.py commit).
- Gate: `extract_text --check` rc 0 ("all documents extracted cleanly"); lint rc 0 ("lint: clean"); `pytest -q` rc 0,
  "1003 passed, 1 xfailed, 10 warnings in 2376.59s (0:39:36)". The first chained run was killed at the 30 minute background limit
  at 64% and rerun separately.
- No CI config (no `.github/workflows`, no `.gitlab-ci.yml`): a push triggers nothing, so there is no watcher target.
- **Caveat: the gate ran with uncommitted work in the tree.** The live adhoc session's modified and untracked files (for example
  `adhoc_sep/drift.py`, `adhoc_sep/fmnmf.py`, `tests/test_drift.py`, `tests/test_fmnmf.py`, `tests/test_sep_fmnmf.py`) were
  present, so the green is for tree-with-WIP, not for HEAD alone. A clean-HEAD run was not done (it would need a stash or worktree,
  forbidden in a shared tree). A push sends committed HEAD only; the live session may also commit more first, so re-check
  `git log origin/main..HEAD`.
- Verdict then: ready to push; not pushed by this session.
