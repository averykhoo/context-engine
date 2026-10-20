"""Orient says "rerank due" (CE-99, DEC-64 and its 2026-10-20b amendment, DEC-68; FRAMEWORK
§5.2): when NOW and NEXT hold no task while tasks are open, and when the charter's `Last rerank:`
line is missing, `never`, not a session key, or older than an owner decision or story. It flags
the rerank; it never runs it."""

import pytest

from test_working import CONFIG, _toml, eng, kw, started, task  # noqa: F401  (eng is a fixture)

from context_engine.working import Engine


def with_charter(root, last: str | None) -> Engine:
    cfg = {**CONFIG, "guards": {**CONFIG["guards"], "charter": "charter.md"}}
    (root / "context.toml").write_text(_toml(cfg), encoding="utf-8")
    line = "" if last is None else f"Last rerank: {last}\n\n"
    (root / "charter.md").write_text(f"# Charter\n\n| # | Goal |\n|---|---|\n| G-1 | one |\n\n## Next milestone\n\n{line}", encoding="utf-8")
    return Engine(root)


def decision(root, did: str, actor: str = "owner", session: str | None = "2026-10-08a", decided: str = "2026-10-08") -> None:
    p = root / "decisions" / f"{did}-x.md"
    p.parent.mkdir(exist_ok=True)
    s = f"session: {session}\n" if session else ""
    p.write_text(f"---\ntype: Decision\nid: {did}\ntitle: t\nactor: {actor}\ndecided: {decided}\n{s}decision_status: PROVISIONAL\n---\n\nwhy\n", encoding="utf-8")


@pytest.mark.criterion("AC-87")
def test_orient_says_rerank_due_when_now_and_next_hold_no_task(eng):
    key = started(eng)
    assert eng.rerank_due() == []  # an empty board: nothing to rank
    task(eng, key, "Later work")
    assert eng.rerank_due() == ["NOW and NEXT hold no task, 1 open below them: the sprint is done"]
    eng.ask_new("A question", pri="NEXT", **kw(key))  # an owner question waits on the owner, not on a rank
    assert len(eng.rerank_due()) == 1
    out = eng.orient(key)
    assert "## Rerank due: tell the owner\n- NOW and NEXT hold no task" in out
    assert "## Top item\nno NOW item: rerank due (above)" in out
    task(eng, key, "Next work", pri="NEXT")
    assert eng.rerank_due() == []
    assert "Rerank due" not in eng.orient(key)


@pytest.mark.criterion("AC-87")
def test_orient_says_rerank_due_when_an_owner_record_is_newer_than_the_last_rerank(eng):
    root = eng.root
    e = with_charter(root, "2026-10-08b")
    key = started(e)
    task(e, key, "Now work", pri="NOW")  # the board is not empty: only the charter can make it due
    decision(root, "DEC-1", session="2026-10-08a")  # older than the rerank
    decision(root, "DEC-2", actor="claude-code/x", session="2026-10-08c")  # an agent's call is not owner direction
    decision(root, "DEC-3", session=None, decided="2026-10-08")  # a bare date on the rerank's day: not newer
    assert e.rerank_due() == []
    decision(root, "DEC-4", actor="human:avery", session="2026-10-08c")
    decision(root, "DEC-5", session=None, decided="2026-10-09")
    assert e.rerank_due() == ["owner records newer than the last rerank (2026-10-08b): DEC-4, DEC-5"]
    assert "## Rerank due: tell the owner\n- owner records newer than the last rerank" in e.orient(key)
    assert with_charter(root, "2026-10-09a").rerank_due() == []


@pytest.mark.criterion("AC-87")
@pytest.mark.parametrize("last, says", [
    (None, "charter.md has no `Last rerank:` line, so no rerank is on record"),
    ("never", "charter.md says `Last rerank: never`"),
    ("yesterday", "charter.md has `Last rerank: yesterday`, which is not a session key"),
])
def test_orient_says_rerank_due_when_the_charter_records_no_usable_rerank(eng, last, says):
    e = with_charter(eng.root, last)
    task(e, started(e), "Now work", pri="NOW")
    assert e.rerank_due() == [says]
