---
type: Decision
id: DEC-95
title: init appends the op log merge=union line to .gitattributes without asking
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:e64fbd5aaad1380de7f352600115dac95eae538a0e42a5a74e81acbc98c46723
---

The agent's call on CE-53, made while building it in session 2026-10-30a: whether `init` asks before giving the op log git's union merge driver in the repo's `.gitattributes`.

Options:
(a) ask the owner first, with a `--merge-`/`--skip-` flag pair like the settings merge (DEC-32), as CE-53's body recommended (that recommendation came from an agent, CE-45, not from the owner);
(b) append the line without asking, as `init` does for the `.gitignore` line (DEC-41).

Chose (b). The line names only the engine's own file (the op log `context.toml` names) and touches nothing of the owner's. The settings file is asked about because it holds the owner's permission grants, which does not apply here. A dry run shows the line, and init's output labels it. (a) would add a flag pair to the CLI, MCP and ops, and a question at every adoption.

Known gap at landing (verifier, 2026-10-30): bootstrap.py::_union_merged reads only the `merge`, `-merge`, `!merge` and `merge=` words, so a later `binary` line or a macro that unsets `merge` on the op log is not seen; init then leaves the file alone while git reads merge as unset. That contradicts "erring toward appending" in the function's docstring and in AC-116's text in that narrow case.

Built in lane commit cf58a1c, on main as 2ae0621 (AC-116). Cheap to undo: add the flag pair and the question.
