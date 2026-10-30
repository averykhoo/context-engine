---
type: Task
id: CE-141
title: Generated build-status table for FRAMEWORK's components, procedures and guards
brief: Generated with a guard that it is current, never hand prose; FRAMEWORK.md may carry no CE ids (AC-33)
pri: NOW
state: closed
deps: []
goals: [G-7]
source: session 2026-10-23f
created: 2026-10-24
moved: 2026-10-30a
updated: 2026-10-30a
status: deprecated
closed: 2026-10-30a
---

Generated build-status table for FRAMEWORK's parts

CE-93 removed every build-status marker from FRAMEWORK.md without a generated status table in its place (DEC-81, the builder's P-4). CE-93's second verifier (verify-2, N3) notes the cost: §8.0.2's table and §11.1's list name the housekeeping script and `hk.close` with no status (CE-6 is open), so a reader of the spec cannot tell what is built. Filed in session 2026-10-23f.

Build a generated table (built / deferred with its §11.2 trigger / not built with its board item) for FRAMEWORK's components, procedures and guards, with a generator and a guard that it is current, or record why the board and the coverage map are enough.

## Traps

- FRAMEWORK.md may carry no CE ids (AC-33): the table lives outside it, or the leak test changes first, which is a decision.
- G-D12's coverage map (`docs/evidence/framework-coverage-*.md`) already maps every name to a board item; reuse it rather than a second source.

## Read first

- `.scratch/ce-93/verify-2.md` (Nonblocking N3) and `.scratch/ce-93/build.md` (P-4); both gitignored, so the finding is restated above
- DEC-81; FRAMEWORK §8.0.2, §11.1, §11.2; charter goal G-7

## Log

- 2026-10-30a (claude-code/claude-opus-5-5): closed: done in 3ad5028 (lane de47cc3), cite in 8ba0b73: `context-engine coverage` (MCP `coverage`) prints each FRAMEWORK component, procedure and G-id with one build status (built/deferred/prose-only/open work/done/map only/unowned), generated on demand from G-D12's spec and newest coverage map, the board and LINT_IDS, never stored (DEC-115). Also: manual-mode by-hand section (kit copy), FRAMEWORK pointers, RELEASE-NOTES line, criteria AC-170 and AC-171.
