---
type: Decision
id: DEC-218
title: "Engine default is a named constant: config.py::GATE_RECEIPT holds the kit pattern; Working.gate_receipt defaults to it and AC-32's test pins it equal to context.toml.template's value"
tasks: [CE-192]
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:8e77d0878d544794cf9ea784ecb1f4fd8d824e64f4b7141b8ef764566e8c2a66
---

The agent's call on CE-192, made while building DEC-162's ruling that `[working] gate_receipt` is on by default in the engine.

The engine's default is a named module constant, config.py::GATE_RECEIPT, holding the kit's pattern `(?i)\d+ passed|passed \d+|not run`, and config.py::Working.gate_receipt defaults to it. The kit template (`kit/context.toml.template`) keeps its own copy of the same value, since AC-32 requires the template to name every key the engine reads and it is where an adopter fits the pattern to their gate. The two copies are pinned equal by tests/test_kit.py::test_the_config_template_names_every_key_the_engine_reads_and_parses (AC-32), so they cannot drift apart.

Rejected: deleting the template line now that the default equals it (AC-32 would fail, and adopters lose the place to fit it); a literal in the dataclass with no name (the parity test would have nothing to cite).

Cost to undo: cheap.
