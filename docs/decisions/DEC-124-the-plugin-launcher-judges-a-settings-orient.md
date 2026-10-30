---
type: Decision
id: DEC-124
title: The plugin launcher judges a settings orient hook stale by its program and --root, not by running it
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:7424e8c22073355785db350f72236c6f7c6135c1263932af88eabba6dec42f78
---

PROVISIONAL decision (actor claude-code/claude-opus-5-5), for CE-146.

**Options.**

- (a) Check that the settings hook's program exists and that its `--root` is this repo. **Chosen.**
- (b) Defer only to `.claude/settings.local.json` and ignore the committed `settings.json`. Rejected: a local file can be stale too (a moved repo, a rebuilt interpreter).
- (c) Parse the settings with the engine's python. Rejected: the hook's interpreter need not be the plugin's `.context-engine` one, and with no engine there the check could not run.
- (d) Run the settings hook's command to see whether it works. Rejected: orient would run twice.

**Why (a).** It needs only POSIX sh plus awk, with no new dependency, and it catches the reported case (another machine's path). A bare program name counts as good when `command -v` finds it, as the hook's shell would. A program or `--root` that names a variable (`$` or `%`, e.g. `--root "$CLAUDE_PROJECT_DIR"`, the portable committed form) or starts with `~` is not judged and is trusted, because the hook's shell expands it and the launcher cannot (review fix 4da8788, on main dcbcef3).

**Cost to undo.** Cheap: one launcher block in `plugin/scripts/ce-engine`.
