---
type: Task
id: CE-162
title: init's merge check reads a later binary line or a macro unsetting merge on the op log
brief: CE-53 residual (b36c32e); narrow case, git check-attr is the oracle
pri: LATER
state: open
deps: []
goals: [G-6]
source: session 2026-10-30a
created: 2026-10-31
moved: 2026-10-30a
updated: 2026-10-30a
---

init's merge check reads a later binary line or a macro that unsets merge on the op log.

Source: CE-53's close (b36c32e), residual (verifier probe against git check-attr, 2026-10-30). bootstrap.py::_union_merged reads only the merge, -merge, !merge and merge= words, so a later `binary` line or a macro unsetting merge on the op log goes unseen: init leaves the file alone while git reads merge as unset, against "erring toward appending" in its docstring and AC-116. Narrow case; asking git (`git check-attr merge`) may be the simpler fix.

## Traps

- none yet

## Read first

- bootstrap.py::_union_merged

## Log
