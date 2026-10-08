# context-engine

The record engine for agent-built repos: one tool that owns every component that is a set of
id'd records (tasks, owner questions, batons, pause blocks, ledger entries, decisions), stores
them as [OKF](https://github.com/GoogleCloudPlatform/open-knowledge-format) markdown files, and
exposes them through a CLI, a per-session MCP server, and a no-model housekeeping script.

The design is [`docs/framework/FRAMEWORK.md`](docs/framework/FRAMEWORK.md) (§8.0 is the engine).
Status: pre-alpha. Nothing here is usable yet.
