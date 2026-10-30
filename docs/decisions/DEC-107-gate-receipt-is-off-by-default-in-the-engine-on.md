---
type: Decision
id: DEC-107
title: gate_receipt is off by default in the engine, on in the kit template and this repo
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:0db7f470e4cb14e7de07686b7b69b680cf218ae5233f16a34732ed0614de6ea9
---

The agent's call on CE-123, made while building it in session 2026-10-30a: where the guards-receipt check is switched on.

Options:
(a) engine default on, with the kit regex, so every adopter's closes start refusing on upgrade;
(b) engine default '' (off), with the kit template and this repo setting `[working] gate_receipt`;
(c) a lint-only warning.

Chose (b): an upgrade does not suddenly refuse closes in existing repos whose gate prints no 'N passed' (e.g. go test), new repos get the check, and an adopter (adhoc) opts in with one config line. The kit value is `(?i)\d+ passed|passed \d+|not run`; this repo's also accepts 'gate status'.

Built in lane commits 72d98a8 and b60c310, on main as e5e68c7 and 2a86f14; pinned by AC-125. Cheap to undo.
