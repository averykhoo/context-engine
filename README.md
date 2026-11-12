# context-engine

LIVING. The record engine for agent-built repos. It is one tool that owns every component made of
id'd records: tasks, owner questions, batons, pause records, ledger entries, decisions and stories.
It stores them as [OKF](https://github.com/GoogleCloudPlatform/open-knowledge-format) markdown
files and exposes them through a CLI and an optional per-session MCP server, which Claude Code
starts itself. It also lints a repo's records, routes and docs against the framework's guards.

The design is [`docs/framework/FRAMEWORK.md`](docs/framework/FRAMEWORK.md) (§8.0 is the engine).

**To read the records without the CLI:** <https://averykhoo.github.io/context-engine/>. The
decisions (grouped by status and tag), the stories, the board, the framework's build status and
the residual-risk register, each record on its own page. CI builds it from the records on every
push to `main` with `context-engine site build` (`.github/workflows/pages.yml`); nothing it shows
is stored in the repo, so there is no index file to keep current.

**Status: alpha, no release tag yet.** The engine runs this repo's own records and is in use in a
few other repos; CI runs the gate on every push to `main`. What is built and what is next is the
board, on the records site above.

**To use it in a repo:** follow the adoption kit's guide,
[`src/context_engine/kit/README.md`](src/context_engine/kit/README.md). It covers installing the
engine into its own pinned environment, `.context-engine/env/` inside the target repo (gitignored,
never the target repo's own environment), pinning it to a commit, `context-engine init`,
bootstrapping by hand, and upgrading. Every operation also has a by-hand fallback in
[`docs/runbooks/manual-mode.md`](docs/runbooks/manual-mode.md).

**To work on it:** read [`CLAUDE.md`](CLAUDE.md) (the rules and the gate) and
[`HANDOFF.md`](HANDOFF.md) (what is true now). The board is `context-engine task list`.
