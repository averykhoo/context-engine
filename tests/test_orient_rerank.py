"""Orient says "rerank due" (CE-99, DEC-64 and its 2026-10-20f amendment; FRAMEWORK §5.2): only
when NEXT holds no task while tasks are open. NOW does not count, owner questions do not count,
and the charter's `Last rerank:` line is quoted, never a trigger. It flags the rerank; it never
runs it."""

import pytest

from test_working import CONFIG, _toml, eng, kw, started, task  # noqa: F401  (eng is a fixture)

from context_engine.working import Engine

from conftest import ASK_BODY


def with_charter(root, last: str | None) -> Engine:
    cfg = {**CONFIG, "guards": {**CONFIG["guards"], "charter": "charter.md"}}
    (root / "context.toml").write_text(_toml(cfg), encoding="utf-8")
    line = "" if last is None else f"Last rerank: {last}\n\n"
    (root / "charter.md").write_text(f"# Charter\n\n| # | Goal |\n|---|---|\n| G-1 | one |\n\n## Next milestone\n\n{line}", encoding="utf-8")
    return Engine(root)


@pytest.mark.criterion("AC-87")
def test_orient_says_rerank_due_only_when_next_holds_no_task(eng):
    key = started(eng)
    assert eng.rerank_due() == []  # an empty board: nothing to rank
    task(eng, key, "Later work")
    assert eng.rerank_due() == ["NEXT holds no task, 1 open: the sprint is done"]
    eng.ask_new("A question", body=ASK_BODY, pri="NEXT", **kw(key))  # an owner question waits on the owner, not on a rank
    assert len(eng.rerank_due()) == 1
    out = eng.orient(key)
    assert "## Rerank due: tell the owner\n- NEXT holds no task" in out
    assert "## Top item\nno NOW item: rerank due (above)" in out
    task(eng, key, "Now work", pri="NOW")  # a task at NOW does not stand in for NEXT
    assert eng.rerank_due() == ["NEXT holds no task, 2 open: the sprint is done"]
    task(eng, key, "Next work", pri="NEXT")
    assert eng.rerank_due() == []
    assert "Rerank due" not in eng.orient(key)


@pytest.mark.criterion("AC-87")
def test_orient_does_not_say_rerank_due_while_next_holds_a_task_and_now_is_empty(eng):
    task(eng, started(eng), "Next work", pri="NEXT")
    assert eng.rerank_due() == []


@pytest.mark.criterion("AC-87")
@pytest.mark.parametrize("last", [None, "never", "yesterday", "2026-10-08b"])
def test_the_charters_last_rerank_line_is_quoted_never_a_trigger(eng, last):
    e = with_charter(eng.root, last)
    key = started(e)
    rid = task(e, key, "Next work", pri="NEXT").id
    assert e.rerank_due() == []  # no line, `never`, a non-key or an old key: none of them make it due
    e.promote(rid, "LATER", **kw(key))
    tail = f" (last rerank: {last})" if last else ""
    assert e.rerank_due() == [f"NEXT holds no task, 1 open: the sprint is done{tail}"]
