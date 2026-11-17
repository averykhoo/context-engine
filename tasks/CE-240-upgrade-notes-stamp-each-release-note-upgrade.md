---
type: Task
id: CE-240
title: 'Upgrade notes: stamp each release-note Upgrade line with its landing ref; a from-pin checklist in kit README § 4'
brief: stamps in one parseable form a later upgrade command can read; no rule change
pri: NOW
state: closed
deps: [CE-238, CE-239]
goals: [G-6]
source: session 2026-11-17b
created: 2026-11-17
moved: 2026-11-17b
updated: 2026-11-17b
status: deprecated
closed: 2026-11-17b
---

Upgrade notes: stamp each release-note Upgrade line with its landing ref; a from-pin checklist in kit README § 4.

The upgrade steps an adopter needs are spread over RELEASE-NOTES sections keyed by framework version and a start date, not by the engine ref each line landed at, and kit README § 4 lists only some of them. intervals and zanzibar read § 4 and missed the banner cut, which the first close then refused; adhoc's and audio-workspace's pins cross all three 0.5 sections and 0.6 (docs/evidence/engine-feedback-2026-11-17.md, F33, F21, F35, F36, F41).

1. Stamp every `**Upgrade:**` line in docs/framework/RELEASE-NOTES.md with the ref it landed at, in one fixed, parseable form (fable proposes `**Upgrade (at <sha>):**`), so a later upgrade command can select the lines after a pin. Recover each ref from `git log` of the line; name the form in the release notes' header.
2. kit README § 4 gets a from-pin checklist, each item naming the ref it applies from:
   - `[gate]` with a code scope (F21: adopters run 43 min to 3.5 h gates every close; the highest-value line, write it first);
   - the first close after the re-pin cuts the banner (F33, CE-195);
   - `[working] gate_receipt` when the gate prints no pass count, or `''` (F30, F34; CE-192);
   - new lint guards and their remedies: G-I4, G-D3 citations and the waiver op (CE-239), G-D8;
   - `decision accept --owners`: a "no owner's decision is PROVISIONAL" refusal is a pass (F35);
   - rename the old env to `env-<oldref>`, delete it once lint and gate are green (F36);
   - delete `[working] decision_index` and `git rm` the stored index (F41; INV-95);
   - G-D0 names the ACCEPTED enum only after the kit block is replaced, so a dry lint before the upgrade understates it (F40).
3. bootstrap.py::next_steps names `[gate]` for a new repo too (F21).
4. Keep the kit README and its copies in step (tests/test_kit.py); the runbook copies stay byte-equal.

## Traps

- Stamp the ref the line landed at, not the date of its section: the date key is exactly what misled the 0.5 pins.
- The stamp form is an interface for the later `upgrade --dry-run` task: pick one form and test that every Upgrade line carries it.
- Order: after CE-238 and CE-239, so § 4 can name the waiver op as the G-D3 step.
- No new rule: this is docs and next_steps only. A changed kit contract turns G-D0 red in every adopter (CE-228's brief).

## Read first

- docs/evidence/engine-feedback-2026-11-17.md: F21, F33, F35, F36, F40, F41, § Upgrade hazards, § Second opinion item 4
- src/context_engine/kit/README.md § 4; docs/framework/RELEASE-NOTES.md (every `**Upgrade:**` line)
- bootstrap.py::next_steps

## Log

- 2026-11-17b (claude-code/claude-opus-5-5): closed: Built in c517640 and 563814e; independent opus verifier PASS round 2 (.scratch/ce-240/verify-2.md): 19 landing refs resolve, the from-pin walk for adhoc 9f0e8ca and audio-workspace 4f2cef2 gives every step each needs and none it has
  residual risk: INV-264
