"""The adoption kit and ``init`` (CE-15, FRAMEWORK §6.9, §10, §11): a repo gets the framework as
text, ``init`` only creates, the kit's config template is the config's schema, and neither the kit
nor FRAMEWORK carries this repo's ids or paths."""

import dataclasses
import re
import tomllib
from pathlib import Path

import pytest

from context_engine import __version__
from context_engine import bootstrap as B
from context_engine import config as C
from context_engine import gate as GATE
from context_engine import guards as G
from context_engine.errors import Refusal
from context_engine.ledger import EMPTY_LEDGER

REPO = Path(__file__).resolve().parents[1]
FRAMEWORK = REPO / "docs" / "framework" / "FRAMEWORK.md"


def snapshot(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


# -- init only creates ---------------------------------------------------------------------


@pytest.mark.criterion("AC-31")
def test_init_never_overwrites_and_a_second_run_is_a_no_op(tmp_path):
    (tmp_path / "docs").mkdir()
    charter = "# Our charter\n\nkept as it is\n".encode()
    (tmp_path / "docs" / "charter.md").write_bytes(charter)
    claude = b"# Our contract\r\n\r\nexisting rules\r\n"
    (tmp_path / "CLAUDE.md").write_bytes(claude)

    out = B.init(tmp_path)
    assert "\n" not in out and out.startswith("init: created")
    assert (tmp_path / "docs" / "charter.md").read_bytes() == charter
    new = (tmp_path / "CLAUDE.md").read_bytes()
    assert new.startswith(claude) and B.BEGIN.encode() in new and B.END.encode() in new
    assert b"\n" not in new.replace(b"\r\n", b"")  # the appended block keeps the file's CRLF
    assert "skipped 1 (docs/charter.md)" in out
    assert (tmp_path / "docs" / "ledger" / "session-log.md").read_text(encoding="utf-8") == EMPTY_LEDGER

    before = snapshot(tmp_path)
    again = B.init(tmp_path)
    assert again.startswith("init: created 0 (none)"), again
    assert snapshot(tmp_path) == before


@pytest.mark.criterion("AC-31")
def test_init_dry_run_writes_nothing(tmp_path):
    out = B.init(tmp_path, dry_run=True)
    assert out.startswith("init (dry run): would create") and "context.toml" in out
    assert list(tmp_path.iterdir()) == []


def _plan_then(monkeypatch, act):
    """Run ``act`` after init's plan and before its writes: another writer in that window."""
    real = B.plan

    def plan(root, prefixes=None, settings=""):
        out = real(root, prefixes, settings)
        act(Path(root))
        return out

    monkeypatch.setattr(B, "plan", plan)


@pytest.mark.criterion("AC-31")
def test_init_refuses_a_file_created_after_its_plan_and_leaves_it_as_it_is(tmp_path, monkeypatch):
    theirs = b"# their charter, written mid-run\n"
    _plan_then(monkeypatch, lambda root: (root / "docs").mkdir() or (root / "docs" / "charter.md").write_bytes(theirs))
    with pytest.raises(Refusal, match=r"docs/charter.md appeared while init ran") as e:
        B.init(tmp_path)
    assert (tmp_path / "docs" / "charter.md").read_bytes() == theirs
    assert "run init again" in e.value.remedy


@pytest.mark.criterion("AC-31")
def test_init_refuses_a_claude_md_edited_after_its_plan_and_leaves_the_edit(tmp_path, monkeypatch):
    (tmp_path / "CLAUDE.md").write_bytes(b"# Ours\n")
    edited = b"# Ours\n\nan edit made while init ran\n"
    _plan_then(monkeypatch, lambda root: (root / "CLAUDE.md").write_bytes(edited))
    with pytest.raises(Refusal, match=r"CLAUDE.md changed while init ran"):
        B.init(tmp_path)
    assert (tmp_path / "CLAUDE.md").read_bytes() == edited


@pytest.mark.criterion("AC-31")
@pytest.mark.parametrize("old,sep",[("rules", "\n\n"), ("rules\n", "\n"), ("rules\n\n", ""), ("", "")])
def test_the_contract_block_starts_on_its_own_line_after_a_blank_one(tmp_path, old, sep):
    (tmp_path / "CLAUDE.md").write_bytes(old.encode())
    B.init(tmp_path)
    assert (tmp_path / "CLAUDE.md").read_text(encoding="utf-8") == old + sep + (B.KIT / B.BOOTLOADER).read_text(encoding="utf-8")


@pytest.mark.criterion("AC-31")
def test_an_older_kit_block_is_never_doubled(tmp_path):
    old = "# Ours\n\n<!-- context-engine kit 0.4 begin -->\nframework: 0.4\n<!-- context-engine kit 0.4 end -->\n"
    (tmp_path / "CLAUDE.md").write_text(old, encoding="utf-8")
    out = B.init(tmp_path)
    assert (tmp_path / "CLAUDE.md").read_text(encoding="utf-8") == old
    assert "CLAUDE.md (holds the kit 0.4 block: replace it" in out, out


GATES = re.compile(r"^#{1,6}[ \t]+Gate\b", re.MULTILINE | re.IGNORECASE)
NO_STUB = "CLAUDE.md (kit block appended without the Gate stub: it has its own "
NUDGE = ": make it end with `&& context-engine lint`)"


@pytest.mark.criterion("AC-31")
@pytest.mark.parametrize("gate, heading, lint", [
    ("## Gate\n\n`pytest -q`, from the repo root.\n", "## Gate", True),
    ("# gate: tests\n\n`make test && context-engine lint`\n", "# gate: tests", False),
    ("## Gate (CI runs the same)\r\n\r\n`pytest -q`\r\n", "## Gate (CI runs the same)", True),
    ("Run `context-engine lint` now and then.\n\n## Gate\n\n`pytest -q`\n\n## Rules\n\n`context-engine lint` again\n", "## Gate", True),
    ("## Gate\n\n`pytest -q && python -m context_engine lint`\n", "## Gate", False),
    ("```\ncode\n```\n\n## Gate\n\n`pytest -q`\n", "## Gate", True),
])
def test_a_claude_md_with_its_own_gate_gets_the_kit_block_without_a_second_gate(tmp_path, gate, heading, lint):
    """CE-51: the repo's Gate stays the only Gate; init says it left the stub out, quoting the
    heading it took for the gate, and asks for `context-engine lint` when that Gate section (not
    the file) lacks it; the next: line asks for a check of that gate."""
    old = f"# Ours\n\n{gate}"
    old = old.replace("\r\n", "\n").replace("\n", "\r\n") if "\r\n" in gate else old
    (tmp_path / "CLAUDE.md").write_bytes(old.encode())
    out = B.init(tmp_path)
    new = (tmp_path / "CLAUDE.md").read_bytes().decode()
    assert new.startswith(old) and len(GATES.findall(new)) == 1, new
    assert B.kit_block(new)[1] == B.bootloader_body() and new.rstrip().endswith(B.END), "the whole kit block, and nothing after it"
    assert B.GATE_PLACEHOLDER not in new and B.GATE_PLACEHOLDER not in out, out
    assert f'{NO_STUB}"{heading}"' + (NUDGE if lint else ")") in out, out
    assert "check CLAUDE.md § Gate runs the repo's tests and ends with `&& context-engine lint`" in out.split("; next: ")[1], out
    assert ("\n" not in new.replace("\r\n", "")) if "\r\n" in old else ("\r" not in new), "the file's line endings are kept"
    assert B.init(tmp_path).startswith("init: created 0"), "a re-run finds the kit block"


@pytest.mark.criterion("AC-31")
@pytest.mark.parametrize("text", [
    "```markdown\n## Gate\n\nan example\n```\n",
    "~~~~\n## Gate\n~~~\nstill in the fence\n~~~~\n",
    "  ```\n## Gate\n  ```\n",
    "<!--\n## Gate\n-->\n",
    "```\nnever closed\n\n## Gate\n",
    "## Deploy\n\n### Gate\n\nmanual approval by ops\n",
    "## Gateway\n\n## Gate-keeping rules\n\n## Gates\n",
])
def test_a_gate_heading_that_is_not_the_repos_gate_leaves_the_stub_in(tmp_path, text):
    """CE-51: a Gate heading in a code fence or an HTML comment is text, and `### Gate` under
    another section or `## Gate-keeping` is not the repo's gate: the stub still goes in, and the
    next: line asks for the test command."""
    old = f"# Ours\n\n{text}"
    (tmp_path / "CLAUDE.md").write_text(old, encoding="utf-8")
    out = B.init(tmp_path)
    assert (tmp_path / "CLAUDE.md").read_text(encoding="utf-8") == old + "\n" + (B.KIT / B.BOOTLOADER).read_text(encoding="utf-8")
    assert NO_STUB not in out and f"replace `{B.GATE_PLACEHOLDER}`" in out, out


@pytest.mark.criterion("AC-31")
def test_inits_next_line_names_the_bootstrap_steps_in_order_and_the_mcp_server_as_optional(tmp_path):
    """CE-70: the steps of kit README § 2a, in its order; the MCP server is optional, never a step."""
    out = B.init(tmp_path)
    nxt = out.split("; next: ")[1]
    steps = ["fill docs/charter.md", f"replace `{B.GATE_PLACEHOLDER}` in CLAUDE.md § Gate", "run lint", "commit the kit's files by path", "then `session start`"]
    assert [nxt.index(s) for s in steps] == sorted(nxt.index(s) for s in steps), nxt
    assert nxt.endswith("(registering the MCP server is optional: kit README § 1)") and "register the MCP server," not in nxt, nxt
    assert B.GATE_PLACEHOLDER in (B.KIT / B.BOOTLOADER).read_text(encoding="utf-8"), "the step names the stub's real placeholder"
    readme = (B.KIT / "README.md").read_text(encoding="utf-8")
    one = readme[readme.index("## 1. ") : readme.index("## 2a. ")]
    assert B.GATE_PLACEHOLDER in readme and "The MCP server is optional" in one, "the line's pointers name what is there"
    assert "; next: " not in B.init(tmp_path), "a re-run that creates nothing has no next steps"
    (tmp_path / "docs" / "charter.md").unlink()
    again = B.init(tmp_path)
    assert again.startswith("init: created 1 (docs/charter.md)") and "; next: " not in again, "a re-run that only fills a gap is no bootstrap"


@pytest.mark.criterion("AC-110")
def test_the_kit_readme_names_the_mcp_connect_timeout_and_its_remedy():
    """CE-85: a server that starts past Claude Code's 30 s connect limit shows no tools; the README says why and what to set."""
    readme = (B.KIT / "README.md").read_text(encoding="utf-8")
    one = readme[readme.index("## 1. ") : readme.index("## 2a. ")]
    reg = one[one.index("The MCP server is optional") :]
    assert "MCP_TIMEOUT" in reg and "30 seconds" in reg and "33 to 36 seconds" in reg, "the registration section must name the limit, the measured start and the remedy"


def _hook_command(root: Path) -> str:
    import json

    doc = json.loads((root / B.SETTINGS).read_text(encoding="utf-8"))
    [entry] = doc["hooks"]["SessionStart"]
    assert "matcher" not in entry, "no matcher: startup, resume, clear and compact all run it"
    [hook] = entry["hooks"]
    assert hook["type"] == "command"
    return hook["command"]


@pytest.mark.criterion("AC-57")
def test_init_writes_the_bootloader_the_contract_and_the_hook(tmp_path):
    import sys

    out = B.init(tmp_path)
    claude = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert claude == f"# {tmp_path.name}: contract\n\n" + (B.KIT / B.BOOTLOADER).read_text(encoding="utf-8")
    assert (tmp_path / B.CONTRACT_DEST).read_bytes() == (B.KIT / B.CONTRACT).read_bytes()
    cmd = _hook_command(tmp_path)
    assert cmd == f'"{Path(sys.executable).as_posix()}" -m context_engine --root "{tmp_path.resolve().as_posix()}" orient'
    assert (tmp_path / B.SETTINGS_IGNORE).read_text(encoding="utf-8") == "settings.local.json\n"
    for rel in (B.CONTRACT_DEST, B.SETTINGS, B.SETTINGS_IGNORE):
        assert rel in out.split("; skipped")[0], (rel, out)


@pytest.mark.criterion("AC-57")
def test_the_hook_command_runs_orient_through_a_shell(tmp_path):
    """The command as Claude Code runs it: a shell line, from another directory, with no CE_ env."""
    import os
    import subprocess

    B.init(tmp_path)
    _fill_gate(tmp_path)  # else orient opens with a Contract section for the Gate stub (CE-71)
    env = {k: v for k, v in os.environ.items() if not k.startswith("CE_")}
    r = subprocess.run(_hook_command(tmp_path), shell=True, capture_output=True, text=True, encoding="utf-8", cwd=tmp_path.parent, env=env, timeout=120)
    assert r.returncode == 0, r.stderr
    assert r.stdout.startswith("# orient (no session)") and "## Banner" in r.stdout and "Contract" not in r.stdout, r.stdout


@pytest.mark.criterion("AC-57")
def test_a_rerun_finds_its_own_hook_and_a_gitignore_that_misses_the_settings_file_is_named(tmp_path):
    B.init(tmp_path)
    again = B.init(tmp_path)
    assert again.startswith("init: created 0") and f"{B.SETTINGS} (holds the orient hook)," in again, again
    other = tmp_path / "other"
    (other / ".claude").mkdir(parents=True)
    (other / B.SETTINGS_IGNORE).write_bytes(b"agents.local/\n")
    out = B.init(other)
    assert (other / B.SETTINGS).exists() and (other / B.SETTINGS_IGNORE).read_bytes() == b"agents.local/\n"
    assert f"{B.SETTINGS_IGNORE} (it does not ignore settings.local.json" in out, out
    (other / B.SETTINGS_IGNORE).write_bytes(b"/agents.local/\r\nsettings.local.json\r\n")
    (other / B.SETTINGS).unlink()
    assert "does not ignore" not in B.init(other)
    assert f"{B.SETTINGS} (holds the orient hook)" in B.init(other, merge_settings=True), "a merge finds the hook already there"


# -- an existing settings file: the hook goes in only with the owner's yes (DEC-32) -----------

GRANTS = '{\n  "permissions": {\n    "allow": [\n      "Bash(git status)"\n    ],\n    "deny": []\n  },\n  "hooks": {\n    "PreToolUse": [\n      {\n        "matcher": "Bash",\n        "hooks": [\n          {\n            "type": "command",\n            "command": "echo pre"\n          }\n        ]\n      }\n    ]\n  },\n  "model": "opus \\u00e9"\n}\n'


def _settings(root: Path, text: str = GRANTS) -> Path:
    (root / ".claude").mkdir(exist_ok=True)
    p = root / B.SETTINGS
    p.write_bytes(text.encode())
    return p


@pytest.mark.criterion("AC-57")
def test_an_existing_settings_file_without_the_hook_refuses_showing_the_change_and_writes_nothing(tmp_path):
    import json

    p = _settings(tmp_path)
    with pytest.raises(Refusal) as e:
        B.init(tmp_path)
    assert e.value.message.startswith(f"{B.SETTINGS} exists, so the hook goes into it: init would append {json.dumps(B.hook_entry(tmp_path))} to hooks.SessionStart and change nothing else")
    assert "ask" in e.value.remedy and "--merge-settings" in e.value.remedy and "--skip-settings" in e.value.remedy
    assert p.read_bytes() == GRANTS.encode() and sorted(x.name for x in tmp_path.iterdir()) == [".claude"], "a refusal writes nothing at all"
    dry = B.init(tmp_path, dry_run=True)  # the owner sees the whole plan, and the question, before answering it
    assert dry.startswith("init (dry run): would create") and f"{B.SETTINGS} (exists without the orient hook)" in dry.split("; warning: ")[0], dry
    assert f"; warning: {B.SETTINGS} is the owner's call: init would append {json.dumps(B.hook_entry(tmp_path))} to hooks.SessionStart" in dry, dry
    too = f"change nothing else in it, and would write {B.SETTINGS_IGNORE} holding settings.local.json beside it (nothing ignores that file)"
    assert too in dry and too in e.value.message, "the question names everything a yes brings"
    assert "--merge-settings" in dry and "--skip-settings" in dry and "; next: " not in dry
    assert p.read_bytes() == GRANTS.encode() and sorted(x.name for x in tmp_path.iterdir()) == [".claude"], "a dry run writes nothing"
    out = B.init(tmp_path, skip_settings=True)
    assert p.read_bytes() == GRANTS.encode() and f"{B.SETTINGS} (--skip-settings: add the SessionStart hook by hand, kit README § Hook)" in out, out
    assert not (tmp_path / B.SETTINGS_IGNORE).exists(), "no ignore file for a settings file init did not write"
    assert "## Hook" in (B.KIT / "README.md").read_text(encoding="utf-8"), "the remedy names a section that exists"
    with pytest.raises(Refusal, match="contradict"):
        B.init(tmp_path, merge_settings=True, skip_settings=True)


@pytest.mark.criterion("AC-57")
@pytest.mark.parametrize("crlf", [False, True])
def test_merge_settings_adds_only_the_hook_keeping_every_key_and_its_order_and_is_idempotent(tmp_path, crlf):
    import json

    old = GRANTS.replace("\n", "\r\n") if crlf else GRANTS
    p = _settings(tmp_path, old)
    out = B.init(tmp_path, merge_settings=True)
    assert f"{B.SETTINGS} (the orient hook merged in)" in out.split("; skipped")[0], out
    new = p.read_bytes().decode()
    assert ("\n" not in new.replace("\r\n", "")) if crlf else ("\r" not in new), "the file's line endings are kept"
    before, after = json.loads(old), json.loads(new)
    assert list(after) == list(before) and list(after["hooks"]) == ["PreToolUse", "SessionStart"]
    assert after["hooks"]["SessionStart"] == [B.hook_entry(tmp_path)]
    after["hooks"].pop("SessionStart")
    assert after == before, "nothing else changed"
    assert "opus é" in new, "non-ASCII stays as it was written"
    assert not list((tmp_path / ".claude").glob("*.tmp")), "the atomic write leaves no temp file"
    again = B.init(tmp_path, merge_settings=True)
    assert p.read_bytes().decode() == new and f"{B.SETTINGS} (holds the orient hook)" in again, again
    assert f"{B.SETTINGS} (holds the orient hook)" in B.init(tmp_path), "with the hook there, no flag is needed"
    other = json.dumps({"hooks": {"SessionStart": [{"matcher": "clear", "hooks": [{"type": "command", "command": "echo hi"}]}]}})
    x = tmp_path / "x"
    x.mkdir()
    _settings(x, other)
    B.init(x, merge_settings=True)
    starts = json.loads((x / B.SETTINGS).read_text(encoding="utf-8"))["hooks"]["SessionStart"]
    assert starts == [json.loads(other)["hooks"]["SessionStart"][0], B.hook_entry(x)], "an existing SessionStart entry is kept, first"


@pytest.mark.criterion("AC-57")
@pytest.mark.parametrize("text, says", [
    ("{not json", "is not JSON init can merge into"),
    ('{"permissions": {"allow": ["A"]}, "permissions": {"allow": []}}', "the key 'permissions' appears twice"),
    ("[]", "is not shaped as init expects"),
    ('{"hooks": []}', "is not shaped as init expects (an object at the top level, an object at `hooks`"),
    ('{"hooks": {"SessionStart": {}}}', "a list at `hooks.SessionStart`"),
    ('{"n": NaN}', "NaN is not JSON"),  # Python's json reads it; a rewrite would hand Claude Code a file it cannot parse
    ('{"n": -Infinity}', "-Infinity is not JSON"),
    ('{"n": 1E400}', "1E400 overflows a float"),
    ('{"a": "' + chr(92) + 'ud800"}', "a lone surrogate escape"),
    ('{"disableAllHooks": true, "permissions": {}}', "sets disableAllHooks, so no hook would run"),
])
def test_merge_settings_refuses_what_it_cannot_merge_into_and_leaves_it_untouched(tmp_path, text, says):
    p = _settings(tmp_path, text)
    with pytest.raises(Refusal, match=re.escape(says)) as e:
        B.init(tmp_path, merge_settings=True)
    assert "left untouched" in e.value.message and "--skip-settings" in e.value.remedy
    assert p.read_bytes() == text.encode()
    p.write_bytes(b'{"a": "\xe9"}')
    with pytest.raises(Refusal, match="is not UTF-8"):
        B.init(tmp_path, merge_settings=True)


@pytest.mark.criterion("AC-57")
@pytest.mark.parametrize("matcher", [None, "compact"])
def test_an_orient_hook_with_another_command_is_never_taken_for_this_repos(tmp_path, matcher):
    import json

    gone = '"C:/gone/python.exe" -m context_engine --root "C:/elsewhere" orient'
    entry = {"hooks": [{"type": "command", "command": gone}]}
    if matcher:  # this repo's own command, but only on compaction
        entry = {"matcher": matcher, "hooks": [{"type": "command", "command": B.hook_entry(tmp_path)["hooks"][0]["command"]}]}
    text = json.dumps({"hooks": {"SessionStart": [entry]}})
    p = _settings(tmp_path, text)
    for flags in ({}, {"merge_settings": True}):
        with pytest.raises(Refusal, match="holds a SessionStart hook running the engine's orient with another command") as e:
            B.init(tmp_path, **flags)
        assert B.hook_entry(tmp_path)["hooks"][0]["command"] in e.value.remedy and "--skip-settings" in e.value.remedy
    assert p.read_bytes() == text.encode()


@pytest.mark.criterion("AC-57")
def test_merge_settings_refuses_a_hard_linked_or_read_only_file_before_writing_anything(tmp_path):
    import os
    import stat

    p = _settings(tmp_path)
    os.link(p, tmp_path / "twin.json")
    with pytest.raises(Refusal, match="is hard-linked, and replacing it would split the link"):
        B.init(tmp_path, merge_settings=True)
    assert sorted(x.name for x in tmp_path.iterdir()) == [".claude", "twin.json"], "refused at plan time: nothing written"
    (tmp_path / "twin.json").unlink()
    os.chmod(p, stat.S_IREAD)
    try:
        with pytest.raises(Refusal, match="is not writable"):
            B.init(tmp_path, merge_settings=True)
        assert p.read_bytes() == GRANTS.encode() and sorted(x.name for x in tmp_path.iterdir()) == [".claude"]
    finally:
        os.chmod(p, stat.S_IREAD | stat.S_IWRITE)


@pytest.mark.criterion("AC-31")
def test_a_hard_linked_claude_md_stays_linked(tmp_path):
    import os

    (tmp_path / "CLAUDE.md").write_bytes(b"# Ours\n")
    os.link(tmp_path / "CLAUDE.md", tmp_path / "AGENTS.md")
    B.init(tmp_path)
    assert B.BEGIN in (tmp_path / "AGENTS.md").read_text(encoding="utf-8"), "CLAUDE.md is written in place, never replaced"


@pytest.mark.criterion("AC-57")
def test_a_merge_names_a_gitignore_that_misses_the_settings_file_and_the_cli_refusal_is_utf8(tmp_path):
    import os
    import subprocess
    import sys

    _settings(tmp_path)
    (tmp_path / B.SETTINGS_IGNORE).write_bytes(b"agents.local/\n")
    assert f"{B.SETTINGS_IGNORE} (it does not ignore settings.local.json" in B.init(tmp_path, merge_settings=True)
    (tmp_path / B.SETTINGS).write_bytes(GRANTS.encode())
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONIOENCODING", "PYTHONUTF8") and not k.startswith("CE_")}
    r = subprocess.run([sys.executable, "-m", "context_engine", "--root", str(tmp_path), "init"], capture_output=True, env=env, timeout=120)
    assert r.returncode == 2 and "kit README § Hook" in r.stderr.decode("utf-8"), r.stderr


@pytest.mark.criterion("AC-57")
def test_a_merge_writes_the_missing_gitignore_and_every_rerun_repeats_a_gitignore_that_misses_the_line(tmp_path):
    """CE-70 (N2): the hook init merged in holds this machine's paths, so a missing
    .claude/.gitignore is written, as on a fresh init; one that misses the line is named on every
    run that finds the hook, not only the merging one."""
    _settings(tmp_path)
    out = B.init(tmp_path, merge_settings=True)
    assert (tmp_path / B.SETTINGS_IGNORE).read_bytes() == b"settings.local.json\n" and B.SETTINGS_IGNORE in out.split("; skipped")[0], out
    (tmp_path / B.SETTINGS_IGNORE).write_bytes(b"agents.local/\n")
    for flags in ({}, {"merge_settings": True}, {"skip_settings": True}):
        again = B.init(tmp_path, **flags)
        assert f"{B.SETTINGS} (holds the orient hook)" in again and f"{B.SETTINGS_IGNORE} (it does not ignore settings.local.json" in again, (flags, again)
    assert (tmp_path / B.SETTINGS_IGNORE).read_bytes() == b"agents.local/\n", "an existing ignore file is never edited"
    (tmp_path / B.SETTINGS_IGNORE).unlink()
    again = B.init(tmp_path)
    assert again.startswith("init: created 0") and f"; warning: {B.SETTINGS_IGNORE} is absent and nothing init reads ignores settings.local.json" in again, again
    assert f"{B.SETTINGS_IGNORE}" not in again.split("; warning: ")[0], "an absent file is not reported as skipped"
    assert not (tmp_path / B.SETTINGS_IGNORE).exists(), "only the run that writes the hook writes the ignore file"
    for line, ignored in ((".claude/settings.local.json", True), ("/.claude/", True), ("*.local.json", True), ("settings.json", False)):
        (tmp_path / ".gitignore").write_text(f"# ours\n{line}\n", encoding="utf-8")
        o = B.init(tmp_path)
        assert ("; warning: " not in o) is ignored, (line, o)
    for text, ignored in ((".claude/\n!.claude/settings.local.json\n", True),  # git cannot re-include under an excluded directory
                          (".claude/*\n!.claude/settings.json\n", True),  # the usual split: shared settings tracked, local ones not
                          (".claude/*\n!.claude/settings.local.json\n", False),  # the last match wins
                          ("*.json\n!settings.local.json\n", False)):
        (tmp_path / ".gitignore").write_text(text, encoding="utf-8")
        o = B.init(tmp_path)
        assert ("; warning: " not in o) is ignored, (text, o)
    (tmp_path / ".gitignore").write_text(".claude/*\n!.claude/settings.json\n", encoding="utf-8")
    (tmp_path / B.SETTINGS_IGNORE).write_text("settings.local.json\n", encoding="utf-8")
    assert "; warning: " not in B.init(tmp_path), "init never warns about the ignore file it wrote itself"
    (tmp_path / B.SETTINGS_IGNORE).write_text("settings.local.json\n!settings.local.json\n", encoding="utf-8")
    assert f"; warning: {B.SETTINGS_IGNORE} (it does not ignore" in B.init(tmp_path), "a deeper negation wins"
    (tmp_path / B.SETTINGS_IGNORE).unlink()
    (tmp_path / ".gitignore").unlink()
    (tmp_path / "x").mkdir()
    _settings(tmp_path / "x")
    (tmp_path / "x" / ".gitignore").write_text(".claude\n", encoding="utf-8")
    B.init(tmp_path / "x", merge_settings=True)
    assert not (tmp_path / "x" / B.SETTINGS_IGNORE).exists(), "a repo that ignores it already gets no second ignore file"


@pytest.mark.criterion("AC-57")
def test_skip_settings_says_the_hook_is_there_when_it_is_and_never_refuses(tmp_path):
    """CE-70 (N3): --skip-settings asks for the hook by hand only when it is missing, and a file
    init cannot read is the owner's to fix, never a refusal, under --skip-settings."""
    import json

    _settings(tmp_path)
    B.init(tmp_path, merge_settings=True)
    out = B.init(tmp_path, skip_settings=True)
    assert f"{B.SETTINGS} (holds the orient hook)" in out and "by hand" not in out, out
    by_hand = f"{B.SETTINGS} (--skip-settings: add the SessionStart hook by hand, kit README § Hook)"
    for text in (b"{not json", b'{"a": "\xe9"}', GRANTS.encode()):
        (tmp_path / B.SETTINGS).write_bytes(text)
        assert by_hand in B.init(tmp_path, skip_settings=True)
        assert (tmp_path / B.SETTINGS).read_bytes() == text
    hooked = json.loads(GRANTS)
    hooked["hooks"]["SessionStart"] = [B.hook_entry(tmp_path)]
    (tmp_path / B.SETTINGS).write_bytes(b"\xef\xbb\xbf" + json.dumps(hooked).encode())  # a BOM, as PowerShell 5.1 writes
    assert f"{B.SETTINGS} (holds the orient hook)" in B.init(tmp_path, skip_settings=True)
    (tmp_path / B.SETTINGS).write_text(json.dumps({**hooked, "disableAllHooks": True}), encoding="utf-8")
    out = B.init(tmp_path, skip_settings=True)
    assert f"{B.SETTINGS} (--skip-settings: it sets disableAllHooks, so no hook runs: run orient by hand at session start)" in out, out
    gone = '"C:/gone/python.exe" -m context_engine --root "C:/elsewhere" orient'
    hooked["hooks"]["SessionStart"] = [{"hooks": [{"type": "command", "command": gone}]}]
    (tmp_path / B.SETTINGS).write_text(json.dumps(hooked), encoding="utf-8")
    out = B.init(tmp_path, skip_settings=True)
    assert f"its orient hook runs another command ({gone}): have the owner replace it with {B.hook_entry(tmp_path)['hooks'][0]['command']})" in out, out
    (tmp_path / B.SETTINGS).unlink()
    (tmp_path / B.SETTINGS).mkdir()
    assert by_hand in B.init(tmp_path, skip_settings=True), "a settings path init cannot read is never a crash under --skip-settings"


@pytest.mark.criterion("AC-57")
def test_merge_settings_refuses_a_settings_file_changed_after_its_plan_and_keeps_that_change(tmp_path, monkeypatch):
    p = _settings(tmp_path)
    granted = GRANTS.replace('"Bash(git status)"', '"Bash(git status)", "Bash(ls)"')
    _plan_then(monkeypatch, lambda root: (root / B.SETTINGS).write_bytes(granted.encode()))
    with pytest.raises(Refusal, match=re.escape(f"{B.SETTINGS} changed while init ran, so nothing was written to it")):
        B.init(tmp_path, merge_settings=True)
    assert p.read_bytes() == granted.encode(), "the grant Claude Code wrote meanwhile is kept"
    assert not list((tmp_path / ".claude").glob("*.tmp"))


@pytest.mark.criterion("AC-57")
def test_an_inline_kit_block_is_left_for_the_upgrade_and_the_contract_still_lands(tmp_path):
    inline = f"# Ours\n\n{B.BEGIN}\nframework: 0.5\n\n### Gate\n\n`make test && context-engine lint`\n{B.END}\n"
    (tmp_path / "CLAUDE.md").write_text(inline, encoding="utf-8")
    out = B.init(tmp_path)
    assert (tmp_path / "CLAUDE.md").read_text(encoding="utf-8") == inline
    assert f"CLAUDE.md (holds a kit 0.5 block that inlines the rules: replace it with kit/{B.BOOTLOADER} by hand, kit README § Upgrade)" in out, out
    assert (tmp_path / B.CONTRACT_DEST).exists()
    assert "## 4. Upgrade" in (B.KIT / "README.md").read_text(encoding="utf-8")
    boot = tmp_path / "boot"
    boot.mkdir()
    kept = "# Ours\r\n\r\n" + (B.KIT / B.BOOTLOADER).read_text(encoding="utf-8").replace("\n", "\r\n")
    (boot / "CLAUDE.md").write_bytes(kept.encode())
    out = B.init(boot)
    assert (boot / "CLAUDE.md").read_bytes() == kept.encode() and "skipped 1 (CLAUDE.md)" in out, out  # a bootloader already there (CRLF too) is kept


@pytest.mark.criterion("AC-31")
def test_init_keeps_an_edited_context_toml_and_writes_only_what_it_points_at(tmp_path):
    B.init(tmp_path, {"task": "PRJ"})
    assert B.init(tmp_path).startswith("init: created 0"), "a bare re-run after --prefix is a no-op"
    cfg = tmp_path / "context.toml"
    text = cfg.read_text(encoding="utf-8").replace('path = "docs/criteria.md"', 'path = "docs/spec/criteria.md"')
    cfg.write_bytes(b"\xef\xbb\xbf" + text.encode())  # edited in place, by an editor that writes a BOM
    (tmp_path / "docs/criteria.md").unlink()
    (tmp_path / "docs/charter.md").unlink()
    out = B.init(tmp_path)
    assert out.startswith("init: created 1 (docs/charter.md)"), out
    assert "docs/criteria.md (not in context.toml)" in out and not (tmp_path / "docs/criteria.md").exists()
    with pytest.raises(Refusal, match="gives task the prefix 'PRJ', not 'T2'"):
        B.init(tmp_path, {"task": "T2"})


@pytest.mark.criterion("AC-31")
def test_init_refuses_a_context_toml_that_does_not_load_and_bad_prefixes(tmp_path):
    (tmp_path / "context.toml").write_text("[enigne]\n", encoding="utf-8")
    with pytest.raises(Refusal, match="exists and does not load: the top level has unknown key 'enigne'"):
        B.init(tmp_path)
    (tmp_path / "context.toml").write_text("[engine\n", encoding="utf-8")
    with pytest.raises(Refusal, match="exists and is not TOML"):
        B.init(tmp_path)
    with pytest.raises(Refusal, match="share the id prefix"):
        B.config_text({"task": "D"})
    with pytest.raises(Refusal, match="does not declare"):
        B.config_text({"nosuch": "X"})
    with pytest.raises(Refusal, match="upper-case"):
        B.config_text({"task": "t-1"})


@pytest.mark.criterion("AC-31")
def test_a_prefix_override_lands_in_its_own_kind_only(tmp_path):
    B.init(tmp_path, {"task": "PRJ", "decision": "DEC"})
    cfg = C.load(tmp_path)
    assert cfg.kinds["task"].prefix == "PRJ" and cfg.kinds["decision"].prefix == "DEC"
    assert cfg.kinds["question"].prefix == "ASK" and cfg.kinds["story"].prefix == "S"
    assert B.init(tmp_path, {"task": "PRJ", "decision": "DEC"}).startswith("init: created 0")


# -- the template is the schema --------------------------------------------------------------


def _keys(cls, drop=()) -> set[str]:
    return {f.name for f in dataclasses.fields(cls)} - set(drop)


@pytest.mark.criterion("AC-32")
def test_the_config_template_names_every_key_the_engine_reads_and_parses():
    raw = tomllib.loads((B.KIT / B.TEMPLATE).read_text(encoding="utf-8"))
    cfg = C.from_dict(raw)
    assert _keys(C.Config, ("kinds", "working", "routes", "guards", "gate")) <= set(raw["engine"])
    assert _keys(GATE.Gate, ("skip",)) <= set(raw["gate"]) and _keys(GATE.Scope, ("name",)) <= set(raw["gate"]["scopes"]["all"])
    assert cfg.gate.scopes and not cfg.gate.command and not cfg.gate.require, "the kit's gate is off until a repo sets its command"
    assert _keys(C.Working) <= set(raw["working"])
    kind_keys = set().union(*(set(k) for k in raw["kinds"].values()))
    assert _keys(C.Kind, ("name",)) <= kind_keys
    route_keys = set().union(*(set(r) for r in raw["routes"]))
    assert _keys(C.Route) <= route_keys
    assert _keys(C.Guards) <= set(raw["guards"])
    assert len(cfg.kinds) == 6 and cfg.working.board
    tuned = G.provenance_problems((B.KIT / B.TEMPLATE).read_text(encoding="utf-8"))  # G-D9 over the template
    assert len(tuned) >= 17 and [t for t in tuned if t.problem] == [], tuned


@pytest.mark.criterion("AC-30")
def test_the_ledger_skeleton_is_the_engines_empty_ledger():
    assert (B.KIT / "docs/ledger/session-log.md").read_text(encoding="utf-8") == EMPTY_LEDGER


# -- the contract ships the framework's delegation rules verbatim ------------------------------


def _paragraph(text: str, start: str) -> str:
    i = text.index(start)
    j = text.find("\n\n", i)
    return text[i : j if j >= 0 else len(text)]


@pytest.mark.criterion("AC-33")
@pytest.mark.parametrize("start", ["**Ultracode**", "**The coordinator:**", "- **Do not use `fable` subagents"])
def test_the_kit_contract_carries_framework_6_6_verbatim(start):
    fw = FRAMEWORK.read_text(encoding="utf-8").replace("\r\n", "\n")
    six = fw[fw.index("### 6.6 ") : fw.index("### 6.7 ")]
    contract = (B.KIT / B.CONTRACT).read_text(encoding="utf-8")
    want = _paragraph(six, start)
    if start.startswith("- "):
        want = "\n".join(want.splitlines()[:2])
    assert want in contract, f"kit/contract.md has drifted from FRAMEWORK §6.6 at {start!r}"


@pytest.mark.criterion("AC-33")
def test_the_bootloader_is_marked_pins_the_framework_and_imports_the_contract():
    boot = (B.KIT / B.BOOTLOADER).read_text(encoding="utf-8")
    assert boot.startswith(B.BEGIN) and B.END in boot
    want = ".".join(__version__.split(".")[:2])
    body = B.bootloader_body()
    assert re.findall(r"^framework: (.*)$", body, re.MULTILINE) == [want], "the pin is the engine's major.minor"
    assert B.IMPORT_RE.findall(body) == [B.CONTRACT_DEST], body
    assert B.BEGIN == f"<!-- context-engine kit {want} begin -->" and B.END == f"<!-- context-engine kit {want} end -->"
    assert "<this repo's own test command>" in boot.split(B.END)[1], "the gate command is the repo's: outside the markers"


@pytest.mark.criterion("AC-33")
def test_the_contract_pins_the_framework_and_starts_a_session_alone():
    text = (B.KIT / B.CONTRACT).read_text(encoding="utf-8")
    want = ".".join(__version__.split(".")[:2])
    assert re.findall(r"^framework: (.*)$", text, re.MULTILINE) == [want]
    assert "<this repo" not in text and B.BEGIN not in text, "the framework's file carries nothing a repo fills in"
    assert not B.IMPORT_RE.search(text), "the contract imports nothing: one hop, nowhere near Claude Code's limit of four"
    # it alone starts a session: no other file is needed to know the first two steps and the fallback
    flat = " ".join(text.split())
    assert "a `SessionStart` hook (`context-engine init` writes it to `.claude/settings.local.json`) prints `context-engine orient`" in flat
    assert "run `context-engine session start`" in flat and "or run `context-engine orient` if it is not in your context" in flat
    assert "if you already hold one (after a resume, `/clear` or compaction), keep it, do not run `session start` again" in flat, "the keyless hook re-fires on compaction"
    assert "where they narrow or override a rule here, `CLAUDE.md` wins" in flat, "the owner changes a grant in an owner-loaded file they may edit"
    assert "a failing hook is silent" in flat, "the fallback says why it exists"


# -- no leaks from this repo ----------------------------------------------------------------

# this repo's ids (an `ASK-n` is not one: ASK is the kit's own default question prefix), its probe
# paths, and this machine's paths in any of the forms a shell writes them (CE-26)
LEAK = re.compile(
    r"\b(?:CE|DEC|US|AC|INV)-\d+|spike/|tools/sabotage|(?i:\b[a-z]:[\\/]users\b|/c/users/|anaconda3)"
    r"|context-engine/docs/evidence|docs/evidence/adhoc"
)
# known leaks awaiting their fix, which then removes the entry here (the test fails until it does)
KNOWN_LEAKS: dict[str, list[str]] = {}


def leaks(text: str) -> list[str]:
    """Every leak in ``text``, as ``line: match``. FRAMEWORK gets no allowance either: its `(CE-n)`
    build marks went to the board (DEC-81), so a mark put back is a leak like any other id."""
    return [f"{n}: {m.group(0)}" for n, line in enumerate(text.splitlines(), 1) for m in LEAK.finditer(line)]


@pytest.mark.criterion("AC-33")
def test_the_kit_and_framework_carry_none_of_this_repos_ids_or_paths():
    kit = sorted(p for p in B.KIT.rglob("*") if p.is_file())
    assert len(kit) >= 7, kit
    found = {p.relative_to(REPO).as_posix(): leaks(p.read_text(encoding="utf-8")) for p in kit}
    found["FRAMEWORK.md"] = leaks(FRAMEWORK.read_text(encoding="utf-8"))
    found = {k: v for k, v in found.items() if v}
    known = {k: [hit.split(": ", 1)[1] for hit in v] for k, v in found.items() if k in KNOWN_LEAKS}
    assert known == KNOWN_LEAKS, f"a known leak was fixed or changed: update KNOWN_LEAKS to {known}"
    assert {k: v for k, v in found.items() if k not in KNOWN_LEAKS} == {}


@pytest.mark.parametrize("planted", ["INV-3", "tools/sabotage_x.py", "C:\\Users\\me", "c:/users/me", "/c/Users/me/x", "anaconda3/envs/x"])
@pytest.mark.criterion("AC-33")
def test_the_leak_check_sees_each_form(planted):
    assert leaks(f"see {planted} here"), planted
    assert not leaks("ASK-n, INV-n, G-3, a T-1 task and C:/Program Files")


# -- the runbooks ship in the kit (CE-24) ----------------------------------------------------

RUNBOOKS = ("manual-mode.md", "procedures.md", "gate.md", "sabotage.md", "fan-out.md", "release.md")


@pytest.mark.criterion("AC-37")
def test_the_kit_runbooks_are_this_repos_runbooks():
    """The kit ships the runbooks this repo runs on: one text, so a fix lands in both or the gate is red."""
    kit = B.KIT / "docs" / "runbooks"
    assert sorted(p.name for p in kit.iterdir()) == sorted(RUNBOOKS)
    for name in RUNBOOKS:
        assert B.FILES[f"docs/runbooks/{name}"] == f"docs/runbooks/{name}"
        ours = (REPO / "docs" / "runbooks" / name).read_bytes()
        assert (kit / name).read_bytes() == ours, f"kit/docs/runbooks/{name} differs from docs/runbooks/{name}: copy one onto the other"


@pytest.mark.criterion("AC-37")
def test_init_copies_the_runbooks_and_keeps_an_edited_one(tmp_path):
    (tmp_path / "docs" / "runbooks").mkdir(parents=True)
    ours = b"# our own procedures\n"
    (tmp_path / "docs" / "runbooks" / "procedures.md").write_bytes(ours)
    out = B.init(tmp_path)
    assert "docs/runbooks/manual-mode.md" in out.split("; skipped")[0], out
    assert (tmp_path / "docs" / "runbooks" / "manual-mode.md").read_bytes() == (B.KIT / "docs" / "runbooks" / "manual-mode.md").read_bytes()
    assert (tmp_path / "docs" / "runbooks" / "procedures.md").read_bytes() == ours
    assert "docs/runbooks/procedures.md" in out.split("; skipped")[1], out


def test_the_kit_and_its_byte_compared_copies_check_out_lf_on_every_machine(tmp_path):
    """CE-46: with core.autocrlf=true (Git for Windows' default) a clone, merge or cherry-pick
    writes text files CRLF, and the kit's byte checks above go red: init copies a CRLF kit, and a
    runbook checked out CRLF beside an LF kit file differs. .gitattributes pins eol=lf for the
    kit and for each copy of it this repo keeps, so every checkout writes them LF. git reads the
    committed .gitattributes in an empty repo, as a fresh clone would (no .git/info/attributes)."""
    import shutil
    import subprocess

    paths = sorted(p.relative_to(REPO).as_posix() for p in B.KIT.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    paths += [f"docs/runbooks/{name}" for name in RUNBOOKS] + [B.CONTRACT_DEST]
    subprocess.run(["git", "init", "-q", str(tmp_path)], capture_output=True, check=True)
    shutil.copyfile(REPO / ".gitattributes", tmp_path / ".gitattributes")
    out = subprocess.run(["git", "check-attr", "text", "eol", "--", *paths], cwd=tmp_path, capture_output=True, text=True, check=True).stdout
    attrs = {}
    for line in out.splitlines():
        path, attr, value = line.rsplit(": ", 2)
        attrs.setdefault(path, {})[attr] = value
    unpinned = [p for p in paths if attrs.get(p) != {"text": "set", "eol": "lf"}]
    assert unpinned == [], f"not pinned `text eol=lf` in .gitattributes: {unpinned}"


@pytest.mark.criterion("AC-37")
def test_the_wheel_carries_every_kit_file(tmp_path):
    """Build the wheel from a copy of the source and check every kit file is in it (package-data
    globs miss a new subdirectory silently)."""
    import shutil
    import subprocess
    import sys
    import zipfile

    src = tmp_path / "src"
    shutil.copy2(REPO / "pyproject.toml", src.parent / "pyproject.toml")
    shutil.copytree(REPO / "src", src, ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"))
    out = tmp_path / "dist"
    r = subprocess.run(
        [sys.executable, "-m", "pip", "wheel", str(tmp_path), "--no-deps", "--no-build-isolation", "--no-cache-dir", "-q", "-w", str(out)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    (wheel,) = out.glob("context_engine-*.whl")
    names = set(zipfile.ZipFile(wheel).namelist())
    kit = {"context_engine/kit/" + p.relative_to(B.KIT).as_posix() for p in B.KIT.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    assert kit and kit - names == set(), f"missing from the wheel: {sorted(kit - names)}"
    assert "context_engine/REGISTER.md" in names


# -- bootstrap end to end, on the CLI and the MCP server -------------------------------------


def _cli(root: Path, *argv: str, key: str = "") -> str:
    from context_engine.cli import run

    code, out = run(["--root", str(root), "--actor", ACTOR, "--session", key or KEY, *argv])
    assert code == 0, out
    return out


ACTOR, KEY = "claude-code/test", "2026-10-12a"
PLACEHOLDER = "<this repo's own test command>"


def _fill_gate(root: Path) -> None:
    """Kit README § 2a step 2: the repo's own test command replaces the Gate stub's placeholder."""
    p = root / "CLAUDE.md"
    p.write_text(p.read_text(encoding="utf-8").replace(PLACEHOLDER, "python -m pytest -q"), encoding="utf-8")


@pytest.mark.criterion("AC-96")
def test_orient_asks_for_the_charter_and_criteria_while_they_are_the_kits_templates(tmp_path):
    """CE-121 (adhoc AAR entry 34): both were still the templates a week after the cutover, with
    lint clean; orient asks at every session start until they are filled."""
    heading = "## Templates still unfilled: ask the owner\n"
    B.init(tmp_path)
    _fill_gate(tmp_path)
    key = _cli(tmp_path, "session", "start").split()[1]

    def section():
        out = _cli(tmp_path, "orient", key=key)
        return out.split(heading, 1)[1].split("\n## ", 1)[0].splitlines() if heading in out else None

    assert section() == [
        "- docs/charter.md is still the kit's template: fill it with the owner (kit README § 2a, step 1)",
        "- docs/criteria.md is still the kit's template: fill it with the owner (kit README § 2a, step 1)",
    ]
    charter = tmp_path / "docs/charter.md"
    charter.write_text(charter.read_text(encoding="utf-8").replace("*(the owner's words)*", "Ship the tool"), encoding="utf-8")
    assert section()[0] == ("- docs/charter.md still holds the template's `*(what this repo must never become)*`, "
                            "`*(the owner's standing rules, each with where it is recorded)*`: replace them with the owner's words"), section()
    charter.write_text(charter.read_text(encoding="utf-8").replace("*(what this repo must never become)*", "a service")
                       .replace("*(the owner's standing rules, each with where it is recorded)*", "none yet"), encoding="utf-8")
    criteria = tmp_path / "docs/criteria.md"
    assert section() == ["- docs/criteria.md is still the kit's template: fill it with the owner (kit README § 2a, step 1)"]
    criteria.write_text(criteria.read_text(encoding="utf-8") + "| AC-1 | it ships | US-1 | planned | |\n", encoding="utf-8")
    assert section() is None
    assert _cli(tmp_path, "lint") == "lint: clean"  # orient's to ask, not lint's to fail


@pytest.mark.criterion("AC-97")
def test_g_d0_fails_a_kit_runbook_that_is_missing_or_unrouted(tmp_path):
    """CE-50 (INV-36): init never edits an existing context.toml, so a repo upgraded to a kit with
    a new runbook got no route and no copy while its contract named it, and lint stayed clean."""
    from context_engine.cli import run

    def lint() -> list[str]:
        return [ln.split(". Remedy:")[0] for ln in run(["--root", str(tmp_path), "lint"])[1].splitlines() if ln.startswith("G-D0")]

    B.init(tmp_path)
    _fill_gate(tmp_path)
    assert lint() == []
    (tmp_path / "docs/runbooks/release.md").unlink()
    assert lint() == ["G-D0 docs/runbooks/release.md: does not exist, but the installed kit ships it and the contract names it"], lint()
    cfg = tmp_path / "context.toml"
    chunks = cfg.read_text(encoding="utf-8").split("\n[[routes]]")
    kept = [c for c in chunks if 'path = "docs/runbooks/release.md"' not in c and 'path = "docs/runbooks"\n' not in c]
    assert len(kept) == len(chunks) - 2
    cfg.write_text("\n[[routes]]".join(kept), encoding="utf-8")
    assert "G-D0 context.toml: no [[routes]] entry covers docs/runbooks/release.md, a runbook the installed kit ships" in lint(), lint()
    # the directory's route covered manual-mode and procedures too; the method runbooks keep their own
    assert sorted(f.split("covers ")[1].split(",")[0] for f in lint() if "covers" in f) == [
        "docs/runbooks/manual-mode.md", "docs/runbooks/procedures.md", "docs/runbooks/release.md"], lint()
    assert run(["--root", str(tmp_path), "lint"])[1].count("kit README § 4, step 2") == 4
    contract = tmp_path / "CLAUDE.md"  # a contract with no kit block (like the engine repo's own): not checked
    contract.write_text(f"# contract\n\nframework: {B.BEGIN.split()[3]}\n", encoding="utf-8")
    assert [f for f in lint() if "runbook" in f] == []


@pytest.mark.criterion("AC-95")
def test_g_d0_fails_a_contract_that_keeps_the_gate_stubs_placeholder(tmp_path):
    """CE-71 (audit 2026-10-14a N1): a repo could keep `<this repo's own test command>` with a
    clean lint, so its gate named nothing to run."""
    from context_engine.cli import run

    assert B.gate_placeholders() == [PLACEHOLDER]  # read from the kit's bootloader, after its end marker
    B.init(tmp_path)
    out = run(["--root", str(tmp_path), "lint"])[1]
    assert f"G-D0 CLAUDE.md: still holds the kit's placeholder `{PLACEHOLDER}`, so its gate names no command to run" in out, out
    assert "kit README § 2a, step 2" in out
    _fill_gate(tmp_path)
    assert run(["--root", str(tmp_path), "lint"])[1] == "lint: clean"


@pytest.mark.criterion("AC-30")
def test_an_empty_repo_bootstraps_with_init_alone_and_runs_a_whole_session(tmp_path):
    assert _cli(tmp_path, "init").startswith("init: created 23")
    _fill_gate(tmp_path)
    assert _cli(tmp_path, "lint") == "lint: clean"
    key = _cli(tmp_path, "session", "start").split()[1]
    assert "no banner" in _cli(tmp_path, "orient", key=key)
    _cli(tmp_path, "task", "new", "First", "--pri", "NOW", key=key)
    _cli(tmp_path, "session", "close", "--rows", "T-1", "--summary", "bootstrapped", "--guards", "lint clean", "--read", "orient", key=key)
    show = _cli(tmp_path, "banner", "show")
    assert show.split()[3] == "none", show
    assert _cli(tmp_path, "banner", "set", "--seen", "none", "--text", "- Bootstrapped.", key=key).startswith("banner written (the first)")
    assert _cli(tmp_path, "lint") == "lint: clean"
    note = (tmp_path / "HANDOFF.md").read_text(encoding="utf-8")
    assert note.index(f"## Banner ({key})") < note.index("## Next session")
    assert f"## {key} · kind: close" in (tmp_path / "docs/ledger/session-log.md").read_text(encoding="utf-8")
    assert "init: created 0" in _cli(tmp_path, "init")


@pytest.mark.criterion("AC-30")
def test_the_mcp_init_tool_needs_no_config(tmp_path):
    import asyncio

    from mcp import Client

    from context_engine.mcp import server

    async def go():
        async with Client(server(tmp_path)) as c:
            return await c.call_tool("init", {"prefix": {"task": "PRJ"}})

    r = asyncio.run(go())
    assert not r.is_error, r.content[0].text
    assert r.content[0].text.startswith("init: created") and C.load(tmp_path).kinds["task"].prefix == "PRJ"


# -- the config refuses what it does not read ------------------------------------------------


@pytest.mark.criterion("AC-32")
@pytest.mark.parametrize("table", ["engine", "working", "kinds.task"])
def test_the_config_refuses_an_unknown_key_naming_the_allowed_ones(table):
    raw = tomllib.loads((B.KIT / B.TEMPLATE).read_text(encoding="utf-8"))
    node = raw
    for part in table.split("."):
        node = node[part]
    node["orient_max_byte"] = 1  # a typo of a real key
    with pytest.raises(Refusal, match=r"unknown key 'orient_max_byte'.*use only"):
        C.from_dict(raw)


@pytest.mark.criterion("AC-32")
@pytest.mark.parametrize(
    "edit,match",
    [
        (lambda r: r.update(enigne={}), r"the top level has unknown key 'enigne'"),
        (lambda r: r.update(kind={"task": {}}), r"the top level has unknown key 'kind'"),
        (lambda r: r["working"]["caps"].update(NEXTT=3), r"\[working.caps\] has unknown key 'NEXTT'"),
        (lambda r: r["working"]["caps"].update(NEXT="5"), r"\[working.caps\] `NEXT` is str"),
        (lambda r: r["working"].update(orient_max_bytes="big"), r"\[working\] `orient_max_bytes` is str 'big', not int"),
        (lambda r: r["working"].update(max_pauses=True), r"`max_pauses` is bool"),
        (lambda r: r["working"].update(board="task"), r"`board` is str"),
        (lambda r: r["engine"].update(lock_timeout="30"), r"\[engine\] `lock_timeout` is str"),
        (lambda r: r["kinds"]["task"].update(required="title"), r"\[kinds.task\] `required` is str"),
        (lambda r: r["kinds"]["task"].update(required=["title", 1]), r"\[kinds.task\] `required` is list"),
        (lambda r: r["routes"][0].update(optional="yes"), r"route 1 `optional` is str"),
    ],
)
def test_the_config_refuses_unknown_tables_tiers_and_mistyped_values(edit, match):
    raw = tomllib.loads((B.KIT / B.TEMPLATE).read_text(encoding="utf-8"))
    edit(raw)
    with pytest.raises(Refusal, match=match):
        C.from_dict(raw)


def test_this_repos_own_config_still_loads():
    C.load(REPO)


# -- the first banner --------------------------------------------------------------------------


@pytest.mark.criterion("AC-34")
@pytest.mark.parametrize("note", [None, "# Note\n\nintro\n\n## Next\n\n- x\n", "# Note\r\n\r\nintro\r\n"])
def test_the_first_banner_is_written_with_seen_none_and_only_then(tmp_path, note):
    B.init(tmp_path)
    handoff = tmp_path / "HANDOFF.md"
    if note is None:
        handoff.unlink()
    else:
        handoff.write_bytes(note.encode())
    assert _cli(tmp_path, "banner", "show").startswith("banner none hash none")
    with pytest.raises(Refusal, match="no banner yet, so pass --seen none"):
        _cli(tmp_path, "banner", "set", "--seen", "sha256:0000", "--text", "- B.")
    _cli(tmp_path, "banner", "set", "--seen", "none", "--text", "- B.")
    text = handoff.read_bytes().decode()
    shown = _cli(tmp_path, "banner", "show")
    assert shown.startswith(f"banner {KEY} hash sha256:") and shown.endswith("\n\n- B."), shown
    if note and "\r\n" in note:
        assert "\n" not in text.replace("\r\n", "")
    if note and "## Next" in note:
        assert text.index("## Banner") < text.index("## Next") and text.startswith("# Note\n\nintro\n\n")
    with pytest.raises(Refusal, match="changed since you read it"):
        _cli(tmp_path, "banner", "set", "--seen", "none", "--text", "- C.")


# -- G-W1: once a session has closed, a banner is owed ------------------------------------------


def test_lint_g_w1_is_red_when_a_session_closed_and_the_note_has_no_banner(tmp_path):
    from context_engine.cli import run

    def lint() -> str:
        return run(["--root", str(tmp_path), "lint"])[1]

    B.init(tmp_path)
    _fill_gate(tmp_path)
    key = _cli(tmp_path, "session", "start").split()[1]
    assert lint() == "lint: clean"  # no close yet: nothing is owed
    _cli(tmp_path, "session", "close", "--rows", "none", "--summary", "s", "--guards", "g", "--read", "r", key=key)
    assert "G-W1" in lint() and "no `## Banner (<key>)` heading" in lint()
    _cli(tmp_path, "banner", "set", "--seen", "none", "--text", "- B.", key=key)
    assert lint() == "lint: clean"
    note = tmp_path / "HANDOFF.md"
    note.write_text(note.read_text(encoding="utf-8").replace("## Banner (", "## Old banner ("), encoding="utf-8")
    assert "G-W1" in lint()


# -- DEC-39: the framework's living text says "procedure", never "ritual" (CE-68) ---------------


def test_no_living_framework_text_says_ritual():
    """FRAMEWORK, the framework contract, CLAUDE.md, HANDOFF.md and every kit file say "procedure".
    The only uses left are names a frozen file still carries: the `Ritual` column of a coverage map
    frozen before DEC-39 (G-D12 reads both), and the quoted "rituals" that count_nouns keeps so a
    count typed in an older doc is still caught."""
    files = [FRAMEWORK, REPO / "docs" / "framework" / "contract.md", REPO / "CLAUDE.md", REPO / "HANDOFF.md"]
    files += [B.KIT.parent / "REGISTER.md"]  # the engine's register ships with it, so its controls are living text too (CE-69)
    files += sorted(p for p in B.KIT.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    found = []
    for path in files:
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r"ritual", line.replace("`Ritual`", "").replace('"rituals"', ""), re.IGNORECASE):
                found.append(f"{path.relative_to(REPO).as_posix()}:{n}: {line.strip()[:80]}")
    assert found == [], "living framework text still says ritual (DEC-39: say procedure):\n" + "\n".join(found)


# -- CE-69: the kit README's file table and directory line are what init does ------------------


def test_the_kit_readme_table_and_dirs_line_match_what_init_writes():
    """The README's `| Kit file | Goes to | What it is |` table names every kit file (bootstrap.FILES,
    the template, the bootloader and the contract), each going where init puts it, and its
    `init also ... creates` line names exactly bootstrap.KEEP and SELF_IGNORING: a kit file added
    without a row, or a directory init stops creating, turns this red."""
    readme = (B.KIT / "README.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    head = readme.index("| Kit file | Goes to | What it is |")
    table = readme[head:].split("\n\n", 1)[0].splitlines()[2:]
    rows = {}
    for line in table:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        kit_file = re.fullmatch(r"`([^`]+)`", cells[0])
        assert kit_file, f"a README table row whose first cell is not one backticked kit file: {line!r}"
        assert kit_file.group(1) not in rows, f"two README table rows for {kit_file.group(1)}"
        rows[kit_file.group(1)] = cells[1]
    assert set(rows) == set(B.FILES) | {B.TEMPLATE, B.BOOTLOADER, B.CONTRACT}, rows
    shipped = {p.relative_to(B.KIT).as_posix() for p in B.KIT.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    assert set(rows) == shipped - {"README.md"}, "every file the kit ships has a row, and every row a file"
    for src, dest in B.FILES.items():
        assert rows[src] == f"`{dest}`", f"{src} goes to {dest}, the README says {rows[src]}"
    assert rows[B.TEMPLATE] == f"`{C.CONFIG_NAME}`" and rows[B.CONTRACT] == f"`{B.CONTRACT_DEST}`"
    assert rows[B.BOOTLOADER].startswith(f"appended to `{B.CONTRACT_TARGET}`")
    line = " ".join(readme[readme.index("`init` also writes") :].split("\n\n", 1)[0].split())
    keep, ignoring = line.split("(each with an empty `.gitkeep`)", 1)
    named = re.findall(r"`([^`]+)/`", keep)
    assert sorted(named) == sorted(B.KEEP), keep
    named = re.findall(r"`([^`]+)/`", ignoring.split("(each carrying its own `.gitignore`", 1)[0])
    assert sorted(named) == sorted(B.SELF_IGNORING), ignoring


# -- CE-76: the kit README gives the provenance note's form, `wrong if` and all ------------------


def test_the_kit_readme_gives_the_provenance_form_g_d9_accepts():
    """An adopter writes a cap's note from the README: each form it gives, with its `wrong if`
    tail, passes G-D9 (docs/evidence/adhoc-dryrun-2026-10-14.md F16: the words were not said)."""
    readme = (B.KIT / "README.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    flat = re.sub(r"\s*\n\s*", " ", readme)
    forms = re.findall(r"`(# provenance: (?:MEASURED|JUDGEMENT) <[^>`]+>)`", flat)
    tail = re.search(r"`(; wrong if <[^>`]+>)`", flat)
    assert len(forms) == 2 and tail, (forms, tail)
    for form in forms:
        assert [t.problem for t in G.provenance_problems(f"cap = 3  {form}{tail.group(1)}")] == [""], form
        assert G.provenance_problems(f"cap = 3  {form}")[0].problem, "without the tail it is red"


# -- CE-81: the engine's env lives in the repo, and the repo's .gitignore ignores it (DEC-41) -------


def _check_ignore(root: Path, rel: str) -> bool:
    """What git itself says: whether ``rel`` (a path inside the engine's env) is ignored in ``root``."""
    import subprocess

    subprocess.run(["git", "init", "-q"], cwd=root, check=True, capture_output=True)
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    (root / rel).write_bytes(b"")
    return subprocess.run(["git", "check-ignore", "-q", rel], cwd=root, capture_output=True).returncode == 0


@pytest.mark.criterion("AC-31")
def test_init_writes_a_gitignore_that_ignores_the_engine_env_and_a_rerun_leaves_it(tmp_path):
    out = B.init(tmp_path)
    assert (tmp_path / B.REPO_IGNORE).read_text(encoding="utf-8") == B.ENGINE_IGNORE
    assert B.REPO_IGNORE in out.split("; skipped")[0], out
    assert _check_ignore(tmp_path, f"{B.ENGINE_ENV}/python.exe"), "git ignores the engine's env"
    before = snapshot(tmp_path)
    again = B.init(tmp_path)
    assert again.startswith("init: created 0 (none)") and f"{B.REPO_IGNORE} (ignores {B.ENGINE_DIR}/)" in again, again
    assert snapshot(tmp_path) == before


@pytest.mark.criterion("AC-31")
@pytest.mark.parametrize("old", [b"*.pyc\r\nbuild/", b"*.pyc\nbuild/\n", b"*.pyc\n\n", b"", b"\xef\xbb\xbf# ours\r\n.env\r\n"])
def test_init_appends_the_engine_env_to_an_existing_gitignore_keeping_every_byte_and_its_line_endings(tmp_path, old):
    (tmp_path / B.REPO_IGNORE).write_bytes(old)
    out = B.init(tmp_path)
    new = (tmp_path / B.REPO_IGNORE).read_bytes()
    assert new.startswith(old) and f"{B.REPO_IGNORE} ({B.ENGINE_DIR}/ appended)" in out, (new, out)
    added = new[len(old) :]
    if b"\r\n" in old:
        assert b"\n" not in added.replace(b"\r\n", b""), "the appended lines keep the file's CRLF"
    assert added.replace(b"\r\n", b"\n").lstrip(b"\n") == B.ENGINE_IGNORE.encode()
    norm = new.replace(b"\r\n", b"\n")
    assert not old or b"\n\n" + B.ENGINE_IGNORE.encode() in norm, "a blank line before the appended lines"
    before = snapshot(tmp_path)
    assert B.init(tmp_path).startswith("init: created 0 (none)") and snapshot(tmp_path) == before, "appended once"
    assert _check_ignore(tmp_path, f"{B.ENGINE_ENV}/bin/python")


@pytest.mark.criterion("AC-31")
@pytest.mark.parametrize("line,ignored", [
    (".context-engine/", True), ("/.context-engine", True), (".context-engine/*", True), (".context-engine/**", True),
    (".*", True), ("*", True), (".context-engine/env/", False), (".context-engine/\n!.context-engine/", False), (".context-engine-old/", False),
    (".context-engine/  ", True), ("*\n!/build/", True), (" .context-engine/", False),
    (".context-engine/*\n!.context-engine/env/", False), (".context-engine/*\n!env/", False), (".context-engine/*\n!**/env", False),
])
def test_init_leaves_a_gitignore_that_already_ignores_the_engine_env_untouched(tmp_path, line, ignored):
    """Left alone only when git itself ignores the env: init errs toward appending, never toward a
    committed env (CE-81 review: a leading space, or a later `!` line reaching inside)."""
    old = f"# ours\n{line}\n".encode()
    git = tmp_path / "git"
    git.mkdir()
    (git / B.REPO_IGNORE).write_bytes(old)
    assert not ignored or _check_ignore(git, f"{B.ENGINE_ENV}/python.exe"), "a case init leaves alone is one git ignores"
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / B.REPO_IGNORE).write_bytes(old)
    out = B.init(repo)
    assert ((repo / B.REPO_IGNORE).read_bytes() == old) == ignored, out
    assert (f"{B.REPO_IGNORE} (ignores {B.ENGINE_DIR}/)" in out) == ignored, out
    assert _check_ignore(repo, f"{B.ENGINE_ENV}/python.exe"), "after init, git ignores the env"


@pytest.mark.criterion("AC-31")
def test_init_refuses_a_gitignore_edited_after_its_plan_and_leaves_a_non_utf8_one_with_a_warning(tmp_path, monkeypatch):
    (tmp_path / B.REPO_IGNORE).write_bytes(b"build/\n")
    edited = b"build/\ndist/\n"
    with monkeypatch.context() as m:
        _plan_then(m, lambda root: (root / B.REPO_IGNORE).write_bytes(edited))
        with pytest.raises(Refusal, match=r"\.gitignore changed while init ran, so \.context-engine/ was not appended"):
            B.init(tmp_path)
    assert (tmp_path / B.REPO_IGNORE).read_bytes() == edited
    latin = b"# caf\xe9\nbuild/\n"
    (tmp_path / B.REPO_IGNORE).write_bytes(latin)
    out = B.init(tmp_path)
    assert (tmp_path / B.REPO_IGNORE).read_bytes() == latin and f"; warning: {B.REPO_IGNORE} is not UTF-8" in out, out


def test_the_kit_text_names_the_engine_env_convention():
    """DEC-41's convention, `.context-engine/env/`, is stated where an adopter installs, bootstraps
    and upgrades (kit README § 1 and § 4, FRAMEWORK §6.9 step 2 and the upgrade procedure, the
    procedures' Bootstrap row), so CE-77's plugin and a by-hand adopter resolve the same path."""
    readme = " ".join((B.KIT / "README.md").read_text(encoding="utf-8").split())
    install = readme[readme.index("## 1. Install and pin the engine") : readme.index("## 2a.")]
    upgrade = readme[readme.index("## 4. Upgrade") : readme.index("## 5.")]
    for text in (install, upgrade):
        assert f"{B.ENGINE_ENV}/" in text, text[:200]
    assert f"{B.ENGINE_DIR}/" in readme[readme.index("`init` also writes") :].split("##", 1)[0]
    framework = " ".join(FRAMEWORK.read_text(encoding="utf-8").split())
    step2 = framework[framework.index("2. The agent installs the engine") : framework.index("3. `context-engine init` writes the kit")]
    assert f"{B.ENGINE_ENV}/" in step2, step2
    up = framework[framework.index("**Upgrade procedure:**") :].split("- **", 1)[0]
    assert f"{B.ENGINE_ENV}/" in up, up
    procedures = (B.KIT / "docs" / "runbooks" / "procedures.md").read_text(encoding="utf-8")
    row = next(ln for ln in procedures.splitlines() if ln.startswith("| 2 | Install the engine"))
    assert f"{B.ENGINE_ENV}/" in row, row


def test_lint_walks_skip_the_engine_env(tmp_path):
    """The engine's env sits in the repo (`.context-engine/env/`), so lint's walks skip it like
    `.venv`: a bare name cited in a doc must not resolve to a file in its site-packages (a false
    green in G-T3), and lint must not read its thousands of files (CE-81 review)."""
    env = tmp_path / B.ENGINE_ENV / "Lib" / "site-packages" / "somepkg"
    env.mkdir(parents=True)
    (env / "only_in_env.py").write_text("def bar(): pass\n", encoding="utf-8")
    (env / "README.md").write_text("# a package's readme\n", encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "ours.py").write_text("def bar(): pass\n", encoding="utf-8")
    files = G.Files(tmp_path)
    assert files.find("ours.py") == tmp_path / "src" / "ours.py", "the control: a repo file resolves"
    assert files.find("only_in_env.py") is None
    assert G.code_ref_problem(files, "only_in_env.py", "bar") == "`only_in_env.py` does not exist (case-exact)"
    assert [rel for rel, _ in G.docs(tmp_path, (".",))] == [], "no doc is read from the env"
