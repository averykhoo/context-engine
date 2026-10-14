"""Working state: session keys and the ledger, the board, owner questions, batons and pauses,
the banner, orient() and the working-state guards (CE-2, AC-10 to AC-17)."""

import copy
import datetime as dt
import re
import shlex
import subprocess

import pytest

from context_engine import __version__
from context_engine import bootstrap as K
from context_engine import ledger as L
from context_engine import okf
from context_engine.cli import main
from context_engine.errors import Refusal
from context_engine.working import Engine

from conftest import _toml

ACTOR = "claude-code/test"
TODAY = dt.date(2026, 10, 8)
BOARD_TYPES = {"created": "date", "moved": "key", "updated": "key", "closed": "key", "deps": "list", "labels": "list", "last_asked": "key", "blocks": "list"}
STATES = {"state": ["open", "closed"], "pri": ["NOW", "NEXT", "LATER", "SOMEDAY"]}
CONFIG = {
    "engine": {"oplog": "ops.jsonl", "lockfile": ".context/engine.lock"},
    "kinds": {
        "task": {"type": "Task", "prefix": "CE", "dir": "tasks", "mode": "replaced", "required": ["title", "pri", "state", "created"], "enums": STATES, "types": BOARD_TYPES},
        "question": {"type": "Question", "prefix": "ASK", "dir": "tasks", "mode": "replaced", "required": ["title", "pri", "state", "created"], "enums": STATES, "types": BOARD_TYPES},
        "decision": {"type": "Decision", "prefix": "DEC", "dir": "decisions", "mode": "append-only", "required": ["title", "actor", "decided", "session", "decision_status"], "enums": {"decision_status": ["PROVISIONAL", "BUILT"]}, "types": {"decided": "date", "session": "key"}},
        "baton": {"type": "Baton", "prefix": "BTN", "dir": "working", "mode": "stamped", "required": ["title", "session", "state"], "enums": {"state": ["open", "done", "expired"]}, "types": {"session": "key"}},
        "pause": {"type": "Pause", "prefix": "PAU", "dir": "working", "mode": "stamped", "required": ["title", "session", "state", "branch", "resume_step"], "enums": {"state": ["open", "done", "expired"]}, "types": {"session": "key", "uncommitted": "list"}},
    },
    "working": {
        "ledger": "ledger.md",
        "handoff": "HANDOFF.md",
        "board": ["task", "question"],
        "task": "task",
        "question": "question",
        "decision": "decision",
        "baton": "baton",
        "pause": "pause",
        "orient_max_bytes": 4000,
    },
    "guards": {"off": ["G-D9"]},  # a fixture's numbers are not tuned, so they carry no provenance
}
LEDGER = """# Session ledger

Newest first.

---

## 2026-10-07b · kind: close

- **rows:** CE-1 (created)
- **receipts:**
  - guards: gate green
  - read: board only
- **summary** (the owner digest):
  - did things
- **Still owed:**
  - nothing

---

## 2026-10-07a · kind: close

- **rows:** none
- **receipts:**
  - guards: gate green
  - read: board only
- **summary** (the owner digest):
  - founding
- **Still owed:**
  - nothing
"""
NOTE = "# HANDOFF\n\n## Banner ({key})\n\n- The banner says where things stand.\n\n## Board\n\n| a | b |\n"
FRAMEWORK = ".".join(__version__.split(".")[:2])  # the framework version this engine implements (DEC-23)


@pytest.fixture
def eng(tmp_path):
    (tmp_path / "context.toml").write_text(_toml(CONFIG), encoding="utf-8")
    (tmp_path / "ledger.md").write_text(LEDGER, encoding="utf-8")
    (tmp_path / "HANDOFF.md").write_text(NOTE.format(key="2026-10-07b"), encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text(f"# contract\n\nframework: {FRAMEWORK}\n", encoding="utf-8")
    return Engine(tmp_path, today=lambda: TODAY)


def started(eng):
    return eng.session_start(actor=ACTOR)


def kw(key):
    return {"session": key, "actor": ACTOR}


def receipts(**extra):
    return {"guards": "gate green", "read": "board only", **extra}


def task(eng, key, title="A task", pri="LATER", **extra):
    return eng.new("task", title, pri=pri, **kw(key), **extra)


# -- session keys (AC-10) ---------------------------------------------------------------


@pytest.mark.parametrize(
    "newest, today, expect",
    [(None, "2026-10-08", "2026-10-08a"), ("2026-10-07c", "2026-10-08", "2026-10-08a"), ("2026-10-08c", "2026-10-08", "2026-10-08d"), ("2026-10-08z", "2026-10-08", "2026-10-08aa"), ("2026-10-09a", "2026-10-08", "2026-10-09b")],
)
def test_next_key_restarts_each_day_and_counts_letters_past_z(newest, today, expect):
    assert L.next_key(newest, dt.date.fromisoformat(today)) == expect


@pytest.mark.criterion("AC-10")
def test_start_mints_one_letter_past_the_newer_of_ledger_and_banner_and_writes_a_stub(eng):
    (eng.root / "HANDOFF.md").write_text(NOTE.format(key="2026-10-08b"), encoding="utf-8")  # banner ahead of the ledger
    key = started(eng)
    assert key == "2026-10-08c"
    led = eng.read_ledger()
    assert (led.entries[0].key, led.entries[0].kind) == ("2026-10-08c", "open")
    assert ACTOR in led.entries[0].field("opened")
    assert [e.key for e in led.entries[1:]] == ["2026-10-07b", "2026-10-07a"]  # older entries untouched
    assert started(eng) == "2026-10-08d"  # the stub itself reserves its key


@pytest.mark.criterion("AC-10")
def test_two_concurrent_starts_get_different_keys(eng, workers):
    workers(eng.root, [["start", "3", f"w{i}"] for i in range(4)])
    keys = [e.key for e in eng.read_ledger().entries if e.kind == "open"]
    assert len(keys) == 12 and len(set(keys)) == 12


# -- close and pause (AC-11) -------------------------------------------------------------


@pytest.mark.criterion("AC-11")
def test_close_finalises_the_stub_with_its_receipts(eng):
    key = started(eng)
    eng.session_close(key, actor=ACTOR, rows="CE-1 (closed)", summary=["built it"], receipts=receipts(), owed=["a push"])
    entry = eng.read_ledger().get(key)
    assert entry.kind == "close"
    assert entry.field("rows") == "CE-1 (closed)"
    assert entry.receipt("guards") == "gate green" and entry.receipt("read") == "board only"
    assert "  - a push" in entry.text
    assert len([e for e in eng.read_ledger().entries if e.key == key]) == 1
    with pytest.raises(Refusal, match="already `kind: close`"):
        eng.session_close(key, actor=ACTOR, rows="x", summary=["y"], receipts=receipts())


@pytest.mark.criterion("AC-11")
@pytest.mark.parametrize(
    "change, match",
    [
        ({"receipts": {"read": "board only"}}, "no `guards` receipt"),
        ({"receipts": {"guards": "green", "read": "  "}}, "no `read` receipt"),
        ({"summary": [f"line {i}" for i in range(8)]}, "8 lines"),
        ({"summary": []}, "0 lines"),
        ({"rows": " "}, "no rows"),
    ],
)
def test_close_refuses_a_malformed_receipt_and_leaves_the_stub(eng, change, match):
    key = started(eng)
    args = {"rows": "CE-1", "summary": ["did it"], "receipts": receipts(), **change}
    before = (eng.root / "ledger.md").read_bytes()
    with pytest.raises(Refusal, match=match):
        eng.session_close(key, actor=ACTOR, **args)
    assert (eng.root / "ledger.md").read_bytes() == before


@pytest.mark.criterion("AC-11")
def test_close_refuses_without_a_stub(eng):
    with pytest.raises(Refusal, match="no entry for 2026-10-08q"):
        eng.session_close("2026-10-08q", actor=ACTOR, rows="x", summary=["y"], receipts=receipts())


@pytest.mark.criterion("AC-11")
def test_close_refuses_until_next_tier_questions_are_named_as_asked(eng):
    key = started(eng)
    q = eng.ask_new("Pick a colour?", pri="NEXT", **kw(key))
    with pytest.raises(Refusal, match=f"does not name {q.id}"):
        eng.session_close(key, actor=ACTOR, rows="x", summary=["y"], receipts=receipts(asked="none"))
    eng.ask_raised([q.id], **kw(key))
    assert q.id in eng.read_ledger().get(key).field("asked")
    eng.session_close(key, actor=ACTOR, rows="x", summary=["y"], receipts=receipts())
    assert eng.read_ledger().get(key).receipt("asked") == q.id  # carried from the stub


def test_a_new_question_asks_for_a_recommendation(eng):
    key = started(eng)
    q = eng.ask_new("Pick a colour?", **kw(key))
    assert "**Recommendation:**" in q.path.read_text(encoding="utf-8")


@pytest.mark.criterion("AC-11")
def test_close_refuses_while_an_overdue_question_is_unraised(eng):
    key = started(eng)
    q = eng.ask_new("Old question?", pri="LATER", **kw(key))
    eng.store.set(q.id, {"last_asked": "2026-09-01a"}, **kw(key))  # 37 days ago
    with pytest.raises(Refusal, match="G-W8"):
        eng.session_close(key, actor=ACTOR, rows="x", summary=["y"], receipts=receipts())
    eng.ask_later(q.id, **kw(key))  # "later" re-stamps but is not an answer
    assert eng.store.get(q.id).doc.get("state") == "open"
    eng.ask_raised([q.id], **kw(key))
    eng.session_close(key, actor=ACTOR, rows="x", summary=["y"], receipts=receipts())


@pytest.mark.criterion("AC-11")
def test_pause_writes_a_pause_entry(eng):
    key = started(eng)
    eng.session_pause(key, actor=ACTOR, rows="CE-2", deferred="the gate; the commit")
    entry = eng.read_ledger().get(key)
    assert entry.kind == "pause" and entry.field("deferred") == "the gate; the commit"


# -- the board (AC-12, AC-13) --------------------------------------------------------------


@pytest.mark.criterion("AC-12")
def test_close_sets_state_and_derives_status_in_place(eng):
    key = started(eng)
    rec = task(eng, key)
    path = rec.path
    eng.close(rec.id, "done in abc123", **kw(key))
    doc = okf.parse(path.read_text(encoding="utf-8"))
    assert (doc.get("state"), doc.get("status"), doc.get("closed")) == ("closed", "deprecated", key)
    assert sorted(p.name for p in (eng.root / "tasks").iterdir()) == [path.name]  # never moved
    assert f"{key} ({ACTOR}): closed: done in abc123" in okf.get_section(doc.body, "Log")
    assert [f for f in eng.lint() if f.guard == "G-W4"] == []
    eng.reopen(rec.id, "not done after all", **kw(key))
    doc = okf.parse(path.read_text(encoding="utf-8"))
    assert (doc.get("state"), doc.get("status"), doc.get("closed")) == ("open", None, None)


@pytest.mark.criterion("AC-12")
@pytest.mark.parametrize("msg", ["", "   "])
def test_close_without_a_message_is_refused(eng, msg):
    key = started(eng)
    rec = task(eng, key)
    before = rec.path.read_bytes()
    with pytest.raises(Refusal, match="without a message"):
        eng.close(rec.id, msg, **kw(key))
    assert rec.path.read_bytes() == before


@pytest.mark.criterion("AC-55")
@pytest.mark.parametrize("next_", [2, 0])
def test_closing_the_only_now_item_closes_and_says_g_w5_is_red_with_the_promote_remedy(eng, next_):
    """CE-36: the close succeeds; its line says what G-W5 will say and names NEXT, or that NEXT is
    empty. It promotes nothing: the next NOW item is the owner's call."""
    key = started(eng)
    now = task(eng, key, "Now", pri="NOW")
    nxt = [task(eng, key, f"Next {i}", pri="NEXT").id for i in range(next_)]
    later = task(eng, key, "Later")
    out = eng.close(now.id, "done in abc123", **kw(key))
    assert eng.store.get(now.id).doc.get("state") == "closed"
    assert "\n" not in out  # a write's text is one line (AC-19)
    short = "NOW holds 0 (none); the cap is exactly 1"
    assert out.startswith(f"{now.id}: closed (done in abc123); G-W5 is red until NOW is refilled: {short}; ")
    assert "ask the owner which item to `task promote <id> NOW`" in out
    assert out.endswith(f"(NEXT holds {', '.join(nxt)})" if nxt else "(NEXT is empty; `task list` shows the rest)")
    assert [f.message for f in guards(eng, "G-W5")] == [short]  # the close and the guard agree
    assert [eng.store.get(i).doc.get("pri") for i in [*nxt, later.id]] == ["NEXT"] * next_ + ["LATER"]  # nothing promoted
    eng.promote((nxt or [later.id])[0], "NOW", **kw(key))
    assert guards(eng, "G-W5") == []


@pytest.mark.criterion("AC-55")
def test_a_close_that_leaves_g_w5_as_it_was_says_nothing_of_it(eng):
    """CE-36: no warning when NOW stays full, when nothing is left open, or when the closed item
    was not at NOW (an empty NOW then was not this close's doing). Each agrees with G-W5."""
    key = started(eng)
    now = task(eng, key, "Now", pri="NOW")
    nxt = task(eng, key, "Next", pri="NEXT")
    assert eng.close(nxt.id, "done", **kw(key)) == f"{nxt.id}: closed (done)"  # NOW still holds one
    assert guards(eng, "G-W5") == []
    assert eng.close(now.id, "done", **kw(key)) == f"{now.id}: closed (done)"  # nothing left open
    assert guards(eng, "G-W5") == []
    a, b = task(eng, key, "A"), task(eng, key, "B")
    assert eng.close(a.id, "done", **kw(key)) == f"{a.id}: closed (done)"  # NOW was already empty
    assert guards(eng, "G-W5")[0].message == "NOW holds 0 (none); the cap is exactly 1"


@pytest.mark.criterion("AC-55")
def test_cli_close_of_the_only_now_item_exits_zero_and_prints_the_warning(eng, capsys):
    key = started(eng)
    now = task(eng, key, "Now", pri="NOW")
    nxt = task(eng, key, "Next", pri="NEXT")
    base = ["--root", str(eng.root), "--actor", ACTOR, "--session", key]
    capsys.readouterr()
    assert main([*base, "task", "close", now.id, "-m", "done"]) == 0
    out = capsys.readouterr().out
    assert "G-W5 is red until NOW is refilled" in out and f"`task promote <id> NOW` (NEXT holds {nxt.id})" in out


@pytest.mark.criterion("AC-55")
def test_answering_an_owner_question_at_now_says_g_w5_is_red_like_a_close(eng):
    """CE-36: `ask answer` closes a board item too; a question at NOW leaves NOW short."""
    key = started(eng)
    q = eng.ask_new("Which way?", pri="NOW", **kw(key))
    nxt = task(eng, key, "Next", pri="NEXT")
    out = eng.ask_answer(q.id, "this way", title="This way", **kw(key))
    short = "NOW holds 0 (none); the cap is exactly 1"
    assert out == (f"{q.id}: answered as DEC-1, closed; unblocked none; G-W5 is red until NOW is refilled: {short}; "
                   f"ask the owner which item to `task promote <id> NOW` (NEXT holds {nxt.id})")
    assert [f.message for f in guards(eng, "G-W5")] == [short]
    q2 = eng.ask_new("Again?", pri="LATER", **kw(key))
    assert eng.ask_answer(q2.id, "no", title="No", **kw(key)) == f"{q2.id}: answered as DEC-2, closed; unblocked none"  # not at NOW: not its doing
    eng.promote(nxt.id, "NOW", **kw(key))
    assert guards(eng, "G-W5") == []


@pytest.mark.criterion("AC-55")
def test_demoting_the_now_item_says_g_w5_is_red_and_other_moves_say_nothing(eng):
    """CE-36: moving the NOW item down empties NOW as surely as closing it."""
    key = started(eng)
    now = task(eng, key, "Now", pri="NOW")
    nxt = task(eng, key, "Next", pri="NEXT")
    out = eng.promote(now.id, "LATER", **kw(key))
    assert out == (f"{now.id}: NOW -> LATER; G-W5 is red until NOW is refilled: NOW holds 0 (none); the cap is exactly 1; "
                   f"ask the owner which item to `task promote <id> NOW` (NEXT holds {nxt.id})")
    assert eng.promote(nxt.id, "NOW", **kw(key)) == f"{nxt.id}: NEXT -> NOW"
    assert eng.promote(now.id, "NEXT", **kw(key)) == f"{now.id}: LATER -> NEXT"
    assert guards(eng, "G-W5") == []


def _engine(tmp_path, cfg):
    tmp_path.mkdir(exist_ok=True)
    (tmp_path / "context.toml").write_text(_toml(cfg), encoding="utf-8")
    (tmp_path / "ledger.md").write_text(LEDGER, encoding="utf-8")
    (tmp_path / "HANDOFF.md").write_text(NOTE.format(key="2026-10-07b"), encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text(f"# contract\n\nframework: {FRAMEWORK}\n", encoding="utf-8")
    return Engine(tmp_path, today=lambda: TODAY)


@pytest.mark.criterion("AC-55")
def test_the_close_says_nothing_of_g_w5_when_it_is_off_or_now_stays_at_or_over_its_cap(tmp_path):
    """CE-36: the warning speaks for G-W5, so it is quiet when G-W5 is off, and when NOW is still at
    or over its cap (refilling NOW is then not the remedy). Below a cap of 2 it speaks."""
    cfg = copy.deepcopy(CONFIG)
    cfg["guards"] = {"off": [*cfg.get("guards", {}).get("off", []), "G-W5"]}
    e = _engine(tmp_path / "off", cfg)
    key = started(e)
    now = task(e, key, "Now", pri="NOW")
    task(e, key, "Next", pri="NEXT")
    assert e.close(now.id, "done", **kw(key)) == f"{now.id}: closed (done)"
    assert guards(e, "G-W5") == []

    cfg = copy.deepcopy(CONFIG)
    cfg["working"]["caps"] = {"NOW": 3}
    e = _engine(tmp_path / "over", cfg)
    key = started(e)
    ids = [task(e, key, f"N{i}", pri="NOW").id for i in range(3)]
    task(e, key, "Next", pri="NEXT")
    cfg["working"]["caps"] = {"NOW": 1}  # the owner lowers the cap: NOW is over it
    e = _engine(tmp_path / "over", cfg)
    assert e.close(ids[0], "done", **kw(key)) == f"{ids[0]}: closed (done)"  # still over: refilling is not the remedy
    assert [f.message for f in guards(e, "G-W5")] == [f"NOW holds 2 ({ids[1]}, {ids[2]}); the cap is exactly 1"]
    assert e.close(ids[1], "done", **kw(key)) == f"{ids[1]}: closed (done)"  # back at its cap
    assert guards(e, "G-W5") == []

    cfg = copy.deepcopy(CONFIG)
    cfg["working"]["caps"] = {"NOW": 2}
    e = _engine(tmp_path / "two", cfg)
    key = started(e)
    a, b = task(e, key, "A", pri="NOW"), task(e, key, "B", pri="NOW")
    nxt = task(e, key, "Next", pri="NEXT")
    out = e.close(a.id, "done", **kw(key))  # below a cap of 2
    assert out.endswith(f"G-W5 is red until NOW is refilled: NOW holds 1 ({b.id}); the cap is exactly 2; "
                        f"ask the owner which item to `task promote <id> NOW` (NEXT holds {nxt.id})")
    e.promote(nxt.id, "NOW", **kw(key))  # the remedy it names works
    assert guards(e, "G-W5") == []


@pytest.mark.criterion("AC-12")
def test_state_and_status_disagreeing_fails_lint(eng):
    key = started(eng)
    rec = task(eng, key)
    eng.store.set(rec.id, {"state": "closed"}, **kw(key))  # a hand edit that skips `close`
    assert [f.path for f in eng.lint() if f.guard == "G-W4"] == [rec.path.relative_to(eng.root).as_posix()]


@pytest.mark.criterion("AC-13")
def test_list_filters_and_sorts_without_reading_bodies(eng):
    key = started(eng)
    a = task(eng, key, "Later one", pri="LATER")
    b = task(eng, key, "The now one", pri="NOW")
    c = task(eng, key, "Next one", pri="NEXT")
    d = task(eng, key, "Done one", pri="NEXT")
    eng.set(c.id, {"labels": "infra, docs"}, **kw(key))
    eng.close(d.id, "done", **kw(key))
    for rec in (a, b, c, d):  # a body no reader could decode: listing must never touch it
        rec.path.write_bytes(rec.path.read_bytes() + b"\n\xff\xfe not utf-8 \xff\n")
    lines = eng.list()
    assert [ln.split()[1] for ln in lines] == [b.id, c.id, a.id]
    assert all("\n" not in ln for ln in lines)
    assert [ln.split()[1] for ln in eng.list(pri="NEXT")] == [c.id]
    assert [ln.split()[1] for ln in eng.list(label="docs")] == [c.id]
    assert [ln.split()[1] for ln in eng.list(state="closed")] == [d.id]
    assert len(eng.list(state=None)) == 4


def test_cli_strings_are_coerced_by_the_declared_types(eng):
    key = started(eng)
    rec = task(eng, key)
    eng.set(rec.id, {"labels": "[a, b]", "due": "2026-10-09"}, **kw(key))
    eng.store.config.kind("task").types["due"] = "date"
    eng.set(rec.id, {"due": "2026-10-09"}, **kw(key))
    text = rec.path.read_text(encoding="utf-8")
    assert "labels: [a, b]\n" in text and "due: 2026-10-09\n" in text
    with pytest.raises(Refusal, match="not a date"):
        eng.set(rec.id, {"due": "tomorrow"}, **kw(key))
    with pytest.raises(Refusal, match="use promote"):
        eng.set(rec.id, {"pri": "NOW"}, **kw(key))


def test_promote_respects_the_tier_caps_and_dep_resolves_ids(eng):
    key = started(eng)
    a = task(eng, key, pri="NOW")
    b = task(eng, key)
    with pytest.raises(Refusal, match="NOW already holds 1"):
        eng.promote(b.id, "NOW", **kw(key))
    eng.promote(a.id, "NEXT", **kw(key))
    eng.promote(b.id, "NOW", **kw(key))
    assert eng.store.get(b.id).doc.get("moved") == key
    eng.dep(b.id, add=[a.id], **kw(key))
    assert eng.store.get(b.id).doc.get("deps") == [a.id]
    with pytest.raises(Refusal, match="no record CE-99"):
        eng.dep(b.id, add=["CE-99"], **kw(key))


def test_comment_section_and_show_slice_the_body(eng):
    key = started(eng)
    rec = task(eng, key)
    for i in range(7):
        eng.comment(rec.id, f"note {i}", **kw(key))
    eng.section(rec.id, "Traps", "- mind the gap", **kw(key))
    out = eng.show(rec.id)
    assert "showing 5 of 7 log entries" in out and out.index("note 6") < out.index("note 2")
    assert "note 1" not in out
    assert eng.show(rec.id, section="Traps").endswith("- mind the gap\n")


# -- owner questions -----------------------------------------------------------------------


def test_answer_records_the_owner_words_as_a_decision_and_unblocks(eng):
    key = started(eng)
    q = eng.ask_new("Red or blue?", **kw(key))
    t = task(eng, key, deps=[q.id])
    out = eng.ask_answer(q.id, "blue, obviously", title="Blue", **kw(key))
    dec = next(eng.store.records("decision"))
    assert dec.doc.get("actor") == "owner" and dec.doc.get("answers") == q.id
    assert '"blue, obviously"' in dec.doc.body
    assert eng.store.get(q.id).doc.get("state") == "closed"
    assert out.endswith(f"unblocked {t.id}")


def test_task_close_refuses_a_question_and_names_ask_answer(eng):
    """FRAMEWORK §5.3: a question closes only on an owner answer (CE-20, audit finding A20)."""
    key = started(eng)
    q = eng.ask_new("Red or blue?", **kw(key))
    before = q.path.read_bytes()
    with pytest.raises(Refusal, match=f"{q.id} is an owner question") as exc:
        eng.close(q.id, "decided it myself", **kw(key))
    assert f"ask answer {q.id}" in exc.value.remedy
    assert q.path.read_bytes() == before  # nothing written
    out = eng.ask_answer(q.id, "blue", title="Blue", **kw(key))  # the one way it closes
    assert out.startswith(f"{q.id}: answered as DEC-")
    assert eng.store.get(q.id).doc.get("state") == "closed"


def test_task_reopen_refuses_an_answered_question_and_names_the_decision_ops(eng):
    """CE-31: an answered question never reopens; its answer is a decision, so the remedy is
    to amend or supersede that decision, or ask a new question. `answered:` is never cleared."""
    cfg = copy.deepcopy(CONFIG)  # this test supersedes a decision, as the remedy says
    cfg["kinds"]["decision"]["enums"]["decision_status"] = ["PROVISIONAL", "BUILT", "SUPERSEDED"]
    (eng.root / "context.toml").write_text(_toml(cfg), encoding="utf-8")
    eng = Engine(eng.root, today=lambda: TODAY)
    key = started(eng)
    q = eng.ask_new("Red or blue?", **kw(key))
    eng.ask_answer(q.id, "blue", title="Blue", **kw(key))
    dec = eng.store.get(q.id).doc.get("answered")["decision"]
    before = q.path.read_bytes()
    with pytest.raises(Refusal, match=f"{q.id} was answered by the owner") as exc:
        eng.reopen(q.id, "the owner changed their mind", **kw(key))
    for op in (f"record amend {dec}", f"decision supersede {dec}", "ask new"):
        assert op in exc.value.remedy
    assert q.path.read_bytes() == before  # nothing written, `answered:` kept
    # the remedy runs as written: each command it names is a real CLI command
    other = eng.ask_answer(eng.ask_new("Which shade?", **kw(key)).id, "navy", title="Navy", **kw(key)).split()[3].rstrip(",")
    fill = {'"<words>"': '"navy, not blue"', '"<question>"': '"Which shade of blue?"', "<new DEC>": other}
    commands = re.findall(r"`((?:record amend|ask new|decision supersede) [^`]*)`", exc.value.remedy)
    assert len(commands) == 3
    for command in commands:
        for k, v in fill.items():
            command = command.replace(k, v)
        assert main(["--root", str(eng.root), "--session", key, "--actor", ACTOR, *shlex.split(command)]) == 0, command
    # after the supersede, the refusal names the decision that stands now, not the replaced one
    with pytest.raises(Refusal) as exc:
        eng.reopen(q.id, "again", **kw(key))
    assert f"was {dec}, superseded by {other}" in exc.value.remedy
    assert f"decision supersede {other}" in exc.value.remedy and f"decision supersede {dec}" not in exc.value.remedy


def test_ask_answer_refuses_an_open_question_that_already_carries_answered(eng):
    """CE-31: a by-hand reopen leaves a question open and answered (G-W4); a second `ask answer`
    would make two decisions answer it and hide that G-W4 failure."""
    key = started(eng)
    q = eng.ask_new("Red or blue?", **kw(key))
    eng.ask_answer(q.id, "blue", title="Blue", **kw(key))
    dec = eng.store.get(q.id).doc.get("answered")["decision"]
    eng.store.set(q.id, {"state": "open", "closed": None}, unset=("status",), **kw(key))  # a hand reopen
    before = q.path.read_bytes()
    decisions = sorted(p.name for p in (eng.root / "decisions").glob("*.md"))
    with pytest.raises(Refusal, match=rf"{q.id} was already answered by the owner \({dec}\)") as exc:
        eng.ask_answer(q.id, "red", title="Red", **kw(key))
    assert "restore `state: closed`" in exc.value.remedy and f"record amend {dec}" in exc.value.remedy
    assert q.path.read_bytes() == before  # `answered:` still names the first decision
    assert sorted(p.name for p in (eng.root / "decisions").glob("*.md")) == decisions  # no second decision


def test_task_set_cannot_clear_answered_to_get_round_the_reopen_refusal(eng):
    key = started(eng)
    q = eng.ask_new("Red or blue?", **kw(key))
    eng.ask_answer(q.id, "blue", title="Blue", **kw(key))
    for call in ({"raw": {"answered": ""}}, {"raw": {}, "unset": ("answered",)}):
        with pytest.raises(Refusal, match="`answered` is changed by an operation"):
            eng.set(q.id, call["raw"], unset=call.get("unset", ()), **kw(key))
    assert eng.store.get(q.id).doc.get("answered")


def test_task_reopen_still_repairs_a_question_closed_without_an_answer(eng):
    """A pre-CE-20 `task close ASK-n` (audit A20) left no `answered:`: reopening it is the repair."""
    key = started(eng)
    q = eng.ask_new("Red or blue?", **kw(key))
    eng.store.set(q.id, {"state": "closed", "status": "deprecated", "closed": key}, **kw(key))  # the old close
    assert eng.reopen(q.id, "closed without an answer (A20)", **kw(key)) == f"{q.id}: reopened"
    assert eng.store.get(q.id).doc.get("state") == "open"


def test_an_open_question_carrying_answered_fails_lint(eng):
    """G-W4 at rest (CE-31): a by-hand reopen of an answered question leaves it open and answered."""
    key = started(eng)
    q = eng.ask_new("Red or blue?", **kw(key))
    eng.ask_answer(q.id, "blue", title="Blue", **kw(key))
    assert [f for f in eng.lint() if f.guard == "G-W4"] == []
    eng.store.set(q.id, {"state": "open", "closed": None}, unset=("status",), **kw(key))  # a hand reopen
    found = [f for f in eng.lint() if f.guard == "G-W4"]
    assert [f.path for f in found] == [q.path.relative_to(eng.root).as_posix()]
    assert "carries `answered:`" in found[0].message and "decision supersede" in found[0].remedy


# -- batons and pauses (AC-14, AC-15) ------------------------------------------------------


def _git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True).stdout


@pytest.mark.criterion("AC-14")
def test_pause_open_records_branch_and_dirty_paths_from_git_and_commits_only_itself(eng):
    """Itself, its op log line and the writes riding along (DEC-36: the session start before it
    is no milestone, so its stub rides with the pause), and nothing else. Its list of
    uncommitted paths leaves out what its own commit carries (INV-45)."""
    root = eng.root
    _git(root, "init", "-q", "-b", "feature-x")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "t")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "base")
    key = started(eng)
    (root / "wip.py").write_text("x = 1\n", encoding="utf-8")
    (root / "HANDOFF.md").write_text("# changed\n", encoding="utf-8")
    _git(root, "add", "HANDOFF.md")  # staged by someone else: must not go into the commit
    out = eng.pause_open("half-built parser", "run the gate, then commit wip.py", evidence="docs/evidence/x.md", **kw(key))
    rec = next(eng.store.records("pause"))
    assert rec.doc.get("branch") == "feature-x"
    assert set(rec.doc.get("uncommitted")) == {"wip.py", "HANDOFF.md"}
    committed = _git(root, "show", "--name-only", "--format=", "HEAD").split()
    assert sorted(committed) == sorted([rec.path.relative_to(root).as_posix(), "ops.jsonl", "ledger.md"])
    status = _git(root, "status", "--porcelain")
    assert "wip.py" in status and "M  HANDOFF.md" in status
    assert rec.id in out and re.search(r"; committed [0-9a-f]{7,}$", out), out


def test_the_pause_commit_ends_with_a_session_trailer(eng):
    """Every agent commit ends with `Session: <key>` (DEC-22, CE-22), the engine's own included."""
    root = eng.root
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "t")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "base")
    key = started(eng)
    eng.pause_open("half-built parser", "run the gate", **kw(key))
    message = _git(root, "log", "-1", "--format=%B")
    trailers = subprocess.run(["git", "interpret-trailers", "--parse"], cwd=root, input=message, check=True, capture_output=True, text=True).stdout
    assert trailers.splitlines() == [f"Session: {key}"], message


def test_the_runbook_pause_commit_carries_the_same_trailer():
    """manual-mode § pause open is the hand fallback of the same commit (CE-22): it must not drift."""
    from pathlib import Path

    runbook = (Path(__file__).resolve().parents[1] / "docs" / "runbooks" / "manual-mode.md").read_text(encoding="utf-8")
    section = runbook.split("### context-engine pause open", 1)[1].split("\n### ", 1)[0]
    assert '-m "Session: <key>"' in section


@pytest.mark.criterion("AC-15")
def test_a_baton_older_than_two_sessions_fails_lint_and_housekeeping_files_a_task(eng):
    k1 = started(eng)
    eng.baton_add("stamp the decisions", "ran out of time", **kw(k1))
    eng.session_close(k1, actor=ACTOR, rows="x", summary=["y"], receipts=receipts())
    for _ in range(2):  # it survives the next two sessions
        assert [f for f in eng.lint() if f.guard == "G-W3"] == []
        assert eng.expire_batons(session=k1) == "expired 0: none"
        k = started(eng)
        eng.session_close(k, actor=ACTOR, rows="x", summary=["y"], receipts=receipts())
    k3 = started(eng)
    g = [f for f in eng.lint() if f.guard == "G-W3"]
    assert len(g) == 1 and "BTN-1" in g[0].message
    out = eng.expire_batons(session=k3)
    assert out == "expired 1: BTN-1->CE-1"
    assert eng.store.get("BTN-1").doc.get("state") == "expired"
    made = eng.store.get("CE-1")
    assert made.doc.get("source") == "BTN-1" and made.doc.get("state") == "open"
    assert [f for f in eng.lint() if f.guard == "G-W3"] == []


def test_baton_done_needs_evidence(eng):
    key = started(eng)
    eng.baton_add("push", "", **kw(key))
    with pytest.raises(Refusal, match="without evidence"):
        eng.baton_done("BTN-1", " ", **kw(key))
    eng.baton_done("BTN-1", "pushed abc123", **kw(key))
    assert eng.store.get("BTN-1").doc.get("state") == "done"


# -- banner (AC-16) ----------------------------------------------------------------------


@pytest.mark.criterion("AC-16")
def test_banner_set_refuses_a_stale_hash_and_takes_a_fresh_one(eng):
    key = started(eng)
    seen = eng.banner().sha
    note = eng.root / "HANDOFF.md"
    note.write_text(note.read_text(encoding="utf-8").replace("where things stand", "where things stand now"), encoding="utf-8")
    before = note.read_bytes()
    with pytest.raises(Refusal, match="changed since you read it"):
        eng.banner_set("- my banner", seen, **kw(key))
    assert note.read_bytes() == before
    eng.banner_set("- my banner", eng.banner().sha, **kw(key))
    b = eng.banner()
    assert (b.key, b.text) == (key, "- my banner")
    assert note.read_text(encoding="utf-8").endswith("## Board\n\n| a | b |\n")


# -- orient (AC-17) ----------------------------------------------------------------------


def _busy_repo(eng, traps="- trap one"):
    other = started(eng)
    key = started(eng)
    eng.baton_add("their baton", "", **kw(other))
    eng.baton_add("my baton", "", **kw(key))
    top = task(eng, key, "The top item", pri="NOW", brief="never move a file")
    eng.section(top.id, "Traps", traps, **kw(key))
    eng.section(top.id, "Read first", "- docs/x.md", **kw(key))
    task(eng, key, "A next item", pri="NEXT")
    task(eng, key, "A later item", pri="LATER")
    q = eng.ask_new("Overdue question?", pri="LATER", **kw(key))
    eng.store.set(q.id, {"last_asked": "2026-09-01a"}, **kw(key))
    return key, other


@pytest.mark.criterion("AC-17")
def test_orient_carries_every_part_in_order_under_the_cap(eng):
    key, other = _busy_repo(eng)
    out = eng.orient(key)
    assert len(out.encode()) <= eng.w.orient_max_bytes
    order = ["## Banner (2026-10-07b)", "where things stand", "## Batons and pauses", "BTN-2", "BTN-1", "## Other open sessions: show the owner, one line each", f"- {other}, opened", "## Board: NOW and NEXT", "The top item", "A next item", "## Raise in chat", "Overdue question?", "## Top item: CE-1", "never move a file", "Traps:", "- trap one", "Read first:", "- docs/x.md"]
    positions = [out.index(s) for s in order]
    assert positions == sorted(positions)
    assert "A later item" not in out
    assert "BTN-2 from " + key + " (yours)" in out  # own batons first


@pytest.mark.criterion("AC-52")
def test_orient_tells_the_session_to_show_the_owner_every_other_open_session(eng):
    heading = "## Other open sessions: show the owner, one line each\n"
    alone = started(eng)
    section = eng.orient(alone).split(heading, 1)[1].split("\n## ", 1)[0]
    assert section.strip().splitlines()[0] == "none"  # said even when there are none
    other = started(eng)
    section = eng.orient(alone).split(heading, 1)[1].split("\n## ", 1)[0]
    assert f"- {other}, opened " in section
    assert f"- {alone}," not in section  # not the session's own stub


@pytest.mark.criterion("AC-17")
def test_orient_never_exceeds_its_cap_and_says_where_the_rest_is(eng):
    huge = "\n".join(f"- trap {i}: " + "x" * 80 for i in range(200))
    key, _ = _busy_repo(eng, traps=huge)
    out = eng.orient(key)
    assert len(out.encode()) <= eng.w.orient_max_bytes
    assert "[cut at the orient cap; the rest: `context-engine task show CE-1`]" in out
    for heading in ("## Banner", "## Batons", "## Other open", "## Board", "## Raise", "## Top item"):
        assert heading in out


# -- the CLI ------------------------------------------------------------------------------


def test_cli_runs_a_session_end_to_end(eng, capsys):
    root = str(eng.root)
    assert main(["--root", root, "--actor", ACTOR, "session", "start"]) == 0
    key = capsys.readouterr().out.split()[1]
    base = ["--root", root, "--actor", ACTOR, "--session", key]
    assert main([*base, "task", "new", "Write the CLI", "--pri", "NOW", "--brief", "one function per op"]) == 0
    assert main([*base, "task", "close", "CE-1"]) == 2
    assert "without a message" in capsys.readouterr().err
    assert main([*base, "task", "close", "CE-1", "-m", "done"]) == 0
    assert main([*base, "session", "close", "--rows", "CE-1 (closed)", "--summary", "built the CLI", "--guards", "green", "--read", "board only"]) == 0
    assert eng.read_ledger().get(key).kind == "close"


def _unstamped(eng, n):
    d = eng.root / "decisions"
    d.mkdir(exist_ok=True)
    path = d / f"DEC-{n}-x.md"
    path.write_text(f"---\ntype: Decision\nid: DEC-{n}\ntitle: x\nactor: owner\ndecided: 2026-10-07\nsession: 2026-10-07a\ndecision_status: BUILT\n---\n\nWords {n}.\n", encoding="utf-8")
    return path


@pytest.mark.criterion("AC-22")
def test_record_stamp_is_all_or_nothing_and_amend_appends(eng, capsys):
    a, b = _unstamped(eng, 1), _unstamped(eng, 2)
    key = started(eng)
    base = ["--root", str(eng.root), "--actor", ACTOR, "--session", key]
    t = task(eng, key)
    assert main([*base, "record", "stamp", "DEC-1", t.id]) == 2  # a task is not append-only
    assert "body_sha" not in a.read_text(encoding="utf-8")  # so DEC-1 was not stamped either
    assert main([*base, "record", "stamp", "DEC-1", "DEC-2"]) == 0
    assert "stamped 2: DEC-1, DEC-2" in capsys.readouterr().out
    assert [f for f in eng.lint() if f.guard == "G-D10"] == []
    assert main([*base, "record", "stamp", "DEC-2"]) == 2  # a stamp is never replaced
    assert main([*base, "record", "amend", "DEC-1", "the owner widened it"]) == 0
    assert "## Amendments" in a.read_text(encoding="utf-8")
    assert [f for f in eng.lint() if f.guard == "G-D10"] == []
    b.write_text(b.read_text(encoding="utf-8").replace("Words 2.", "Other words."), encoding="utf-8")
    assert main([*base, "record", "amend", "DEC-2", "x"]) == 2  # the body moved: restore, then amend


@pytest.mark.criterion("AC-25")
def test_record_new_writes_a_stamped_decision_and_fills_only_now_keys(eng, capsys, tmp_path):
    key = started(eng)
    base = ["--root", str(eng.root), "--actor", ACTOR, "--session", key]
    words = tmp_path / "words.md"
    words.write_text("Owner: *\"keep it\nin one file\"*.\n", encoding="utf-8")
    assert main([*base, "record", "new", "decision", "One file", "--file", str(words), "--set", "actor=owner", "--set", "decision_status=BUILT"]) == 0
    assert "DEC-1: created and stamped" in capsys.readouterr().out
    rec = eng.store.get("DEC-1")
    assert (rec.doc.get("decided"), rec.doc.get("session"), rec.doc.get("actor")) == (dt.date.today(), key, "owner")  # main() builds its own engine on the real clock
    assert "keep it\nin one file" in rec.doc.body
    assert eng.lint() == []  # stamped when created
    assert main([*base, "record", "new", "decision", "No actor", "--body", "x", "--set", "decision_status=BUILT"]) == 2
    assert "no `actor`" in capsys.readouterr().err  # an actor is never guessed
    assert main([*base, "record", "new", "task", "Not here", "--body", "x"]) == 2
    assert "task new" in capsys.readouterr().err


def test_record_amend_and_ask_answer_take_the_owners_words_from_a_file(eng, capsys, tmp_path):
    """CE-73: intake writes owner words to a file, never a heredoc, so every intake command reads
    one: `record amend` and `ask answer` take --file as `record new` does, or the argument, never both."""
    key = started(eng)
    base = ["--root", str(eng.root), "--actor", ACTOR, "--session", key]
    words = tmp_path / "words.md"
    words.write_bytes('\ufeffkeep "it" C:\\one\\file\n\nsecond paragraph\n'.encode("utf-8"))  # PowerShell 5.1's BOM, quotes, backslashes
    assert main([*base, "record", "new", "decision", "One file", "--body", "x", "--set", "actor=owner", "--set", "decision_status=BUILT"]) == 0
    assert main([*base, "record", "amend", "DEC-1", "--file", str(words)]) == 0
    body = eng.store.get("DEC-1").doc.body
    assert f'- **{key} ({ACTOR}):** keep "it" C:\\one\\file\n\n  second paragraph\n' in body and "\ufeff" not in body, body
    assert main([*base, "record", "amend", "DEC-1", "by argument"]) == 0
    assert eng.store.get("DEC-1").doc.body.endswith(f"- **{key} ({ACTOR}):** by argument\n")
    q = eng.ask_new("Which way?", **kw(key))
    assert main([*base, "ask", "answer", q.id, "--file", str(words), "--title", "This way"]) == 0
    assert f"{q.id}: answered as DEC-2" in capsys.readouterr().out
    assert 'keep "it" C:\\one\\file\n\nsecond paragraph' in eng.store.get("DEC-2").doc.body
    q2 = eng.ask_new("Again?", **kw(key))
    before = eng.store.get("DEC-1").doc.body
    for argv, says in ((["record", "amend", "DEC-1", "x", "--file", str(words)], "both as an argument and with --file"),
                       (["ask", "answer", q2.id, "x", "--file", str(words), "--title", "T"], "both as an argument and with --file"),
                       (["record", "amend", "DEC-1"], "neither as an argument nor with --file"),
                       (["ask", "answer", q2.id, "--title", "T"], "neither as an argument nor with --file")):
        assert main([*base, *argv]) == 2, argv
        assert says in capsys.readouterr().err, argv
    assert eng.store.get(q2.id).doc.get("state") == "open" and eng.store.get("DEC-1").doc.body == before
    assert main([*base, "record", "amend", "DEC-1", "--file", str(tmp_path / "gone.md")]) == 2
    assert "there is no file" in capsys.readouterr().err
    for extra in (["x", "y"], ["--bogus"]):  # anything else unrecognized is still a usage error, never the words
        with pytest.raises(SystemExit):
            main([*base, "record", "amend", "DEC-1", *extra])
    assert eng.store.get("DEC-1").doc.body == before


def test_owner_words_after_an_option_land_even_where_argparse_fills_the_positional_too_early(eng, capsys, monkeypatch):
    """CE-73: argparse before about 3.12.7 fills an optional positional with nothing when an option
    comes first, and calls the words unrecognized (`ask answer ASK-1 --title T "<words>"`). The
    words still land. Simulated here, since the gate's Python has the fix."""
    import argparse

    real = argparse.ArgumentParser.parse_known_args

    def old_argparse(self, args=None, namespace=None):
        ns, extra = real(self, args, namespace)
        for name in ("words", "text"):
            if getattr(ns, name, None) is not None and getattr(ns, "op", None) in ("answer", "amend"):
                extra, ns = [*extra, getattr(ns, name)], argparse.Namespace(**{**vars(ns), name: None})
        return ns, extra

    monkeypatch.setattr(argparse.ArgumentParser, "parse_known_args", old_argparse)
    key = started(eng)
    base = ["--root", str(eng.root), "--actor", ACTOR, "--session", key]
    q = eng.ask_new("Which way?", **kw(key))
    assert main([*base, "ask", "answer", q.id, "--title", "This way", "this way, said after the title"]) == 0
    assert "this way, said after the title" in eng.store.get("DEC-1").doc.body
    assert main([*base, "record", "amend", "DEC-1", "amended"]) == 0
    assert eng.store.get("DEC-1").doc.body.endswith(f"- **{key} ({ACTOR}):** amended\n")


# -- routing (G-R1) -----------------------------------------------------------------------


ROUTES = [
    {"component": "Ledger", "path": "ledger.md", "mode": "append-only"},
    {"component": "Stories", "path": "stories", "pattern": "US-n-<slug>.md", "mode": "append-only", "note": "owner's words"},
    {"component": "Scratch", "path": ".scratch", "mode": "throwaway", "optional": True},
]


def routed(tmp_path, routes):
    (tmp_path / "context.toml").write_text(_toml({**CONFIG, "routes": routes}), encoding="utf-8")
    (tmp_path / "ledger.md").write_text(LEDGER, encoding="utf-8")
    (tmp_path / "HANDOFF.md").write_text(NOTE.format(key="2026-10-07b"), encoding="utf-8")
    return Engine(tmp_path, today=lambda: TODAY)


@pytest.mark.criterion("AC-24")
def test_routes_print_and_a_missing_routed_path_fails_lint(tmp_path, capsys):
    eng = routed(tmp_path, ROUTES)
    (tmp_path / "stories").mkdir()
    assert main(["--root", str(tmp_path), "routes"]) == 0
    assert capsys.readouterr().out.splitlines() == [
        "Ledger: ledger.md (append-only)",
        "Stories: stories/US-n-<slug>.md (append-only); owner's words",
        "Scratch: .scratch (throwaway)",
    ]
    assert [f for f in eng.lint() if f.guard == "G-R1"] == []  # .scratch is optional
    (tmp_path / "stories").rmdir()
    assert [f.message for f in eng.lint() if f.guard == "G-R1"] == ["route 'Stories' points at stories, which does not exist"]


@pytest.mark.criterion("AC-24")
@pytest.mark.parametrize("route, says", [({"component": "X", "path": "x"}, "no `mode`"), ({**ROUTES[0], "dir": "x"}, "unknown key 'dir'")])
def test_a_malformed_route_is_refused_at_load(tmp_path, route, says):
    with pytest.raises(Refusal) as e:
        routed(tmp_path, [route])
    assert says in e.value.message


# -- G-D0: the contract's framework: pin against the installed engine (DEC-23) ---------------


def pinned(eng, text, version="0.5.0.dev0", name="CLAUDE.md"):
    (eng.root / name).write_text(text, encoding="utf-8", newline="")
    return [(f.path, f.message, f.remedy) for f in eng.lint_contract(version)]


@pytest.mark.criterion("AC-35")
@pytest.mark.parametrize("text", ["framework: 0.5\n", "# c\n\nframework: 0.5.*\n", "framework: 0.5 (engine mode since CE-8)\r\n", "framework:0.5"])
def test_a_framework_pin_equal_to_the_engines_major_minor_passes(eng, text):
    assert pinned(eng, text) == []
    assert pinned(eng, text, version="0.5.17") == []  # the engine's patch number is its own


@pytest.mark.criterion("AC-35")
@pytest.mark.parametrize("text, version, says, remedy", [
    ("framework: 0.4\n", "0.5.0.dev0", "`framework: 0.4` does not match the installed engine 0.5.0.dev0 (framework 0.5)", "otherwise run an engine 0.4.x"),
    ("framework: 1.5\n", "0.5.0", "`framework: 1.5` does not match the installed engine 0.5.0 (framework 0.5)", "set `framework: 0.5`"),
    ("framework: 0.5.*\n", "0.6.1", "`framework: 0.5.*` does not match the installed engine 0.6.1 (framework 0.6)", "follow the upgrade procedure"),
])
def test_a_framework_pin_with_another_major_minor_fails_lint_naming_the_remedy(eng, text, version, says, remedy):
    [(path, message, rem)] = pinned(eng, text, version)
    assert path == "CLAUDE.md" and message == says and remedy in rem


@pytest.mark.criterion("AC-35")
@pytest.mark.parametrize("text, says", [
    ("# contract\n\nno pin here\n", "has no `framework:` line"),
    ("  framework: 0.5\n", "has no `framework:` line"),  # only a line of its own is the pin
    ("framework: 0.5-draft\n", "`framework: 0.5-draft` is not a major.minor version"),
    ("framework: 0.5.3\n", "`framework: 0.5.3` is not a major.minor version"),
    ("framework: five\n", "`framework: five` is not a major.minor version"),
    ("framework:\n", "`framework: ` is not a major.minor version"),
])
def test_a_missing_or_garbled_framework_pin_fails_lint(eng, text, says):
    [(_, message, remedy)] = pinned(eng, text)
    assert message.startswith(says) and "framework: 0.5" in remedy


@pytest.mark.criterion("AC-35")
def test_every_pin_and_the_kit_block_marker_must_match(eng):
    stale = "framework: 0.5\n\n<!-- context-engine kit 0.4 begin -->\nframework: 0.4\n<!-- context-engine kit 0.4 end -->\n"
    got = pinned(eng, stale)
    assert [m for _, m, _ in got] == ["`framework: 0.4` does not match the installed engine 0.5.0.dev0 (framework 0.5)", "holds the kit 0.4 block, but the installed engine is framework 0.5"]
    assert "kit/bootloader.md" in got[1][2]
    current = "framework: 0.5\n\n" + (K.KIT / K.BOOTLOADER).read_text(encoding="utf-8")
    copy_contract(eng)
    assert pinned(eng, current) == []
    assert [m for _, m, _ in pinned(eng, current.replace("0.5", "0.4"))] == ["`framework: 0.4` does not match the installed engine 0.5.0.dev0 (framework 0.5)"] * 2 + ["holds the kit 0.4 block, but the installed engine is framework 0.5"]


# -- G-D0's bootloader half (CE-38): the kit block and the contract it imports ----------------


def copy_contract(eng, text=None):
    p = eng.root / K.CONTRACT_DEST
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes((K.KIT / K.CONTRACT).read_bytes() if text is None else text.encode())
    return p


def booted(crlf=False):
    text = "# Ours\n\nour own rule\n\n" + (K.KIT / K.BOOTLOADER).read_text(encoding="utf-8")
    return text.replace("\n", "\r\n") if crlf else text


@pytest.mark.criterion("AC-58")
@pytest.mark.parametrize("crlf", [False, True])
def test_a_bootloader_importing_the_engines_contract_passes(eng, crlf):
    copy_contract(eng, (K.KIT / K.CONTRACT).read_text(encoding="utf-8").replace("\n", "\r\n") if crlf else None)
    assert pinned(eng, booted(crlf)) == []  # a checkout with CRLF line endings is the same text


@pytest.mark.criterion("AC-58")
def test_a_missing_import_target_fails_g_d0(eng):
    [(path, message, remedy)] = pinned(eng, booted())
    assert path == "CLAUDE.md" and message == f"imports @{K.CONTRACT_DEST}, which does not exist, so the framework's rules are not loaded"
    assert "context-engine init" in remedy and K.CONTRACT_DEST in remedy


@pytest.mark.criterion("AC-58")
@pytest.mark.parametrize("edit", [lambda t: t.replace("Never reuse or renumber an id.", "Never reuse an id."), lambda t: t + "\nour own rule\n", lambda t: t.replace("framework: 0.5", "framework: 0.6")])
def test_an_imported_contract_that_is_not_the_engines_fails_g_d0(eng, edit):
    copy_contract(eng, edit((K.KIT / K.CONTRACT).read_text(encoding="utf-8")))
    [(path, message, remedy)] = pinned(eng, booted())
    assert path == K.CONTRACT_DEST and message.startswith("is not the installed engine's kit/contract.md")
    assert "copy the engine's kit/contract.md over it" in remedy and "CLAUDE.md, outside the kit markers" in remedy


@pytest.mark.criterion("AC-58")
def test_an_import_resolves_against_the_file_that_holds_it(eng):
    copy_contract(eng)
    (eng.root / "sub").mkdir()
    (eng.root / "context.toml").write_text(_toml({**CONFIG, "engine": {**CONFIG["engine"], "contract": "sub/CLAUDE.md"}}), encoding="utf-8")
    mapped = Engine(eng.root, today=lambda: TODAY)
    [(_, message, remedy)] = pinned(mapped, booted(), name="sub/CLAUDE.md")
    assert message.startswith(f"imports @{K.CONTRACT_DEST}, which does not exist"), "sub/docs/framework/contract.md, not the root's"
    assert remedy == f"copy the engine's kit/contract.md to sub/{K.CONTRACT_DEST}", "init writes only the root's copy, so it is not the remedy here"


@pytest.mark.criterion("AC-58")
@pytest.mark.parametrize("where", ["CLAUDE.md", K.CONTRACT_DEST])
def test_a_contract_that_is_not_utf8_is_a_red_and_orient_still_runs(eng, where):
    (eng.root / "CLAUDE.md").write_text(booted(), encoding="utf-8")
    p = copy_contract(eng)
    target = eng.root / where
    target.write_bytes(target.read_bytes() + b"\nr\xe9sum\xe9\n")
    [f] = [f for f in eng.lint() if f.guard == "G-D0"]
    assert f.path == where and ("is not UTF-8" in f.message if where == "CLAUDE.md" else f.message.startswith("is not the installed engine's kit/contract.md"))
    out = eng.orient()  # the hook's read: never a traceback
    assert out.split("\n## ", 2)[1].startswith("Contract: fix this first") and p.exists()


@pytest.mark.criterion("AC-58")
def test_the_inline_block_from_before_the_bootloader_fails_g_d0_naming_the_upgrade(eng):
    copy_contract(eng)
    inline = f"# Ours\n\n{K.BEGIN}\nframework: 0.5\n\n### Gate\n\n`make test`\n{K.END}\n"
    [(path, message, remedy)] = pinned(eng, inline)
    assert path == "CLAUDE.md" and message == "holds a kit 0.5 block that copies the framework's rules instead of importing them"
    assert "`## Gate`" in remedy and "kit/bootloader.md" in remedy and "kit README § Upgrade" in remedy


@pytest.mark.criterion("AC-58")
@pytest.mark.parametrize("edit, says", [
    (lambda t: t.replace("is never\nedited here", "may be\nedited here"), "the text between the kit 0.5 markers is not the engine's kit/bootloader.md block"),
    (lambda t: t.replace(f"{K.END}\n", ""), "has the kit 0.5 begin marker but no end marker after it"),
])
def test_a_hand_edited_bootloader_fails_g_d0(eng, edit, says):
    copy_contract(eng)
    text = edit(booted())
    assert text != booted()
    assert [m for _, m, _ in pinned(eng, text)] == [says]


@pytest.mark.criterion("AC-59")
def test_orient_leads_with_a_red_contract_and_says_nothing_when_it_is_green(eng):
    (eng.root / "CLAUDE.md").write_text(booted(), encoding="utf-8")
    out = eng.orient()
    first = out.split("\n## ", 2)[1]
    assert first.startswith("Contract: fix this first\n") and f"imports @{K.CONTRACT_DEST}, which does not exist" in first and "Remedy: run `context-engine init`" in first
    copy_contract(eng)
    assert "Contract" not in eng.orient()
    (eng.root / K.CONTRACT_DEST).unlink()
    (eng.root / "context.toml").write_text(_toml({**CONFIG, "guards": {"off": ["G-D9", "G-D0"]}}), encoding="utf-8")
    assert "Contract" not in Engine(eng.root, today=lambda: TODAY).orient(), "[guards] off G-D0 silences it here too"


@pytest.mark.criterion("AC-35")
def test_a_missing_contract_fails_lint_and_the_contract_can_be_mapped(eng, tmp_path):
    assert [f for f in eng.lint() if f.guard == "G-D0"] == []  # lint runs G-D0 against the installed engine
    (tmp_path / "CLAUDE.md").unlink()
    [f] = [f for f in eng.lint() if f.guard == "G-D0"]
    assert (f.path, f.message) == ("CLAUDE.md", "the contract CLAUDE.md does not exist") and "[engine]" in f.remedy
    (tmp_path / "context.toml").write_text(_toml({**CONFIG, "engine": {**CONFIG["engine"], "contract": "AGENTS.md"}}), encoding="utf-8")
    mapped = Engine(tmp_path, today=lambda: TODAY)
    assert pinned(mapped, "framework: 0.4\n", name="AGENTS.md")[0][:2] == ("AGENTS.md", "`framework: 0.4` does not match the installed engine 0.5.0.dev0 (framework 0.5)")


# -- the other working-state guards (G-W1, G-W2, G-W5, G-W6) -------------------------------


def guards(eng, name):
    return [f for f in eng.lint() if f.guard == name]


def test_a_banner_older_than_the_newest_close_fails_lint(eng):
    assert guards(eng, "G-W1") == []
    key = started(eng)
    eng.session_close(key, actor=ACTOR, rows="x", summary=["y"], receipts=receipts())
    assert len(guards(eng, "G-W1")) == 1
    eng.banner_set("- fresh", eng.banner().sha, **kw(key))
    assert guards(eng, "G-W1") == []


def test_more_than_two_pauses_in_a_row_fail_lint(eng):
    for n in range(3):
        assert guards(eng, "G-W2") == []
        key = started(eng)
        eng.session_pause(key, actor=ACTOR, rows="x", deferred="the gate")
    assert "3 consecutive pause entries" in guards(eng, "G-W2")[0].message


def test_the_newest_close_needs_its_receipts_at_rest(eng):
    assert guards(eng, "G-W6") == []
    path = eng.root / "ledger.md"
    path.write_text(LEDGER.replace("  - read: board only\n", "", 1), encoding="utf-8")
    assert [f.message for f in guards(eng, "G-W6")] == ["the newest close (2026-10-07b) has no `read:` receipt"]


def test_tier_caps_fail_lint(eng):
    key = started(eng)
    a = task(eng, key, pri="NOW")
    assert guards(eng, "G-W5") == []
    b = task(eng, key)
    eng.store.set(b.id, {"pri": "NOW"}, **kw(key))  # a hand edit past the cap
    assert "NOW holds 2" in guards(eng, "G-W5")[0].message
    eng.store.set(a.id, {"pri": "LATER"}, **kw(key))
    eng.store.set(b.id, {"pri": "LATER"}, **kw(key))
    assert "NOW holds 0" in guards(eng, "G-W5")[0].message  # NOW is exactly one


def test_an_empty_now_names_the_promote_step_and_an_overfull_one_the_re_rank(eng):
    """CE-70: a fresh board's first `task new` lands at LATER and turns G-W5 red; its remedy says
    one item goes to NOW, where `re-rank with promote` left a new user guessing."""
    key = started(eng)
    a = task(eng, key)
    [f] = guards(eng, "G-W5")
    assert f.message == "NOW holds 0 (none); the cap is exactly 1"
    assert f.remedy == "ask the owner which open item is worked on now, then `task promote <id> NOW`", f.remedy
    eng.store.set(a.id, {"pri": "NOW"}, **kw(key))
    b = task(eng, key)
    eng.store.set(b.id, {"pri": "NOW"}, **kw(key))  # a hand edit past the cap: demoting is the fix, not promoting
    assert guards(eng, "G-W5")[0].remedy == "re-rank with `promote`"


def test_an_empty_now_with_a_cap_of_two_asks_for_items(tmp_path):
    """CE-70: the G-W5 remedy names the cap when it is not one."""
    cfg = copy.deepcopy(CONFIG)
    cfg["working"]["caps"] = {"NOW": 2}
    e = _engine(tmp_path, cfg)
    key = started(e)
    task(e, key)
    assert guards(e, "G-W5")[0].remedy == "ask the owner which open items are worked on now (NOW holds exactly 2), then `task promote <id> NOW`"


def test_a_value_of_the_wrong_declared_type_is_refused(eng):
    key = started(eng)
    rec = task(eng, key)
    with pytest.raises(Refusal, match="not a date"):
        eng.store.set(rec.id, {"created": "2026-10-08"}, **kw(key))  # a quoted string, not a date
    with pytest.raises(Refusal, match="not a key"):
        eng.store.set(rec.id, {"moved": "yesterday"}, **kw(key))
