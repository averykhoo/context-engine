# Design: procedures as skills, and the context-engine Claude Code plugin (CE-77)

FROZEN 2026-10-16 (session 2026-10-16a): CE-77 closed; below, the design as it stood (its CE-7
mention is in passing, not a plan for it)

ACTIVE-PLAN while CE-77 is open; freeze it when CE-77 closes.

Session 2026-10-14g. What Claude Code does with skills, plugins, plugin hooks and plugin MCP servers
is in `claude-code-plugins-2026-10-14.md` (read 2026-10-14). The adhoc trial (CE-7) has produced no
data yet, so each call below is the agent's, with its reason, for the owner to confirm or overturn.

## What was built

- `.claude-plugin/marketplace.json` at the engine repo's root: the repo is a marketplace named
  `context-engine` with one plugin, `context-engine`, at `./plugin`.
- `plugin/.claude-plugin/plugin.json` (name and metadata only), `plugin/hooks/hooks.json` (the
  `SessionStart` hook), `plugin/.mcp.json` (the server `engine`), `plugin/scripts/ce-engine` (the
  launcher both run), and nine skills under `plugin/skills/`.
- `init --skip-settings` now also means "write no hook" when there is no settings file.
- Kit README § Hook and § Claude Code plugin (install, and the by-hand fallback), FRAMEWORK §7.5,
  §10 and §11.2, the procedures runbook's preamble, manual-mode's `init` step.
- `tests/test_plugin.py`: the guards listed at the end.

## Decisions

1. **One skill per procedure, not one umbrella.** A skill is chosen by its description, and each
   procedure starts at its own moment (the owner gives intent; the work is done; a stop is
   forced; a push is asked for). One umbrella description would have to name every moment and would
   load every procedure's text at each. Nine short descriptions cost about 3 KB of context, always.
   Session start is not a skill: the hook and the contract carry it.
2. **Skills point at runbook sections; they copy no steps.** Each SKILL.md has `Runbook: <path> §
   <heading>` lines and a few lines on what sessions miss there, nothing more. A copy would be a
   second text to keep byte-equal (CE-26) and could disagree with the runbook the repo is pinned to;
   a pointer reads the repo's own copy. A test checks every pointer names a heading that exists in
   the kit, and that every procedure in the runbook but session start has a skill.
3. **The contract is not a skill** (CE-77 out of scope): it stays in the `CLAUDE.md` import and the
   hook. A skill that does not trigger fails silently.
4. **Each repo's pinned engine, through one launcher started by `git`.** The hook and the server
   must run the repo's own engine (CE-7 trap F18, DEC-41), so neither can name one interpreter
   path. Exec form on Windows needs a real `.exe` (a `.cmd` or script cannot be spawned), the
   interpreter's place differs by OS and env kind, and the `${VAR:-default}` form cannot nest. So
   both run `git -c alias.ce-run=!sh ce-run <launcher> <project dir> <mode>`: `git` is a real
   executable on the PATH of every machine that runs the framework (the engine needs it), and git
   runs a `!` alias with the `sh` it ships, on Windows too. The launcher (POSIX sh, LF endings kept
   by `.gitattributes`) unsets the `GIT_DIR` git exports into an alias from a linked worktree, then
   takes the interpreter from `.context-engine/engine-python` (one line: for an engine env kept
   elsewhere, such as this
   repo's editable one) or from `.context-engine/env/` in its three layouts: `bin/python` (posix
   venv or conda), `python.exe` (Windows `conda -p`, adhoc's), `Scripts/python.exe` (Windows venv).
   Rejected: a per-OS manifest (one file serves every OS); a shell-form hook (Git Bash is not
   always there, and PowerShell needs other quoting); a copied launcher in the repo (a step per
   clone, and it cannot serve the MCP entry on Windows).
5. **Failure is loud where it can be.** No interpreter: the hook prints why on stdout, so it reaches
   the session's context (a failing `SessionStart` hook only shows the user its error), and exits 0;
   the server writes it to stderr and exits 1. No `context.toml`: the hook prints nothing, so a
   plugin enabled in a repo the framework does not run costs nothing.
6. **Orient never runs twice.** Claude Code runs a plugin's hook and a settings file's hook both,
   even when they are the same. init keeps writing its hook (the engine runs without the plugin,
   DEC-1, DEC-20, DEC-32), and the launcher stays quiet when the repo's `.claude/settings.local.json`
   or `.claude/settings.json` already has a hook `command` running the engine's orient. A repo
   that takes the plugin runs `init --skip-settings`, which now writes no hook.
7. **The server's name is `engine`**, so its tools are `mcp__plugin_context-engine_engine__<op>`.
   Claude Code does not merge it with a local-scope `context-engine` registration (another
   command), so a repo moving to the plugin removes that registration.
8. **No plugin `version`.** With none, every commit of the engine repo is a new plugin version;
   with one, a change that forgets to bump it never reaches anyone. The plugin holds pointers and
   a launcher that defer to each repo's pinned runbooks and engine, so following the repo's head
   is safe. `claude plugin validate` warns about it; that warning is expected.
9. **The plugin lives in the engine repo, outside the wheel**: Claude Code installs it from git
   (the marketplace), and `init` never copies it. By hand, its skills are copied into
   `.claude/skills/` (kit README § Claude Code plugin).

## Live probes (2026-10-14, Claude Code 2.1.280, Windows 11)

In a throwaway repo made by `init`, with `.context-engine/engine-python` naming the engine
interpreter, `claude -p --plugin-dir <engine repo>/plugin`:
- the hook ran in exec form through `git`, and `# orient (no session)` reached the context;
- all nine skills were listed as `context-engine:<name>`;
- the server `plugin:context-engine:engine` was listed, then timed out connecting (30000 ms). The
  launcher is not the cause: an MCP stdio client took 36.5 s to initialize the server started
  directly and 33.0 s through the launcher (46 tools both), while the gate ran on the same laptop.
  Server start-up under load against Claude Code's connect timeout is an open finding; it applies
  to the local-scope registration too.
- re-run with `MCP_TIMEOUT=180000`: the session loaded `mcp__plugin_context-engine_engine__orient`
  after a wait and its result began `# orient (no session)`, so the plugin's server works end to
  end through the launcher.

## Guards (`tests/test_plugin.py`)

The manifests are valid JSON of the documented shape and run a launcher that exists; the hook and
the server run exactly as the manifests say (placeholders filled in) through `git`, in a temp repo:
orient output, quiet without `context.toml`, quiet beside a settings hook, the missing-env message,
the server answering over stdio; the env layouts resolve; every skill's frontmatter is valid and
names its directory; every `Runbook:` pointer names a heading that exists; every procedure but
session start has a skill; the launcher keeps LF endings.

## Not done

- A Linux run of the launcher outside CI's own runs, and macOS at all.
- Live probes of `resume`, `/clear` and compaction with the plugin's hook (INV-31's probes).
- Whether a skill triggers when its moment comes: measured only by real sessions (CE-7's data).
