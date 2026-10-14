# context-engine

LIVING. The record engine for agent-built repos. It is one tool that owns every component made of
id'd records: tasks, owner questions, batons, pause records, ledger entries, decisions and stories.
It stores them as [OKF](https://github.com/GoogleCloudPlatform/open-knowledge-format) markdown
files and exposes them through a CLI and an optional per-session MCP server, which Claude Code
starts itself. It also lints a repo's records, routes and docs against the framework's guards.

The design is [`docs/framework/FRAMEWORK.md`](docs/framework/FRAMEWORK.md) (§8.0 is the engine).

**Status: alpha, no release tag yet.** The engine runs this repo's own records, and the gate and
CI were green on `main` at `8990dd0` (2026-10-13). It has not yet been adopted in a second repo; that trial is next on the
board. The no-model housekeeping script is not built yet (`context-engine task show CE-6`).

**To use it in a repo:** follow the adoption kit's guide,
[`src/context_engine/kit/README.md`](src/context_engine/kit/README.md). It covers installing the
engine into its own pinned environment, `.context-engine/env/` inside the target repo (gitignored,
never the target repo's own environment), pinning it to a commit, `context-engine init`,
bootstrapping by hand, and upgrading. Every operation also has a by-hand fallback in
[`docs/runbooks/manual-mode.md`](docs/runbooks/manual-mode.md).

**To work on it:** read [`CLAUDE.md`](CLAUDE.md) (the rules and the gate) and
[`HANDOFF.md`](HANDOFF.md) (what is true now). The board is `context-engine task list`.
