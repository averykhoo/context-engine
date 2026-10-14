# Claude Code skills, plugins, plugin hooks and plugin MCP servers, as read for CE-77

FROZEN 2026-10-14g: provenance, as written. The design built on it is `plugin-design-2026-10-14.md`.

Read 2026-10-14 (session 2026-10-14g) from the official docs with WebFetch, which answers through a
summarising model: each line is a short quote or a close paraphrase of what that returned, with its
page. Claude Code on this machine was 2.1.280. READ means stated in the docs; PROBED means run here;
NOT FOUND means the docs are silent.

## Skills (https://code.claude.com/docs/en/skills)

- READ: a skill is `.claude/skills/<skill-name>/SKILL.md`, YAML frontmatter between `---` markers,
  then markdown. "Claude Code reads the frontmatter only when the opening `---` is the file's first
  line."
- READ: every field is optional; `description` is recommended ("Claude uses this to decide when to
  apply the skill"); `name` "Defaults to the directory name". "Claude Code ignores a field it doesn't
  recognize without reporting an error", so a typo in a field name is silent.
- READ: "The combined `description` and `when_to_use` text is truncated at 1,536 characters in the
  skill listing". Descriptions are always in context; "a skill's body loads only when it's used".
- READ: other fields include `when_to_use`, `disable-model-invocation`, `user-invocable`,
  `allowed-tools`, `argument-hint`, `paths`, `context: fork`, `metadata`, `license`, `compatibility`.
- READ: plugin skills live at `<plugin>/skills/<name>/SKILL.md` and are invoked as
  `/<plugin>:<name>`; "The bare `/fancy` also invokes the skill unless another command already uses
  that name."
- READ: in skill content, `${CLAUDE_SKILL_DIR}`, `${CLAUDE_PLUGIN_ROOT}` (plugin skills only) and
  `${CLAUDE_PROJECT_DIR}` are substituted.

## Plugin manifest and layout (https://code.claude.com/docs/en/plugins-reference)

- READ: the manifest is `.claude-plugin/plugin.json`, and it is optional; "`name` is the only
  required key", kebab-case, no spaces, `@`, `:` or path separators; names starting `claude-` or
  `anthropic-` are refused. "Every component is namespaced under it."
- READ: default locations: `skills/`, `hooks/hooks.json`, `.mcp.json` at the plugin root; "Put every
  other plugin file at the plugin root, not inside `.claude-plugin/`". Component paths in the manifest
  start with `./` and must stay inside the plugin root.
- READ: `version` "Setting it keeps users on that version until you change it".
- READ: `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}` and `${CLAUDE_PROJECT_DIR}` resolve "Anywhere
  in `command` and `args`" of hook commands, and in `command`, `args`, `env` of MCP stdio servers.
  "On Windows, the substituted paths use forward slashes". "The variables aren't present in the
  environment of commands Claude runs through the Bash tool".
- READ: a hooks file wraps the event map in a top-level `"hooks"` key; "A file that contains only the
  event map, without that wrapper, fails to load."
- READ: "A `CLAUDE.md` at the plugin root isn't loaded as context ... put them in a skill."
- READ: `claude plugin validate <dir>` is "the authoritative check for a manifest".

## Marketplace (https://code.claude.com/docs/en/plugins/marketplace-reference)

- READ: `.claude-plugin/marketplace.json` at the marketplace root, with required `name`, `owner`
  (`name` required) and `plugins` (each `name` and `source`); a relative `source` "Must start with
  `./`" and resolves from the marketplace root. A GitHub repo is added with
  `claude plugin marketplace add owner/repo`; a plugin id is `plugin@marketplace`.
- READ: `extraKnownMarketplaces` in settings declares a marketplace by a `source` object (`github`
  with `repo`, `git` with `url`, `directory` with `path`): "An `extraKnownMarketplaces` value is a
  map from marketplace name to an object with `source`". The settings reference page
  (https://code.claude.com/docs/en/settings-reference), read through the same summariser, gave it
  as a list of URLs instead; the kit README follows the marketplace reference's object form, and a
  live probe of a committed `.claude/settings.json` is owed. `enabledPlugins` maps a plugin id to
  `true` or `false`, in any settings file.

## Hooks (https://code.claude.com/docs/en/hooks)

- READ: "Exec form runs when `args` is present ... resolves `command` as an executable on `PATH` and
  spawns it directly ... There is no shell". "On Windows, exec form requires `command` to resolve to a
  real executable such as a `.exe`. The `.cmd` and `.bat` shims ... can't be spawned without a shell."
- READ: shell form runs under "`sh -c` on macOS and Linux, Git Bash on Windows, or PowerShell when
  Git Bash isn't installed"; the `shell` field picks `bash` or `powershell`.
- READ: "All matching hooks run in parallel. If you define the same handler in more than one settings
  file, it runs once. A plugin's or skill's copy of the same handler stays separate." So a plugin's
  orient hook and init's settings hook would both run.
- READ: SessionStart plain-text stdout is added to Claude's context; matchers `startup`, `resume`,
  `clear`, `compact`, `fork`. The `command` hook timeout defaults to 600 s.

## MCP (https://code.claude.com/docs/en/mcp)

- READ: a plugin's servers are in `.mcp.json` at the plugin root or inline in `plugin.json`; their
  tools are named `mcp__plugin_<plugin-name>_<server-name>__<tool-name>`, and the server registers
  as `plugin:<plugin-name>:<server-name>`.
- READ: a plugin's stdio server starts with "The plugin's root directory" as its working directory.
- READ: precedence on a name clash: local, project, user, then plugin servers; "For plugins and
  connectors, it matches by endpoint (URL or command)". A plugin server running another command than
  a local-scope registration is a second server, not a duplicate.
- READ: an unset `${VAR}` with no default loads as the literal text, with a warning in
  `claude mcp list`.
- NOT FOUND: any Windows note on how a stdio `command` is spawned (whether a `.cmd` works), and
  whether a `${VAR:-default}` default may hold another `${...}`.

## Probes (PROBED, Git Bash on Windows 11, git 2.x, 2026-10-14)

- `git -c alias.ce-run=!sh ce-run <script> <a> <b>` runs `<script>` under the sh git ships, with
  `<a>` and `<b>` as its arguments; a path with spaces and a `$` survives, and stdin passes through.
- Inside a linked worktree (where `.git` is a file) git exports `GIT_DIR` into the alias; in a plain
  checkout it does not, though it still exports `GIT_PREFIX` and `GIT_CONFIG_PARAMETERS`; inside a
  repo either way it runs the alias from the top level.
