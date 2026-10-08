"""Working state: session keys and the ledger, the board, owner questions, batons and pauses,
the banner, orient() and the working-state guards (CE-2, AC-10 to AC-17)."""

import datetime as dt
import subprocess

import pytest

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
        "decision": {"type": "Decision", "prefix": "DEC", "dir": "decisions", "mode": "append-only", "required": ["title", "actor", "session", "decision_status"], "enums": {"decision_status": ["PROVISIONAL", "BUILT"]}},
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


@pytest.fixture
def eng(tmp_path):
    (tmp_path / "context.toml").write_text(_toml(CONFIG), encoding="utf-8")
    (tmp_path / "ledger.md").write_text(LEDGER, encoding="utf-8")
    (tmp_path / "HANDOFF.md").write_text(NOTE.format(key="2026-10-07b"), encoding="utf-8")
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


# -- batons and pauses (AC-14, AC-15) ------------------------------------------------------


def _git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True).stdout


@pytest.mark.criterion("AC-14")
def test_pause_open_records_branch_and_dirty_paths_from_git_and_commits_only_itself(eng):
    root = eng.root
    _git(root, "init", "-q", "-b", "feature-x")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "t")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "base")
    key = started(eng)
    (root / "wip.py").write_text("x = 1\n", encoding="utf-8")
    (root / "HANDOFF.md").write_text("# changed\n", encoding="utf-8")
    _git(root, "add", "HANDOFF.md")  # staged by someone else: must not ride along
    out = eng.pause_open("half-built parser", "run the gate, then commit wip.py", evidence="docs/evidence/x.md", **kw(key))
    rec = next(eng.store.records("pause"))
    assert rec.doc.get("branch") == "feature-x"
    assert set(rec.doc.get("uncommitted")) == {"wip.py", "HANDOFF.md", "ledger.md", "ops.jsonl"}
    committed = _git(root, "show", "--name-only", "--format=", "HEAD").split()
    assert committed == [rec.path.relative_to(root).as_posix()]
    status = _git(root, "status", "--porcelain")
    assert "wip.py" in status and "M  HANDOFF.md" in status
    assert rec.id in out and "committed" in out


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
    order = ["## Banner (2026-10-07b)", "where things stand", "## Batons and pauses", "BTN-2", "BTN-1", "## Other open sessions", f"- {other}, opened", "## Board: NOW and NEXT", "The top item", "A next item", "## Raise in chat", "Overdue question?", "## Top item: CE-1", "never move a file", "Traps:", "- trap one", "Read first:", "- docs/x.md"]
    positions = [out.index(s) for s in order]
    assert positions == sorted(positions)
    assert "A later item" not in out
    assert "BTN-2 from " + key + " (yours)" in out  # own batons first


@pytest.mark.criterion("AC-17")
def test_orient_never_exceeds_its_cap_and_says_where_the_rest_is(eng):
    huge = "\n".join(f"- trap {i}: " + "x" * 80 for i in range(200))
    key, _ = _busy_repo(eng, traps=huge)
    out = eng.orient(key)
    assert len(out.encode()) <= eng.w.orient_max_bytes
    assert "[cut at the orient cap; the rest: `ce task show CE-1`]" in out
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
    path.write_text(f"---\ntype: Decision\nid: DEC-{n}\ntitle: x\nactor: owner\nsession: 2026-10-07a\ndecision_status: BUILT\n---\n\nWords {n}.\n", encoding="utf-8")
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


def test_a_value_of_the_wrong_declared_type_is_refused(eng):
    key = started(eng)
    rec = task(eng, key)
    with pytest.raises(Refusal, match="not a date"):
        eng.store.set(rec.id, {"created": "2026-10-08"}, **kw(key))  # a quoted string, not a date
    with pytest.raises(Refusal, match="not a key"):
        eng.store.set(rec.id, {"moved": "yesterday"}, **kw(key))
