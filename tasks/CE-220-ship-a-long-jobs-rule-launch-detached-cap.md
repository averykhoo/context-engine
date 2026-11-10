---
type: Task
id: CE-220
title: 'Ship a long-jobs rule: launch detached, cap workers, stop by process group, pin committed-output tools'
pri: LATER
state: open
deps: []
goals: [G-6]
source: session 2026-11-10b
created: 2026-11-10
moved: 2026-11-10b
updated: 2026-11-10b
---

Ship a rule for long-running jobs in the kit (adhoc's layer-2 note, pasted by the owner 2026-11-10; audit: .scratch/adhoc-feedback-2026-11-10/audit.md items 7 and 8).

- Launch a long job detached, as one script. Never background an `&&` chain.
- Cap its workers when it is launched.
- Stop it by process group, and check with `ps` that it is gone. In adhoc, neither `ulimit -u` nor `taskkill /T` stopped Git Bash workers (its AD-52; the ulimit half here is DEC-131, docs/evidence/ulimit-gitbash-2026-11-01.md).
- A detached or login shell can resolve a different tool on PATH. In adhoc, `bash -l` picked up pixi's pdftotext, which would have silently rewritten committed text (its AD-75). Pin, by path or version, every tool whose output is committed, and record which one ran.

Changes: kit/docs/runbooks/fan-out.md (a "Long jobs" part under Watchers; the docs/runbooks copy stays byte-equal, LF), and FRAMEWORK §6.6 in place. CE-110 holds the owner's global-file half; this item is the half that ships.
