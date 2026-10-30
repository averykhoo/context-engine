---
type: Decision
id: DEC-109
title: A residual stated at close uses the design-review residual line format plus a required affects field
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:f2091100e9b7be0ac4cc0e92ffa1a25e94a8cc2a1a2e8dc187127934e9b618a5
---

The agent's call on CE-120, made while building it in session 2026-10-30a: the format of a residual stated at close.

Options:
(a) a free-text line;
(b) the design-review residual line format plus a required `affects:` field: `<risk> | rung: | why: | control: | affects:`.

Chose (b): one format feeds the register (P18 E), so a residual stated at close and one from a design review are filed the same way.

Built in lane commit 1a89d74, on main as 750aff7 (working.py::Engine._stated_residuals); pinned by AC-127. Cheap to undo.
