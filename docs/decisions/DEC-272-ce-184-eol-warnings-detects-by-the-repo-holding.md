---
type: Decision
id: DEC-272
title: "CE-184: eol_warnings detects by the repo holding .git, core.autocrlf true/yes/on/1, and context.toml's text/eol attributes. Known gaps: core.eol=crlf with a text attribute, and pins that cover other paths but not context.toml"
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:5636803e7721df433689a3083352c5c6224545c77046407b95dc92609ea1574e
---

`bootstrap.py::eol_warnings` detects a converting checkout by three things: the repo holds `.git` (so a plain directory never reads the global config, and no subprocess runs there); the repo's effective `core.autocrlf` is true, yes, on or 1 (read as a string, since `--type=bool` errors on `input`); and `git check-attr text eol -- context.toml` shows neither `eol: lf` nor `text: unset`. Any git failure or a missing git gives no warning: it is advisory and never refuses.

Known gaps, accepted for an advisory warning: `core.eol=crlf` together with a `text` attribute also converts and is not caught; a `.gitattributes` that pins other paths `eol=lf` but not `context.toml` still warns, and one that pins `context.toml` alone silences it. A census over every tracked file was rejected: binaries with `text` unspecified would count as unpinned, and it is more code for a warning.
