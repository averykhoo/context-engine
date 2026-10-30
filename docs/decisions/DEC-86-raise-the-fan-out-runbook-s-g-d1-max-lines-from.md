---
type: Decision
id: DEC-86
title: Raise the Fan-out runbook's G-D1 max_lines from 90 to 110
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-30
session: 2026-10-30a
body_sha: sha256:6d4cd36faa570ff592fb187333a6e4d0560283ec5e11a8724db51871b5f3f98e
---

The Fan-out runbook (`docs/runbooks/fan-out.md`, and its kit copy) outgrew its 90-line G-D1 cap
once CE-106, CE-107 and CE-118 added the cross-run, watcher and worktree notes: MEASURED
2026-10-30a, 102 lines and 7457 bytes. Its `max_lines` is raised from 90 to 110 in `context.toml`
and in the kit's `context.toml.template`, with a MEASURED provenance note; `max_bytes` stays at
8000 and `max_width` at 100.

Options weighed:
- Trim existing prose to stay at 90: rejected, about 19 lines were needed against 7 free, and
  the cap's own provenance says it is wrong if a method step is left out to stay under it.
- Raise the cap, with provenance: chosen.
- Split fan-out.md into two files: rejected, a new route and a new kit file for 12 lines.

Consequence: a repo that copied the old template keeps a 90-line cap for the Fan-out route and
goes G-D1 red when an upgrade replaces fan-out.md, until it raises the cap. The release notes or
the upgrade runbook must say so.

Landed in the CE-107 commit, the first to push fan-out.md past 90 lines (lane commit fae0a31,
integrated on main as 55c47ec).
