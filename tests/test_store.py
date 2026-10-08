"""The record store: ids under a lock, write-time refusal, the op log, append-only bodies."""

import json

import pytest

from context_engine import okf
from context_engine.errors import Refusal

from conftest import ACTOR, SESSION

KW = {"session": SESSION, "actor": ACTOR}


def new_task(repo, title="A task", **extra):
    return repo.new("task", {"title": title, "pri": "LATER", "state": "open", **extra}, "Body.", **KW)


def oplog(repo):
    path = repo.root / "ops.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []


# -- AC-3: type -------------------------------------------------------------------------


@pytest.mark.criterion("AC-3")
def test_every_written_record_has_its_kinds_type(repo):
    rec = new_task(repo)
    assert okf.parse(rec.path.read_text(encoding="utf-8")).get("type") == "Task"


@pytest.mark.criterion("AC-3")
def test_an_md_without_type_in_a_bundle_directory_fails_lint(repo):
    new_task(repo)
    (repo.root / "tasks" / "README.md").write_text("# Tasks\n", encoding="utf-8")
    (repo.root / "tasks" / "notes.md").write_text("---\ntitle: no type\n---\n", encoding="utf-8")
    (repo.root / "tasks" / "index.md").write_text("---\ntitle: x\n---\n- a\n", encoding="utf-8")
    failures = {(f.guard, f.path) for f in repo.lint()}
    assert ("G-D11", "tasks/README.md") in failures
    assert ("G-D11", "tasks/notes.md") in failures
    assert ("G-D11", "tasks/index.md") in failures


@pytest.mark.criterion("AC-3")
def test_a_typed_readme_and_a_plain_index_pass_lint(repo):
    new_task(repo)
    (repo.root / "tasks" / "README.md").write_text("---\ntype: Readme\n---\n# Tasks\n", encoding="utf-8")
    (repo.root / "tasks" / "index.md").write_text("- [CE-1](CE-1-a-task.md)\n", encoding="utf-8")
    assert repo.lint() == []


# -- AC-4: ids --------------------------------------------------------------------------


@pytest.mark.criterion("AC-4")
def test_ids_count_closed_and_legacy_records_and_are_never_reused(repo):
    closed = repo.root / "tasks" / "closed"
    closed.mkdir(parents=True)
    (closed / "CE-7-old.md").write_text("---\ntype: Task\nid: CE-7\ntitle: old\npri: LATER\nstate: closed\n---\n", encoding="utf-8")
    (repo.root / "tasks" / "CE-2-open.md").write_text("---\ntype: Task\nid: CE-2\ntitle: open\npri: NEXT\nstate: open\n---\n", encoding="utf-8")
    assert new_task(repo).id == "CE-8"
    assert new_task(repo).id == "CE-9"


@pytest.mark.criterion("AC-4")
def test_concurrent_allocations_never_return_the_same_id(repo, workers):
    workers(repo.root, [["new", "10", f"w{i}"] for i in range(4)])
    ids = sorted(int(r.id.split("-")[1]) for r in repo.records("task"))
    assert ids == list(range(1, 41))
    assert len(oplog(repo)) == 40


# -- AC-5: write-time refusal -----------------------------------------------------------


@pytest.mark.criterion("AC-5")
def test_a_new_record_that_breaks_its_schema_is_refused_and_nothing_is_written(repo):
    with pytest.raises(Refusal) as e:
        repo.new("task", {"title": "x", "pri": "URGENT", "state": "open"}, **KW)
    assert "NOW, NEXT, LATER, SOMEDAY" in e.value.remedy
    assert not (repo.root / "tasks").exists() or not list((repo.root / "tasks").glob("*.md"))
    assert oplog(repo) == []


@pytest.mark.criterion("AC-5")
def test_a_change_that_breaks_the_schema_is_refused_before_any_byte_changes(repo):
    rec = new_task(repo)
    before = rec.path.read_bytes()
    log_before = oplog(repo)
    for bad in ({"state": "done"}, {"title": ""}, {"status": "closed"}):
        with pytest.raises(Refusal) as e:
            repo.set(rec.id, bad, **KW)
        assert e.value.remedy
    with pytest.raises(Refusal):
        repo.set(rec.id, {}, unset=("pri",), **KW)
    assert rec.path.read_bytes() == before
    assert oplog(repo) == log_before


@pytest.mark.criterion("AC-5")
def test_engine_owned_keys_cannot_be_set(repo):
    rec = new_task(repo)
    for key in ("id", "type", "body_sha"):
        with pytest.raises(Refusal):
            repo.set(rec.id, {key: "x"}, **KW)
    with pytest.raises(Refusal):
        repo.new("task", {"id": "CE-99", "title": "x", "pri": "NOW", "state": "open"}, **KW)


# -- AC-6: operation log ----------------------------------------------------------------


@pytest.mark.criterion("AC-6")
def test_every_write_logs_session_actor_and_whether_it_was_mechanical(repo):
    rec = new_task(repo)
    repo.set(rec.id, {"pri": "NEXT"}, session=SESSION, actor="process:housekeep", mechanical=True)
    log = oplog(repo)
    assert [(e["op"], e["id"], e["session"], e["actor"], e["mechanical"]) for e in log] == [
        ("new", "CE-1", SESSION, ACTOR, False),
        ("set", "CE-1", SESSION, "process:housekeep", True),
    ]
    assert log[1]["fields"] == ["pri"]
    assert log[1]["path"] == "tasks/CE-1-a-task.md"


@pytest.mark.criterion("AC-6")
@pytest.mark.parametrize("session,actor", [("", ACTOR), ("today", ACTOR), (SESSION, ""), (SESSION, "owner")])
def test_a_write_without_a_session_key_or_an_okf_actor_is_refused(repo, session, actor):
    with pytest.raises(Refusal):
        repo.new("task", {"title": "x", "pri": "NOW", "state": "open"}, session=session, actor=actor)
    assert oplog(repo) == []


# -- AC-7: line endings at the store level ----------------------------------------------


@pytest.mark.criterion("AC-7")
def test_a_crlf_record_stays_crlf_and_its_stamp_matches_the_lf_copy(repo):
    text = "---\ntype: Decision\nid: DEC-1\ntitle: t\ndecision_status: BUILT\n---\n\nOwner words.\n"
    d = repo.root / "docs" / "decisions"
    d.mkdir(parents=True)
    (d / "DEC-1-t.md").write_bytes(text.replace("\n", "\r\n").encode())
    repo.stamp("DEC-1", **KW)
    raw = (d / "DEC-1-t.md").read_bytes()
    assert b"\n" not in raw.replace(b"\r\n", b"")
    assert okf.parse(raw.decode()).get("body_sha") == okf.body_sha("\nOwner words.\n")
    assert repo.lint() == []


# -- AC-8: append-only bodies -----------------------------------------------------------


def new_decision(repo):
    return repo.new("decision", {"title": "Use a lock", "decision_status": "BUILT"}, "Owner: *\"use a lock\"*.", **KW)


@pytest.mark.criterion("AC-8")
def test_editing_an_append_only_body_fails_lint_and_amend_passes(repo):
    rec = new_decision(repo)
    assert repo.lint() == []
    repo.amend(rec.id, "Later: the lock is per tree.", **KW)
    repo.amend(rec.id, "Two lines\nof amendment.", **KW)
    assert repo.lint() == []
    text = rec.path.read_text(encoding="utf-8")
    assert "## Amendments" in text and "Later: the lock is per tree." in text
    rec.path.write_text(text.replace("use a lock", "use two locks"), encoding="utf-8")
    assert [(f.guard, f.path) for f in repo.lint()] == [("G-D10", "docs/decisions/DEC-1-use-a-lock.md")]


@pytest.mark.criterion("AC-8")
def test_amend_refuses_a_record_whose_body_was_already_changed(repo):
    rec = new_decision(repo)
    rec.path.write_text(rec.path.read_text(encoding="utf-8").replace("use a lock", "use none"), encoding="utf-8")
    with pytest.raises(Refusal) as e:
        repo.amend(rec.id, "note", **KW)
    assert "git" in e.value.remedy


@pytest.mark.criterion("AC-8")
def test_an_unstamped_append_only_record_fails_lint_until_stamped(repo):
    d = repo.root / "docs" / "decisions"
    d.mkdir(parents=True)
    (d / "DEC-4-x.md").write_text("---\ntype: Decision\nid: DEC-4\ntitle: x\ndecision_status: BUILT\n---\n\nWords.\n", encoding="utf-8")
    assert [f.guard for f in repo.lint()] == ["G-D10"]
    repo.stamp("DEC-4", **KW)
    assert repo.lint() == []
    with pytest.raises(Refusal):
        repo.stamp("DEC-4", **KW)


def test_amend_is_only_for_append_only_records(repo):
    rec = new_task(repo)
    with pytest.raises(Refusal):
        repo.amend(rec.id, "x", **KW)


# -- AC-9: concurrent writers -----------------------------------------------------------


@pytest.mark.criterion("AC-9")
def test_two_processes_writing_different_records_both_succeed(repo, workers):
    a, b = new_task(repo, "a"), new_task(repo, "b")
    workers(repo.root, [["set", "15", "a", a.id], ["set", "15", "b", b.id]])
    assert repo.get(a.id).doc.get("note_a") == 14
    assert repo.get(b.id).doc.get("note_b") == 14


@pytest.mark.criterion("AC-9")
def test_two_processes_writing_the_same_record_lose_nothing(repo, workers):
    rec = new_decision(repo)
    workers(repo.root, [["amend", "15", "a", rec.id], ["amend", "15", "b", rec.id], ["set", "15", "c", rec.id]])
    text = rec.path.read_text(encoding="utf-8")
    for tag in "ab":
        for i in range(15):
            assert f"{tag} {i}\n" in text, f"lost amendment {tag} {i}"
    assert repo.get(rec.id).doc.get("note_c") == 14
    assert repo.lint() == []
    assert len(oplog(repo)) == 1 + 45
