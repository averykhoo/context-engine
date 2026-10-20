"""Reconciling foreign commits (FRAMEWORK §6.10 item 2, CE-65): the baseline is the newest
``start head`` another session recorded, so another live session's milestone, which commits the
ledger, never moves it past a foreign commit no session has reconciled."""

from __future__ import annotations

import subprocess

import pytest

from context_engine import ledger as L
from context_engine.working import Engine

from conftest import _toml
from test_working import ACTOR, CONFIG, LEDGER, NOTE, TODAY, receipts


def git(root, *args):
    p = subprocess.run(["git", "-c", "user.name=Agent", "-c", "user.email=agent@example.com", *args], cwd=root, capture_output=True, text=True, encoding="utf-8")
    assert p.returncode == 0, p.stderr
    return p.stdout.strip()


def commit(root, title, *, session=None, author=None, body="", paths=(".",)):
    msg = title + (f"\n\n{body}" if body else "") + (f"\n\nSession: {session}" if session else "")
    who = ["-c", f"user.name={author}"] if author else []
    git(root, "add", "--", *paths)
    subprocess.run(["git", "-c", "user.email=x@example.com", *who, "commit", "-q", "--allow-empty", "-m", msg], cwd=root, check=True, capture_output=True)
    return git(root, "rev-parse", "HEAD")


def human(root, name, title):
    (root / name).write_text(title + "\n", encoding="utf-8")
    return commit(root, title, author="Human", paths=(name,))


@pytest.fixture
def eng(tmp_path):
    (tmp_path / "context.toml").write_text(_toml(CONFIG), encoding="utf-8")
    (tmp_path / "ledger.md").write_text(LEDGER, encoding="utf-8")
    (tmp_path / "HANDOFF.md").write_text(NOTE.format(key="2026-10-07b"), encoding="utf-8")
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "core.autocrlf", "false")
    commit(tmp_path, "founding", session="2026-10-07b")
    return Engine(tmp_path, today=lambda: TODAY)


def found(eng, key):
    return [sha for sha, _, _ in L.foreign_commits(eng.root, eng.read_ledger(), key, "ledger.md")]


def test_start_records_head_and_close_and_pause_keep_it(eng):
    head = git(eng.root, "rev-parse", "HEAD")
    a, b = eng.session_start(actor=ACTOR), eng.session_start(actor=ACTOR)
    assert eng.read_ledger().get(a).field(L.START_HEAD) == head
    eng.session_close(a, actor=ACTOR, rows="none", summary=["did things"], receipts=receipts())
    eng.session_pause(b, actor=ACTOR, rows="none", deferred="the gate")
    led = eng.read_ledger()
    assert (led.get(a).kind, led.get(a).field(L.START_HEAD)) == ("close", head)
    assert (led.get(b).kind, led.get(b).field(L.START_HEAD)) == ("pause", head)


def test_outside_git_the_stub_has_no_start_head(tmp_path):
    (tmp_path / "context.toml").write_text(_toml(CONFIG), encoding="utf-8")
    (tmp_path / "ledger.md").write_text(LEDGER, encoding="utf-8")
    e = Engine(tmp_path, today=lambda: TODAY)
    key = e.session_start(actor=ACTOR)
    assert e.read_ledger().get(key).field(L.START_HEAD) is None


def test_another_sessions_milestone_does_not_hide_an_earlier_foreign_commit(eng):
    """Session A opens; a human commits H; A's milestone commits the ledger (M); B opens. The old
    baseline (the newest ledger commit B did not make) is M, past H, so H was never reconciled."""
    a = eng.session_start(actor=ACTOR)
    assert found(eng, a) == []  # A reconciles at its start: nothing yet
    h = human(eng.root, "notes.txt", "a hand edit")
    commit(eng.root, "CE-1: a milestone", session=a)
    b = eng.session_start(actor=ACTOR)
    assert found(eng, b) == [h]


def foreign_entry(eng, key, sha, by):
    """A ``kind: foreign`` entry naming ``sha``, written by hand as the runbook says."""
    led = eng.read_ledger()
    led.entries.insert(0, L.Entry(key, "foreign", f"## {key} · kind: foreign\n\n- **commits:** {sha[:7]} Human: a hand edit\n- **reconciled by:** {by}\n"))
    (eng.root / "ledger.md").write_bytes(led.render().encode("utf-8"))  # write_text would add a CR on Windows


def test_sessions_opened_at_the_same_head_split_the_work_once(eng):
    """B and C open at the same HEAD after a human commit H: it is B's to reconcile (the earlier
    key), not C's, and not nobody's (each counting the other's start head as reconciled)."""
    eng.session_start(actor=ACTOR)
    h = human(eng.root, "notes.txt", "a hand edit")
    b = eng.session_start(actor=ACTOR)
    c = eng.session_start(actor=ACTOR)
    assert found(eng, b) == [h]
    assert found(eng, c) == []


def test_a_commit_belongs_to_the_first_session_whose_start_head_reaches_it(eng):
    """A opens; a human commits H; B opens. Both reconcile before either writes an entry: H is
    B's (the first start head at or after it), and A's range ends at A's own start head."""
    a = eng.session_start(actor=ACTOR)
    h = human(eng.root, "notes.txt", "a hand edit")
    b = eng.session_start(actor=ACTOR)
    assert found(eng, a) == []
    assert found(eng, b) == [h]


def test_a_commit_after_the_newest_start_head_is_the_next_sessions(eng):
    """A and B open; then a human commits H. Neither range reaches H; C, opened after it, has it.
    A `kind: foreign` entry already naming a commit leaves it out."""
    a = eng.session_start(actor=ACTOR)
    b = eng.session_start(actor=ACTOR)
    h = human(eng.root, "notes.txt", "a hand edit")
    assert found(eng, a) == found(eng, b) == []
    c = eng.session_start(actor=ACTOR)
    assert found(eng, c) == [h]
    foreign_entry(eng, "2026-10-08z", h, c)
    assert found(eng, c) == []  # named already
    commit(eng.root, "CE-2: B's milestone", session=b)
    h2 = human(eng.root, "more.txt", "another hand edit")
    commit(eng.root, "CE-3: A's milestone", session=a)
    d = eng.session_start(actor=ACTOR)
    assert found(eng, d) == [h2]  # several sessions open at once: H2 is found, H is not again


def test_a_session_line_outside_the_trailer_paragraph_is_an_agents(eng):
    eng.session_start(actor=ACTOR)
    commit(eng.root, "an older layout", body="Session: 2026-10-07b\n\nCo-Authored-By: X <x@example.com>")
    h = human(eng.root, "notes.txt", "a hand edit")
    b = eng.session_start(actor=ACTOR)
    assert found(eng, b) == [h]


def test_before_any_start_head_the_older_rule_is_the_fallback(eng):
    """A ledger written before CE-65 records no start head: the baseline is then the newest
    commit touching the ledger that this session did not make."""
    h = human(eng.root, "notes.txt", "a hand edit")
    assert found(eng, None) == [h]
    (eng.root / "ledger.md").write_text(LEDGER + "\n", encoding="utf-8")
    commit(eng.root, "CE-1: ledger", session="2026-10-07b", paths=("ledger.md",))
    assert found(eng, None) == []


def test_the_fallback_skips_this_sessions_own_ledger_commits(eng):
    """With no start head anywhere, this session's own ledger commit is not the baseline: a
    human commit before it is still found."""
    h = human(eng.root, "notes.txt", "a hand edit")
    (eng.root / "ledger.md").write_text(LEDGER + "\n", encoding="utf-8")
    commit(eng.root, "CE-1: my milestone", session="2026-10-08a", paths=("ledger.md",))
    assert found(eng, "2026-10-08a") == [h]


def test_a_start_head_no_longer_in_the_history_is_dropped(eng):
    """B's start head was rebased away: it is dropped, and the baseline is A's."""
    a = eng.session_start(actor=ACTOR)
    h = human(eng.root, "notes.txt", "a hand edit")
    b = eng.session_start(actor=ACTOR)
    git(eng.root, "commit", "--amend", "-q", "-m", "a hand edit, reworded")  # B's start head leaves the history
    h_new = git(eng.root, "rev-parse", "HEAD")
    c = eng.session_start(actor=ACTOR)
    assert L.foreign_baseline(eng.root, eng.read_ledger(), c, "ledger.md") == git(eng.root, "rev-parse", "HEAD~1")
    assert found(eng, c) == [h_new] and h_new != h
    git(eng.root, "commit", "--amend", "-q", "-m", "a hand edit, reworded again")  # now C's own start head goes
    assert found(eng, c) == [git(eng.root, "rev-parse", "HEAD")]  # its range runs to HEAD instead
    assert a and b
