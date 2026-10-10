# adhoc baseline: session start and clean close cost, 2026-10-11 (CE-4)

The baseline CE-7 (adhoc trial cutover) is scored against. FRAMEWORK §8.0.3 pre-registers the
rubric's shape: *context spent on session start and clean close against the same rituals done
by hand, plus collisions or lost blocks across two concurrent sessions.* This doc fixes the
details **before** measuring, then records the numbers.

Measured read-only in `PycharmProjects/adhoc-microphone-array` at commit `3e3f442`
(2026-10-10 23:25, "HANDOFF write-back for the overnight run ..."). Tree clean at the time:
no uncommitted or untracked files, no index lock, nothing modified in the prior 15 minutes;
`main` 60 commits ahead of `origin/main` (unpushed, not ours to touch).

## 1. Rubric (written before measuring)

### What is measured

**S, session start.** The bytes a cold session must read before its first task action, if it
follows adhoc's own rituals to the letter. Split:
- **S-auto:** loaded without a tool call: the repo `CLAUDE.md`, any subtree `CLAUDE.md` /
  `AGENTS.md`, and the owner's global `~/.claude/CLAUDE.md`. The global file is the same in
  both arms of the trial, so it is recorded but **excluded from the comparison**.
- **S-must:** files the start ritual says to read every session (the global contract says
  "read `HANDOFF.md` in full"), plus anything those files say to read unconditionally.
- **S-cond:** files read only on a condition (the top item's notes, "if needed" reads). Listed
  with sizes, not summed into S.

**W, clean close.** What the close ritual makes a session read and write:
- **W-read:** bytes of every file the close ritual edits or must consult (to edit a file, a
  session reads it).
- **W-write:** bytes actually changed at a close, taken from git history: the median and the
  range over adhoc's recent close / write-back commits (`git log --numstat`, bytes from
  `git diff`), naming the commits used.
- **W-steps:** the number of distinct ritual steps and files touched at a close.

**C, concurrency.** Collisions or lost blocks between concurrent sessions. The tree can't
measure this directly. The baseline is the number of such incidents recorded in adhoc's own
history (HANDOFF, decisions, commit messages), each cited.

### How

- Bytes are `wc -c` of the file as committed at the measured SHA. Lines are reported beside
  them.
- **Tokens: not measured.** No tokenizer or API key was available on 2026-10-11 (`anthropic`
  and `tiktoken` not installed, `ANTHROPIC_API_KEY` unset). Bytes are the proxy for context;
  every number below is bytes unless it says otherwise. CE-7 must use the same unit, so any
  token count added later is added to both arms.
  *Added 2026-10-11b, after the measurements: proxy token counts from two tokenizers (tiktoken
  `o200k_base` and Gemma's, via Vertex AI; neither is Claude's) are in §3. The thresholds are still judged on bytes; tokens are reported
  beside them.*
- A file is counted once per ritual even if two rules point at it.

### What counts as better (for CE-7)

The engine arm is **better** when all of these hold:
1. **S-must + S-auto (repo part)** is at least **25% lower** than the baseline. A change
   within ±10% is "no change".
2. **W-read + W-write** at a close is no higher than the baseline.
3. **C does not rise:** no collision or lost block in the trial that the baseline rituals
   would have prevented.
4. **Nothing needed goes missing:** the trial sessions' `read:` receipts show they did not
   have to fall back to reading the old `HANDOFF.md` / `decisions.md` to do their work. A
   session that had to counts against the engine arm, with its bytes added to S.

The thresholds are this session's proposal, recorded before the numbers. They may be changed
only by a decision recorded before CE-7 is scored.

## 2. Measurements (2026-10-11, adhoc `3e3f442`, bytes)

Gathered by a read-only subagent. The file sizes, the HANDOFF rule, three commits' diff bytes
and the concurrency search were re-run first-hand, and all matched.

### S, session start

| part | path | bytes | lines | why it is read |
|---|---|---|---|---|
| S-auto | `CLAUDE.md` | 16,553 | 290 | auto-loaded; the only `CLAUDE.md`/`AGENTS.md` adhoc tracks |
| S-auto (excluded) | `~/.claude/CLAUDE.md` | 24,764 | 411 | global contract, the same in both arms |
| S-must | `HANDOFF.md` | 31,987 | 428 | adhoc `CLAUDE.md` opening: "read it in full at session start, right after this file" |

**S = S-auto (repo) + S-must = 48,540 bytes** (excluding the global file; 73,304 with it).
Growth since 2026-10-08, the sizes quoted in CE-4: `CLAUDE.md` 16,196 → 16,553 (+2%),
`HANDOFF.md` 28,407 → 31,987 (+13%) in three days.

S-cond, not summed into S:

| path | bytes | condition |
|---|---|---|
| `docs/decisions.md` | 64,175 | "read it before proposing a method" (`CLAUDE.md`) |
| `docs/methods.md` | 9,349 | before touching `adhoc_loc/` or `adhoc_sep/` (`CLAUDE.md`) |
| `docs/project-brief.txt` | 5,667 | named in `CLAUDE.md`'s opening, with no "every session" wording |
| `docs/results/2026-10-06-talker-count.md` | 10,677 | the current top item's (1h) reading list, HANDOFF § "next session: start here" |
| `docs/results/2026-10-07-sep-estimated.md` | 7,905 | the same |
| `docs/results/2026-10-10-fresh-meeting-scoring.md` | 11,397 | the same |

For reference, a cold session that picks up today's top item reads S plus its reading list
(29,979): **78,519 bytes before its first task action.** One that also proposes a method adds
`decisions.md`: 142,694.

Judgement calls: the top item's reading list is S-cond, because it would change if a different
item were NOW. `project-brief.txt` is S-cond, because nothing says to read it every session.

### W, clean close

W-read, the files the close ritual edits or consults:

| path | bytes | rule |
|---|---|---|
| `HANDOFF.md` | 31,987 | its header: session-log entry, refresh the banner, edit rows in place, sweep closed ids |
| `CLAUDE.md` | 16,553 | promote any durable rule into `CLAUDE.md` |
| `docs/decisions.md` | 64,175 | a new D-n entry, append-only, newest first (`CLAUDE.md` § "Where findings go"), when there is a decision |
| `docs/archive/README.md` | 1,616 | a redirect row when the session log is rotated (over 10 entries) |

**W-read = 48,540 bytes every close** (`HANDOFF.md` + `CLAUDE.md`); **114,715** when a
decision is recorded; plus 1,616 at a rotation.

W-write, the bytes changed by the 10 most recent write-back / close commits. They were picked
by subject from the last 60 commits. The eleventh match, `17909f0` (2026-10-03), was dropped.
Bytes are the `+` and `-` lines of `git show`, prefix character included.

| sha | date | subject (shortened) | files | +bytes | -bytes | total |
|---|---|---|---|---|---|---|
| `3e3f442` | 2026-10-10 | HANDOFF write-back for the overnight run | 8 | 19,289 | 14,191 | 33,480 |
| `31b1c9f` | 2026-10-09 | HANDOFF: where the paused overnight run stopped | 1 | 1,593 | 0 | 1,593 |
| `d130711` | 2026-10-07 | Docs housekeeping: method notes out of CLAUDE.md, session-log rotation | 6 | 20,687 | 18,129 | 38,816 |
| `9f02e90` | 2026-10-07 | Handoff: estimated rung in, start-here refreshed | 1 | 931 | 433 | 1,364 |
| `b710698` | 2026-10-06 | Handoff: downstream sweep owed | 1 | 2,128 | 553 | 2,681 |
| `0bbd8e2` | 2026-10-05 | Activity sensitivity results, handoff write-back | 3 | 12,283 | 2,232 | 14,515 |
| `eab1578` | 2026-10-04 | Refresh README and write back HANDOFF | 2 | 3,412 | 611 | 4,023 |
| `c030ce1` | 2026-10-04 | Write back HANDOFF.md before a context clear | 1 | 4,814 | 2,358 | 7,172 |
| `37e46f5` | 2026-10-04 | HANDOFF: point peass-nway | 1 | 652 | 444 | 1,096 |
| `4d2eab5` | 2026-10-04 | HANDOFF: track the python-peass per-source branch | 1 | 1,016 | 0 | 1,016 |

**W-write median 3,352 bytes, range 1,016 to 38,816.** The two largest commits also carry
results docs or a housekeeping rotation, so the per-commit numbers overstate the ritual's own
write. CE-7 must pick its commits by the same subject rule.

W-steps, adhoc's close ritual as written (HANDOFF header and `CLAUDE.md` § "Where findings go"):
1. a session-log entry; 2. refresh the banner; 3. edit open-item rows in place; 4. sweep closed
ids; 5. promote durable rules into `CLAUDE.md`; 6. list anything skipped under "still owed";
7. *(conditional)* rotate the session log to `docs/archive/` with a redirect row; 8.
*(conditional)* a D-n entry in `docs/decisions.md`. **6 unconditional + 2 conditional steps**,
all hand edits. Core files: `HANDOFF.md`, `CLAUDE.md`, `docs/decisions.md`.

### C, concurrency

**None recorded.** `concurrent|collision|another session|clobber|overwrote` gets zero hits in
`HANDOFF.md`, `docs/decisions.md` and the full commit-message history. The subagent's wider
search also tried `lost` and `race`; every `lost` hit was the separation metric "lost
talkers", not a session incident. Baseline C = 0. This is weak evidence: adhoc may simply
have had few concurrent sessions, so the trial has to say how many it ran.

### What the baseline does not have

adhoc has **no `read:` receipt**, so its sessions do not record what they actually read; the
numbers above are what the rituals *require*, not what sessions did. CE-7's engine arm will
have receipts. The comparison has to set required against required, and report receipts on
the side.

## 3. Proxy token counts (2026-10-11b)

**These are proxies, not Claude's count.** Claude has no local tokenizer release, and an exact
count needs the token-counting API and a key, which this machine does not have. Two proxies
give a spread:
- **tiktoken** 0.14.0, encoding `o200k_base` (OpenAI's);
- **gemma**: Vertex AI's local tokenizer for `gemini-1.5-pro` (`google-cloud-aiplatform`
  2.4.0, `vertexai.preview.tokenization`), which is Gemma's sentencepiece model, fetched once
  without a key. Newer Gemini model names are not supported locally.

Use them to compare the two arms, not as absolute context figures. Regenerate with
`tools/count_context.py <adhoc> 3e3f442 <paths>`; both packages are installed in the engine
env, and neither is an engine dependency. Bytes matched §2 exactly.

| path | bytes | tiktoken | gemma | bytes/token (tiktoken) |
|---|---|---|---|---|
| `CLAUDE.md` | 16,553 | 4,356 | 4,695 | 3.8 |
| `HANDOFF.md` | 31,987 | 9,739 | 11,050 | 3.3 |
| `docs/decisions.md` | 64,175 | 17,969 | 19,582 | 3.6 |
| `docs/methods.md` | 9,349 | 2,584 | 2,860 | 3.6 |
| `docs/project-brief.txt` | 5,667 | 1,136 | 1,171 | 5.0 |
| `docs/archive/README.md` | 1,616 | 488 | 567 | 3.3 |
| `docs/results/2026-10-06-talker-count.md` | 10,677 | 3,471 | 3,774 | 3.1 |
| `docs/results/2026-10-07-sep-estimated.md` | 7,905 | 2,657 | 2,942 | 3.0 |
| `docs/results/2026-10-10-fresh-meeting-scoring.md` | 11,397 | 4,002 | 4,433 | 2.8 |
| `~/.claude/CLAUDE.md` (global, excluded; read from disk, not a commit) | 24,764 | 6,550 | 6,854 | 3.8 |

The §2 totals (tiktoken / gemma):
- **S = 14,095 / 15,745** (20,645 / 22,599 with the global file); with today's top item's
  reading list 24,225 / 26,894; with `decisions.md` as well 42,194 / 46,476.
- **W-read = 14,095 / 15,745 every close**; 32,064 / 35,327 with a decision; plus 488 / 567
  at a rotation.

gemma counts 3% to 16% more tokens than tiktoken file by file (11.7% more on S). Bytes per
token runs from 2.8 to 5.0 across these files (tables and numbers tokenize densely), so bytes
and tokens can rank two versions of a doc differently. CE-7 reports all three.
