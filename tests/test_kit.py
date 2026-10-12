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


@pytest.mark.criterion("AC-31")
def test_init_refuses_a_different_context_toml_and_bad_prefixes(tmp_path):
    (tmp_path / "context.toml").write_text("[engine]\n", encoding="utf-8")
    with pytest.raises(Refusal, match="exists and differs"):
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
    assert _keys(C.Config, ("kinds", "working", "routes")) <= set(raw["engine"])
    assert _keys(C.Working) <= set(raw["working"])
    kind_keys = set().union(*(set(k) for k in raw["kinds"].values()))
    assert _keys(C.Kind, ("name",)) <= kind_keys
    route_keys = set().union(*(set(r) for r in raw["routes"]))
    assert _keys(C.Route) <= route_keys
    assert len(cfg.kinds) == 6 and cfg.working.board
    tuned = [ln for ln in (B.KIT / B.TEMPLATE).read_text(encoding="utf-8").splitlines() if re.match(r"^(\w+_(bytes|sessions|days|age|pauses|timeout)|NOW|NEXT) = ", ln)]
    assert len(tuned) == 9 and all("provenance: " in ln and ("wrong if" in ln or "wrong as above" in ln) for ln in tuned), tuned


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


# -- bootstrap end to end, on the CLI and the MCP server -------------------------------------


def _cli(root: Path, *argv: str, key: str = "") -> str:
    from context_engine.cli import run

    code, out = run(["--root", str(root), "--actor", ACTOR, "--session", key or KEY, *argv])
    assert code == 0, out
    return out


ACTOR, KEY = "claude-code/test", "2026-10-12a"


@pytest.mark.criterion("AC-30")
def test_an_empty_repo_bootstraps_with_init_alone_and_runs_a_whole_session(tmp_path):
    assert _cli(tmp_path, "init").startswith("init: created 14")
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
