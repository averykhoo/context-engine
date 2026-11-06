# Owner review queue: fable advice, 2026-11-06b

FROZEN 2026-11-06b. What the advice said when it was given; the owner's answers go in the records, not here.

On the owner's "ask fable about the rest" (2026-11-06b), one fable agent advised on what is waiting for the owner. It worked from a sonnet digest of the records and the items flagged in the 2026-11-06a banner. This is advice, not owner words: nothing in it is decided until the owner answers.


Written from the digest only; no record opened, nothing written but this file. Each item ends in the one word the owner says.

## 1. Two unfiled questions

(i) HOLD tier — **yes, task, LATER.** An engine tier that is never ready and that rerank (CE-99) skips. SOMEDAY is standing in for it today and rerank still touches SOMEDAY, so held items keep resurfacing. No decision needed now; the agent records the shape at build time (cheap to undo). Word: **file**.

(ii) Louder close on empty NOW — **yes, task, NEXT, warn not refuse.** Close prints the G-W5 red line and the remedy (`task promote <id>`) in the digest. A refusal would block a legitimate "everything is done" close. Word: **warn**.

## 2. The three lifecycle findings

1. PROVISIONAL is overloaded — **decision (owner words) + task, NOW.** This is the root of the whole §3 pile. Shape to rule: owner-actor records are born ACCEPTED (an owner's word awaits nothing); agent records stay PROVISIONAL until a new op `decision accept <ids>` (ranges allowed) marks them reviewed; BUILT stays for ones a task carried out. With that op the 60-odd agent decisions below close in one line instead of 60 `decision set` edits. Word: **yes**.

2. No conflict check — **task, LATER, no decision.** Do not try to detect semantic conflict. Two cheap mechanical checks: lint fails two non-superseded decisions with the same title (catches DEC-91/92), and a `relates:`/`narrows:` link kind so DEC-125→DEC-88 and DEC-126→DEC-112 are links, not prose. Word: **file**.

3. One-off permissions — **task, LATER, no decision now.** `ask answer --grant` records the owner's words on the ask record and in the ledger `summary:`, and mints no decision. The agent rules the exact shape at build time. Three records in 161 is not worth more than that. Word: **file**.

## 3. PROVISIONAL decisions

**Accept as they stand, in one op once `decision accept` exists (do nothing by hand before then; 60 `decision set` lines would be op-log noise):** DEC-86..90, DEC-92..96, DEC-98..106, DEC-108..109, DEC-111..119, DEC-121..130, DEC-133, DEC-148..149, DEC-159..160. All cheap to undo, all carried out by lanes already merged, and their known gaps are already tasks (CE-150..166, CE-186). Word: **accept**.

**Need a real owner call (one question each):**
- DEC-97 — "Should `init` install the roster as named agents (`.claude/agents/*.md`), or is FRAMEWORK §6.6 text enough?" My answer: text is enough until an adopter asks. **text**.
- DEC-107 — "Should `gate_receipt` be on by default in the engine too, so adhoc goes red until it adds a receipt?" My answer: yes; a check that is off where nobody opted in is the house failure mode. **on**.
- DEC-110 — "Make `--residual` mandatory on `task close`?" My answer: no; the optional flag plus nudge already over-produces (INV-97 is a reworded duplicate). **optional**.
- DEC-120 — "Fine to cut OKF `log.md` and `generated.by`, so §9.3 claims three parts, not four?" My answer: yes; OKF does not require a changelog. **cut**.

**Supersede or link:**
- DEC-88 → superseded by DEC-125: DEC-125 contains DEC-88 entirely (every append-only kind, not behind G-I3's switch). One `decision supersede` op. **supersede**.
- DEC-126 ↔ DEC-112: `decision link`, nothing more. **link**.
- DEC-91/92: already done (SUPERSEDED/PROVISIONAL); the title clash is finding 2's lint case. **nothing**.
- Merge nothing. The multi-decision lanes (DEC-99..101, 102..104, 108..110, 116..119, 121..123, 127..128) are one decision per call, which is the right grain; merging rewrites append-only records for no reader's benefit. **no merge**.

## 4. Residuals CE-150..166 and CE-186

| id | call | note |
|---|---|---|
| CE-150 | keep LATER | correctness of the criteria count; small |
| CE-151 | keep LATER | pairs with DEC-126 |
| CE-152 | keep LATER | the `pause resume` half loses asked tasks; fix that half first |
| CE-153 | **merge into CE-154**, do now | archiving the op log or `context.toml` is a one-line refusal; same file as CE-154 |
| CE-154 | keep LATER | takes CE-153 |
| CE-155 | keep LATER | |
| CE-156 | **keep NEXT, matters most** | the runbooks are "the only place" every session reads the steps; stale text there misleads every session |
| CE-157 | keep LATER, dep on next release | release-note lines; not a floating task, a release step |
| CE-158 | **promote NEXT, matters** | a refusal whose printed remedy does not clear it is a trap, and the contract tells agents to follow remedies |
| CE-159 | **merge into CE-156** | the fix is the doc sentence ("any unused id"), not the code |
| CE-160 | keep LATER | |
| CE-161 | keep NEXT | |
| CE-162 | **drop** | an edge of an edge (`binary` after `merge=union`); nobody writes that |
| CE-163 | **close as a register entry** | the task itself says "or a register entry"; file INV, close task |
| CE-164 | keep NOW | the pick |
| CE-165 | keep LATER | sabotage debt; list the tests in the task body so it can be split |
| CE-166 | keep LATER, done in adhoc | see §6 |
| CE-186 | keep LATER; retire INV-97 now | the INV-97 retire is one op the coordinator can do today; pins wait |

The two that matter: **CE-156** and **CE-158**. Both are "what the agent reads tells it the wrong thing", which costs every session, not one.

## 5. Register entries

- INV-84, 85, 87, 95, 96: **keep**.
- INV-86: **keep, but it is the one worth a task**: a receipt that passes on "lint not run" anywhere is a hole, not a residual; the fix is a stricter match (the whole receipt is "not run", or nothing). Fold into CE-165 or file a LATER task.
- INV-88: **keep** (a different cause: the matcher's narrowness).
- INV-89 + INV-90: **merge** into one entry ("the launcher judges a hook by its text and never runs or expands it"); retire the other, never delete.
- INV-97: **retire now** as a duplicate of INV-95 (one op, today; CE-186 then only carries the pins).

## 6. Owner-held tasks

- CE-40 (global CLAUDE.md audit): **needs the owner**, but is blocked on CE-11 or on the owner accepting the gap. Action: owner says "gap" (accept it), an agent drafts the trimmed text to a tracked doc, the owner pastes. Until then, SOMEDAY. Word: **gap**.
- CE-47 (trim this repo's CLAUDE.md): **needs the owner only to approve the diff**; the agent can produce it today. Every session pays for that file's length, so this is cheap and recurring. Action: promote to NEXT, agent writes the diff, owner reads it once. Word: **promote**.
- CE-56 rename half: **needs the owner, and the answer is no.** DEC-37's alias mechanism exists so this repo can keep US/INV/G while the kit defaults use STORY/RISK/GOAL. A yes rewrites many records for nothing. Close the rename half as declined; the kit-defaults half stands. Word: **no**.
- CE-132 (contract wording): **needs the owner for timing only.** Bundle all three wording fixes into the contract bump that the PROVISIONAL split (§2.1) forces anyway, since "Who decides" changes then. Action: `task dep` CE-132 on the new status task. Word: **bundle**.
- CE-166 (adhoc gate_receipt): **does not need the owner**, only an adhoc session; and if DEC-107 flips to on-by-default it needs nothing but adding the receipt line there. Action: first thing in the next adhoc session, then close here. Word: **adhoc**.
- CE-28 (cross-repo question index): **owner decides, and the case is now made**: three repos run the framework and this very session exists because the question queue is invisible. Action: move SOMEDAY → LATER, keep the CE-15 dep. Word: **later**.
- CE-110 (paste global rules 1 and 2): **needs the owner's hands, two minutes.** Paste them and close. Word: **paste**.

(ASK-26 / DEC-161 / CE-182 needs no advice: it is being carried out; the only standing item is the zanzibar backup, which stays until zanzibar's next clean close.)

## The three that matter, ranked

1. **Fix PROVISIONAL (§2.1): one decision in your words, one NOW task.** It is why 146 of 161 decisions are unreviewable and why this digest had to be written; once `decision accept` exists, all of §3's "accept" list closes in one op and this never piles up again.
2. **Give six one-word answers now:** DEC-97 text / DEC-107 on / DEC-110 optional / DEC-120 cut, CE-56 no, CE-110 paste. Nothing else in §3 or §6 needs you.
3. **Promote CE-156 and CE-158, and take CE-153's one-line refusal with them.** Stale runbook steps and a refusal whose remedy fails mislead every session that follows the contract to the letter.
