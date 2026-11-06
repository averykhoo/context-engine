---
type: Decision
id: DEC-166
title: session start --continues is a link of its own, beside --follows, and orient reads the thread (CE-195)
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
refs: [DEC-163, US-21, DEC-105]
decided: 2026-11-06
session: 2026-11-06f
body_sha: sha256:9a61dd8401dec41e36d1c0a5d12cdd37503978f566d4657f3bf6c0a351b58a42
---

The agent's call on CE-195 (DEC-163, US-21), made while building it in session 2026-11-06f: how `session start --continues <key>` relates to the existing `--follows <key>` (CE-84).

Options:
(a) a link of its own: the stub carries `- **continues:** <key>`, which the close or pause keeps first in the entry, as `follows` is; the same closed-only rule and refusals (DEC-105); a session has one link or none (the engine refuses both, the CLI makes them mutually exclusive); orient shows a `Continues <key>: what it closed with` part that starts with the conversation's thread (`a > b > c`, walked back through `continues:` links, ledger.py::thread), and other open sessions show `; continues <key>`;
(b) `--continues` as another spelling of `--follows`, writing `follows:`.

Chose (a): a follow-up fixes what a closed session left (work found wanting); a continuation is the next turn of the same conversation. Keeping them apart is what lets the ledger and orient read a back-and-forth as one thread without mistaking every follow-up for one.

Built in ledger.py::CONTINUES, ledger.py::thread, working.py::Engine.session_start and working.py::Engine.orient; pinned by AC-185. Cheap to undo.
