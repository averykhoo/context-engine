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

from conftest import ASK_BODY
from test_working import ACTOR, _closes, _git, _repo, eng, kw, receipts, started, task  # noqa: F401  (eng is a fixture)


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
def test_hk_close_through_the_cli_defaults_its_actor_to_housekeeping(eng, capsys):
    me, a, _ = _board(eng)
    good = _commit(eng.root, f"by hand\n\nCloses: {a.id}\n")
    assert main(["--root", str(eng.root), "--session", me, "hk", "close", a.id, "--commit", good]) == 0
    assert capsys.readouterr().out.startswith(f"{a.id}: closed (done in {good[:7]}")
    assert [o["actor"] for o in _ops(eng) if o["op"] == "close"] == ["process:housekeep"]


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
