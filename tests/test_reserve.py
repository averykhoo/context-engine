"""Ids reserved before a batch of records that cite each other is written (CE-105, CE-119; adhoc
AAR entries 31 and 32): `id reserve` holds the next ids of a series for one session, no other write
hands them out, and the session writes each record with `--id`."""

import json

import pytest

from context_engine.cli import main
from context_engine.errors import Refusal
from context_engine.store import RESERVE_MAX
from context_engine.working import Engine

from conftest import _toml
from test_working import ACTOR, CONFIG, FRAMEWORK, LEDGER, NOTE, TODAY


@pytest.fixture
def eng(tmp_path):
    (tmp_path / "context.toml").write_text(_toml(CONFIG), encoding="utf-8")
    (tmp_path / "ledger.md").write_text(LEDGER, encoding="utf-8")
    (tmp_path / "HANDOFF.md").write_text(NOTE.format(key="2026-10-07b"), encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text(f"# contract\n\nframework: {FRAMEWORK}\n", encoding="utf-8")
    return Engine(tmp_path, today=lambda: TODAY)


def kw(key):
    return {"session": key, "actor": ACTOR}


def oplog(root):
    return [json.loads(ln) for ln in (root / "ops.jsonl").read_text(encoding="utf-8").splitlines()]


def reserves(root):
    return [o for o in oplog(root) if o["op"] == "id.reserve"]


DECISION = {"actor": "owner", "decision_status": "BUILT"}


# -- AC-130: what a reservation holds ---------------------------------------------------


@pytest.mark.criterion("AC-130")
def test_reserve_takes_ids_above_every_file_created_and_reserved_id_and_new_skips_them(eng):
    key = eng.session_start(actor=ACTOR)
    for n in (1, 2):
        eng.new("task", f"Task {n}", **kw(key))
    # an id the op log shows created, whose file is gone: never handed out again
    with open(eng.root / "ops.jsonl", "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({"at": "2026-10-08T10:00:00+08:00", "session": key, "actor": ACTOR, "op": "new", "id": "CE-5", "path": "tasks/CE-5-gone.md", "fields": [], "mechanical": False}) + "\n")
    assert eng.reserve("task", 2, **kw(key)) == f"reserved CE-6, CE-7 for session {key}: cite them, then write each with `task new --id`"
    assert eng.reserve("task", **kw(key)).startswith("reserved CE-8 ")  # above the earlier reservation
    assert eng.new("task", "Next", **kw(key)).id == "CE-9"  # `new` skips every reserved id
    lines = reserves(eng.root)
    assert [(o["id"], o["session"], o["path"], o["fields"]) for o in lines] == [(f"CE-{n}", key, "", []) for n in (6, 7, 8)]
    assert eng.reserve("decision", **kw(key)).endswith("`record new --id`")
    assert eng.reserve("question", **kw(key)).endswith("`ask new --id`")


@pytest.mark.criterion("AC-130")
def test_concurrent_reserves_and_news_never_share_an_id(repo, workers):
    workers(repo.root, [["reserve", "6", "r1"], ["reserve", "6", "r2"], ["new", "6", "n1"], ["new", "6", "n2"]])
    made = {r.id for r in repo.records("task")}
    held = set(repo.reserved_ids())
    assert len(made) == 12 and len(held) == 12 and not made & held
    assert made | held == {f"CE-{n}" for n in range(1, 25)}


@pytest.mark.criterion("AC-130")
@pytest.mark.parametrize("kind, count, says", [("task", 0, "a count of 0"), ("task", RESERVE_MAX + 1, f"a count of {RESERVE_MAX + 1}"), ("baton", 1, "'baton' is a stamped kind")])
def test_a_count_out_of_range_or_a_kind_no_operation_creates_is_refused_before_any_line(eng, kind, count, says):
    key = eng.session_start(actor=ACTOR)
    before = (eng.root / "ops.jsonl").read_bytes()
    with pytest.raises(Refusal) as r:
        eng.reserve(kind, count, **kw(key))
    assert says in r.value.message
    assert (eng.root / "ops.jsonl").read_bytes() == before


# -- AC-131: writing what was reserved -----------------------------------------------------


@pytest.mark.criterion("AC-131")
def test_a_linked_batch_cites_its_reserved_ids_and_lint_is_green_once_all_are_written(eng):
    key = eng.session_start(actor=ACTOR)
    eng.reserve("task", 2, **kw(key))
    eng.reserve("decision", **kw(key))
    eng.new("task", "Measure it", body="Measure it.\n\nFeeds CE-2; decided by DEC-1.\n\n## Log\n", rid="CE-1", **kw(key))
    red = [f.message for f in eng.lint() if f.guard == "G-D3"]
    assert red and all("which is no record" in m for m in red)  # a reserved id is not yet a record
    eng.new("task", "Use the measure", body="Use the measure.\n\nNeeds CE-1.\n\n## Log\n", rid="CE-2", **kw(key))
    dec = eng.record_new("decision", "Measure first", "Measure before building (CE-1, CE-2).", DECISION, rid="DEC-1", **kw(key))
    assert dec.id == "DEC-1" and dec.doc.get("body_sha")
    assert [f for f in eng.lint() if f.guard in ("G-D2", "G-D3", "G-D10", "G-W7")] == []  # an `id.reserve` line names no file: no lost record
    assert eng.new("task", "Unrelated", **kw(key)).id == "CE-3"


@pytest.mark.criterion("AC-131")
def test_another_sessions_reserved_id_is_refused_naming_the_holder(eng):
    mine = eng.session_start(actor=ACTOR)
    eng.reserve("task", **kw(mine))
    eng.reserve("decision", **kw(mine))
    other = eng.session_start(actor=ACTOR)
    with pytest.raises(Refusal) as r:
        eng.new("task", "Taken", rid="CE-1", **kw(other))
    assert r.value.message == f"CE-1 is reserved by session {mine}" and "id reserve" in r.value.remedy
    with pytest.raises(Refusal, match=f"DEC-1 is reserved by session {mine}"):
        eng.record_new("decision", "Taken", "words", DECISION, rid="DEC-1", **kw(other))
    assert not list(eng.root.glob("tasks/CE-1*")) and not (eng.root / "decisions").exists()
    assert eng.new("task", "Mine", rid="CE-1", **kw(mine)).id == "CE-1"
    with pytest.raises(Refusal, match="already in use"):  # written once, an id is spent
        eng.new("task", "Again", rid="CE-1", **kw(mine))


@pytest.mark.criterion("AC-131")
def test_the_cli_reserves_and_record_new_takes_the_id(eng, capsys):
    key = eng.session_start(actor=ACTOR)
    base = ["--root", str(eng.root), "--session", key, "--actor", ACTOR]
    assert main([*base, "id", "reserve", "decision", "--count", "2"]) == 0
    assert capsys.readouterr().out.startswith(f"reserved DEC-1, DEC-2 for session {key}")
    assert main([*base, "record", "new", "decision", "Second", "--id", "DEC-2", "--body", "Follows DEC-1.", "--set", "actor=owner", "--set", "decision_status=BUILT"]) == 0
    assert capsys.readouterr().out.startswith("DEC-2: created and stamped")
    assert main([*base, "id", "reserve", "decision", "--count", "0"]) == 2
    assert "a count of 0" in capsys.readouterr().err
