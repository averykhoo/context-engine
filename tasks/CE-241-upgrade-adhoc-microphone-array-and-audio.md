---
type: Task
id: CE-241
title: Upgrade adhoc-microphone-array and audio-workspace to 0.6
brief: adhoc first as the rehearsal; each repo through its own session; the owner pushes
pri: LATER
state: open
deps: [CE-238, CE-239, CE-240]
goals: [G-6]
source: session 2026-11-17b
created: 2026-11-17
moved: 2026-11-17b
updated: 2026-11-17b
---

Upgrade adhoc-microphone-array and audio-workspace to framework 0.6.

Owner, 2026-11-17: "collate all the feedback, let's handle that now and then we can upgrade those to 0.6". At engine 5d806f7 a dry lint is red 6 times in adhoc (pin 9f0e8ca) and 141 times in audio-workspace (pin 4f2cef2), and neither can get green legally until CE-238 and CE-239 land (docs/evidence/engine-feedback-2026-11-17.md, § Upgrade hazards).

1. adhoc first, as the rehearsal (6 lint lines, newer pin, the banner-note fix already in), through its own session and its AD-113: kit README § 4 as CE-240 leaves it, then the hazards list for adhoc. Note in this Log every step the checklist missed.
2. Then audio-workspace (141 lines, a stacked banner, `gate_receipt` to set, 41 commits ahead of origin), through its own session: the hazards list for audio-workspace. This is also the re-pin CE-193 still owes for entry 3 (guards.py::ask_problems).
3. In each repo: rename the old env to `env-<oldref>` and delete it once lint and gate are green; remove `[working] decision_index` and the stored index; a ledger line naming the new ref.
4. The owner pushes each repo (DEC-22); every push gets a CI watcher where the repo has CI (adhoc has none).

## Traps

- Not before CE-238, CE-239 and CE-240: without them adhoc's 3 and audio-workspace's 137 G-D3 lines have no legal fix, and turning G-D3 off is not one.
- Each repo's work is done by that repo's own session, under its own CLAUDE.md, not from this repo; this task tracks it.
- audio-workspace's `gate_receipt`: a pattern on "engine gate green" leaves its newest close (2026-11-15b) red; use `''` or a pattern that also matches the 15b wording (F34).
- Deleting `.context-engine/env-309641b` in intervals and graph-reachability-zanzibar-index is the owner's (deleting untracked files), and so is removing their dead `decision_index` files once pushed (F41): list them in the digest, do not do them.
- The pins cross all three 0.5 sections of RELEASE-NOTES and 0.6: read them all, not only kit README § 4 (F33).

## Read first

- docs/evidence/engine-feedback-2026-11-17.md: § Upgrade hazards (adhoc, audio-workspace), F7, F21, F24, F30, F34, F41
- src/context_engine/kit/README.md § 4 (after CE-240); docs/framework/RELEASE-NOTES.md
- CE-193 (entry 3's owed re-pin); CE-166 (adhoc's `gate_receipt`)

## Log
