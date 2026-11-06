---
type: Decision
id: DEC-168
title: Orient serves Last close after the banner, and drops it whole when the banner would be cut
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
decided: 2026-11-06
session: 2026-11-06f
body_sha: sha256:db5fb1519d688b35e3cdf969c6401a4a736ddbdd7699e38804617496ef1a2be1
---

CE-195, verify-1 D1. The banner now holds only durable hand-written lines, held nowhere else; the Last close part is a copy of a ledger entry the cut note points to. So at orient's cap Last close is served after the banner (working.py::LAST_CLOSE_RANK = 4, banner BANNER_RANK = 3), and when the banner would still be cut, the part is left out, heading too (working.py::Engine.orient re-fits without it): even its heading and cut note cut the last item of adhoc's banner, which sat 33 bytes short of the cap. This is the one exception to every heading appearing (manual-mode § context-engine orient). Wrong if sessions miss the last digest because a long banner keeps hiding it; then cap the banner instead.
