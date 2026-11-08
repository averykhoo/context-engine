---
type: Decision
id: DEC-302
title: 'Housekeeper agent tools: only hk_run and hk_comment, model haiku; the test pins only existing hk_ ops, hk_comment among them'
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:662960f70caabf66b9843b18bd59b11f52838c26aee3f6ecd7e1167113f16039
---

**Decision:** this repo's tier-1 housekeeping agent (`.claude/agents/housekeeper.md`, CE-12) names only `mcp__context-engine__hk_run` and `mcp__context-engine__hk_comment` in its `tools:` frontmatter, and runs on `model: haiku` (the roster's "least" model). Its frontmatter keys are exactly `name`, `description`, `tools` and `model`. The test (`tests/test_roster.py::test_this_repos_housekeeping_agent_names_only_hk_tools`) pins the invariant, not the exact set: every tool is `mcp__context-engine__hk_<op>` with `hk_<op>` an existing operation in `ops.OPS`, the list is non-empty, and `hk_comment` is among them.

**Why:** FRAMEWORK §6.11 gives tier 1 only `hk_` tools. The agent's job is the judgement `hk comment --scan` lists as `tier 1:` lines; it reads with `hk_run(phase="start", check=True)` and writes with `hk_comment(..., text=...)`. `hk_close`, `hk_expire_batons` and `hk_stamp_asked` are tier 0's, done by `hk run`, so the agent does not need them. A missing `tools:` line would make the agent inherit every tool, and a `mcpServers` key could widen what it reaches, so the key set is pinned.

**Rejected:** giving it Read, Grep, Glob or Bash (breaks "only hk_"; Bash fencing is session-wide); pinning the exact tool set (a weaker statement of the same invariant, and it would break on a harmless addition such as another hk_ read).
