---
type: Decision
id: DEC-223
title: gate_receipt is on by default in the engine; '' turns it off
actor: claude-code/claude-opus-5-5
tasks: [CE-192]
refs: [DEC-162]
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:52cd4d47b4599b73b69afb7e6b9a2f9227edf33b4d5698050c2fc9a5113d51fb
supersedes: [DEC-107]
---

Built per DEC-162, the owner's ruling that DEC-107 goes "on" (docs/evidence/owner-review-advice-2026-11-06b.md § 3), in CE-192.

`[working] gate_receipt` is on by default in the engine: its default is config.py::GATE_RECEIPT, the kit's pattern `(?i)\d+ passed|passed \d+|not run`, equal to the value `kit/context.toml.template` carries (pinned by AC-32's test, tests/test_kit.py::test_the_config_template_names_every_key_the_engine_reads_and_parses). An absent key means that default; an explicit `gate_receipt = ''` turns the check off; a repo's own pattern replaces it, and one that is not a regex is still refused at load. So `session close` refuses, and lint G-W6 fails the newest close of, a `guards:` receipt with no pass count and no "not run" in a repo that never set the key (AC-125).

Options, as DEC-107 framed them:
(a) engine default on, with the kit pattern: chosen by the owner (DEC-162);
(b) engine default '' (off), the kit template and this repo opting in: DEC-107's choice, superseded by this decision;
(c) a lint-only warning: rejected, as DEC-107 rejected it.

The upgrade effect is intended: in a repo whose gate prints no `N passed` (e.g. go test), the next close is refused and G-W6 fails its existing newest close until it fits `gate_receipt` to its gate's result line or sets it to `''`. RELEASE-NOTES.md 0.6 says so. Supporting calls: DEC-218 to DEC-222.

Cost to undo: cheap (one default and its tests).
