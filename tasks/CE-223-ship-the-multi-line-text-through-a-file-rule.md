---
type: Task
id: CE-223
title: Ship the multi-line-text-through-a-file rule (pick the shell first)
pri: LATER
state: open
deps: []
goals: [G-6]
source: session 2026-11-10b
created: 2026-11-10
moved: 2026-11-10b
updated: 2026-11-10b
---

Ship the portable core of the shell rule (adhoc's layer-2 note, 2026-11-10; audit item 5). In adhoc, a PowerShell here-string used in Bash gave a commit message of just `@`.

- Multi-line text (commit messages, owner words, bodies) goes through a file: `git commit -F`, `--file`/`--body-file`, or the harness's file-write tool.
- Pick the shell first, then write for that shell.

The syntax table stays machine notes (docs/evidence/global-claude-md-audit-2026-11-07e.md R2 classed it MACHINE).

Changes: kit/docs/runbooks/manual-mode.md § context-engine commit (byte-equal copy). Or the contract's Environment section, if the owner prefers; a contract change waits for the next framework version bump.
