"""The adoption kit and ``init`` (CE-15, FRAMEWORK §6.9, §10, §11): a repo gets the framework as
text, ``init`` only creates, the kit's config template is the config's schema, and neither the kit
nor FRAMEWORK carries this repo's ids or paths."""

import dataclasses
import re
import tomllib
from pathlib import Path

import pytest

from context_engine import bootstrap as B
from context_engine import config as C
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

    def plan(root, prefixes=None):
        out = real(root, prefixes)
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
    assert (tmp_path / "CLAUDE.md").read_text(encoding="utf-8") == old + sep + (B.KIT / B.CONTRACT).read_text(encoding="utf-8")


@pytest.mark.criterion("AC-31")
def test_an_older_kit_block_is_never_doubled(tmp_path):
    old = "# Ours\n\n<!-- context-engine kit 0.4 begin -->\nframework: 0.4\n<!-- context-engine kit 0.4 end -->\n"
    (tmp_path / "CLAUDE.md").write_text(old, encoding="utf-8")
    out = B.init(tmp_path)
    assert (tmp_path / "CLAUDE.md").read_text(encoding="utf-8") == old
    assert "CLAUDE.md (holds the kit 0.4 block: replace it" in out, out


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
    assert _keys(C.Config, ("kinds", "working", "routes", "guards")) <= set(raw["engine"])
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
@pytest.mark.parametrize("start", ["**Ultracode**", "**Several tasks in one session:**", "- **Do not use `fable` subagents"])
def test_the_kit_contract_carries_framework_6_6_verbatim(start):
    fw = FRAMEWORK.read_text(encoding="utf-8").replace("\r\n", "\n")
    six = fw[fw.index("### 6.6 ") : fw.index("### 6.7 ")]
    contract = (B.KIT / B.CONTRACT).read_text(encoding="utf-8")
    want = _paragraph(six, start)
    if start.startswith("- "):
        want = "\n".join(want.splitlines()[:2])
    assert want in contract, f"kit/contract.md has drifted from FRAMEWORK §6.6 at {start!r}"


@pytest.mark.criterion("AC-33")
def test_the_contract_block_is_marked_and_pins_the_framework():
    text = (B.KIT / B.CONTRACT).read_text(encoding="utf-8")
    assert text.startswith(B.BEGIN) and text.rstrip("\n").endswith(B.END)
    assert re.search(r"^framework: \d+\.\d+$", text, re.MULTILINE)
    # the block alone starts a session: no other file is needed to know the first two steps
    assert re.search(r"\*\*Session start:\*\* `context-engine session start`.*\n?.*then `context-engine orient`", text), text


# -- no leaks from this repo ----------------------------------------------------------------

LEAK = re.compile(r"\b(?:CE|DEC|US|AC)-\d+|spike/|C:/Users|context-engine/docs/evidence|docs/evidence/adhoc")
BOARD_MARK = re.compile(r"\bCE-\d+\)")  # FRAMEWORK's `(CE-n)` build-status marks, explained in its Summary


def leaks(text: str, allow_marks: bool) -> list[str]:
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        if allow_marks:
            line = BOARD_MARK.sub("", line)
        out += [f"{n}: {m.group(0)}" for m in LEAK.finditer(line)]
    return out


@pytest.mark.criterion("AC-33")
def test_the_kit_and_framework_carry_none_of_this_repos_ids_or_paths():
    kit = sorted(p for p in B.KIT.rglob("*") if p.is_file())
    assert len(kit) >= 7, kit
    found = {p.relative_to(REPO).as_posix(): leaks(p.read_text(encoding="utf-8"), False) for p in kit}
    found["FRAMEWORK.md"] = leaks(FRAMEWORK.read_text(encoding="utf-8"), True)
    assert {k: v for k, v in found.items() if v} == {}


# -- the runbooks ship in the kit (CE-24) ----------------------------------------------------

RUNBOOKS = ("manual-mode.md", "rituals.md")


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
    ours = b"# our own rituals\n"
    (tmp_path / "docs" / "runbooks" / "rituals.md").write_bytes(ours)
    out = B.init(tmp_path)
    assert "docs/runbooks/manual-mode.md" in out.split("; skipped")[0], out
    assert (tmp_path / "docs" / "runbooks" / "manual-mode.md").read_bytes() == (B.KIT / "docs" / "runbooks" / "manual-mode.md").read_bytes()
    assert (tmp_path / "docs" / "runbooks" / "rituals.md").read_bytes() == ours
    assert "docs/runbooks/rituals.md" in out.split("; skipped")[1], out


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


@pytest.mark.criterion("AC-30")
def test_an_empty_repo_bootstraps_with_init_alone_and_runs_a_whole_session(tmp_path):
    assert _cli(tmp_path, "init").startswith("init: created 15")
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
    key = _cli(tmp_path, "session", "start").split()[1]
    assert lint() == "lint: clean"  # no close yet: nothing is owed
    _cli(tmp_path, "session", "close", "--rows", "none", "--summary", "s", "--guards", "g", "--read", "r", key=key)
    assert "G-W1" in lint() and "no `## Banner (<key>)` heading" in lint()
    _cli(tmp_path, "banner", "set", "--seen", "none", "--text", "- B.", key=key)
    assert lint() == "lint: clean"
    note = tmp_path / "HANDOFF.md"
    note.write_text(note.read_text(encoding="utf-8").replace("## Banner (", "## Old banner ("), encoding="utf-8")
    assert "G-W1" in lint()
