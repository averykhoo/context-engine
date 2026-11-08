---
type: Decision
id: DEC-255
title: 'CE-196: register show counts retired entries in N, adds `, M retired`, prints the merged and retired lines and the heading as written'
actor: claude-code/claude-opus-5-5
tasks: [CE-196]
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:3a4f067c448d889ac5caaca13ef5960dda73a527d600d214278b9b9b020b81e1
---

A build-time call for CE-196, the agent's own, PROVISIONAL until the owner reviews it.

`register show` (`review.py::summary`) counts retired entries in its `N residual risks`, because ids are never reused and orient's pointer at the engine register already counts every entry. It appends `, M retired` only when M is above 0, so a register with nothing retired reads exactly as before. Each entry prints its heading as written, so the retired marker shows, followed by the four required fields and then the `merged:` and `retired:` lines, which were hidden before. The site's register page uses the heading as written too.
