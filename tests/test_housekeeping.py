"""Housekeeping's tier-0 operations (FRAMEWORK §6.11, CE-6): `hk close` closes only on recorded
evidence and G-W9 re-checks every mechanical close (AC-20, AC-165); `hk stamp` stamps
`last_asked` from `asked` receipts, and G-W7 reads the key it stamped (AC-166); an abandoned
stub carries a digest derived from git and the op log (AC-167)."""

import json
import os
import subprocess

import pytest

from context_engine.cli import main
from context_engine.errors import Refusal
from context_engine.working import Engine

from conftest import ASK_BODY, _toml
from test_working import ACTOR, CONFIG, _closes, _git, _repo, eng, kw, receipts, started, task  # noqa: F401  (eng is a fixture)


def _commit(root, message, name="work.txt", text="x\n"):
    """A by-hand commit of one file (a human's, or an agent's outside the engine); its full hash."""
    (root / name).write_text(text, encoding="utf-8")
    _git(root, "add", "--", name)
    subprocess.run(["git", "commit", "-q", "-F", "-", "--", name], cwd=root, check=True, input=message, text=True)
    return _git(root, "rev-parse", "HEAD").strip()


def _ops(eng):
    return [json.loads(ln) for ln in (eng.root / "ops.jsonl").read_text(encoding="utf-8").splitlines() if ln.strip()]


def _g(eng, guard):
    return [f for f in eng.lint() if f.guard == guard]


def _board(eng):
    """A repo with two open tasks, committed, and a session to work in."""
    _repo(eng.root)
    me = started(eng)
    a, b = task(eng, me, "Finished by hand"), task(eng, me, "Not finished")
    eng.commit([], "file the tasks", **kw(me))
    return me, a, b


# -- hk close (AC-20) ------------------------------------------------------------------------


@pytest.mark.criterion("AC-20")
def test_hk_close_closes_only_on_a_commit_whose_trailer_git_reads_names_the_item(eng):
    me, a, b = _board(eng)
    good = _commit(eng.root, f"finish it by hand\n\nCloses: {a.id}\n")
    buried = _commit(eng.root, f"not a trailer\n\nCloses: {b.id}\n\nmore words after it\n", "other.txt")
    with pytest.raises(Refusal, match=rf"does not carry `Closes: {b.id}` as a trailer"):
        eng.hk_close(b.id, buried, **kw(me))
    with pytest.raises(Refusal, match=rf"does not carry `Closes: {a.id}`"):
        eng.hk_close(a.id, buried, **kw(me))  # a commit naming another item is no evidence for this one
    with pytest.raises(Refusal, match="git knows no commit"):
        eng.hk_close(a.id, "0123456789abcdef", **kw(me))
    with pytest.raises(Refusal, match="exactly one piece of evidence"):
        eng.hk_close(a.id, **kw(me))
    out = eng.hk_close(a.id, good[:9], **kw(me))
    assert out.startswith(f"{a.id}: closed (done in {good[:7]} (its `Closes: {a.id}` trailer, checked in git))"), out
    rec = eng.store.get(a.id)
    assert rec.doc.get("state") == "closed" and f"closed: done in {good[:7]} (its `Closes: {a.id}` trailer" in rec.doc.body
    line = [o for o in _ops(eng) if o["op"] == "close" and o["id"] == a.id][-1]
    assert line["mechanical"] is True and line["session"] == me, line
    msg = _git(eng.root, "log", "-1", "--format=%B")
    assert msg.startswith(f"{a.id}: close; done in {good[:7]}") and f"Closes: {a.id}" in msg, msg  # the close is a milestone
    assert eng.store.get(b.id).doc.get("state") == "open"
    assert _g(eng, "G-W9") == []
    eng.reopen(a.id, "not done after all", **kw(me))
    with pytest.raises(Refusal, match=rf"log already cites {good[:7]}"):
        eng.hk_close(a.id, good, **kw(me))  # a reopen outweighs the trailer it was closed on


@pytest.mark.criterion("AC-20")
def test_hk_close_takes_a_ledger_entry_whose_rows_name_the_item_closed(eng):
    me = started(eng)
    a, b = task(eng, me, "One"), task(eng, me, "Two")
    eng.session_close(me, actor=ACTOR, rows=f"{a.id} (closed); {b.id} (created)", summary=["did it"], receipts=receipts())
    hk = started(eng)
    with pytest.raises(Refusal, match=rf"no finished entry {me} whose `rows:` names {b.id} closed"):
        eng.hk_close(b.id, ledger=me, **kw(hk))
    with pytest.raises(Refusal, match=rf"no finished entry {hk} "):
        eng.hk_close(a.id, ledger=hk, **kw(hk))  # an open stub is no record of a close
    assert eng.hk_close(a.id, ledger=me, **kw(hk)).startswith(f"{a.id}: closed (closed in session {me} (its ledger entry's rows name it closed))")
    assert _g(eng, "G-W9") == []
    later = started(eng)
    eng.reopen(a.id, "not done after all", **kw(later))
    assert _g(eng, "G-W9") == []  # G-W9 reads the log before the close: a later reopen does not turn it red
    with pytest.raises(Refusal, match=rf"{a.id} was reopened in session {later}, after session {me}"):
        eng.hk_close(a.id, ledger=me, **kw(later))  # a reopen outweighs the old rows


@pytest.mark.criterion("AC-20")
def test_hk_close_refuses_a_ledger_entry_whose_session_closed_the_item_that_was_reopened_since(eng):
    """Session A closed it and its rows say so; session B reopened it. A's rows are no evidence
    that it is done now (the 2026-10-30a review's probe). B started before A, as concurrent
    sessions do, so A's own close line, not a later reopen, is what shows it."""
    b_key = started(eng)
    a_key = started(eng)
    c = task(eng, a_key, "Closed then reopened")
    eng.close(c.id, "done", **kw(a_key))
    eng.session_close(a_key, actor=ACTOR, rows=f"{c.id} (closed)", summary=["did it"], receipts=receipts())
    eng.reopen(c.id, "found a bug, not done", **kw(b_key))
    with pytest.raises(Refusal, match=rf"{c.id}'s log has a close from session {a_key}: it was closed then, and has been reopened since"):
        eng.hk_close(c.id, ledger=a_key, **kw(b_key))
    assert eng.store.get(c.id).doc.get("state") == "open"
    eng.close(c.id, f"closed in session {a_key} (its ledger entry's rows name it closed)", mechanical=True, **kw(b_key))  # skipped the check
    red = _g(eng, "G-W9")
    assert len(red) == 1 and f"cites the ledger entry {a_key}, but {c.id}'s log has a close from session {a_key}" in red[0].message, red


@pytest.mark.criterion("AC-20")
def test_hk_close_scan_closes_what_a_trailer_names_and_skips_a_reopened_close_and_questions(eng):
    me, a, b = _board(eng)
    q = eng.ask_new("Which way?", body=ASK_BODY, pri="LATER", **kw(me))
    c = task(eng, me, "Closed then reopened")
    eng.close(c.id, "done", **kw(me))  # its own close commit carries `Closes: <c>` and shows it closed
    eng.reopen(c.id, "found a bug", **kw(me))
    eng.commit([], "reopen it", **kw(me))
    _commit(eng.root, f"by hand\n\nCloses: {a.id}\nCloses: {q.id}\n")
    out = eng.hk_close(scan=True, **kw(me))
    assert out.splitlines()[0].startswith(f"{a.id}: closed (done in"), out
    assert f"{c.id}: not closed ({c.id} was already closed in" in out, out
    assert q.id not in out and eng.store.get(q.id).doc.get("state") == "open"  # a question closes only on the owner's answer
    assert eng.store.get(c.id).doc.get("state") == "open" and eng.store.get(b.id).doc.get("state") == "open"
    assert eng.hk_close(scan=True, **kw(me)) == f"{c.id}: not closed ({c.id} was already closed in {_git(eng.root, 'log', '-1', '--format=%h', f'--grep=^{c.id}: close').strip()[:7]} (its close commit), and has been reopened since)"


@pytest.mark.criterion("AC-20")
def test_hk_close_through_the_cli_defaults_its_actor_to_housekeeping(eng, capsys, monkeypatch):
    monkeypatch.delenv("CE_ACTOR", raising=False)  # the --actor default reads it; a session's gate run sets it
    me, a, _ = _board(eng)
    good = _commit(eng.root, f"by hand\n\nCloses: {a.id}\n")
    assert main(["--root", str(eng.root), "--session", me, "hk", "close", a.id, "--commit", good]) == 0
    assert capsys.readouterr().out.startswith(f"{a.id}: closed (done in {good[:7]}")
    assert [o["actor"] for o in _ops(eng) if o["op"] == "close"] == ["process:housekeep"]


@pytest.mark.criterion("AC-169")
def test_one_scan_closing_two_items_commits_once_with_a_closes_trailer_for_each(eng, capsys):
    """Every operation runs in one store batch that commits once (ops.py::Op.call), so a scan
    that closes two items makes one commit, and it must name both: a later close overwrote the
    first one's trailer (the 2026-11-01b plan critic's finding #4)."""
    me, a, b = _board(eng)
    _commit(eng.root, f"by hand\n\nCloses: {a.id}\n")
    _commit(eng.root, f"more by hand\n\nCloses: {b.id}\n", "other.txt")
    assert main(["--root", str(eng.root), "--session", me, "--actor", ACTOR, "hk", "close", "--scan"]) == 0
    out = capsys.readouterr().out
    assert f"{a.id}: closed" in out and f"{b.id}: closed" in out, out
    assert {eng.store.get(a.id).doc.get("state"), eng.store.get(b.id).doc.get("state")} == {"closed"}
    msg = _git(eng.root, "log", "-1", "--format=%B")
    said = _git(eng.root, "log", "-1", "--format=%(trailers:key=Closes,valueonly,separator=%x2C)").strip()
    assert sorted(x.strip() for x in said.split(",")) == sorted([a.id, b.id]), msg  # git reads both as trailers
    assert msg.splitlines()[0] in (f"housekeeping: close {a.id}, {b.id}", f"housekeeping: close {b.id}, {a.id}"), msg
    assert f"{a.id}: close; done in" in msg and f"{b.id}: close; done in" in msg, msg  # each close's own title is kept
    assert _git(eng.root, "status", "--porcelain", "--", "tasks").strip() == ""  # both closes are in that one commit
    assert _g(eng, "G-W9") == []


# -- G-W9: every mechanical close cites evidence that holds (AC-165) --------------------------


@pytest.mark.criterion("AC-165")
def test_g_w9_fails_a_mechanical_close_without_evidence_or_with_evidence_that_does_not_hold(eng):
    me, a, b = _board(eng)
    good = _commit(eng.root, f"by hand\n\nCloses: {a.id}\n")
    plain = _commit(eng.root, "no trailer\n", "other.txt")
    eng.hk_close(a.id, good, **kw(me))
    assert _g(eng, "G-W9") == []
    eng.close(b.id, "done, I am sure", mechanical=True, **kw(me))  # a mechanical close that skipped the check
    red = _g(eng, "G-W9")
    assert len(red) == 1 and red[0].path.startswith(f"tasks/{b.id}-") and "has no close line from session" in red[0].message, red
    assert f"`hk close {b.id} --commit <sha>`" in red[0].remedy
    path = eng.store.get(a.id).path
    path.write_text(path.read_text(encoding="utf-8").replace(f"done in {good[:7]}", f"done in {plain[:7]}"), encoding="utf-8")
    red = [f for f in _g(eng, "G-W9") if a.id in f.message]
    assert len(red) == 1 and f"cites {plain[:7]}, whose trailers do not carry `Closes: {a.id}`" in red[0].message, red
    assert [f.guard for f in eng.lint(working=True) if f.guard == "G-W9"] == ["G-W9", "G-W9"]  # it is a working-state guard


@pytest.mark.criterion("AC-165")
def test_g_w9_and_hk_close_refuse_a_commit_outside_heads_history(eng):
    me, a, _ = _board(eng)
    _git(eng.root, "checkout", "-q", "-b", "side")
    side = _commit(eng.root, f"on another branch\n\nCloses: {a.id}\n", "side.txt")
    _git(eng.root, "checkout", "-q", "main")
    with pytest.raises(Refusal, match=rf"{side[:7]} is not in HEAD's history"):
        eng.hk_close(a.id, side, **kw(me))
    eng.close(a.id, f"done in {side[:7]} (its `Closes: {a.id}` trailer, checked in git)", mechanical=True, **kw(me))  # skipped the check
    red = _g(eng, "G-W9")
    assert len(red) == 1 and f"cites {side[:7]}, which is not in HEAD's history" in red[0].message, red


@pytest.mark.criterion("AC-165")
def test_g_w9_fails_an_unknown_commit_in_a_full_clone_and_trusts_it_without_one(eng):
    """A shallow checkout (CI's) lacks old commits, so there, and with no git, the citation is
    trusted; in a full clone a commit git does not know is no evidence."""
    me = started(eng)
    a = task(eng, me, "One")
    eng.close(a.id, "done in 0123456 (its `Closes: " + a.id + "` trailer, checked in git)", mechanical=True, **kw(me))
    assert _g(eng, "G-W9") == []  # no git at all: trusted
    _repo(eng.root)
    red = _g(eng, "G-W9")
    assert len(red) == 1 and "cites 0123456, which git does not know in this full clone" in red[0].message, red
    _commit(eng.root, "a second commit, so a depth-1 clone is cut off\n")
    shallow = eng.root.parent / "shallow"
    subprocess.run(["git", "clone", "-q", "--depth", "1", f"file://{eng.root.as_posix()}", str(shallow)], check=True, capture_output=True)
    assert _git(shallow, "rev-parse", "--is-shallow-repository").strip() == "true"
    assert [f for f in Engine(shallow).lint() if f.guard == "G-W9"] == []  # the same records, in CI's kind of checkout


# -- hk stamp: last_asked from asked receipts (AC-166) ----------------------------------------


@pytest.mark.criterion("AC-166")
def test_hk_stamp_sets_last_asked_from_the_newest_asked_receipt_and_g_w7_reads_the_stamp(eng):
    first = started(eng)
    q = eng.ask_new("Which way?", body=ASK_BODY, pri="NEXT", **kw(first))
    eng.session_close(first, actor=ACTOR, rows="none", summary=["asked"], receipts=receipts(asked=q.id))  # no `ask raised`
    assert not eng.store.get(q.id).doc.get("last_asked")
    me = started(eng)
    other = eng.ask_new("And this?", body=ASK_BODY, pri="LATER", **kw(me))  # no receipt names it
    out = eng.stamp_asked(**kw(me))
    assert out == f"{q.id}: last_asked {first} (was empty)", out
    rec = eng.store.get(q.id)
    assert rec.doc.get("last_asked") == first and rec.doc.get("updated") == me
    assert not eng.store.get(other.id).doc.get("last_asked")
    line = _ops(eng)[-1]
    assert line["op"] == "hk.stamp_asked" and line["mechanical"] is True and line["as"] == {"last_asked": first} and line["session"] == me, line
    assert _g(eng, "G-W7") == []
    assert eng.stamp_asked(**kw(me)).startswith("no open question")  # idempotent
    eng.ask_raised([q.id], **kw(me))
    assert eng.stamp_asked(**kw(me)).startswith("no open question")  # a newer stamp is never moved back
    path = rec.path
    path.write_text(path.read_text(encoding="utf-8").replace(f"last_asked: {me}", f"last_asked: {first}"), encoding="utf-8")
    assert [f.guard for f in _g(eng, "G-W7")] == ["G-W7"]  # a hand edit still fails


@pytest.mark.criterion("AC-166")
def test_g_w7_fails_a_last_asked_that_is_not_the_key_housekeeping_stamped(eng):
    first = started(eng)
    q = eng.ask_new("Which way?", body=ASK_BODY, pri="NEXT", **kw(first))
    eng.session_close(first, actor=ACTOR, rows="none", summary=["asked"], receipts=receipts(asked=q.id))
    me = started(eng)
    eng.stamp_asked(**kw(me))
    path = eng.store.get(q.id).path
    path.write_text(path.read_text(encoding="utf-8").replace(f"last_asked: {first}", f"last_asked: {me}"), encoding="utf-8")
    red = _g(eng, "G-W7")
    assert len(red) == 1 and f"stamped {first}" in red[0].message, red


# -- the abandoned stub's derived digest (AC-167) ---------------------------------------------


@pytest.mark.criterion("AC-167")
def test_an_abandoned_stub_carries_a_digest_derived_from_git_and_the_op_log(eng):
    _repo(eng.root)
    dead = started(eng)
    t = task(eng, dead, "Its work")
    sha = _commit(eng.root, f"{t.id}: the work\n\nCloses: {t.id}\nSession: {dead}\nCo-Authored-By: x <x@example.com>\n")
    _commit(eng.root, f"looks alike\n\nSession: {dead}b\n", "other.txt")  # another key that starts with it
    task(eng, dead, "Left uncommitted")
    _closes(eng, 3)
    me = started(eng)
    eng.session_abandon(dead, **kw(me))
    lines = sum(1 for o in _ops(eng) if o["session"] == dead)
    assert eng.read_ledger().get(dead).field("derived digest") == f"1 commit with `Session: {dead}` ({sha[:7]}); `Closes:` {t.id}; {lines} op log lines"
    assert lines == 3  # its stub's start and its two tasks


@pytest.mark.criterion("AC-167")
def test_a_digest_without_git_says_no_commits(eng):
    dead = started(eng)
    _closes(eng, 3)
    me = started(eng)
    eng.session_abandon(dead, **kw(me))
    assert eng.read_ledger().get(dead).field("derived digest") == f"0 commits with `Session: {dead}`; `Closes:` none; 1 op log line"


# -- session touch: a live session that only reads resets its staleness (AC-172) --------------


@pytest.mark.criterion("AC-172")
def test_session_touch_logs_one_line_writes_no_file_and_resets_staleness(eng, capsys):
    reader = started(eng)
    _closes(eng, 3)
    me = started(eng)
    assert [k for k, *_ in eng.stale_stubs(me)] == [reader]
    ledger = (eng.root / "ledger.md").read_bytes()
    lines = len(_ops(eng))
    assert main(["--root", str(eng.root), "--session", reader, "--actor", ACTOR, "session", "touch"]) == 0
    assert capsys.readouterr().out.startswith(f"{reader}: touched; last active ")
    assert (eng.root / "ledger.md").read_bytes() == ledger  # no file but the op log
    new = _ops(eng)[lines:]
    assert [(o["op"], o["id"], o["session"], o["path"], o["fields"], o["mechanical"]) for o in new] == [("session.touch", reader, reader, "ledger.md", [], False)], new
    assert eng.staleness([reader])[reader][0] == 0
    assert eng.stale_stubs(me) == []
    assert eng.session_abandon(stale=True, **kw(me)).startswith("no stale stubs")
    assert eng.read_ledger().get(reader).kind == "open"


@pytest.mark.criterion("AC-172")
def test_session_touch_is_refused_on_a_stub_that_is_not_open(eng):
    dead = started(eng)
    _closes(eng, 3)
    me = started(eng)
    eng.session_abandon(dead, **kw(me))
    lines = len(_ops(eng))
    with pytest.raises(Refusal, match="this session's stub is `kind: abandoned`") as r:
        eng.session_touch(**kw(dead))
    assert "do the baton it was abandoned with" in r.value.remedy
    eng.session_close(me, actor=ACTOR, rows="none", summary=["done"], receipts=receipts())
    with pytest.raises(Refusal, match=r"`kind: close`") as r:
        eng.session_touch(**kw(me))
    assert f"session start --follows {me}" in r.value.remedy
    assert len(_ops(eng)) == lines + 1  # only the close: a refused touch logs nothing


# -- G-W11: no stale `kind: open` stub (AC-173) -------------------------------------------------


def _w11(e):
    return [f for f in e.lint(working=True) if f.guard == "G-W11"]


@pytest.mark.criterion("AC-173")
def test_g_w11_fails_a_stub_with_3_closes_since_its_last_activity_and_passes_with_2(eng):
    quiet = started(eng)
    _closes(eng, 2)
    assert _w11(eng) == []
    _closes(eng, 1)
    red = _w11(eng)
    assert len(red) == 1 and red[0].path == "ledger.md", red
    assert red[0].message.startswith(f"{quiet} never closed or paused; last active ") and "3 closes or pauses since (window 3" in red[0].message, red
    assert "session touch" in red[0].remedy and "session abandon --stale" in red[0].remedy and f"whether {quiet} is live" in red[0].remedy
    assert [f.guard for f in eng.lint() if f.guard == "G-W11"] == ["G-W11"]  # the full lint runs it too


@pytest.mark.criterion("AC-173")
def test_g_w11_passes_after_session_touch_and_after_session_abandon(eng):
    live, dead = started(eng), started(eng)
    _closes(eng, 3)
    assert sorted(f.message.split()[0] for f in _w11(eng)) == sorted([live, dead])
    eng.session_touch(**kw(live))
    assert [f.message.split()[0] for f in _w11(eng)] == [dead]
    me = started(eng)
    eng.session_abandon(stale=True, **kw(me))
    assert _w11(eng) == []


@pytest.mark.criterion("AC-173")
def test_g_w11_reports_nothing_in_a_shallow_clone(eng):
    started(eng)
    _closes(eng, 3)
    _repo(eng.root)
    assert len(_w11(eng)) == 1  # a full clone
    _commit(eng.root, "a second commit, so a depth-1 clone is cut off\n")
    shallow = eng.root.parent / f"{eng.root.name}-shallow"  # the basetemp is shared: G-W9's test clones to `shallow`
    subprocess.run(["git", "clone", "-q", "--depth", "1", f"file://{eng.root.as_posix()}", str(shallow)], check=True, capture_output=True)
    assert _git(shallow, "rev-parse", "--is-shallow-repository").strip() == "true"
    assert _w11(Engine(shallow)) == []


@pytest.mark.criterion("AC-173")
def test_guards_off_silences_g_w11(eng):
    started(eng)
    _closes(eng, 3)
    assert len(_w11(eng)) == 1
    cfg = json.loads(json.dumps(CONFIG))
    cfg["guards"]["off"] = [*cfg["guards"].get("off", []), "G-W11"]
    (eng.root / "context.toml").write_text(_toml(cfg), encoding="utf-8")
    assert _w11(Engine(eng.root)) == []


# -- hk comment: commits become dated task comments (AC-174) ----------------------------------


def _agent_commit(root, title, key, name="work.txt", closes=""):
    """An agent's commit made outside the engine: its trailer paragraph carries `Session:`."""
    trailers = (f"Closes: {closes}\n" if closes else "") + f"Session: {key}\nCo-Authored-By: x <x@example.com>\n"
    return _commit(root, f"{title}\n\nwhat it did\n\n{trailers}", name, text=title + "\n")


def _comments(eng, rid):
    return [o for o in _ops(eng) if o["op"] == "comment" and o["id"] == rid]


@pytest.mark.criterion("AC-174")
def test_hk_comment_writes_one_dated_mechanical_comment_and_refuses_what_is_not_its_to_say(eng):
    me, a, b = _board(eng)
    sha = _agent_commit(eng.root, f"{a.id}: the first step", me)
    out = eng.hk_comment(a.id, sha[:9], **kw(me))
    assert out == f"{a.id}: comment {sha[:7]}: {a.id}: the first step", out
    assert f"({ACTOR}): {sha[:7]}: {a.id}: the first step" in eng.store.get(a.id).doc.body
    line = _comments(eng, a.id)[-1]
    assert line["mechanical"] is True and line["session"] == me, line
    with pytest.raises(Refusal, match=rf"{a.id}'s log already cites {sha[:7]}"):
        eng.hk_comment(a.id, sha, **kw(me))  # the full hash: the log's short one is its prefix
    other = _agent_commit(eng.root, f"{b.id}: its own step", me, "b.txt")
    with pytest.raises(Refusal, match=rf"title does not lead with {a.id}"):
        eng.hk_comment(a.id, other, **kw(me))
    assert eng.hk_comment(a.id, other, text="this step also unblocked it", **kw(me)).startswith(f"{a.id}: comment this step")  # tier 1's text
    _git(eng.root, "checkout", "-q", "-b", "side")
    side = _agent_commit(eng.root, f"{a.id}: on a side branch", me, "side.txt")
    _git(eng.root, "checkout", "-q", "main")
    with pytest.raises(Refusal, match=rf"{side[:7]} is not in HEAD's history"):
        eng.hk_comment(a.id, side, **kw(me))
    done = _agent_commit(eng.root, f"{a.id}: finish it", me, "done.txt", closes=a.id)
    with pytest.raises(Refusal, match=rf"carries `Closes: {a.id}`: left for hk close") as r:
        eng.hk_comment(a.id, done, **kw(me))
    assert f"hk close {a.id} --commit {done[:7]}" in r.value.remedy
    eng.close(b.id, "done", **kw(me))
    with pytest.raises(Refusal, match=rf"{b.id} is closed"):
        eng.hk_comment(b.id, other, **kw(me))
    assert len(_comments(eng, a.id)) == 2 and _comments(eng, b.id) == []


@pytest.mark.criterion("AC-174")
def test_hk_comment_scan_comments_its_range_once_and_leaves_closes_to_hk_close(eng):
    me, a, b = _board(eng)
    one = _agent_commit(eng.root, f"{a.id}: step one", me, "1.txt")
    two = _agent_commit(eng.root, f"{a.id}, {b.id}: step two", me, "2.txt")
    foreign = _commit(eng.root, f"{b.id}: by hand\n", "3.txt")
    fin = _agent_commit(eng.root, f"{b.id}: finish it", me, "4.txt", closes=b.id)
    eng.session_close(me, actor=ACTOR, rows="none", summary=["worked"], receipts=receipts())
    nxt = started(eng)  # its range: after me's start head, up to its own
    later = _agent_commit(eng.root, f"{a.id}: after nxt started", nxt, "5.txt")  # the next session's range
    out = eng.hk_comment(scan=True, **kw(nxt)).splitlines()
    assert out[:3] == [f"{a.id}: comment {one[:7]}: {a.id}: step one", f"{a.id}: comment {two[:7]}: {a.id}, {b.id}: step two",
                       f"{b.id}: comment {two[:7]}: {a.id}, {b.id}: step two"], out
    assert f"{foreign[:7]}: foreign: reconcile (no `Session:` line; procedures § Reconciling foreign commits)" in out
    assert f"{fin[:7]} {b.id}: skipped ({fin[:7]} carries `Closes: {b.id}`: left for hk close (`hk close {b.id} --commit {fin[:7]}`))" in out
    assert not any(later[:7] in ln for ln in out)
    assert {o["mechanical"] for o in _comments(eng, a.id) + _comments(eng, b.id)} == {True}
    log = (eng.root / "ops.jsonl").read_bytes()
    again = eng.hk_comment(scan=True, **kw(nxt))
    assert (eng.root / "ops.jsonl").read_bytes() == log, again  # a second run writes nothing
    assert f"{one[:7]} {a.id}: skipped ({a.id}'s log already cites {one[:7]})" in again
    assert eng.hk_close(scan=True, **kw(nxt)).startswith(f"{b.id}: closed (done in {fin[:7]}")  # the comment did not block it
    eng.session_close(nxt, actor=ACTOR, rows="none", summary=["housekept"], receipts=receipts())
    third = started(eng)
    out = eng.hk_comment(scan=True, **kw(third))
    assert out == f"{a.id}: comment {later[:7]}: {a.id}: after nxt started", out  # nothing from before its baseline


@pytest.mark.criterion("AC-174")
def test_hk_comment_scan_without_a_ledger_entry_needs_since_and_the_cli_signs_as_housekeeping(eng, capsys, monkeypatch):
    monkeypatch.delenv("CE_ACTOR", raising=False)
    me, a, _ = _board(eng)
    sha = _agent_commit(eng.root, f"{a.id}: a step", me)
    with pytest.raises(Refusal, match="has no ledger entry") as r:
        eng.hk_comment(scan=True, **kw("2026-10-09a"))
    assert "--since <rev>" in r.value.remedy
    assert main(["--root", str(eng.root), "--session", me, "hk", "comment", "--scan", "--since", f"{sha}~1"]) == 0
    assert capsys.readouterr().out.startswith(f"{a.id}: comment {sha[:7]}: {a.id}: a step")
    assert [o["actor"] for o in _comments(eng, a.id)] == ["process:housekeep"]


# -- hk run: tier-0 housekeeping in one call, and orient's owed line (AC-175, AC-176) ----------


def _owed(eng):
    """A repo where every sub-operation of `hk run` has one thing to do: a stale stub, an `asked`
    receipt that stamped nothing, an expired baton, a commit whose title leads with an open task's
    id, and one carrying `Closes:` for another. Returns (the session that runs it, the ids)."""
    me, a, b = _board(eng)
    dead = started(eng)
    eng.session_close(me, actor=ACTOR, rows="none", summary=["filed"], receipts=receipts())
    bt = started(eng)
    baton = eng.baton_add("a skipped step", "no time", **kw(bt)).split(":")[0]
    eng.session_close(bt, actor=ACTOR, rows="none", summary=["left a baton"], receipts=receipts())
    _closes(eng, 2)
    worker = started(eng)
    q = eng.ask_new("Which way?", body=ASK_BODY, pri="LATER", **kw(worker))
    step = _agent_commit(eng.root, f"{b.id}: a step", worker, "step.txt")
    fin = _agent_commit(eng.root, f"{a.id}: finish it", worker, "fin.txt", closes=a.id)  # the objection-1 commit
    eng.session_close(worker, actor=ACTOR, rows="none", summary=["worked"], receipts=receipts(asked=q.id))  # no `ask raised`
    now = started(eng)
    return now, {"a": a.id, "b": b.id, "q": q.id, "dead": dead, "baton": baton, "step": step, "fin": fin}


def _ops_listed(out):
    """The operations a `hk run` reply lists, in order (`  - <operation>: <line>`)."""
    return [ln[4:].split(": ", 1)[0] for ln in out.splitlines() if ln.startswith("  - ") and not ln.startswith("  - not done:")]


def _state(eng):
    files = sorted(p for p in eng.root.rglob("*") if p.is_file() and ".git" not in p.parts and ".context" not in p.parts)
    return {p.relative_to(eng.root).as_posix(): p.read_bytes() for p in files}


@pytest.mark.criterion("AC-175")
def test_hk_run_start_then_close_runs_each_sub_operation_in_order_with_the_hk_actor_rule(eng):
    now, x = _owed(eng)
    before = len(_ops(eng))
    out = eng.hk_run("start", **kw(now))
    heads = [ln.split(":")[0] for ln in out.splitlines() if ln.startswith("- ")]
    assert heads == ["- session abandon --stale", "- hk stamp", "- hk comment --scan"], out
    assert _ops_listed(out) == [f"session abandon {x['dead']}", f"hk stamp {x['q']}", f"hk comment {x['b']} {x['step'][:7]}"], out
    assert f"  - not done: {x['fin'][:7]} {x['a']}: skipped ({x['fin'][:7]} carries `Closes: {x['a']}`: left for hk close" in out, out
    assert out.splitlines()[-2].startswith("not done by hk run (do these rows of procedures § Housekeeping yourself): foreign commits"), out
    new = _ops(eng)[before:]
    assert [(o["op"], o["mechanical"]) for o in new] == [("session.abandon", False), ("hk.stamp_asked", True), ("comment", True)], new
    assert {o["actor"] for o in new} == {ACTOR} and {o["session"] for o in new} == {now}
    assert eng.read_ledger().get(x["dead"]).kind == "abandoned"
    out = eng.hk_run("close", **kw(now))
    assert [ln.split(":")[0] for ln in out.splitlines() if ln.startswith("- ")] == ["- baton expire", "- hk close --scan"], out
    assert _ops_listed(out) == [f"baton expire {x['baton']}", f"hk close {x['a']}"], out
    assert eng.store.get(x["a"]).doc.get("state") == "closed"  # the comment pass left its `Closes:` commit for hk close
    assert "record stamp" in out.splitlines()[-2] and "task touch --mechanical" in out.splitlines()[-2]
    closes = [o for o in _ops(eng) if o["op"] == "close" and o["id"] == x["a"]]
    assert closes[-1]["mechanical"] is True and closes[-1]["actor"] == ACTOR
    assert _g(eng, "G-W9") == [] and _w11(eng) == []
    with pytest.raises(Refusal, match="no housekeeping phase 'middle'"):
        eng.hk_run("middle", **kw(now))


@pytest.mark.criterion("AC-175")
def test_hk_run_through_the_cli_signs_as_housekeeping_and_commits_once(eng, capsys, monkeypatch):
    monkeypatch.delenv("CE_ACTOR", raising=False)
    now, x = _owed(eng)
    head = _git(eng.root, "rev-parse", "HEAD").strip()
    assert main(["--root", str(eng.root), "--session", now, "hk", "run", "start"]) == 0
    assert capsys.readouterr().out.startswith("hk run start:\n- session abandon --stale: 1 operation")
    assert {o["actor"] for o in _ops(eng) if o["session"] == now and o["op"] != "session.start"} == {"process:housekeep"}
    assert _git(eng.root, "rev-list", "--count", f"{head}..HEAD").strip() == "1"  # the abandon is a milestone: one commit for the run
    assert _git(eng.root, "log", "-1", "--format=%s").startswith("engine: ")


@pytest.mark.criterion("AC-176")
def test_hk_run_check_writes_nothing_and_lists_what_the_run_then_does(eng):
    now, x = _owed(eng)
    for phase in ("start", "close"):
        before = _state(eng)
        plan = eng.hk_run(phase, check=True, **kw(now))
        assert _state(eng) == before, phase  # the op log, the ledger and the board are byte-equal
        assert plan.startswith(f"hk run {phase} --check:"), plan
        done = eng.hk_run(phase, **kw(now))
        assert _ops_listed(plan) == _ops_listed(done) and _ops_listed(done), (plan, done)
    assert _ops_listed(eng.hk_run("start", check=True, **kw(now))) == []  # nothing is owed now


@pytest.mark.criterion("AC-176")
def test_orient_without_a_key_shows_what_housekeeping_is_owed_and_nothing_once_it_is_done(eng):
    now, x = _owed(eng)
    text = eng.orient()  # as the SessionStart hook runs it: no key
    assert "## Housekeeping owed" in text, text
    part = text.split("## Housekeeping owed", 1)[1].split("\n## ", 1)[0]
    assert f"1 stale stub ({x['dead']}; if one is yours, `session touch`)" in part, part
    assert f"1 unstamped asked receipt ({x['q']})" in part and "run `hk run start`" in part, part
    eng.hk_run("start", **kw(now))
    assert "Housekeeping owed" not in eng.orient() and "Housekeeping owed" not in eng.orient(now)
    for _ in range(3):  # now its own stub is stale too: orient with no key names it
        k = started(eng)
        eng.session_close(k, actor=ACTOR, rows="none", summary=["nothing"], receipts=receipts(asked=x["q"]))
    assert f"1 stale stub ({now};" in eng.orient()


# -- G-W10: every hk run counts its writes; an optional cap stops it and asks (AC-177) ----------


def _capped(eng, cap):
    cfg = json.loads(json.dumps(CONFIG))
    cfg["housekeeping"] = {"max_writes": cap}
    (eng.root / "context.toml").write_text(_toml(cfg), encoding="utf-8")
    return Engine(eng.root, today=eng.today)


@pytest.mark.criterion("AC-177")
def test_hk_run_ends_with_its_writes_and_the_op_log_lines_it_added(eng):
    _repo(eng.root)
    dead = started(eng)
    task(eng, dead, "Left uncommitted")  # so its abandon files a baton too: two op log lines
    _closes(eng, 3)
    me = started(eng)
    before = len(_ops(eng))
    out = eng.hk_run("start", **kw(me))
    gained = len(_ops(eng)) - before
    assert gained == 2 and [o["op"] for o in _ops(eng)[before:]] == ["session.abandon", "new"], _ops(eng)[before:]
    assert out.splitlines()[-1] == f"hk run start: 1 write, {gained} op log lines; no model (0 tokens)", out
    plan = eng.hk_run("close", check=True, **kw(me))
    assert plan.splitlines()[-1] == "hk run close --check: 0 writes planned; nothing written; no model (0 tokens)", plan


@pytest.mark.criterion("AC-177")
def test_a_max_writes_cap_below_the_plan_refuses_before_any_write_and_anyway_runs_it(eng):
    now, x = _owed(eng)
    capped = _capped(eng, 2)
    before = _state(capped)
    with pytest.raises(Refusal, match=r"hk run start would make 3 writes, cap 2 \(`\[housekeeping\] max_writes`, G-W10\)") as r:
        capped.hk_run("start", **kw(now))
    assert "--anyway" in r.value.remedy and "max_writes" in r.value.remedy
    assert _state(capped) == before  # nothing written
    assert capped.hk_run("start", check=True, **kw(now)).splitlines()[-1] == "hk run start --check: 3 writes planned, cap 2; nothing written; no model (0 tokens)"
    out = capped.hk_run("start", anyway=True, **kw(now))  # on the owner's word
    assert out.splitlines()[-1].startswith("hk run start: 3 writes, "), out
    assert _capped(eng, 2).hk_run("close", **kw(now)).splitlines()[-1].startswith("hk run close: 2 writes, ")  # within the cap


# -- session close in one call (CE-195, DEC-163, AC-185) ------------------------------------------


@pytest.mark.criterion("AC-185")
def test_session_close_does_the_clean_close_in_one_call_and_one_commit(eng, capsys, tmp_path_factory):
    """Close housekeeping, the ledger entry and, only when given, the banner: one command, one
    commit, and the entry says what housekeeping did and what became of the banner."""
    now, x = _owed(eng)
    head = _git(eng.root, "rev-parse", "HEAD").strip()
    words = tmp_path_factory.mktemp("words") / "banner.md"
    words.write_text("- A durable line.\n", encoding="utf-8")
    base = ["--root", str(eng.root), "--actor", ACTOR, "--session", now]
    close = [*base, "session", "close", "--rows", f"{x['a']} (closed)", "--summary", "closed it", "--guards", "gate green", "--read", "board only", "--asked", x["q"]]
    assert main([*close, "--banner-file", str(words), "--seen", eng.banner().sha]) == 0, capsys.readouterr().err
    out = capsys.readouterr().out
    assert out.startswith(f"session {now} closed: ledger entry written (1-line summary); banner replaced (lines 1 -> 1), key {now}, "), out
    assert "\nhk run close:\n- baton expire: 1 operation\n" in out and f"  - hk close {x['a']}: " in out, out
    entry = eng.read_ledger().get(now)
    assert entry.kind == "close" and entry.receipt("banner") == "set", entry.text
    assert entry.receipt("housekeeping").startswith("hk run close: 2 writes, ") and "no model" not in entry.receipt("housekeeping"), entry.text
    assert eng.store.get(x["a"]).doc.get("state") == "closed" and eng.store.get(x["baton"]).doc.get("state") == "expired"
    assert (eng.banner().key, eng.banner().text.strip()) == (now, "- A durable line.")
    assert _git(eng.root, "rev-list", "--count", f"{head}..HEAD").strip() == "1"  # one commit for the whole close
    assert _git(eng.root, "status", "--porcelain", "--", "ops.jsonl", "ledger.md", "HANDOFF.md", "tasks", "working") == ""
    assert _g(eng, "G-W1") == [] and _g(eng, "G-W6") == []
    nxt = started(eng)  # the next close keeps that banner, and still passes G-W1
    assert main([*base[:-2], "--session", nxt, "session", "close", "--rows", "none", "--summary", "s", "--guards", "g", "--read", "r", "--asked", x["q"], "--no-housekeeping"]) == 0
    assert f"; banner kept {now}" in capsys.readouterr().out
    entry = eng.read_ledger().get(nxt)
    assert entry.receipt("banner") == f"kept {now}" and entry.receipt("housekeeping") is None and _g(eng, "G-W1") == []


@pytest.mark.criterion("AC-185")
def test_a_refused_one_call_close_writes_nothing_not_even_housekeeping(eng):
    now, x = _owed(eng)
    before = _state(eng)
    close = {"actor": ACTOR, "rows": "none", "summary": ["s"], "housekeeping": True}
    with pytest.raises(Refusal, match="the banner changed since you read it"):
        eng.session_close(now, receipts=receipts(asked=x["q"]), banner="- new", seen="sha256:stale", **close)
    with pytest.raises(Refusal, match="a banner was given without the hash of the one it replaces"):
        eng.session_close(now, receipts=receipts(asked=x["q"]), banner="- new", **close)
    with pytest.raises(Refusal, match="overdue owner questions"):
        eng.session_close(now, receipts=receipts(), **close)  # the question is not named: refused before housekeeping runs
    assert _state(eng) == before
    (eng.root / "HANDOFF.md").write_text("# HANDOFF\n\nNo banner yet.\n", encoding="utf-8")
    before = _state(eng)
    with pytest.raises(Refusal, match="has no banner yet, and the first close writes it"):
        eng.session_close(now, receipts=receipts(asked=x["q"]), **close)
    assert _state(eng) == before


@pytest.mark.criterion("AC-185")
def test_a_one_call_close_whose_digest_lint_would_fail_is_refused_before_housekeeping_writes(eng):
    """verify-1: the entry's prose (CE-63) is checked before `hk run close` runs, not after it
    wrote, so this refusal too leaves the tree as it was."""
    now, x = _owed(eng)
    cfg = json.loads(json.dumps(CONFIG))
    cfg.setdefault("routes", []).append({"component": "Ledger", "path": "ledger.md", "mode": "append-only", "max_width": 70})
    (eng.root / "context.toml").write_text(_toml(cfg), encoding="utf-8")
    e = Engine(eng.root, today=eng.today)
    before = _state(e)
    with pytest.raises(Refusal, match="would make ledger.md fail G-D1"):
        e.session_close(now, actor=ACTOR, rows="none", summary=["x" * 80], receipts=receipts(asked=x["q"]), housekeeping=True)
    assert _state(e) == before, "housekeeping wrote before the refusal"
    assert e.session_close(now, actor=ACTOR, rows="none", summary=["short"], receipts=receipts(asked=x["q"]), housekeeping=True).startswith(f"session {now} closed")


@pytest.mark.criterion("AC-177")
@pytest.mark.parametrize("table, match", [({"max_write": 1}, "unknown key 'max_write'"), ({"max_writes": "5"}, "is str"), ({"max_writes": -1}, "`max_writes` is -1")])
def test_a_bad_housekeeping_table_fails_the_config(eng, table, match):
    cfg = json.loads(json.dumps(CONFIG))
    cfg["housekeeping"] = table
    (eng.root / "context.toml").write_text(_toml(cfg), encoding="utf-8")
    with pytest.raises(Refusal, match=match):
        Engine(eng.root)
