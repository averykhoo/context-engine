"""The Claude Code plugin (CE-77): procedures as skills that point at their runbook sections, and
the SessionStart hook and MCP server run with each repo's own pinned engine through one launcher
(docs/evidence/plugin-design-2026-10-14.md).

The hook and the server are run here exactly as the manifests say, placeholders filled in, so a
test that passes has run the plugin's own command line, not a copy of it."""

import asyncio
import json
import os
import re
import subprocess
import sys
import sysconfig
from pathlib import Path

import pytest
from mcp import Client, StdioServerParameters
from ruamel.yaml import YAML

import context_engine
from context_engine import bootstrap as B
from context_engine import ops

from conftest import _toml
from test_mcp import text
from test_working import CONFIG, LEDGER, NOTE

REPO = Path(__file__).resolve().parents[1]
PLUGIN = REPO / "plugin"
LAUNCHER = PLUGIN / "scripts" / "ce-engine"
KIT = REPO / "src" / "context_engine" / "kit"
SRC = os.path.dirname(os.path.dirname(context_engine.__file__))  # the code under test, not an install
# Where a skill's `Runbook:` path is read in the engine repo: a target repo's runbooks are copies
# of the kit's, and the kit README is the installed engine's.
POINTER_ROOTS = {"docs/runbooks/": KIT / "docs" / "runbooks", "kit/": KIT}
RUNBOOK_RE = re.compile(r"^Runbook: `(?P<path>[^`]+)` § (?P<section>.+?)\s*$", re.MULTILINE)
# Frontmatter keys Claude Code reads in a SKILL.md (docs/evidence/claude-code-plugins-2026-10-14.md);
# it ignores any other silently, so a typo would pass unnoticed without this list.
SKILL_KEYS = {"name", "description", "when_to_use", "argument-hint", "arguments", "disable-model-invocation", "user-invocable", "allowed-tools", "disallowed-tools", "model", "effort", "context", "agent", "background", "hooks", "paths", "shell", "metadata", "license", "compatibility"}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
# procedures.md sections that are not a procedure a skill starts: the map, and session start (the
# hook and the contract carry it; a skill that does not trigger would fail silently)
NOT_SKILLS = ("Where each part of FRAMEWORK §6 is done", "Session start")


def _json(rel: str) -> dict:
    return json.loads((REPO / rel).read_text(encoding="utf-8"))


def _hook() -> dict:
    (entry,) = _json("plugin/hooks/hooks.json")["hooks"]["SessionStart"]
    (hook,) = entry["hooks"]
    return hook


def _server() -> dict:
    return _json("plugin/.mcp.json")["mcpServers"]["engine"]


def _argv(entry: dict, project: Path) -> list[str]:
    """The entry's command line as Claude Code runs it: the plugin's placeholders filled in, with
    forward slashes as Claude Code substitutes them on Windows; any other `${...}` is an error."""
    fill = {"${CLAUDE_PLUGIN_ROOT}": PLUGIN.as_posix(), "${CLAUDE_PROJECT_DIR}": project.as_posix()}
    out = []
    for a in [entry["command"], *entry["args"]]:
        for k, v in fill.items():
            a = a.replace(k, v)
        assert "${" not in a, f"an unfilled placeholder in {a!r}"
        out.append(a)
    return out


def _env(**extra: str) -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CE_", "GIT_DIR", "GIT_WORK_TREE"))}
    env["PYTHONPATH"] = SRC
    return {**env, **extra}


def _run(argv: list[str], cwd: Path, **extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(argv, cwd=cwd, env=_env(**extra), capture_output=True, timeout=300)


def _framework_repo(path: Path, python: str | None = sys.executable) -> Path:
    """A repo the engine runs, with `.context-engine/engine-python` naming `python` (none: no
    engine at all)."""
    path.mkdir(parents=True, exist_ok=True)
    (path / "context.toml").write_text(_toml(CONFIG), encoding="utf-8")
    (path / "ledger.md").write_text(LEDGER, encoding="utf-8")
    (path / "HANDOFF.md").write_text(NOTE.format(key="2026-10-07b"), encoding="utf-8")
    if python:
        (path / ".context-engine").mkdir(exist_ok=True)
        (path / ".context-engine" / "engine-python").write_text(python + "\n", encoding="utf-8")
    return path


def _out(p: subprocess.CompletedProcess) -> str:
    return p.stdout.decode("utf-8", "replace")


# -- the manifests ----------------------------------------------------------------------------


def test_the_marketplace_and_the_plugin_manifest_name_one_plugin_that_exists():
    market = _json(".claude-plugin/marketplace.json")
    assert market["name"] == "context-engine" and market["owner"]["name"]
    (entry,) = market["plugins"]
    assert entry["source"].startswith("./") and (REPO / entry["source"] / ".claude-plugin" / "plugin.json").is_file()
    manifest = _json("plugin/.claude-plugin/plugin.json")
    assert manifest["name"] == entry["name"] == "context-engine" and NAME_RE.match(manifest["name"])
    assert not (PLUGIN / ".claude-plugin" / "hooks").exists(), "only plugin.json goes in .claude-plugin/"


@pytest.mark.parametrize("entry, mode", [(_hook, "orient"), (_server, "mcp")], ids=["hook", "mcp"])
def test_the_hook_and_the_server_run_the_launcher_through_git_in_exec_form(entry, mode, tmp_path):
    """Exec form (`args` present): on Windows only a real executable can be spawned, and `git` is
    one on every machine the framework runs on; it runs the launcher with its own sh."""
    e = entry()
    if mode == "orient":
        assert e["type"] == "command" and "shell" not in e
    argv = _argv(e, tmp_path)
    assert argv[:4] == ["git", "-c", "alias.ce-run=!sh", "ce-run"]
    assert Path(argv[4]) == LAUNCHER and LAUNCHER.is_file()
    assert argv[5:] == [tmp_path.as_posix(), mode]


def test_the_launcher_keeps_lf_line_endings_on_every_checkout():
    """sh reads a CR as part of the word, so a CRLF checkout (core.autocrlf on Windows) would break
    every line: .gitattributes pins LF, and the file in the tree has no CR."""
    attr = subprocess.run(["git", "check-attr", "eol", "--", "plugin/scripts/ce-engine"], cwd=REPO, capture_output=True, text=True, check=True)
    assert attr.stdout.strip().endswith("eol: lf"), attr.stdout
    assert b"\r" not in LAUNCHER.read_bytes()


# -- the hook ---------------------------------------------------------------------------------


def test_the_hook_runs_orient_with_the_repos_engine(tmp_path):
    root = _framework_repo(tmp_path / "repo")
    p = _run(_argv(_hook(), root), cwd=tmp_path)
    assert p.returncode == 0, p.stderr
    out = _out(p)
    assert out.startswith("# orient") and "## Banner (2026-10-07b)" in out, out


def test_the_hook_does_nothing_where_the_framework_does_not_run(tmp_path):
    p = _run(_argv(_hook(), tmp_path), cwd=tmp_path)
    assert p.returncode == 0 and p.stdout == b"" and p.stderr == b"", p


def test_with_no_engine_the_hook_says_so_in_the_sessions_context(tmp_path):
    """stdout reaches the session's context; a failing SessionStart hook's stderr does not."""
    root = _framework_repo(tmp_path / "repo", python=None)
    p = _run(_argv(_hook(), root), cwd=tmp_path)
    out = _out(p)
    assert p.returncode == 0 and out.startswith("context-engine plugin: orient did not run: no engine env at "), p
    assert "Run orient by hand and tell the owner" in out and "kit README § 1" in out
    (root / ".context-engine").mkdir()
    (root / ".context-engine" / "engine-python").write_text((tmp_path / "gone" / "python").as_posix() + "\n", encoding="utf-8")
    out = _out(_run(_argv(_hook(), root), cwd=tmp_path))
    assert "engine-python names '" in out and "which is not a file" in out, out


def test_orient_never_runs_twice_beside_a_settings_hook(tmp_path):
    """Claude Code runs a plugin's hook and a settings file's both: the plugin's stays quiet when the
    repo's settings already run the engine's orient (init's hook), and only then."""
    root = _framework_repo(tmp_path / "repo")
    (root / ".claude").mkdir()
    settings = root / B.SETTINGS
    grant = {"permissions": {"allow": ["Bash(python -m context_engine orient)"]}}
    settings.write_text(json.dumps(grant), encoding="utf-8")
    assert _out(_run(_argv(_hook(), root), cwd=tmp_path)).startswith("# orient"), "a permission grant is not a hook"
    settings.write_text(B.hook_settings(root), encoding="utf-8")
    p = _run(_argv(_hook(), root), cwd=tmp_path)
    assert p.returncode == 0 and p.stdout == b"", p


def test_the_launcher_hands_the_engine_a_clean_git_environment(tmp_path):
    """Started from inside a linked worktree, git exports that worktree's GIT_DIR into an alias
    (a plain checkout does not) and runs it from the worktree's top level: the engine still sees
    no GIT_DIR, runs in the project, with the project as --root. A stand-in `context_engine`
    package on PYTHONPATH reports what it was given."""
    root = _framework_repo(tmp_path / "repo")
    main, other = tmp_path / "main", tmp_path / "other"
    main.mkdir()
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run([*git, "init", "-q"], cwd=main, check=True)
    subprocess.run([*git, "commit", "-q", "--allow-empty", "-m", "x"], cwd=main, check=True)
    subprocess.run([*git, "worktree", "add", "-q", str(other)], cwd=main, check=True)
    shim = tmp_path / "shim" / "context_engine"
    shim.mkdir(parents=True)
    (shim / "__init__.py").write_text("", encoding="utf-8")
    (shim / "__main__.py").write_text("import json, os, sys\nprint(json.dumps({'argv': sys.argv[1:], 'cwd': os.getcwd(), 'git_dir': os.environ.get('GIT_DIR'), 'exe': sys.executable}))\n", encoding="utf-8")
    p = subprocess.run(_argv(_hook(), root), cwd=other, env={**_env(), "PYTHONPATH": str(shim.parent)}, capture_output=True, timeout=300)
    seen = json.loads(_out(p))
    assert seen["git_dir"] is None, seen
    assert seen["argv"][-1] == "orient" and Path(seen["argv"][seen["argv"].index("--root") + 1]) == root
    assert Path(seen["cwd"]).resolve() == root.resolve()


def test_the_pinned_env_inside_the_repo_is_found_without_a_pointer(tmp_path):
    """DEC-41's layout: a venv at `.context-engine/env/` (`bin/python` on posix,
    `Scripts/python.exe` on Windows) runs, not the interpreter that started the test."""
    root = _framework_repo(tmp_path / "repo", python=None)
    env = root / ".context-engine" / "env"
    subprocess.run([sys.executable, "-m", "venv", "--without-pip", str(env)], check=True, timeout=300)
    # the engine's dependencies from the interpreter running the test (on CI a venv itself, whose
    # packages a child venv's --system-site-packages would not see)
    deps = dict.fromkeys(sysconfig.get_paths()[k] for k in ("purelib", "platlib"))
    p = _run(_argv(_hook(), root), cwd=tmp_path, PYTHONPATH=os.pathsep.join([SRC, *deps]))
    assert p.returncode == 0 and _out(p).startswith("# orient"), (p.stdout, p.stderr)
    shim = tmp_path / "shim" / "context_engine"
    shim.mkdir(parents=True)
    (shim / "__init__.py").write_text("", encoding="utf-8")
    (shim / "__main__.py").write_text("import sys\nprint(sys.prefix)\n", encoding="utf-8")
    p = subprocess.run(_argv(_hook(), root), cwd=tmp_path, env={**_env(), "PYTHONPATH": str(shim.parent)}, capture_output=True, timeout=300)
    assert Path(_out(p).strip()).resolve() == env.resolve(), (p.stdout, p.stderr)


# -- the MCP server ---------------------------------------------------------------------------


def test_the_plugins_mcp_entry_serves_the_repos_engine_over_stdio(tmp_path):
    root = _framework_repo(tmp_path / "repo")
    cmd, *args = _argv(_server(), root)
    params = StdioServerParameters(command=cmd, args=args, env=_env(), cwd=str(PLUGIN))  # a plugin's server starts in the plugin's root

    async def go():
        async with Client(params) as c:
            tools = {t.name for t in (await c.list_tools()).tools}
            out = text(await c.call_tool("orient", {}))
            return tools, out

    tools, out = asyncio.run(go())
    assert tools == set(ops.OPS)
    assert out.startswith("# orient") and "## Banner (2026-10-07b)" in out  # the project, not the plugin root


def test_with_no_engine_the_server_fails_saying_why(tmp_path):
    root = _framework_repo(tmp_path / "repo", python=None)
    p = _run(_argv(_server(), root), cwd=PLUGIN)
    assert p.returncode == 1 and p.stdout == b""
    assert p.stderr.decode().startswith("context-engine plugin: the MCP server did not start: no engine env at ")
    p = _run(_argv(_server(), tmp_path), cwd=PLUGIN)
    assert p.returncode == 1 and b"has no context.toml" in p.stderr


# -- the skills -------------------------------------------------------------------------------


def _skills() -> dict[str, str]:
    found = {p.parent.name: p.read_text(encoding="utf-8") for p in sorted((PLUGIN / "skills").glob("*/SKILL.md"))}
    assert found, "no skills found"
    return found


def _frontmatter(text: str) -> dict:
    assert text.startswith("---\n"), "Claude Code reads frontmatter only when `---` is the first line"
    head, _, _ = text[4:].partition("\n---\n")
    return YAML(typ="safe").load(head)


@pytest.mark.parametrize("name", sorted(p.parent.name for p in (PLUGIN / "skills").glob("*/SKILL.md")))
def test_every_skill_has_valid_frontmatter_naming_its_directory(name):
    meta = _frontmatter(_skills()[name])
    assert isinstance(meta, dict) and set(meta) <= SKILL_KEYS, set(meta) - SKILL_KEYS
    assert meta["name"] == name and NAME_RE.match(name) and len(name) <= 64
    d = meta["description"]
    assert isinstance(d, str) and 0 < len(d) <= 1024, len(d)  # the Agent Skills limit; Claude Code cuts the listing at 1536


def _headings(path: Path) -> set[str]:
    """Every level 2 or 3 heading of a markdown file, and the same without a trailing
    parenthesis (`Clean close (§6.3)` is also `Clean close`)."""
    out = set()
    for m in re.finditer(r"^#{2,3} (.+?)\s*$", path.read_text(encoding="utf-8"), re.MULTILINE):
        out.add(m[1])
        out.add(re.sub(r"\s*\([^()]*\)$", "", m[1]))
    return out


def _pointers() -> list[tuple[str, str, str]]:
    return [(name, m["path"], m["section"]) for name, text in _skills().items() for m in RUNBOOK_RE.finditer(text)]


def test_every_skill_points_at_runbook_sections_that_exist():
    """A skill holds no steps: it names the section that does. A renamed or removed heading
    turns this red, not a skill that sends a session nowhere."""
    pointed = {name for name, _, _ in _pointers()}
    assert pointed == set(_skills()), f"skills with no Runbook: line: {set(_skills()) - pointed}"
    for name, path, section in _pointers():
        base = next((POINTER_ROOTS[p] / path[len(p):] for p in POINTER_ROOTS if path.startswith(p)), None)
        assert base is not None and base.is_file(), f"{name}: {path} is not a kit file"
        assert section in _headings(base), f"{name}: {path} has no section {section!r}"


def test_every_procedure_but_session_start_has_a_skill():
    procedures = KIT / "docs" / "runbooks" / "procedures.md"
    sections = {re.sub(r"\s*\([^()]*\)$", "", m[1]) for m in re.finditer(r"^## (.+?)\s*$", procedures.read_text(encoding="utf-8"), re.MULTILINE)}
    wanted = sections - set(NOT_SKILLS)
    assert set(NOT_SKILLS) <= sections, "a section this test leaves out was renamed: update NOT_SKILLS"
    covered = {section for _, path, section in _pointers() if path == "docs/runbooks/procedures.md"}
    assert wanted <= covered, f"procedures with no skill: {sorted(wanted - covered)}"


def test_the_skills_copy_no_runbook_rows():
    """Pointers, not copies (CE-26): no skill carries a runbook table row."""
    for name, text in _skills().items():
        assert not re.search(r"^\|.*\|\s*$", text, re.MULTILINE), f"{name} holds a table"


def _flat(text: str) -> str:
    return " ".join(text.split())


def _section_text(path: Path, section: str) -> str:
    """The text under a heading `_headings` matches, up to the next heading of its level or above."""
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^(#{2,3}) (.+?)\s*$", line)
        if m and section in (m[2], re.sub(r"\s*\([^()]*\)$", "", m[2])):
            level = len(m[1])
            end = next((j for j in range(i + 1, len(lines)) if re.match(rf"^#{{1,{level}}} ", lines[j])), len(lines))
            return "\n".join(lines[i + 1:end])
    raise AssertionError(f"{path} has no section {section!r}")


def _bullets(text: str) -> list[str]:
    """Every list item of a skill, its indented continuation lines joined on."""
    out = []
    for line in text.splitlines():
        if line.startswith("- "):
            out.append(line[2:])
        elif out and line.startswith("  ") and line.strip():
            out[-1] += " " + line.strip()
        elif line.strip():
            out.append(None)  # a paragraph ends the item before it
    return [b for b in out if b is not None]


def test_every_line_a_skill_adds_is_quoted_word_for_word_from_its_sections():
    """Pointers, not copies (CE-26): a skill's list of what sessions miss is quotes, not a
    restatement, so a changed runbook row cannot leave a stale skill line under a green gate.
    Each item, whitespace aside, is one excerpt of a section the skill points at, or several
    joined by ` ... ` that occur in that order in one section."""
    for name, text in _skills().items():
        _, _, body = text[4:].partition("\n---\n")
        assert not re.search(r"^\s*[*+] |^\s+- ", body, re.MULTILINE), f"{name}: a list item this test does not read"
        items = _bullets(body)
        assert items, f"{name} has no list: if that is meant, this test needs no quote check for it"
        sections = []
        for _, path, section in (p for p in _pointers() if p[0] == name):
            base = next(POINTER_ROOTS[p] / path[len(p):] for p in POINTER_ROOTS if path.startswith(p))
            sections.append(_flat(_section_text(base, section)))
        for item in items:
            fragments = [_flat(f) for f in item.split(" ... ")]

            def in_order(sec: str) -> bool:
                at = 0
                for f in fragments:
                    at = sec.find(f, at)
                    if at < 0:
                        return False
                    at += len(f)
                return True

            assert any(in_order(s) for s in sections), f"{name}: not word for word in its sections: {item!r}"


# -- init beside the plugin -------------------------------------------------------------------


def test_skip_settings_writes_no_hook_when_there_is_no_settings_file(tmp_path):
    """With the plugin carrying the hook, `init --skip-settings` must not write a second one."""
    out = B.init(tmp_path, skip_settings=True)
    assert not (tmp_path / B.SETTINGS).exists() and not (tmp_path / B.SETTINGS_IGNORE).exists()
    assert f"{B.SETTINGS} ({B.SKIP_ABSENT})" in out, out
    assert (tmp_path / "context.toml").is_file()
