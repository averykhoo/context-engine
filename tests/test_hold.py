"""The held tier (CE-188, DEC-162): an open task at HOLD is never ready. G-W5's NOW rule, the empty-NOW
warnings of `task close` and `session close`, and orient's rerank due count only items not at HOLD;
orient flags a NOW or NEXT item whose dep is held; `task promote` to HOLD on a repo whose task enum
lacks it says how to enable it. HOLD is on the task kind only, last after SOMEDAY, in the kit's
template and here. The rerank's skipping of HOLD is procedure (procedures.md § Rerank), not code."""

import copy
import tomllib
from pathlib import Path

import pytest

from test_working import ACTOR, CONFIG, WARN, _engine, eng, guards, kw, receipts, started, task  # noqa: F401  (eng is a fixture)

from context_engine.errors import Refusal

from conftest import ASK_BODY

ROOT = Path(__file__).resolve().parent.parent
PARKED = "## Next work waits on parked items: tell the owner\n"


def held(tmp_path):
    """The shared fixture config with HOLD added to the task kind's enum only (the question kind keeps
    test_working's STATES, which other tests read)."""
    cfg = copy.deepcopy(CONFIG)
    cfg["kinds"]["task"]["enums"] = {"state": ["open", "closed"], "pri": ["NOW", "NEXT", "LATER", "SOMEDAY", "HOLD"]}
    return _engine(tmp_path, cfg)


@pytest.mark.criterion("AC-193")
def test_a_board_of_held_items_needs_no_now_item(tmp_path):
    e = held(tmp_path)
    key = started(e)
    task(e, key, "Held", pri="HOLD")
    assert guards(e, "G-W5") == []
    assert e.rerank_due() == []
    assert "Rerank due" not in e.orient(key)
    task(e, key, "Later")
    [f] = guards(e, "G-W5")
    assert f.message == "NOW holds 0 (none); the cap is exactly 1"
    assert e.rerank_due() == ["NEXT holds no task, 1 open: the sprint is done"]  # 1, not 2: the held task does not count


@pytest.mark.criterion("AC-193")
def test_closing_the_now_item_leaves_no_warning_when_only_held_items_stay_open(tmp_path):
    e = held(tmp_path / "a")
    key = started(e)
    now = task(e, key, "Now", pri="NOW")
    task(e, key, "Held", pri="HOLD")
    out = e.close(now.id, msg="done", **kw(key))
    assert "G-W5 is red" not in out, out
    control = held(tmp_path / "b")  # the same close with a LATER item open: the warning is there to be lost
    key = started(control)
    now = task(control, key, "Now", pri="NOW")
    task(control, key, "Later")
    assert "G-W5 is red until NOW is refilled" in control.close(now.id, msg="done", **kw(key))


@pytest.mark.criterion("AC-193")
def test_a_session_close_over_a_held_only_board_does_not_warn(tmp_path):
    e = held(tmp_path)
    key = started(e)
    task(e, key, "Held", pri="HOLD")
    out = e.session_close(key, actor=ACTOR, rows="x", summary=["y"], receipts=receipts())
    assert out.startswith(f"session {key} closed: ledger entry written")
    assert WARN not in out, out


@pytest.mark.criterion("AC-193")
def test_orient_flags_next_work_that_waits_on_a_held_item(tmp_path):
    e = held(tmp_path)
    key = started(e)
    h = task(e, key, "Held", pri="HOLD")
    n = task(e, key, "Next work", pri="NEXT", deps=[h.id])
    task(e, key, "Now", pri="NOW")
    section = e.orient(key).split(PARKED, 1)[1].split("\n## ", 1)[0]
    assert section.splitlines() == [f"- {n.id} (NEXT) waits on {h.id}, which is HOLD (held): drop the dep, promote it, or re-rank {n.id}"], section
    e.promote(h.id, "LATER", **kw(key))
    assert PARKED not in e.orient(key)


@pytest.mark.criterion("AC-193")
def test_task_list_sorts_held_items_last(tmp_path):
    e = held(tmp_path)
    key = started(e)
    h = task(e, key, "Held", pri="HOLD")
    s = task(e, key, "Someday", pri="SOMEDAY")
    l = task(e, key, "Later")  # noqa: E741
    rows = e.list()
    order = [rid for row in rows for rid in (h.id, s.id, l.id) if row.split()[1] == rid]
    assert order == [l.id, s.id, h.id], rows


@pytest.mark.criterion("AC-193")
def test_promote_to_hold_without_the_tier_names_the_enum(eng):
    key = started(eng)
    t = task(eng, key, "Later")
    with pytest.raises(Refusal) as exc:
        eng.promote(t.id, "HOLD", **kw(key))
    assert "HOLD" in exc.value.remedy and "[kinds.task]" in exc.value.remedy and "context.toml.template" in exc.value.remedy, exc.value.remedy
    assert exc.value.remedy.startswith("use one of NOW, NEXT, LATER, SOMEDAY; ")
    q = eng.ask_new("A question", body=ASK_BODY, pri="LATER", **kw(key))
    with pytest.raises(Refusal) as exc:
        eng.promote(q.id, "HOLD", **kw(key))
    assert exc.value.remedy == "use one of NOW, NEXT, LATER, SOMEDAY"  # a question is never held


@pytest.mark.criterion("AC-193")
@pytest.mark.parametrize("rel", ["context.toml", "src/context_engine/kit/context.toml.template"])
def test_hold_is_on_the_task_kind_only_in_the_kit_and_here(rel):
    kinds = tomllib.loads((ROOT / rel).read_text(encoding="utf-8"))["kinds"]
    assert kinds["task"]["enums"]["pri"][-1] == "HOLD"
    assert "HOLD" not in kinds["question"]["enums"]["pri"]


@pytest.mark.criterion("AC-193")
def test_an_open_question_is_not_held(tmp_path):
    e = held(tmp_path)
    key = started(e)
    task(e, key, "Held", pri="HOLD")
    e.ask_new("A question", body=ASK_BODY, pri="LATER", **kw(key))
    assert [f.message for f in guards(e, "G-W5")] == ["NOW holds 0 (none); the cap is exactly 1"]
