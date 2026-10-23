---
type: Task
id: CE-142
title: G-D3 checks backticked repo paths in prose, not only links and file::symbol
brief: Must tell a pointer from a glob, placeholder or example; sabotage with CE-93 verify-2's S3 rename
pri: LATER
state: open
deps: []
goals: [G-2]
source: session 2026-10-23f
created: 2026-10-24
moved: 2026-10-23f
updated: 2026-10-23f
---

G-D3 checks backticked repo paths in prose, not only links and file::symbol

CE-93's second verifier (verify-2, N5 and its sabotage S3) renamed the backticked `FRAMEWORK-v0.5-2026-10-23.md` in `docs/framework/RELEASE-NOTES.md` to a file that does not exist, and lint stayed clean. G-D3 (`guards.py::links`) checks markdown links and `file::symbol` only, so prose pointers to the archive, `RELEASE-NOTES.md` and `docs/engine.md` are guarded only by routes (G-R1, for the last two). Filed in session 2026-10-23f.

Extend G-D3 (or add a guard) so a backticked path to a repo file resolves, sabotage it with S3's rename, and say in FRAMEWORK §8.3 what it does not check.

## Traps

- Backticked text also holds globs (`FRAMEWORK-v0.*.md`), placeholders (`<path>`), example paths in other repos and paths that are meant not to exist yet; the check must tell a pointer from an example, or be limited to the docs `[guards] links` names.
- Frozen docs (archives, evidence) cite paths that were later moved; decide whether they are read.

## Read first

- `.scratch/ce-93/verify-2.md` (Nonblocking N5, sabotage S3; gitignored, so the finding is restated above)
- `guards.py::links`; `guards.py::Files`; FRAMEWORK §8.3 G-D3

## Log
