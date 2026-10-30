---
type: Task
id: CE-46
title: A fresh Windows clone turns kit runbooks CRLF and fails a kit byte check
brief: core.autocrlf=true; pin eol=lf for files the gate compares byte for byte
pri: LATER
state: closed
deps: []
source: session 2026-10-13b
created: 2026-10-13
moved: 2026-10-30a
updated: 2026-10-30a
goals: [G-6]
status: deprecated
closed: 2026-10-30a
---

Found 2026-10-13b: a worktree checked out with core.autocrlf=true fails tests/test_kit.py::test_init_copies_the_runbooks_and_keeps_an_edited_one (the copied runbook is CRLF, the kit's LF). Any fresh Windows clone, and every target repo's init on Windows, can hit it. Recommendation: a .gitattributes with eol=lf for docs/runbooks/*.md, src/context_engine/kit/**, docs/framework/contract.md, and have init's byte checks compare with line endings normalised where the file is the owner's (G-D0 already ignores line endings for the contract).

## Log

- 2026-10-13b (claude-code/claude-opus-5-5): 2026-10-13b: it hit the main tree, not only fresh clones: fast-forwarding main onto a branch built in a worktree checked out every changed file as CRLF (core.autocrlf=true), and the gate went red on test_init_copies_the_runbooks_and_keeps_an_edited_one. Fixed locally by writing the committed LF bytes back (33 files; content identical, git diff empty). Trap: Git Bash's grep here does not see \r (grep -c $'\r' printed 0 on a CRLF file); check with Python or file(1). Raises this item's priority: any merge on this machine can redden the gate.
- 2026-10-14a (claude-code/claude-opus-5-5): 2026-10-14a: also bites on cherry-pick. Merging worktree commits into main with autocrlf=true wrote the kit files they touched with CRLF, and test_init_writes_the_bootloader... and test_init_copies_the_runbooks... went red. Fixed with git -c core.autocrlf=false checkout -- <those files>. A .gitattributes 'eol=lf' for src/context_engine/kit and docs/runbooks would end it.
- 2026-10-19f (claude-code/claude-opus-5-5): Repo half done in 20b1ad9 (.gitattributes eol=lf for the kit, docs/runbooks/*.md and docs/framework/contract.md; tests/test_kit.py pins it). Left: the init/bootstrap.py half, after CE-43.
- 2026-10-30a (claude-code/claude-opus-5-5): closed: Done in 4cc4e1a (lane ec4dd4d), cites in 8f9851f: the init half was already in place. init reads the kit with universal newlines, so it writes LF whatever the engine's checkout; G-D0's kit-block and contract checks and init's own checks compare line endings aside. tests/test_kit.py::test_line_endings_change_nothing_init_writes_or_lint_checks_in_an_adopting_repo (new AC-115) pins it. No eol=lf for adopting repos (DEC-94). Kit README notes it. Sabotaged red three ways.
