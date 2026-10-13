---
type: Task
id: CE-46
title: A fresh Windows clone turns kit runbooks CRLF and fails a kit byte check
brief: core.autocrlf=true; pin eol=lf for files the gate compares byte for byte
pri: LATER
state: open
deps: []
source: session 2026-10-13b
created: 2026-10-13
moved: 2026-10-13b
updated: 2026-10-13b
---

Found 2026-10-13b: a worktree checked out with core.autocrlf=true fails tests/test_kit.py::test_init_copies_the_runbooks_and_keeps_an_edited_one (the copied runbook is CRLF, the kit's LF). Any fresh Windows clone, and every target repo's init on Windows, can hit it. Recommendation: a .gitattributes with eol=lf for docs/runbooks/*.md, src/context_engine/kit/**, docs/framework/contract.md, and have init's byte checks compare with line endings normalised where the file is the owner's (G-D0 already ignores line endings for the contract).

## Log

- 2026-10-13b (claude-code/claude-opus-5-5): 2026-10-13b: it hit the main tree, not only fresh clones: fast-forwarding main onto a branch built in a worktree checked out every changed file as CRLF (core.autocrlf=true), and the gate went red on test_init_copies_the_runbooks_and_keeps_an_edited_one. Fixed locally by writing the committed LF bytes back (33 files; content identical, git diff empty). Trap: Git Bash's grep here does not see \r (grep -c $'\r' printed 0 on a CRLF file); check with Python or file(1). Raises this item's priority: any merge on this machine can redden the gate.
