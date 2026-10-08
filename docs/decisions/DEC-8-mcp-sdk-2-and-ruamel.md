---
type: Decision
id: DEC-8
title: Target the MCP Python SDK 2.x and ruamel.yaml
actor: agent (claude-opus-5-5)
decided: 2026-10-08
session: 2026-10-08a
decision_status: BUILT
tags: [packaging]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-08T15:00:00+08:00 }
body_sha: sha256:1648ed4e00c775129e1edabd668dd0b6f7b994829ad2d9bdc758c4dc84ae423f
---

The env has `mcp` 2.3.0, where `FastMCP` was renamed `MCPServer` (`mcp.server.mcpserver`);
the spike server uses it (`spike/probe_server.py`). Frontmatter is read and written with
`ruamel.yaml` (0.19.1), because round-tripping must preserve unknown keys, key order and
comments (OKF §4.1; FRAMEWORK §8.0.1); PyYAML drops comments.

## Amendments
