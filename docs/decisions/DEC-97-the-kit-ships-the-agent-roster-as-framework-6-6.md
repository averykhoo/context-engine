---
type: Decision
id: DEC-97
title: The kit ships the agent roster as FRAMEWORK §6.6 text, not as .claude/agents/*.md named agents
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:1c37289f989db0a1f2deb61d84e47011ada0affcc9e2e283eac84cef6d074c6f
---

The agent's call on CE-39, made while building it in session 2026-10-30a: how the kit ships the agent roster.

Options:
(a) ship each subagent role as a named agent in the kit (`.claude/agents/*.md` with its prompt, tools and model);
(b) ship the roster as FRAMEWORK §6.6 text only, each role run on the harness's built-in agent types with its row's limits in the prompt, and a repo free to add named agents.

Chose (b): it is cheap to undo and harness-neutral. The coordinator is the main thread, and making it a named agent replaces Claude Code's default system prompt (docs/evidence/claude-code-hooks-2026-10-13.md). Model choice stays in each repo's contract, so the rows use tiers (least, reading, most), with `fable` only for the arbiter where the owner asked. A kit-shipped named-agent set (with the hk agent of CE-12) can be filed later.

Built in lane commit 7f298c7, on main as cdc7261 (review fixes in 9bcdfc3); pinned by AC-113 and tests/test_roster.py. Cheap to undo: file the named-agent set as a task.
