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


def test_init_dry_run_writes_nothing(tmp_path):
    out = B.init(tmp_path, dry_run=True)
    assert out.startswith("init (dry run): would create") and "context.toml" in out
    assert list(tmp_path.iterdir()) == []


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


def test_a_prefix_override_lands_in_its_own_kind_only(tmp_path):
    B.init(tmp_path, {"task": "PRJ", "decision": "DEC"})
    cfg = C.load(tmp_path)
    assert cfg.kinds["task"].prefix == "PRJ" and cfg.kinds["decision"].prefix == "DEC"
    assert cfg.kinds["question"].prefix == "ASK" and cfg.kinds["story"].prefix == "S"
    assert B.init(tmp_path, {"task": "PRJ", "decision": "DEC"}).startswith("init: created 0")


# -- the template is the schema --------------------------------------------------------------


def _keys(cls, drop=()) -> set[str]:
    return {f.name for f in dataclasses.fields(cls)} - set(drop)


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
    assert len(tuned) == 9 and all("provenance: " in ln and "wrong if" in ln or "wrong as above" in ln for ln in tuned), tuned


def test_the_ledger_skeleton_is_the_engines_empty_ledger():
    assert (B.KIT / "docs/ledger/session-log.md").read_text(encoding="utf-8") == EMPTY_LEDGER


# -- the contract ships the framework's delegation rules verbatim ------------------------------


def _paragraph(text: str, start: str) -> str:
    i = text.index(start)
    j = text.find("\n\n", i)
    return text[i : j if j >= 0 else len(text)]


@pytest.mark.parametrize("start", ["**Ultracode**", "**Several tasks in one session:**", "- **Do not use `fable` subagents"])
def test_the_kit_contract_carries_framework_6_6_verbatim(start):
    fw = FRAMEWORK.read_text(encoding="utf-8").replace("\r\n", "\n")
    six = fw[fw.index("### 6.6 ") : fw.index("### 6.7 ")]
    contract = (B.KIT / B.CONTRACT).read_text(encoding="utf-8")
    want = _paragraph(six, start)
    if start.startswith("- "):
        want = "\n".join(want.splitlines()[:2])
    assert want in contract, f"kit/contract.md has drifted from FRAMEWORK §6.6 at {start!r}"


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


def test_the_kit_and_framework_carry_none_of_this_repos_ids_or_paths():
    kit = sorted(p for p in B.KIT.rglob("*") if p.is_file())
    assert len(kit) >= 7, kit
    found = {p.relative_to(REPO).as_posix(): leaks(p.read_text(encoding="utf-8"), False) for p in kit}
    found["FRAMEWORK.md"] = leaks(FRAMEWORK.read_text(encoding="utf-8"), True)
    assert {k: v for k, v in found.items() if v} == {}
