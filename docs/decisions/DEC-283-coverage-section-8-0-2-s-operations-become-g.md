---
type: Decision
id: DEC-283
title: "coverage: section 8.0.2's operations become G-D12's fourth class: backticked noun.verb names, file names excluded, floor 30 (38 counted 2026-11-08); an entry-point class, a whole-spec scan and an hk-only regex were rejected"
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:57b127421f15eff1f718dd6343d53daf43592f7ac6a0b038cb78ede8b8afc8ef
---

The agent's call on CE-164 (session 2026-11-07e): FRAMEWORK §8.0.2's operations become G-D12's fourth class.

Inside §8.0.2 only (its `###` heading to the next heading of level 3 or less), outside fenced code, every backticked `noun.verb` name followed by `(` or a closing backtick is an operation (`guards.py::OPERATION_RE`, `OPERATION_SECTION_RE`); a name whose verb is a file extension (`md`, `toml`, `json`, `yaml`, `yml`, `py`, `txt`) is a file name, not an operation. The floor is 30 (`COVERAGE_FLOORS["operation"]`); the pattern found 39 at 6688e49 on 2026-11-08 (38 at 77e043e, the planner's count). This closes N3 of CE-141's residuals: `hk.run` is §8.0.2's housekeeping script and `hk.close` its mechanical close, and both are now spec items.

Rejected:
- dotted names from the whole spec: it picks up `gate.md`, `context.toml`, `major.minor` and `register.append` from prose;
- an entry-point class (CLI, MCP server, housekeeping script): three items, and it needs a hand map from name to code, while `hk.run` already is the script;
- a regex for `hk.` names only: ad hoc, and it leaves the other operations unmeasured.

Not extracted: the task-row operations §8.0.2 writes bare (`list`, `show`, `.set`); said in the docstrings' "Not checked".

Cheap to undo: the class is one entry in each of the class tables in guards.py.
