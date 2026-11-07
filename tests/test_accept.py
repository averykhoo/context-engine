"""CE-187 (DEC-162): an owner's own decision is born ACCEPTED, an agent's call is born PROVISIONAL
and stays so until `decision accept <ids>` marks it reviewed, in one write and ONE op line; the
born-ACCEPTED rule applied at rest (`--owners`); `decision set` and `record new` refuse what only
the op may write; lint (G-W4) fails an agent's call ACCEPTED with no logged accept, and G-D0 a
kit-block repo whose enum lacks ACCEPTED."""

import datetime as dt
import json
import subprocess

import pytest

from context_engine import commit as C
from context_engine import decisions as D
from context_engine import guards as G
from context_engine import ops as engine_ops
from context_engine.cli import main
from context_engine.errors import Refusal
from context_engine.working import Engine

from conftest import ASK_BODY, _toml

S, ACTOR = "2026-11-07d", "claude-code/test"
W = {"session": S, "actor": ACTOR}
STATUSES = ["BUILT", "ACCEPTED", "PROVISIONAL", "DEFERRED", "SUPERSEDED", "REJECTED"]
LISTS = {k: "list" for k in ("tags", "supersedes", "superseded_by", "relaxes", "narrowed_by", "creates", "amends", "retires", "tasks", "code", "refs")}
BOARD = {"enums": {"state": ["open", "closed"], "pri": ["NOW", "NEXT", "LATER", "SOMEDAY"]}, "types": {"created": "date", "moved": "key", "updated": "key", "closed": "key", "deps": "list", "last_asked": "key"}}


def config(statuses=STATUSES):
    return {
        "engine": {"oplog": "ops.jsonl", "lockfile": ".context/engine.lock", "bundles": ["decisions"]},
        "kinds": {
            "task": {"type": "Task", "prefix": "CE", "dir": "tasks", "mode": "replaced", "required": ["title", "pri", "state", "created"], **BOARD},
            "question": {"type": "Question", "prefix": "ASK", "dir": "tasks", "mode": "replaced", "required": ["title", "pri", "state", "created"], **BOARD},
            "decision": {"type": "Decision", "prefix": "DEC", "dir": "decisions", "mode": "append-only", "required": ["title", "actor", "decided", "session", "decision_status"],
                         "enums": {"decision_status": list(statuses)}, "types": {"decided": "date", "session": "key", **LISTS}},
        },
        "working": {"board": ["task", "question"], "task": "task", "question": "question", "decision": "decision"},
    }


def engine(root, statuses=STATUSES):
    (root / "context.toml").write_text(_toml(config(statuses)), encoding="utf-8")
    return Engine(root, today=lambda: dt.date(2026, 11, 7))


@pytest.fixture
def eng(tmp_path):
    return engine(tmp_path)


def new(e, actor="owner", status=None, title="A decision", **fields):
    raw = {"actor": actor, **({"decision_status": status} if status else {}), **fields}
    body = "The owner said: do it.\n" if "ruled_by" not in fields else "Owner: *\"you decide\"*\n\n## Ruling\n\nRuled by fable: this way.\n"
    return e.record_new("decision", title, body, raw, **W).id


def status(e, rid):
    return e.store.get(rid).doc.get("decision_status")


def lines(e):
    p = e.root / "ops.jsonl"
    return [json.loads(ln) for ln in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []


def snapshot(e):
    return {p.name: p.read_bytes() for p in (e.root / "decisions").glob("*.md")}, (e.root / "ops.jsonl").read_bytes()


# -- born ACCEPTED, born PROVISIONAL ---------------------------------------------------------------


def test_an_owners_own_decision_is_born_accepted_and_an_agents_call_provisional(eng):
    assert status(eng, new(eng)) == "ACCEPTED"
    assert status(eng, new(eng, actor="human:avery")) == "ACCEPTED"
    assert status(eng, new(eng, actor="Owner")) == "ACCEPTED"  # any case (CE-138)
    assert status(eng, new(eng, actor=ACTOR)) == "PROVISIONAL"
    assert status(eng, new(eng, actor=G.DELEGATED_ACTOR, ruled_by="claude-code/fable")) == "PROVISIONAL"
    assert status(eng, new(eng, status="BUILT")) == "BUILT"  # what became of it, taken as given
    assert status(eng, new(eng, actor=ACTOR, status="REJECTED")) == "REJECTED"
    # a ruling with the owner's own actor (G-I3 off, or a hand edit) is still the ruler's call
    assert not D.owners_own({"actor": "owner", "ruled_by": "claude-code/fable"}) and not D.owners_own({"actor": "owner", "ruled_by": ""})


def test_record_new_refuses_provisional_on_owner_words_and_accepted_on_an_agents_call(eng):
    with pytest.raises(Refusal, match="the owner's own .* would be created PROVISIONAL") as r:
        new(eng, status="PROVISIONAL")
    assert "drop `--set decision_status=PROVISIONAL`" in r.value.remedy
    with pytest.raises(Refusal, match="an agent's call .* would be created ACCEPTED") as r:
        new(eng, actor=ACTOR, status="ACCEPTED")
    assert "decision accept <id>" in r.value.remedy
    with pytest.raises(Refusal, match="ruled_by: claude-code/fable.* would be created ACCEPTED"):
        new(eng, actor=G.DELEGATED_ACTOR, status="ACCEPTED", ruled_by="claude-code/fable")
    assert not (eng.root / "decisions").exists() or not list((eng.root / "decisions").glob("*.md"))


def test_a_repo_whose_enum_lacks_accepted_is_born_provisional_as_before_and_accept_refuses(tmp_path):
    e = engine(tmp_path, [s for s in STATUSES if s != "ACCEPTED"])
    rid = new(e, status="PROVISIONAL")  # not refused: the repo has not upgraded its enum
    assert status(e, new(e)) == "PROVISIONAL" and status(e, rid) == "PROVISIONAL"
    with pytest.raises(Refusal, match="enum in context.toml has no ACCEPTED") as r:
        e.decision_accept([rid], **W)
    assert "context.toml.template" in r.value.remedy


def _ask(e):
    (e.root / "tasks").mkdir(exist_ok=True)
    return e.ask_new("Which way?", body=ASK_BODY, **W).id


def test_ask_answer_is_born_accepted_and_a_delegated_ruling_provisional(eng):
    eng.ask_answer(_ask(eng), "this way", title="This way", **W)
    eng.ask_answer(_ask(eng), "you decide", title="Fable's way", ruling="that way", ruled_by="claude-code/fable", **W)
    by = {r.doc.get("title"): r.doc for r in eng.store.heads("decision")}
    assert (by["This way"].get("actor"), by["This way"].get("decision_status")) == ("owner", "ACCEPTED")
    assert (by["Fable's way"].get("ruled_by"), by["Fable's way"].get("decision_status")) == ("claude-code/fable", "PROVISIONAL")


# -- decision accept -------------------------------------------------------------------------------


def test_accept_takes_ids_and_ranges_in_one_write_and_one_op_line(eng):
    calls = [new(eng, actor=ACTOR, title=f"Call {n}") for n in range(1, 6)]
    assert calls == ["DEC-1", "DEC-2", "DEC-3", "DEC-4", "DEC-5"]
    before = len(lines(eng))
    out = eng.decision_accept(["DEC-1..3", "DEC-5", "DEC-2"], **W)
    assert out == "accepted 4: DEC-1..3, DEC-5 (one `accept` op line)"
    assert [status(eng, i) for i in calls] == ["ACCEPTED", "ACCEPTED", "ACCEPTED", "PROVISIONAL", "ACCEPTED"]
    added = lines(eng)[before:]
    assert len(added) == 1, added
    (line,) = added
    paths = [eng.store._rel(eng.store.get(i).path) for i in ("DEC-1", "DEC-2", "DEC-3", "DEC-5")]
    assert (line["op"], line["id"], line["ids"], line["paths"], line["path"], line["fields"], line["session"], line["actor"]) == (
        "accept", "DEC-1..3, DEC-5", ["DEC-1", "DEC-2", "DEC-3", "DEC-5"], paths, paths[0], ["decision_status"], S, ACTOR)
    assert C.op_paths(line) == paths
    assert eng.lint_working() == [] or all(f.guard != "G-W4" for f in eng.lint_working())
    assert [f for f in eng._decision_status_failures()] == []
    for i in ("DEC-1", "DEC-5"):  # the body and its stamp never move
        doc = eng.store.get(i).doc
        assert doc.get("body_sha") and eng.store.body_problem(eng.store.config.kind("decision"), doc) is None


def test_accept_refuses_an_unknown_id_a_decision_not_provisional_and_a_superseded_one_writing_nothing(eng):
    a, built, b = new(eng, actor=ACTOR), new(eng, status="BUILT"), new(eng, actor=ACTOR)
    old, newer = new(eng, actor=ACTOR, title="Old call"), new(eng, actor=ACTOR, title="New call")
    eng.supersede(old, newer, **W)
    owner = new(eng)  # born ACCEPTED
    keep = snapshot(eng)
    cases = [
        (["DEC-99"], r"no decision DEC-99"),
        ([f"{a}..9"], r"no decision DEC-7\.\.9"),  # a range over numbers no decision has
        ([a, built], rf"only a PROVISIONAL decision is accepted: {built} is BUILT\. Remedy"),
        ([old], rf"{old} is SUPERSEDED \(by {newer}\)"),
        ([owner, b], rf"{owner} is ACCEPTED\. Remedy"),
        ([], r"no decisions to accept"),
        (["DEC-3..1"], r"runs downward"),
        (["DEC-1..CE-3"], r"is not a range of ids"),
        (["CE-1"], r"CE-1 is not a decision"),
    ]
    for ids, says in cases:
        with pytest.raises(Refusal, match=says):
            eng.decision_accept(ids, **W)
        assert snapshot(eng) == keep, ids  # all or nothing: no file and no op line
    assert status(eng, a) == status(eng, b) == "PROVISIONAL"


def test_owners_applies_the_born_accepted_rule_to_decisions_recorded_before_it(tmp_path):
    old = engine(tmp_path, [s for s in STATUSES if s != "ACCEPTED"])  # before the upgrade
    mine, theirs = new(old, status="PROVISIONAL"), new(old, actor="human:avery", status="PROVISIONAL")
    call = new(old, actor=ACTOR)
    ruled = new(old, actor=G.DELEGATED_ACTOR, ruled_by="claude-code/fable")
    built = new(old, status="BUILT")
    e = engine(tmp_path)  # the upgrade adds ACCEPTED to the enum
    before = len(lines(e))
    assert e.decision_accept([], owners=True, **W) == f"accepted 2: {mine}..{theirs[-1]} (one `accept` op line)"
    assert [status(e, i) for i in (mine, theirs, call, ruled, built)] == ["ACCEPTED", "ACCEPTED", "PROVISIONAL", "PROVISIONAL", "BUILT"]
    assert len(lines(e)) == before + 1
    with pytest.raises(Refusal, match="no owner's decision is PROVISIONAL"):
        e.decision_accept([], owners=True, **W)
    assert e.decision_accept([call], owners=True, **W) == f"accepted 1: {call} (one `accept` op line)"  # the ids, with nothing to sweep


def test_decision_set_refuses_accepted_and_names_the_op(eng):
    rid = new(eng, actor=ACTOR)
    with pytest.raises(Refusal, match="does not mark DEC-1 ACCEPTED") as r:
        eng.decision_set(rid, {"decision_status": "ACCEPTED"}, **W)
    assert "decision accept DEC-1" in r.value.remedy and status(eng, rid) == "PROVISIONAL"


# -- lint: an agent's call accepted by hand ---------------------------------------------------------


def test_g_w4_fails_an_agents_call_accepted_by_hand_and_passes_one_the_op_accepted(eng):
    hand, op, owner = new(eng, actor=ACTOR, title="By hand"), new(eng, actor=ACTOR, title="By the op"), new(eng)
    path = eng.store.get(hand).path
    path.write_bytes(path.read_bytes().replace(b"decision_status: PROVISIONAL\n", b"decision_status: ACCEPTED\n"))
    eng.decision_accept([op], **W)
    got = [(f.guard, f.path, f.message) for f in eng.lint() if f.guard == "G-W4"]
    assert got == [("G-W4", eng.store._rel(path), f"{hand} is an agent's call (`actor: {ACTOR}`) and ACCEPTED, but no `decision accept` of it is logged, so nothing records that it was reviewed")], got
    assert status(eng, owner) == "ACCEPTED"  # born so: no line needed


# -- the one op line is carried whole --------------------------------------------------------------


def test_a_line_for_many_records_is_carried_with_every_file_it_names():
    mine = json.dumps({"session": "a", "op": "accept", "id": "DEC-1..2", "path": "d/DEC-1.md", "paths": ["d/DEC-1.md", "d/DEC-2.md"]})
    theirs = json.dumps({"session": "b", "op": "set", "id": "DEC-2", "path": "d/DEC-2.md"})
    other = json.dumps({"session": "b", "op": "accept", "id": "DEC-3..4", "path": "d/DEC-3.md", "paths": ["d/DEC-3.md", "d/DEC-4.md"]})
    taken, left = C.select([mine, theirs, other], "a")
    assert taken == [mine, theirs] and left == [other]  # DEC-2's file holds both sessions' writes
    assert C.select([theirs, other], "a", given=("d/DEC-4.md",)) == ([other], [theirs])  # a given path in `paths` takes the line


def test_g_w7_names_every_file_a_line_for_many_records_names_that_is_not_in_the_tree(eng):
    a, b = new(eng, actor=ACTOR), new(eng, actor=ACTOR)
    eng.decision_accept([a, b], **W)
    gone = eng.store.get(b).path
    rel = eng.store._rel(gone)
    gone.unlink()
    got = [f.message for f in G.op_records(eng)]
    assert got == [f"line 2 (new {b}, session {S}) and 1 more name {rel}, which is not in the tree: the op line was committed without the record it wrote"], got
    log = eng.root / "ops.jsonl"  # the accept line alone names it: it is still found
    log.write_text("".join(ln + "\n" for ln in log.read_text(encoding="utf-8").splitlines() if '"op": "new"' not in ln), encoding="utf-8")
    assert [f.message for f in G.op_records(eng)] == [f"line 1 (accept DEC-1..2, session {S}) names {rel}, which is not in the tree: the op line was committed without the record it wrote"]


def git(root, *args):
    p = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8")
    assert p.returncode == 0, p.stderr
    return p.stdout


def test_commit_carries_every_decision_an_accept_line_names(tmp_path):
    e = engine(tmp_path)
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "config", "user.email", "t@example.com")
    git(tmp_path, "config", "user.name", "T")
    ids = [new(e, actor=ACTOR, title=f"Call {n}") for n in range(1, 4)]
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-q", "-m", "three calls")
    e.decision_accept(["DEC-1..3"], **W)
    e.commit([], "the review", **W)
    shown = set(git(tmp_path, "show", "--name-only", "--format=", "HEAD").split())
    assert shown == {"ops.jsonl", *(e.store._rel(e.store.get(i).path) for i in ids)}, shown
    assert git(tmp_path, "status", "--porcelain").strip() == ""


# -- the CLI and the MCP tool ------------------------------------------------------------------------


def test_the_cli_and_the_tool_accept_ids_and_ranges(eng):
    for n in range(1, 5):
        new(eng, actor=ACTOR, title=f"Call {n}")
    base = ["--root", str(eng.root), "--session", S, "--actor", ACTOR]
    assert main([*base, "decision", "accept", "DEC-1..2,", "DEC-4"]) == 0
    code, out = engine_ops.OPS["decision_accept"].call(Engine(eng.root), engine_ops.Caller(S, ACTOR), ids=["DEC-3"])
    assert (code, out) == (0, "accepted 1: DEC-3 (one `accept` op line)")
    assert [status(eng, f"DEC-{n}") for n in range(1, 5)] == ["ACCEPTED"] * 4
    assert main([*base, "decision", "accept"]) == 2  # neither ids nor --owners: refused


def test_ranges_spell_out_and_fold_back():
    assert D.expand_ids(["DEC-86..90", "DEC-92", "DEC-92..DEC-93"]) == ["DEC-86", "DEC-87", "DEC-88", "DEC-89", "DEC-90", "DEC-92", "DEC-93"]
    assert D.compact_ids(["DEC-86", "DEC-87", "DEC-88", "DEC-90", "DEC-133", "D-1", "D-2"]) == "DEC-86..88, DEC-90, DEC-133, D-1..2"
    with pytest.raises(Refusal, match="holds 501 ids"):
        D.expand_ids(["DEC-1..501"])


def test_g_d0_fails_a_kit_repo_whose_decision_enum_lacks_accepted(tmp_path):
    """`init` never edits an existing context.toml, so a repo upgraded from a kit before CE-187
    keeps an enum without ACCEPTED: its owner decisions would be born PROVISIONAL, against its
    contract, with a clean lint."""
    from context_engine import bootstrap as B
    from context_engine.cli import run
    from test_kit import _fill_gate

    def d0() -> list[str]:
        return [ln.split(". Remedy:")[0] for ln in run(["--root", str(tmp_path), "lint"])[1].splitlines() if ln.startswith("G-D0")]

    B.init(tmp_path)
    _fill_gate(tmp_path)
    assert d0() == []
    cfg = tmp_path / "context.toml"
    text = cfg.read_text(encoding="utf-8")
    assert text.count('"ACCEPTED", ') == 1
    cfg.write_text(text.replace('"ACCEPTED", ', ""), encoding="utf-8")
    assert d0() == ["G-D0 context.toml: the decision kind's `decision_status` enum has no ACCEPTED, the status the kit's contract gives an owner's decision at birth (CE-187)"], d0()
