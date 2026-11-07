---
type: Decision
id: DEC-199
title: The shallow-clone wording fix also covers Engine._stale_stub_failures and the FRAMEWORK G-W11 bullet, which carried the same stale (CI's checkout) phrase
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:48aaea76eba80d7514fa28a5481956a8bc21179b7f1fe2b47ed5a31e32da33f0
---

CE-170's shallow-clone wording fix covers three places, not the one the item names: guards.py::mechanical_closes's docstring, working.py::Engine._stale_stub_failures's docstring, and the G-W11 bullet in FRAMEWORK §8, all of which called a shallow clone "CI's checkout". CI fetches full history since 5858302 (AC-180), so each now says a shallow clone is a `--depth` clone and that CI fetches full history. docs/runbooks/gate.md's row "Give CI's checkout the repository's full history" is an instruction, accurate as written, and is left alone. CE-170.
