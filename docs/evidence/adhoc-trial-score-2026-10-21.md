FROZEN. The CE-7 trial's score against the CE-4 baseline, measured 2026-10-21 for CE-79 at adhoc `4c894cb` and engine `1f3f7d7`; provenance, as written.

# adhoc trial under context-engine: sessions and score, 2026-10-21 (CE-7, CE-79)

The baseline is `docs/evidence/adhoc-baseline-2026-10-11.md` (adhoc `3e3f442`). Its rubric is used
as written there. Every number below was measured on 2026-10-21. Everything was read-only in adhoc.
The probe scripts and logs are in `.scratch/ce7-score/`, which is gitignored, so this file is the
record.

Baseline numbers, re-read from that file on 2026-10-21:
- **S** = 48,540 B (CLAUDE.md 16,553 + HANDOFF.md 31,987). That is 14,095 tiktoken and 15,745 gemma
  proxy tokens.
- **W-read** = 48,540 B every close (114,715 B when a decision is recorded).
- **W-write**: median 3,352 B per close commit, range 1,016 to 38,816 B, over 10 commits.
- **W-steps**: 6 unconditional steps plus 2 conditional ones, all hand edits.
- **C** = 0. In the baseline, C counts *concurrency* incidents (collisions or lost blocks between
  sessions), not forgotten items. Forgotten items are reported separately below. The baseline has
  no count of them, so they cannot be compared against it.
- **What counts as better:**
  1. S at least 25% lower, judged on bytes (within ±10% is no change).
  2. W-read + W-write no higher.
  3. C does not rise.
  4. No fallback to the old `HANDOFF.md` or `docs/decisions.md`.

## 1. Sessions since the cutover

- **The cutover.** adhoc `7100077` (2026-10-14 14:32): init at engine pin `38ed38e`, on branch
  context-engine-trial. That branch was fast-forwarded into main at `eef0ecc` (DEC-42).
- **Sources.** adhoc `docs/ledger/ops.jsonl` (271 op lines at `4c894cb`), `docs/ledger/session-log.md`
  and `git log 444efcc..4c894cb`.
- **Count.** 12 session keys. Each has one `session.start` op line. Nine have a `session.close` op
  line. The ledger has no op for an abandon.

| key | opened through `session start` | how it ended | end commit | actor (as signed) | note |
|---|---|---|---|---|---|
| 2026-10-14a | yes | `session close` | `fc7bdff` | claude-code/claude-opus-5-5 | the cutover itself, in the worktree; run by the engine-repo agent |
| 2026-10-14b | yes | `session close` | `8d244e5` | claude-code/claude-opus-5-5 | move onto main (DEC-42); setup only |
| 2026-10-14c | yes | `session close` | `5cb11b7` | claude-code/claude-haiku-5-5 | first real session; a whole top-level session on the cheapest tier (AAR 35) |
| 2026-10-14d | yes | **abandoned by hand**, in 2026-10-15a | `2612284` | claude-code/opus-5.5 | died: laptop restart mid-workflow (AAR 21) |
| 2026-10-15a | yes | `session close` | `71237e4` | claude-code/opus-5.5 | finished 2026-10-14d's round |
| 2026-10-15b | yes | `session close` | `92c0cc7` | claude-code/opus | |
| 2026-10-16a | yes | **abandoned by hand**, in 2026-10-16b | `4c8e4f3` | claude-code/fable-5.1 | planning session; never closed (AAR 3) |
| 2026-10-16b | yes | `session close` | `03e89b0` | claude-code/opus-5.5 | the coordinated multi-agent session the AAR covers |
| 2026-10-17a | yes | **abandoned by hand**, after 2026-10-19a's close | `5c61449` | claude-code/opus | died: out of commit memory (AAR 19, 25) |
| 2026-10-19a | yes | `session close` | `bb0892b` | claude-code/opus | recovery |
| 2026-10-21a | yes | `session close` | `1421357` | claude-code/opus-5.5 | AAR gap audit |
| 2026-10-21b | yes | `session close` | `dce9737` | claude-code/opus-5.5 | CLAUDE.md cleanup; dropped the AAR file from adhoc |

- **Totals.** 12 opened, 9 closed through the engine, 3 abandoned by ledger hand edits, none still
  open. The 3 dead sessions were 25% of all sessions.
- **The sessions scored.** Seven are *trial sessions*: 2026-10-14c, 15a, 15b, 16b, 19a, 21a and 21b.
  2026-10-14a and 14b were set-up sessions. They are shown, but left out of the medians. 14a was
  measured against the pre-split HANDOFF, which was 43,375 B.
- **No overlap.** No two live sessions overlapped. In the op log, every session's span (first op to
  last op) is disjoint from every other's.
- **A push outside any session.** One push was made with no session open: `444efcc..5c61449` on
  2026-10-20 (AAR 26). No record names it.

## 2. Score against the CE-4 rubric

### S, session start (measured at each session's start commit)

- **What S is made of.** The same rule as the baseline: what the rituals require, not what the
  receipts show.
  - **S-auto:** `CLAUDE.md`, its @-import `docs/framework/contract.md`, and the orient output the
    SessionStart hook prints.
  - **S-must:** `HANDOFF.md`, because adhoc's `CLAUDE.md` line 4 still says "read it in full at
    session start". Also the top NOW item, which the contract says to read with `task show`. Its
    record file is used as the proxy for that print.
  - The global `~/.claude/CLAUDE.md` is excluded, as in the baseline.
- **The start commit.** For each session, the newest adhoc commit at or before its `session.start`
  op line.
- **Orient.** Orient was re-run by adhoc's own pinned engine (38ed38e, `.context-engine/env`), with
  `--root` set to a `git archive` of that commit. Its real output could differ slightly: for example,
  2026-10-19a's real orient also listed 2026-10-17a's uncommitted stub. Orient is capped at
  6,000 B (adhoc `context.toml`).
- **Tokens** are the CE-4 proxies (tiktoken o200k_base and gemma), counted with the same code as
  `tools/count_context.py`.

| session | start commit | CLAUDE.md | contract | orient | HANDOFF | top item | **S bytes** | tiktoken | gemma | vs 48,540 B |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-14a (setup) | `7100077` | 17,768 | 6,560 | 5,573 | 43,375 | none | 73,276 | 21,674 | 24,330 | +51.0% |
| 2026-10-14b (setup) | `eef0ecc` | 18,549 | 6,560 | 3,855 | 4,698 | 2,309 (AD-5) | 35,971 | 9,838 | 10,812 | -25.9% |
| 2026-10-14c | `8d244e5` | 18,549 | 6,560 | 3,834 | 4,677 | 2,309 | 35,929 | 9,830 | 10,802 | -26.0% |
| 2026-10-14d (died) | `5cb11b7` | 18,549 | 6,560 | 4,156 | 4,864 | 2,309 | 36,438 | 10,035 | 11,029 | -24.9% |
| 2026-10-15a | `053e4d4` | 18,549 | 6,560 | 4,156 | 4,864 | 2,309 | 36,438 | 10,035 | 11,029 | -24.9% |
| 2026-10-15b | `6badce7` | 18,549 | 6,560 | 3,720 | 5,573 | 1,494 (AD-3) | 35,896 | 9,884 | 10,915 | -26.0% |
| 2026-10-16a (abandoned) | `4e42542` | 18,549 | 6,560 | 4,132 | 6,234 | 1,494 | 36,969 | 10,211 | 11,316 | -23.8% |
| 2026-10-16b | `3323199` | 18,549 | 6,560 | 4,200 | 6,234 | 1,494 | 37,037 | 10,248 | 11,368 | -23.7% |
| 2026-10-17a (died) | `03e89b0` | 18,855 | 6,560 | 5,515 | 7,533 | 1,494 | 39,957 | 11,120 | 12,325 | -17.7% |
| 2026-10-19a | `03e89b0` | 18,855 | 6,560 | 5,515 | 7,533 | 1,494 | 39,957 | 11,120 | 12,325 | -17.7% |
| 2026-10-21a | `5c61449` | 18,883 | 6,560 | 5,193 | 7,589 | 1,494 | 39,719 | 11,183 | 12,450 | -18.2% |
| 2026-10-21b | `7107254` | 18,883 | 6,560 | 5,327 | 7,723 | 1,494 | 39,987 | 11,271 | 12,582 | -17.6% |

- **The median over the trial sessions** (n 7) is S = 37,037 B, 10,248 tiktoken and 11,368 gemma:
  **-23.7% on bytes**, and -27.3% and -27.8% on the two token proxies.
- **Verdict on line 1: narrowly not met, and getting worse.** The threshold is judged on bytes. The
  first trial sessions were at -26%. The newest are at -17.6%, which is close to the ±10%
  no-change band.
- **What grew.** S grew because HANDOFF.md grew from 4,677 to 7,723 B, and orient from 3,834 to
  5,327 B. Both grew mostly in the banner (1,963 B at `322fe9f`, 4,208 B at `51fb1df`).
- **Fixed costs.** The contract import is a new cost of 6,560 B that the baseline did not have.
  CLAUDE.md sits close to its G-D1 cap (18,883 of 19,000 B on 2026-10-21, before 21b cut it to
  15,355 B).
- **The banner is read twice.** Orient prints HANDOFF's banner, and the `CLAUDE.md` rule then has the
  session read HANDOFF in full. If that rule went, and the session read only orient plus HANDOFF's
  rest, S at 2026-10-21b would be about 35.8 KB (-26%). This is arithmetic on the numbers above,
  not a measurement.

### W, clean close (measured at the parent of each close's first commit)

- **W-read.** The engine's clean close (adhoc `docs/runbooks/procedures.md` § Clean close) makes a
  session consult two things:
  - the banner (`banner show`, which is HANDOFF's `## Banner` section);
  - `CLAUDE.md` (step 5, durable rules, as the baseline counted it).

  The engine writes the ledger and the op log itself, so the session does not read them.
  procedures § Clean close (5,280 B) is shown beside them: the receipts of 2026-10-15b and 16b
  list it as read.
- **W-write.** The close's commits, picked by subject: `engine: ... session.close <key>`,
  `engine: ... banner.set <key>`, and `docs: <key> close ...`. Bytes are the `+`/`-` lines of
  `git show` with the prefix included and the file headers excluded.
- **Calibration.** The method reproduced all 10 of the baseline's commit totals exactly
  (2026-10-21).

| session | read at | W-read B (banner + CLAUDE.md) | tiktoken | gemma | with procedures § Clean close | close commits | W-write B | W-read + W-write | vs 51,892 B |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-14a (setup) | `e3f5c40` | 20,386 | 5,476 | 5,944 | 25,666 | `fc7bdff` `eef0ecc` | 2,372 | 22,758 | -56.1% |
| 2026-10-14b (setup) | `eef0ecc` | 20,533 | 5,513 | 5,991 | 25,813 | `fbe3090` `8d244e5` | 2,700 | 23,233 | -55.2% |
| 2026-10-14c | `322fe9f` | 20,512 | 5,509 | 5,986 | 25,792 | `9c9dbf0` `5cb11b7` | 4,329 | 24,841 | -52.1% |
| 2026-10-15a | `271329c` | 20,741 | 5,601 | 6,087 | 26,021 | `43a6faa` `71237e4` `6badce7` | 20,103 | 40,844 | -21.3% |
| 2026-10-15b | `90e59ba` | 21,150 | 5,737 | 6,270 | 26,430 | `50e10c2` `92c0cc7` `4e42542` | 8,365 | 29,515 | -43.1% |
| 2026-10-16b | `28f8d57` | 21,587 | 5,870 | 6,429 | 26,867 | `667bb19` `4c8e4f3` `7106276` `360db88` `3bc4051` `03e89b0` | 38,958 | 60,545 | **+16.7%** |
| 2026-10-19a | `8e9a2be` | 22,901 | 6,265 | 6,869 | 28,181 | `9f7a5a7` `bb0892b` | 4,253 | 27,154 | -47.7% |
| 2026-10-21a | `bfea740` | 22,957 | 6,356 | 7,000 | 28,237 | `1421357` `b2856aa` `7107254` | 2,522 | 25,479 | -50.9% |
| 2026-10-21b | `51fb1df` | 19,563 | 5,402 | 5,992 | 24,843 | `dce9737` `4c894cb` | 2,059 | 21,622 | -58.3% |

Trial-session medians (n 7, 2026-10-21):

| measure | baseline | trial | change |
|---|---|---|---|
| W-read | 48,540 B (14,095 / 15,745 tokens) | 21,150 B (5,737 / 6,270 tokens) | -56% |
| W-write per close commit | 3,352 B over 10 commits | 2,134 B over 21 commits (range 202 to 24,026) | -36% |
| W-write per close | not measured | 4,329 B | (none) |
| W-read + W-write per close (median of the per-session sums, not the sum of the medians above) | 51,892 B | 27,154 B | **-47.7%** |

- **Verdict on line 2: met** in 6 of the 7 trial closes and at the median.
- **2026-10-16b is the exception.** Its close-docs commit `4c8e4f3` carried the 24 KB AAR, and the
  close took 3 extra `banner set` rounds to get lint clean (AAR 18). It is the same kind of outlier
  as the baseline's `3e3f442` and `d130711`.
- **W-steps.** The engine's close table has 10 rows, against 8 in the baseline (6 plus 2
  conditional). The baseline's steps were all hand edits. The engine's only routine hand edit is
  step 5 (durable rules). So the close has more steps, but fewer edits by hand. Outside the
  procedure, the three abandons were done by hand.

### C, concurrency (the baseline's definition)

- **Collisions or lost blocks: 0.** C did not rise, so **line 3 is met**.
- **The evidence is weak, as the baseline's was.** No two live sessions overlapped in the op log, so
  the trial never really tested concurrency.
- **Near-misses:**
  - **Op lines carried across sessions** (AAR 22). 2026-10-17a's 4 uncommitted op lines, the owner's
    delegation words among them, went into 2026-10-19a's first commit `a24d18d`. Until then they
    existed only in the working tree, for about 39 hours. With two live sessions, one session's
    commit would carry the other's op lines.
  - **Dead stubs that look open** (AAR 1, 25). Each time, someone had to ask the owner which
    sessions were live.

### Line 4, nothing needed goes missing

**Met.** No `read:` receipt after 2026-10-14a lists `docs/decisions.md` (frozen) or
`docs/archive/`. 2026-10-14a, the cutover, read them to import them. The `HANDOFF.md` that 21a read
is the new 7.6 KB one, which the rules require.

### Forgotten items (CE-79's "what was forgotten"; not in the baseline)

- **The method.** Each close's "Still owed" item was followed into the next closes and the tree.
- **Carried properly.**
  - Owed items that became batons were all carried: BTN-1 and BTN-2 from 2026-10-14c, and BTN-3 for
    2026-10-14d's round, all done in 15a.
  - 2026-10-15b's Fable review: done in 16b, `4f92697`.
  - 2026-10-16b's ASK-11 and AD-22 salvage: done in 19a, `f802f8a`.
  - 2026-10-21a's crash-rule home: done in 21b.
- **Forgotten: 3.** Each was written as ledger text, not as a baton, which goes against procedures
  § Clean close row 6.
  1. **INV-31's live hook probes** (resume, `/clear`, compaction). They were owed in 14a and 14b,
     then dropped from every later list, and were never run. Only the startup print is evidenced
     (AAR Timeline, update of 2026-10-21).
  2. **2026-10-19a's `docs/facts.md` `.scratch` inventory** for `ad16-r1`, `ad24-fresh` and
     `rung2b/fresh`. It is not in 21a's or 21b's owed list, and `docs/facts.md` does not mention
     those directories (grep, 2026-10-21).
  3. **AD-17's unexplained -187 dB outlier**, owed in 16b. It was dropped from 19a's list. The fact
     is in a results file, but no task or residual tracks it (AAR 33).
- **UNCLEAR: 2026-10-15b's secondary items.** The window-seed arm, the extra class's looked-at
  checks, osd.py's aggregation choice, and the scout's papers. None is in a later list or a task.
  AD-13 was parked by DEC-79, so they may be moot. Deciding that needs the owner.
- **Still open, and carried:** HANDOFF's stale lines (AAR 27), owed by 21a and 21b.
- **A false record.** The newest closes' ledger said "Nothing pushed" after the 2026-10-20 push.

### Other rubric-adjacent checks

- **INV-31 probes.** Only the startup print is evidenced. Resume, `/clear` and compaction are
  unprobed (see Forgotten item 1).
- **Read receipts.** The engine arm has them in every close, as CE-4 expected. 2026-10-19a's
  `guards:` receipt has no gate pass count (AAR 36).

## 3. Engine errors, refusals and by-hand fallbacks in adhoc

| # | what | where | AAR item | engine task (open, 2026-10-21) |
|---|---|---|---|---|
| 1 | Stale sessions were abandoned by a hand edit of the ledger, 3 times, with no op line. The third was signed by a session that had already closed. | `2612284`, `4c8e4f3`, `5c61449` | 3, 21, 25 | CE-124 |
| 2 | Orient cannot tell a dead session from a live one, so the owner had to be asked. | ledger 2026-10-16a, 17a | 1 | CE-104 |
| 3 | `banner set` accepted a banner that lint then rejected (G-D8, G-D1), and `commit` ran no lint. It took 3 extra `banner set` rounds. | `667bb19`, `7106276`, `360db88`, `3bc4051` | 18 | CE-63 (G-D5 at write time; G-D1/G-D8 not yet named there) |
| 4 | Lint's G-D1 cap went red on a CLAUDE.md rule, so the rule was deferred, and two durable rules had no tracked home until 21b. | `.scratch` log only; `51fb1df` | 10, 20 | CE-109 |
| 5 | An owner answer given through the chat tool needed a hand-built `record new decision`. | 2026-10-16b | 14 | CE-111 |
| 6 | A dead session's op lines were swept into the next session's commit. | `a24d18d` | 22 | none found (CE-101 is foreign commits) |
| 7 | `ask answer` froze agent text as owner words, and delegated rulings are stamped `actor: owner`. | DEC-80, DEC-81, DEC-82 | 24 | CE-113 |
| 8 | A push was made outside any session, and no record names it. | `444efcc..5c61449` | 26 | CE-114 |
| 9 | `banner set` and `close` leave the rest of HANDOFF stale, and lint does not see it. The banner's "next" item is blocked. | HANDOFF at `4c894cb` | 27, 28 | CE-115, CE-116 |
| 10 | Records in one batch cited each other's ids before the ids existed, and drafts held literal `DEC-<NEW>` placeholders. | AD-16..AD-23; AD-7 fix | 31, 32 | CE-105, CE-119 |
| 11 | `register show` refuses because the register has never been created: 6 task closes filed no residual. | 2026-10-21 | 33 | CE-120 |
| 12 | CE_ACTOR is free text: 5 actor strings sign one op log. | `docs/ledger/ops.jsonl` | 35 | CE-122 |
| 13 | A `guards:` receipt with no gate count was accepted. | ledger 2026-10-19a | 36 | CE-123 |
| 14 | The charter and criteria are still templates, and lint passes. | `docs/charter.md`, `docs/criteria.md` | 34 | CE-121 |

**What worked as designed:** `ask answer` in one step (AAR 4); G-D1 catching growth (AAR 10, first
half); recovery from the workflow journals (AAR 23); batons carrying 2026-10-14d's round.

## 4. Verdict (CE-79): fix first, then keep going

- **Keep the trial; do not stop it.**
  - Lines 2 to 4 of the rubric are met.
  - The close costs about half the baseline's context (median -47.7%).
  - Every session opened through the engine, and 9 of 12 closed through it.
  - No collision, and no fallback to the pre-engine files.
- **Fix first.**
  - **Line 1 is missed, and the gap is widening.** S is at -23.7% at the median and -17.6% now.
    Two causes are cheap to fix:
    - adhoc's `CLAUDE.md` still says to read HANDOFF in full, so the banner is read twice;
    - the banner grows with no cap.
  - **A quarter of the sessions ended outside the engine**, by hand abandon (rows 1, 2).
  - **The 3 forgotten items** all come from "still owed" written as text, not batons.
  - **Before the next real use:** an abandon path (CE-124), last activity in orient (CE-104), lint at
    `banner set` (row 3), and session-scoped `commit` (row 6, which has no task yet).
- **Re-pin adhoc, but once, after those fixes, not now.**
  - **The gap.** The pin `38ed38e` is 156 commits behind engine `1f3f7d7` (2026-10-21).
  - **What adhoc would gain:**
    - CE-78 and CE-92: a scoped gate and `gate status` at close step 7. These matter most there,
      because adhoc's gate runs about 12 minutes (728.80 s on 2026-10-21).
    - CE-83 and CE-82: the contract itself now carries the coordinator rule and close-eagerly. So
      adhoc's "The main conversation coordinates" section in `CLAUDE.md` could go, which helps
      G-D1 (row 4).
    - CE-91: who decides, by reversibility.
    - CE-64: the trailer paragraph.
    - CE-81: lint skips `.context-engine/`.
    - CE-41: G-D3 bare names.
    - CE-27: doc freeze and doc archive.
    - CE-58: record confirm.
    - CE-65: the foreign-commit start head.
    - CE-99: rerank and goals.
    - CE-72: CLI help.
  - **Not fixed since the pin:** none of the engine rows in §3.
  - **Dry run (2026-10-21).** Engine `1f3f7d7` linted a copy of adhoc `4c894cb`. Only G-D0 was red,
    for the contract. After copying the kit's contract over it, lint was clean.
  - **The cost.** The contract grows from 6,560 to 9,102 B, which adds 2,542 B to S unless adhoc's
    `CLAUDE.md` drops what the contract now says.
