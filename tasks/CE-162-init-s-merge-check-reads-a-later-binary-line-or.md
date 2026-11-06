---
type: Task
id: CE-162
title: init's merge check reads a later binary line or a macro unsetting merge on the op log
brief: CE-53 residual (b36c32e); narrow case, git check-attr is the oracle
pri: LATER
state: closed
deps: []
goals: [G-6]
source: session 2026-10-30a
created: 2026-10-31
moved: 2026-11-06c
updated: 2026-11-06c
status: deprecated
closed: 2026-11-06c
---

init's merge check reads a later binary line or a macro that unsets merge on the op log.

Source: CE-53's close (b36c32e), residual (verifier probe against git check-attr, 2026-10-30). bootstrap.py::_union_merged reads only the merge, -merge, !merge and merge= words, so a later `binary` line or a macro unsetting merge on the op log goes unseen: init leaves the file alone while git reads merge as unset, against "erring toward appending" in its docstring and AC-116. Narrow case; asking git (`git check-attr merge`) may be the simpler fix.

## Traps

- none yet

## Read first

- bootstrap.py::_union_merged

## Log

- 2026-11-06c (claude-code/claude-opus-5-5): closed: dropped (DEC-162): an edge of an edge (a binary line or macro after merge=union on the op log); nobody writes that
  residual risk: none
