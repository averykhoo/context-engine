---
type: Task
id: CE-214
title: Move the .scratch sweep classes, eager commit and CI-config-branch rules into the kit runbooks
brief: Kit change per CE-40's audit section 3; byte-equal kit runbook copies; contract edit means a version bump
pri: LATER
state: open
deps: []
goals: [G-6, G-7]
source: session 2026-11-07e
created: 2026-11-08
moved: 2026-11-07e
updated: 2026-11-07e
---

Filed by CE-40's builder (session 2026-11-07e, 2026-11-08), as DEC-320 says. CE-40's audit, `docs/evidence/global-claude-md-audit-2026-11-07e.md` § 3, found four framework-shaped rules in the owner's global `~/.claude/CLAUDE.md` that no FRAMEWORK, contract or runbook text holds (0 hits at HEAD, checked by that doc's § 5 checker), plus one candidate:

- R19: the `.scratch/` sweep's four classes (DERIVABLE, SUPERSEDED with the file named and the line quoted, SALVAGE naming the tracked file the finding belongs in, UNCLEAR), and "SALVAGE is the deliverable". Proposed home: `docs/runbooks/fan-out.md` § Delegating reading and auditing, as the sweep auditor's verdict form; FRAMEWORK § 6.6's roster row "`.scratch/` sweep auditor" points at it.
- R20: exclude the auditing agent's own report directory from the sweep. Same bullet.
- R30: commit whenever the gate is green and the session changed something. Proposed home: contract § Rules (this repo already has it as DEC-22 in `CLAUDE.md`); a contract change needs a framework version bump.
- R34: keep CI/CD config changes out of feature branches unless that is the task. Proposed home: `docs/runbooks/procedures.md` § Push and CI.
- R10 (candidate): a session that starts a long-lived process owns stopping it, and names what it leaves up. Proposed home: `docs/runbooks/fan-out.md` § Watchers.

A kit change: every runbook edit goes to both `src/context_engine/kit/docs/runbooks/` and `docs/runbooks/` byte-equal and LF (CE-46), and plugin skill quotes (tests/test_plugin.py) may need updating. Once moved, the owner can drop the matching lines from the global file's "Not yet in the framework" section.
