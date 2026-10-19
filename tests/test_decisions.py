"""Decision records (CE-5, FRAMEWORK §6.5): bracketed corrections, supersede and link in both
directions, decision set (CE-32), relink (CE-35), find, show and why(), the generated index
(G-D6), and the single-file log importer (AC-38 to AC-42, AC-53, AC-54)."""

import datetime as dt
import json
import re

import pytest

from context_engine import decisions as D
from context_engine import guards as G
from context_engine import okf
from context_engine import ops as engine_ops
from context_engine.cli import main
from context_engine.errors import Refusal
from context_engine.working import Engine

from conftest import _toml

S, ACTOR = "2026-10-12d", "claude-code/test"
W = {"session": S, "actor": ACTOR}
STATUSES = ["BUILT", "PROVISIONAL", "DEFERRED", "SUPERSEDED", "REJECTED"]
LISTS = {k: "list" for k in ("tags", "supersedes", "superseded_by", "relaxes", "narrowed_by", "creates", "amends", "retires", "tasks", "code", "refs")}
BOARD = {"enums": {"state": ["open", "closed"], "pri": ["NOW", "NEXT", "LATER", "SOMEDAY"]}, "types": {"created": "date", "moved": "key", "updated": "key", "closed": "key", "deps": "list", "last_asked": "key"}}
CONFIG = {
    "engine": {"oplog": "ops.jsonl", "lockfile": ".context/engine.lock", "bundles": ["decisions"]},
    "kinds": {
        "task": {"type": "Task", "prefix": "CE", "dir": "tasks", "mode": "replaced", "required": ["title", "pri", "state", "created"], **BOARD},
        "question": {"type": "Question", "prefix": "ASK", "dir": "tasks", "mode": "replaced", "required": ["title", "pri", "state", "created"], **BOARD},
        "decision": {"type": "Decision", "prefix": "D", "dir": "decisions", "mode": "append-only", "required": ["title", "actor", "decided", "session", "decision_status"], "enums": {"decision_status": STATUSES}, "types": {"decided": "date", "session": "key", **LISTS}},
        "story": {"type": "Story", "prefix": "US", "dir": "stories", "mode": "append-only", "required": ["title", "actor"]},
    },
    "working": {"board": ["task", "question"], "task": "task", "question": "question", "decision": "decision", "decision_index": "decisions/index.md", "criteria": "criteria.md"},
}
WORDS = "The owner said: we meet on Monday at noon.\n\nA second paragraph, with a [bracket] already in it.\n"


@pytest.fixture
def eng(tmp_path):
    (tmp_path / "context.toml").write_text(_toml(CONFIG), encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "mod.py").write_text("class Store:\n    def lint(self):\n        pass\n", encoding="utf-8")
    (tmp_path / "criteria.md").write_text("| id | criterion |\n| --- | --- |\n| AC-7 | a criterion |\n\nAC-8 is named in prose, not a row.\n", encoding="utf-8")
    return Engine(tmp_path, today=lambda: dt.date(2026, 10, 12))


def dec(e, title="A decision", body=WORDS, status="BUILT", **fields):
    return e.record_new("decision", title, body, {"actor": "owner", "decision_status": status, **fields}, **W).id


def ops(e):
    return [json.loads(ln) for ln in (e.root / "ops.jsonl").read_text(encoding="utf-8").splitlines()]


# -- corrections are bracketed insertions (DEC-13) -----------------------------------------------


@pytest.mark.criterion("AC-38")
def test_a_correction_inserts_brackets_and_stripping_them_gives_back_the_words_byte_for_byte(eng):
    rid = dec(eng)
    original = okf.canonical(eng.store.get(rid).doc.body)
    stamp = eng.store.get(rid).doc.get("body_sha")
    eng.amend(rid, "an amendment before any correction", **W)
    eng.correct(rid, "on Monday", "sic: the owner meant Tuesday", **W)
    eng.correct(rid, "[sic: the", " owner's", **W)  # an insertion inside an earlier one
    eng.correct(rid, "noon.", "12:00", **W)
    doc = eng.store.get(rid).doc
    text = okf.canonical(doc.body)
    assert "on Monday[sic: the[ owner's] owner meant Tuesday] at noon.[12:00]" in text
    assert okf.strip_corrections(doc.body) == original  # the words as typed, exactly
    assert doc.get("body_sha") == stamp == okf.typed_sha(doc.body)  # never re-stamped: it pins the words as typed
    amendments = okf.get_section(doc.body, "Amendments")
    assert amendments.count("corrected: at ") == 3 and "an amendment before any correction" in amendments
    assert [o["op"] for o in ops(eng)].count("correct") == 3
    assert eng.store.lint() == []


@pytest.mark.criterion("AC-38")
def test_a_correction_applies_to_every_append_only_kind(eng):
    sid = eng.record_new("story", "A story", "I want it on Monday.\n", {"actor": "owner"}, **W).id
    eng.correct(sid, "Monday", "sic", **W)
    assert "Monday[sic]." in eng.store.get(sid).doc.body


@pytest.mark.criterion("AC-38")
@pytest.mark.parametrize(
    "after, text, match",
    [
        ("Thursday", "x", "not in the text"),
        ("on", "x", "occurs"),  # "on" appears more than once
        ("Monday", "two\nlines", "one line"),
        ("", "x", "no anchor"),
        ("Monday", "  ", "empty correction"),
    ],
)
def test_a_correction_needs_one_unique_anchor_and_one_line_of_text(eng, after, text, match):
    rid = dec(eng)
    before = eng.store.get(rid).path.read_bytes()
    with pytest.raises(Refusal, match=match):
        eng.correct(rid, after, text, **W)
    assert eng.store.get(rid).path.read_bytes() == before


@pytest.mark.criterion("AC-38")
def test_a_correction_refuses_unstamped_changed_and_board_records(eng):
    rid = dec(eng)
    path = eng.store.get(rid).path
    path.write_text(path.read_text(encoding="utf-8").replace("noon", "dusk"), encoding="utf-8")
    with pytest.raises(Refusal, match="changed since it was stamped"):
        eng.correct(rid, "dusk", "x", **W)
    tid = eng.new("task", "A task", **W).id
    with pytest.raises(Refusal, match="replaced record"):
        eng.correct(tid, "A", "x", **W)


@pytest.mark.criterion("AC-38")
def test_lint_g_d10_fails_when_a_corrected_line_does_not_match_the_body(eng):
    rid = dec(eng)
    eng.correct(rid, "on Monday", "sic", **W)
    path = eng.store.get(rid).path
    text = path.read_text(encoding="utf-8")
    pos = int(re.search(r"corrected: at (\d+) ", text).group(1))
    assert eng.store.lint() == []
    path.write_text(text.replace(f"corrected: at {pos} ", f"corrected: at {pos - 4} "), encoding="utf-8")  # the log lies about where
    assert any(f.guard == "G-D10" and "corrected:" in f.message for f in eng.store.lint())


@pytest.mark.criterion("AC-38")
@pytest.mark.parametrize("edit", ["drop the corrected line", "drop the bracket", "stamp the bracketed text"])
def test_lint_g_d10_fails_a_correction_passed_off_as_the_words_as_typed(eng, edit):
    rid = dec(eng)
    eng.correct(rid, "on Monday", "not Monday: Friday", **W)
    path = eng.store.get(rid).path
    text = path.read_text(encoding="utf-8")
    assert eng.store.lint() == []
    if edit == "drop the corrected line":  # the bracket would read as typed, with nothing logging it
        text = "\n".join(ln for ln in text.splitlines() if "corrected: at" not in ln) + "\n"
    elif edit == "drop the bracket":  # the log names a bracket that is not there
        text = text.replace("Monday[not Monday: Friday] at", "Monday at")
    else:  # a hand stamp over the corrected text: undoing the log no longer gives the stamped words
        text = re.sub(r"body_sha: \S+", "body_sha: " + okf.body_sha(eng.store.get(rid).doc.body), text)
    path.write_text(text, encoding="utf-8")
    assert [f.guard for f in eng.store.lint()] == ["G-D10"]


# -- supersede and link: both directions under one lock ------------------------------------------


@pytest.mark.criterion("AC-39")
def test_supersede_writes_both_directions_and_derives_okf_status(eng):
    old, new = dec(eng, "Old way"), dec(eng, "New way")
    out = eng.supersede(old, new, **W)
    assert "\n" not in out
    o, n = eng.store.get(old).doc, eng.store.get(new).doc
    assert (o.get("decision_status"), o.get("status"), o.get("superseded_by")) == ("SUPERSEDED", "deprecated", [new])
    assert n.get("supersedes") == [old] and n.get("decision_status") == "BUILT"
    assert [x["op"] for x in ops(eng) if x["op"] == "supersede"] == ["supersede", "supersede"]
    assert eng.store.lint() == []


@pytest.mark.criterion("AC-39")
def test_supersede_refuses_itself_a_repeat_and_a_dead_replacement(eng):
    a, b, c = dec(eng, "A"), dec(eng, "B"), dec(eng, "C", status="REJECTED")
    with pytest.raises(Refusal, match="itself"):
        eng.supersede(a, a, **W)
    with pytest.raises(Refusal, match="REJECTED"):
        eng.supersede(a, c, **W)
    eng.supersede(a, b, **W)
    with pytest.raises(Refusal, match="already superseded"):
        eng.supersede(a, b, **W)
    with pytest.raises(Refusal, match="SUPERSEDED"):
        eng.supersede(b, a, **W)  # a superseded decision replaces nothing, so no cycle
    tid = eng.new("task", "T", **W).id
    with pytest.raises(Refusal, match="not a decision"):
        eng.supersede(a, tid, **W)


@pytest.mark.criterion("AC-39")
def test_relaxes_writes_the_narrowed_by_backlink(eng):
    a, b = dec(eng, "Strict rule"), dec(eng, "A narrower rule")
    eng.link(b, a, "relaxes", **W)
    assert eng.store.get(b).doc.get("relaxes") == [a]
    assert eng.store.get(a).doc.get("narrowed_by") == [b]
    with pytest.raises(Refusal, match="decision supersede"):
        eng.link(b, a, **W)  # a decision target needs --rel


# -- decision set: a decision's own frontmatter (CE-32) ------------------------------------------


@pytest.mark.criterion("AC-53")
def test_decision_set_writes_a_decisions_own_keys_logs_set_and_regenerates_the_index(eng):
    rid = dec(eng, "Provisional call", status="PROVISIONAL")
    before = eng.store.get(rid).doc
    sha, body = before.get("body_sha"), before.body
    out = eng.decision_set(rid, {"decision_status": "REJECTED", "tags": "storage, index", "reopen_if": "plain files get slow"}, **W)
    assert out == f"{rid}: set decision_status, tags, reopen_if"
    d = eng.store.get(rid).doc
    assert (d.get("decision_status"), d.get("tags"), d.get("reopen_if")) == ("REJECTED", ["storage", "index"], "plain files get slow")
    assert (d.get("body_sha"), d.body) == (sha, body)  # the words and their stamp are untouched
    sets = [o for o in ops(eng) if o["op"] == "set"]
    assert [(o["id"], o["fields"], o["session"], o["actor"]) for o in sets] == [(rid, ["decision_status", "tags", "reopen_if"], S, ACTOR)]
    assert ops(eng)[-1]["op"] == "index"  # regenerated in the same write
    text = (eng.root / "decisions" / "index.md").read_text(encoding="utf-8")
    assert "## PROVISIONAL" not in text and f"### storage\n\n- [{rid}]" in text
    assert eng.decision_set(rid, {}, unset=("reopen_if",), **W) == f"{rid}: set reopen_if"
    assert eng.store.get(rid).doc.get("reopen_if") is None
    assert eng.store.lint() == []  # schema, G-D10 and G-D6 (the index equals a regeneration)


@pytest.mark.criterion("AC-53")
@pytest.mark.parametrize(
    "key, match",
    [
        ("type", "owned by the engine"),
        ("id", "owned by the engine"),
        ("body_sha", "owned by the engine"),
        ("status", "decision supersede"),
        ("answers", "ask answer"),
        ("actor", "fixed when the record is created"),
        ("decided", "fixed when the record is created"),
        ("session", "fixed when the record is created"),
        ("attribution", "fixed when the record is created"),
        ("imported_from", "fixed when the record is created"),
        ("generated", "fixed when the record is created"),
        ("verified", "record amend"),
        ("supersedes", "decision supersede"),
        ("superseded_by", "decision supersede"),
        ("relaxes", "decision link"),
        ("narrowed_by", "--rel relaxes"),
        ("creates", "decision link"),
        ("amends", "decision link"),
        ("retires", "decision link"),
        ("tasks", "decision link"),
        ("code", "decision relink"),
        ("refs", "decision link"),
    ],
)
def test_decision_set_refuses_keys_another_operation_owns_or_creation_fixed(eng, key, match):
    rid = dec(eng)
    path = eng.store.get(rid).path
    before = path.read_bytes()
    for raw, unset in (({key: "x"}, ()), ({}, (key,))):
        with pytest.raises(Refusal) as got:
            eng.decision_set(rid, raw, unset=unset, **W)
        assert match in str(got.value)
    assert path.read_bytes() == before


@pytest.mark.criterion("AC-53")
def test_decision_set_never_marks_or_unmarks_superseded_and_names_the_operation_that_does(eng):
    a, b = dec(eng, "Old way"), dec(eng, "New way")
    with pytest.raises(Refusal, match=rf"use `decision supersede {a} <new>`"):
        eng.decision_set(a, {"decision_status": "SUPERSEDED"}, **W)
    assert eng.store.get(a).doc.get("decision_status") == "BUILT"
    # the remedy's command works as named, through the CLI
    assert main(["--root", str(eng.root), "--session", S, "--actor", ACTOR, "decision", "supersede", a, b]) == 0
    for raw, unset in (({"decision_status": "BUILT"}, ()), ({}, ("decision_status",))):
        with pytest.raises(Refusal, match=rf"{a} is SUPERSEDED by {b}"):
            eng.decision_set(a, raw, unset=unset, **W)
    assert eng.store.get(a).doc.get("decision_status") == "SUPERSEDED"
    eng.decision_set(a, {"tags": "history"}, **W)  # its own other keys still change
    assert eng.store.get(a).doc.get("tags") == ["history"]
    tid = eng.new("task", "T", **W).id
    sid = eng.record_new("story", "A story", "words", {"actor": "owner"}, **W).id
    for other in (tid, sid):
        with pytest.raises(Refusal, match="not a decision"):
            eng.decision_set(other, {"tags": "x"}, **W)
    with pytest.raises(Refusal, match="has decision_status 'MAYBE'"):
        eng.decision_set(b, {"decision_status": "MAYBE"}, **W)  # the kind's enum still holds


@pytest.mark.criterion("AC-53")
def test_decision_set_narrowed_by_remedy_is_a_command_that_writes_it(eng):
    a, b = dec(eng, "Broad rule"), dec(eng, "Narrower rule")
    with pytest.raises(Refusal, match=rf"run `decision link <other> <id> --rel relaxes`"):
        eng.decision_set(a, {"narrowed_by": b}, **W)
    # the remedy, followed through the CLI on the decision that narrows `a`, writes the backlink
    assert main(["--root", str(eng.root), "--session", S, "--actor", ACTOR, "decision", "link", b, a, "--rel", "relaxes"]) == 0
    assert eng.store.get(a).doc.get("narrowed_by") == [b]


@pytest.mark.criterion("AC-53")
def test_decision_set_allows_reopen_if_only_on_a_rejected_decision(eng):
    built = dec(eng, "Built call")
    path = eng.store.get(built).path
    before = path.read_bytes()
    with pytest.raises(Refusal, match=rf"`reopen_if` is for a REJECTED decision, and {built} would be BUILT"):
        eng.decision_set(built, {"reopen_if": "never"}, **W)
    assert path.read_bytes() == before
    rid = dec(eng, "Tried and dropped", status="PROVISIONAL")
    eng.decision_set(rid, {"decision_status": "REJECTED", "reopen_if": "it gets slow"}, **W)  # together: allowed
    eng.decision_set(rid, {"tags": "storage"}, **W)  # a call that touches neither still writes
    before = path.read_bytes(), eng.store.get(rid).path.read_bytes()
    with pytest.raises(Refusal, match=r"--unset reopen_if"):
        eng.decision_set(rid, {"decision_status": "PROVISIONAL"}, **W)  # moving off REJECTED keeps a stale reopen_if
    assert (path.read_bytes(), eng.store.get(rid).path.read_bytes()) == before
    eng.decision_set(rid, {"decision_status": "PROVISIONAL"}, unset=("reopen_if",), **W)
    d = eng.store.get(rid).doc
    assert (d.get("decision_status"), d.get("reopen_if")) == ("PROVISIONAL", None)
    assert eng.store.lint() == []


@pytest.mark.criterion("AC-53")
def test_decision_set_runs_from_the_cli_with_set_and_unset(eng):
    rid = dec(eng, status="REJECTED")
    argv = ["--root", str(eng.root), "--session", S, "--actor", ACTOR, "decision", "set", rid]
    assert main([*argv, "--set", "reopen_if=it gets slow", "--set", "tags=[storage]"]) == 0
    assert (eng.store.get(rid).doc.get("reopen_if"), eng.store.get(rid).doc.get("tags")) == ("it gets slow", ["storage"])
    assert main([*argv, "--unset", "tags"]) == 0
    assert eng.store.get(rid).doc.get("tags") is None
    assert main([*argv, "--set", "actor=owner"]) == 2  # a refusal exits 2


# -- link, find, show and why() ------------------------------------------------------------------


# Links that name no code (CE-35): each resolves to something under the old check (the root, a
# directory, a file outside the repo, a whole file for an empty symbol, a Windows-only path).
NO_CODE = [
    ("", "names no file"),
    (".", "names no file"),
    ("src", "is a directory, not a file"),
    ("..", "not a path inside the repo"),
    ("../outside.py::f", "not a path inside the repo"),
    ("/src/mod.py", "not a path inside the repo"),
    ("src/mod.py::", "empty symbol part"),
    ("src/mod.py::Store.", "empty symbol part"),
    ("src\\mod.py::Store", r"written with `\\`"),
]


def outside(e):
    """Make `../outside.py::f` resolve from the engine root, so only the inside-the-repo rule refuses it."""
    (e.root.parent / "outside.py").write_text("def f():\n    pass\n", encoding="utf-8")


@pytest.mark.criterion("AC-47")
def test_lint_g_t3_fails_a_stored_code_link_that_names_no_code(eng):
    rid = dec(eng)
    outside(eng)

    def store(recs):
        recs[rid].doc.set("code", [t for t, _ in NO_CODE])
        return {rid: ["code"]}

    eng.store.update([rid], store, session=S, actor=ACTOR, op="link")  # a hand edit, as G-T3 would meet it
    msgs = [f.message for f in eng.lint() if f.guard == "G-T3"]
    assert len(msgs) == len(NO_CODE)
    for msg, (t, m) in zip(msgs, NO_CODE):
        assert msg.startswith(f"`code:` links `{t}`, but") and re.search(m, msg), msg


@pytest.mark.criterion("AC-47")
def test_lint_g_t3_fails_a_current_decisions_code_link_that_no_longer_resolves(eng):
    rid, gone = dec(eng), dec(eng, "Superseded")
    eng.link(rid, "src/mod.py::Store.lint", **W)
    eng.link(rid, "src/mod.py", **W)
    eng.link(gone, "src/mod.py::Store", **W)
    eng.supersede(gone, rid, **W)
    t3 = lambda: [f"{f.path}: {f.message}" for f in eng.lint() if f.guard == "G-T3"]
    assert t3() == []
    path = eng.store.find(rid).relative_to(eng.root).as_posix()
    (eng.root / "src" / "mod.py").write_text("class Store:\n    def check(self):\n        pass\n", encoding="utf-8")
    assert t3() == [f"{path}: `code:` links `src/mod.py::Store.lint`, but `src/mod.py` has no `lint`"]
    (eng.root / "src" / "mod.py").unlink()
    assert t3() == [  # the superseded decision's link to the same file is history, so it is not red
        f"{path}: `code:` links `src/mod.py::Store.lint`, but `src/mod.py` does not exist (case-exact)",
        f"{path}: `code:` links `src/mod.py`, but `src/mod.py` does not exist (case-exact)",
    ]


@pytest.mark.criterion("AC-40")
def test_link_infers_tasks_and_code_and_checks_the_target_exists(eng):
    rid, tid = dec(eng), eng.new("task", "T", **W).id
    outside(eng)
    sid = eng.record_new("story", "A story", "words", {"actor": "owner"}, **W).id
    eng.link(rid, tid, **W)
    eng.link(rid, "src/mod.py::Store.lint", **W)
    eng.link(rid, sid, "creates", **W)
    eng.link(rid, "AC-7", "amends", **W)  # a criterion: a table row of the [working] criteria file
    d = eng.store.get(rid).doc
    assert (d.get("tasks"), d.get("code"), d.get("creates"), d.get("amends")) == ([tid], ["src/mod.py::Store.lint"], [sid], ["AC-7"])
    for target, rel, match in [
        ("CE-99", "", "no record CE-99"),
        ("US-9", "retires", "no record US-9"),
        ("src/Mod.py", "", "case-exact"),
        ("src/mod.py::Missing", "", "has no `Missing`"),
        *[(t, "code", m) for t, m in NO_CODE],
        ("AC-3", "", "pass --rel"),
        ("AC-999", "creates", "not a record or a criterion in criteria.md"),
        ("AC-8", "amends", "not a record or a criterion"),  # named in prose, not a table row
        ("ZZ-404", "refs", "not a record or a criterion"),  # no record kind has this prefix
        ("D-404", "refs", "no record D-404"),
        (tid, "", "already has"),
        ("x", "supersedes", "not a link this operation writes"),
    ]:
        with pytest.raises(Refusal, match=match):
            eng.link(rid, target, rel, **W)


@pytest.mark.criterion("AC-54")
def test_relink_moves_a_code_link_in_place_and_logs_relink(eng):
    rid = dec(eng)
    eng.link(rid, "src/mod.py", **W)
    eng.link(rid, "src/mod.py::Store.lint", **W)
    eng.link(rid, "src/mod.py::Store", **W)
    sha = eng.store.get(rid).doc.get("body_sha")
    (eng.root / "src" / "store.py").write_text("class Store:\n    def check(self):\n        pass\n", encoding="utf-8")
    assert eng.relink(rid, "src/mod.py::Store.lint", "src/store.py::Store.check", **W) == f"{rid}: code src/mod.py::Store.lint -> src/store.py::Store.check"
    d = eng.store.get(rid).doc
    assert d.get("code") == ["src/mod.py", "src/store.py::Store.check", "src/mod.py::Store"]  # in place, order kept
    assert d.get("body_sha") == sha
    assert [(o["op"], o["id"], o["fields"], o["session"], o["actor"]) for o in ops(eng)[-1:]] == [("relink", rid, ["code"], S, ACTOR)]
    eng.relink(rid, "src/mod.py::Store", "src/store.py::Store.check", **W)  # onto a link it already has: kept once
    assert eng.store.get(rid).doc.get("code") == ["src/mod.py", "src/store.py::Store.check"]
    assert eng.store.lint() == []


@pytest.mark.criterion("AC-54")
def test_the_g_t3_remedy_for_a_moved_code_link_is_a_relink_that_turns_it_green(eng):
    rid = dec(eng)
    eng.link(rid, "src/mod.py::Store.lint", **W)
    (eng.root / "src" / "store.py").write_text("class Store:\n    def lint(self):\n        pass\n", encoding="utf-8")
    (eng.root / "src" / "mod.py").unlink()
    [red] = [f for f in eng.lint() if f.guard == "G-T3"]
    cmd = re.search(r"`decision relink ([^`]*)`", red.remedy).group(1).replace("<file::symbol>", "src/store.py::Store.lint").split()
    assert cmd[:2] == [rid, "src/mod.py::Store.lint"]
    assert "decision supersede" in red.remedy and "hand-edit" in red.remedy
    assert main(["--root", str(eng.root), "--session", S, "--actor", ACTOR, "decision", "relink", *cmd]) == 0
    assert [f for f in eng.lint() if f.guard == "G-T3"] == []


@pytest.mark.criterion("AC-54")
def test_relink_refuses_writing_nothing_unless_it_moves_an_existing_code_link_of_a_current_decision_to_code_that_exists(eng):
    rid, gone, new, other, tid = dec(eng), dec(eng, "Old"), dec(eng, "New"), dec(eng, "Also new"), eng.new("task", "T", **W).id
    outside(eng)
    eng.link(rid, "src/mod.py::Store", **W)
    eng.link(rid, tid, **W)
    eng.link(gone, "src/mod.py::Store", **W)
    eng.supersede(gone, new, **W)
    eng.supersede(gone, other, **W)  # two successors: one runnable `decision link` each
    before = {i: eng.store.get(i).path.read_bytes() for i in (rid, gone)}
    n_ops = len(ops(eng))
    for who, old, target, match in [
        (rid, "src/mod.py::Store", "src/mod.py::Store", "the same"),
        (rid, "src/mod.py::Store", "src/Mod.py::Store", "case-exact"),
        (rid, "src/mod.py::Store", "src/mod.py::Missing", "has no `Missing`"),
        *[(rid, "src/mod.py::Store", t, m) for t, m in NO_CODE],
        (rid, "src/mod.py::Other", "src/mod.py::Store.lint", "has no `code:` link"),
        (rid, tid, "src/mod.py::Store.lint", f"in `tasks`, not `code`"),
        (gone, "src/mod.py::Store", "src/mod.py::Store.lint", f"superseded.*`decision link {new} src/mod.py::Store.lint` or `decision link {other} src/mod.py::Store.lint`"),
        (tid, "src/mod.py::Store", "src/mod.py::Store.lint", "not a decision"),
    ]:
        with pytest.raises(Refusal, match=match):
            eng.relink(who, old, target, **W)
    assert {i: eng.store.get(i).path.read_bytes() for i in (rid, gone)} == before
    assert len(ops(eng)) == n_ops
    argv = ["--root", str(eng.root), "--session", S, "--actor", ACTOR, "decision", "relink", rid]
    assert main([*argv, "src/mod.py::Other", "src/mod.py::Store.lint"]) == 2  # a refusal exits 2


@pytest.mark.criterion("AC-40")
def test_link_refuses_a_criterion_id_when_no_criteria_file_is_set(tmp_path):
    cfg = {**CONFIG, "working": {k: v for k, v in CONFIG["working"].items() if k != "criteria"}}
    (tmp_path / "context.toml").write_text(_toml(cfg), encoding="utf-8")
    (tmp_path / "criteria.md").write_text("| AC-7 | a criterion |\n", encoding="utf-8")
    e = Engine(tmp_path)
    rid = dec(e)
    with pytest.raises(Refusal, match=r"no `\[working\] criteria` file"):
        e.link(rid, "AC-7", "amends", **W)
    assert e.store.get(rid).doc.get("amends") is None


@pytest.mark.criterion("AC-40")
def test_why_lists_exactly_the_decisions_that_link_a_target_with_the_field(eng):
    a, b, c = dec(eng, "Uses the lint"), dec(eng, "Uses the file"), dec(eng, "Unrelated")
    tid = eng.new("task", "T", **W).id
    eng.link(a, "src/mod.py::Store.lint", **W)
    eng.link(b, "src/mod.py", **W)
    eng.link(b, tid, **W)
    rows = eng.why("src/mod.py::Store.lint")
    assert [r.split()[0] for r in rows] == [a, b] and all(r.endswith("via code") for r in rows)
    assert [r.split()[0] for r in eng.why("src/mod.py")] == [a, b]  # a file covers its symbols
    assert [r.split()[0] for r in eng.why(tid)] == [b] and eng.why(tid)[0].endswith("via tasks")
    assert eng.why("CE-404") == [] and c not in " ".join(eng.why("src/mod.py"))


@pytest.mark.criterion("AC-40")
def test_find_filters_by_status_tag_link_and_text_and_show_gives_one_section(eng):
    a = dec(eng, "Alpha", tags="[records]")
    b = dec(eng, "Beta", body="Mentions the zebra.\n", status="PROVISIONAL", tags="[records, ops]")
    eng.amend(b, "widened later", **W)
    ids = lambda rows: [r.split()[0] for r in rows]  # noqa: E731
    assert ids(eng.find(status="provisional")) == [b]
    assert ids(eng.find(tag="records")) == [a, b] and ids(eng.find(tag="ops")) == [b]
    assert ids(eng.find(text="ZEBRA")) == [b]
    eng.link(a, "src/mod.py", **W)
    assert ids(eng.find(links_to="src/mod.py::Store")) == [a]
    shown = eng.decision_show(b, "Amendments")
    assert shown.startswith(f"{b} · PROVISIONAL · Beta\n") and "widened later" in shown and "zebra" not in shown
    with pytest.raises(Refusal, match="no `## Nope`"):
        eng.decision_show(b, "Nope")


# -- the generated index (G-D6) ------------------------------------------------------------------


@pytest.mark.criterion("AC-41")
def test_every_decision_write_regenerates_the_index_grouped_by_status_then_tag(eng):
    index = eng.root / "decisions" / "index.md"
    a = dec(eng, "Alpha", tags="[zeta, records]")
    assert f"[{a}](" in index.read_text(encoding="utf-8")
    b = dec(eng, "Beta", status="PROVISIONAL")
    c = dec(eng, "Gamma")
    eng.supersede(b, c, **W)
    eng.correct(a, "Monday", "sic", **W)
    q = eng.ask_new("Which?", **W)
    eng.ask_answer(q.id, "this one", title="Delta", **W)  # a decision made through another operation
    text = index.read_text(encoding="utf-8")
    assert text == eng.store.render_index()
    assert text.index("## BUILT") < text.index("## PROVISIONAL") < text.index("## SUPERSEDED")
    built = text[text.index("## BUILT") : text.index("## PROVISIONAL")]
    assert built.index("### zeta") < built.index("### untagged")  # by first tag; untagged last
    assert f"- [{b}]({b}-beta.md): Beta *(owner, 2026-10-12)*; superseded by {c}" in text
    assert "D-4" in text and "Delta" in text
    assert eng.store.lint() == []


@pytest.mark.criterion("AC-41")
def test_lint_g_d6_fails_on_a_hand_edited_or_missing_index_and_decision_index_restores_it(eng):
    dec(eng)
    index = eng.root / "decisions" / "index.md"
    assert eng.reindex(**W).endswith("already current")
    index.write_text(index.read_text(encoding="utf-8") + "- a line typed by hand\n", encoding="utf-8")
    assert [f.guard for f in eng.store.lint()] == ["G-D6"]
    assert eng.reindex(**W).endswith("regenerated") and eng.store.lint() == []
    index.unlink()
    assert [(f.guard, "missing" in f.message) for f in eng.store.lint()] == [("G-D6", True)]
    eng.reindex(**W)
    assert eng.store.lint() == []


def test_no_index_is_written_or_checked_when_none_is_configured(tmp_path):
    cfg = {**CONFIG, "working": {k: v for k, v in CONFIG["working"].items() if k != "decision_index"}}
    (tmp_path / "context.toml").write_text(_toml(cfg), encoding="utf-8")
    e = Engine(tmp_path)
    dec(e)
    assert not (tmp_path / "decisions" / "index.md").exists() and e.store.lint() == []
    with pytest.raises(Refusal, match="decision_index"):
        e.reindex(**W)


# -- the single-file log importer (FRAMEWORK §11.4) ----------------------------------------------

LOG = """# Decisions log

Newest first. Append-only.

## Built and rejected, or decided against evidence

| thing | standing verdict | written up under |
|---|---|---|
| `tool -x` for three papers | **rejected**: it interleaves the copies (2026-10-09) | D-3 |
| keeping two duplicates | **removed**: duplicates | D-1 |

## Entries

### D-4 -- the new way *(owner asked + agent, 2026-10-06)* -- **relaxes D-2**

> (owner, 2026-10-06: "start work on it")

- **What it is.** `mod.py::thing`.

### D-3 -- the gate is X *(agent, 2026-10-05)* -- **SUPERSEDED by D-4 (for X); the rest stands**

Body three.

#### a sub-heading inside an entry

More of three.

### D-2 — scope is narrow *(owner, brief added 2026-09-02)* -- **narrowed by D-4: allowed**

> "the owner's words"

### D-1 – the first *(owner, 2026-09-01; amended by evidence)*

Body one.

## Appendix

Not an entry.
"""


def write_log(eng, text=LOG):
    path = eng.root / "decisions-copy.md"
    path.write_text(text, encoding="utf-8")
    return path.name


@pytest.mark.criterion("AC-42")
def test_import_keeps_every_id_and_text_verbatim_stamped_with_links_both_ways(eng):
    out = eng.import_log(write_log(eng), **W)
    assert "\n" not in out and "4 entries (D-1..D-4, ids kept); 2 rejected rows as D-5..D-6; 3 heading notes" in out
    get = lambda i: eng.store.get(i).doc  # noqa: E731
    for rid, start in [("D-4", '> (owner, 2026-10-06: "start work on it")\n\n- **What it is.**'), ("D-3", "Body three.\n\n#### a sub-heading inside an entry\n\nMore of three."), ("D-1", "Body one.")]:
        assert okf.canonical(get(rid).body).startswith(start), rid
        assert okf.canonical(get(rid).body).strip("\n") in LOG  # a verbatim slice of the log
    assert okf.canonical(get("D-1").body) == "Body one.\n\n## Appendix\n\nNot an entry.\n"  # CE-98: the last entry runs to the end of the log, like every entry
    assert "not imported: lines 1-3 (before the first entry, from '# Decisions log'), line 12 (before the first entry, from '## Entries')" in out  # not the rejected table's lines: they are records
    d3, d4, d2, d1 = get("D-3"), get("D-4"), get("D-2"), get("D-1")
    assert (d3.get("decision_status"), d3.get("status"), d3.get("superseded_by")) == ("SUPERSEDED", "deprecated", ["D-4"])
    assert (d4.get("supersedes"), d4.get("relaxes"), d4.get("actor"), d4.get("decided")) == (["D-3"], ["D-2"], "owner asked + agent", dt.date(2026, 10, 6))
    assert d2.get("narrowed_by") == ["D-4"] and d2.get("attribution") == "owner, brief added 2026-09-02" and d2.get("title") == "scope is narrow"
    assert d1.get("attribution") == "owner, 2026-09-01; amended by evidence" and d1.get("decision_status") == "BUILT"
    assert "imported heading note: **SUPERSEDED by D-4 (for X); the rest stands**" in okf.get_section(d3.body, "Amendments")
    assert all(get(f"D-{n}").get("body_sha") == okf.body_sha(get(f"D-{n}").body) for n in range(1, 7))
    d5, d6 = get("D-5"), get("D-6")
    assert (d5.get("decision_status"), d5.get("decided"), d5.get("refs"), d5.get("actor")) == ("REJECTED", dt.date(2026, 10, 9), ["D-3"], "agent")
    assert "| `tool -x` for three papers | **rejected**: it interleaves the copies (2026-10-09) | D-3 |" in d5.body
    assert d6.get("decided") == dt.date(2026, 9, 1)  # no date in the row: the entry it names
    assert all(get(f"D-{n}").get("imported_from") == "decisions-copy.md" for n in range(1, 7))
    assert eng.store.lint() == []
    assert "## REJECTED" in (eng.root / "decisions" / "index.md").read_text(encoding="utf-8")


@pytest.mark.criterion("AC-42")
@pytest.mark.parametrize(
    "edit, match",
    [
        (("### D-1 – the first", "### X-2 – the first"), "entries D-2, X-2 would all become D-2"),
        (("### D-1 – the first", "### D-2 – the first"), "two entries D-2"),
        (("*(owner, 2026-09-01; amended by evidence)*", "(owner, 2026-09-01)"), "has no `\\*\\(actor, date\\)\\*`"),
        (("*(agent, 2026-10-05)*", "*(agent, yesterday)*"), "no YYYY-MM-DD date"),
        (("**relaxes D-2**", "**relaxes D-9**"), "links D-9"),
        (("| keeping two duplicates | **removed**: duplicates | D-1 |", "| keeping two | duplicates | **removed** | D-1 |"), "has 4 cells"),
        # CE-98: a heading the import cannot read refuses, naming its line; none folds into the entry above
        (("### D-1 – the first", "### D-1 FIX – the first"), "line 32: .* starts with D-1 but is not an entry heading"),
        (("### D-4 -- the new way", "### D-4a -- the new way"), "line 14: .* has the id D-4a, which has no number of its own"),
        (("*(agent, 2026-10-05)*", "*(2026-10-05)*"), "the heading of D-3 \\(line 20\\) has a date where the actor goes"),
        (("Body three.", "Body three.\n\n```python"), "line 24: a code fence '```python' is never closed"),
        (("More of three.", "More of three.\n\n## Amendments\n\n### D-1 FIX -- under D-3's amendments, so not D-1's"), "starts with D-1 but is not an entry heading"),
        (("More of three.", "More of three.\n\n### D-3 FIX -- its own id, but not under its own amendments"), "line 28: .* starts with D-3 but is not an entry heading"),
        (("*(agent, 2026-10-05)*", "*(, 2026-10-05)*"), "the heading of D-3 \\(line 20\\) names no actor"),
        (("*(agent, 2026-10-05)*", "*(agent, 2026-02-30)*"), "the heading of D-3 \\(line 20\\) has a date '2026-02-30' that is not a real day"),
        (("Body three.\n\n#### a sub-heading inside an entry\n\nMore of three.", "## Amendments\n\nOnly an amendment."), "D-3 \\(line 20\\) has no text under its heading"),
        # CE-98, 2026-10-19e: what the review found folding, cut or unstamped now refuses, naming its line
        (("*(agent, 2026-10-05)*", "*(made normative 2026-10-05)*"), "the heading of D-3 \\(line 20\\) has no comma between its actor and its date, so the actor would be 'made normative 2026-10-05'"),
        (("### D-3 -- the gate", " ### D-3 -- the gate"), "line 20: .* starts with D-3 but is not an entry heading"),
        (("### D-3 -- the gate", "###  D-3 -- the gate"), "line 20: .* starts with D-3 but is not an entry heading"),
        (("### D-3 -- the gate", "### **D-3** -- the gate"), "line 20: .* starts with D-3 but is not an entry heading"),
        (("### D-3 -- the gate", "### [D-3] -- the gate"), "line 20: .* starts with D-3 but is not an entry heading"),
        (("More of three.", "More of three.\n\n## Amendments\n\n- a fix\n\n## 3. More rules\n\nX must be Y."), "line 32: '## 3. More rules' comes after D-3's own `## Amendments` \\(line 28\\)"),
        (("More of three.", "More of three.\n\n```md\n## Amendments\n```"), "line 29: a `## Amendments` line inside a code fence or comment in D-3"),
        (("More of three.", "More of three.\n\n<!--\n## Amendments\n-->"), "line 29: a `## Amendments` line inside a code fence or comment in D-3"),
        (("Body three.", "Body three.\n\n<!-- a comment"), "line 24: an HTML comment '<!-- a comment' is never closed"),
        (("| keeping two duplicates | **removed**: duplicates | D-1 |", "| keeping two duplicates | **removed**: duplicates | D-1 |\n\n| other | table |\n|---|---|"), "line 12: a second table under `## Built and rejected"),
        (("More of three.", "More of three.\n\n## Amendments\n\n### D-3 -- FIX *(owner, 2026-10-06)*\n\nThe fix."), "line 30: .* is an entry heading for D-3 under D-3's own `## Amendments` \\(line 28\\)"),
    ],
)
def test_import_is_all_or_nothing(eng, edit, match, tmp_path_factory):
    dec(eng, "Unrelated")  # D-1 exists already: the import refuses before writing anything
    before = sorted(p.name for p in (eng.root / "decisions").iterdir())
    with pytest.raises(Refusal, match="D-1 is already a record"):
        eng.import_log(write_log(eng), **W)
    assert sorted(p.name for p in (eng.root / "decisions").iterdir()) == before
    fresh = tmp_path_factory.mktemp("fresh")
    (fresh / "context.toml").write_text(_toml(CONFIG), encoding="utf-8")
    e = Engine(fresh)
    path = write_log(e, LOG.replace(*edit))
    with pytest.raises(Refusal, match=match):
        e.import_log(path, **W)
    assert not (fresh / "decisions").exists() and not (fresh / "ops.jsonl").exists()


@pytest.mark.criterion("AC-42")
def test_import_writes_nothing_when_a_later_record_breaks_the_schema(tmp_path):
    kinds = {**CONFIG["kinds"], "decision": {**CONFIG["kinds"]["decision"], "enums": {"decision_status": ["BUILT", "SUPERSEDED"]}}}
    (tmp_path / "context.toml").write_text(_toml({**CONFIG, "kinds": kinds}), encoding="utf-8")
    e = Engine(tmp_path)
    with pytest.raises(Refusal, match="decision_status 'REJECTED'"):
        e.import_log(write_log(e), **W)  # the entries are valid; the rejected rows, written last, are not
    assert not (tmp_path / "decisions").exists() and not (tmp_path / "ops.jsonl").exists()


@pytest.mark.criterion("AC-42")
def test_import_dry_run_writes_nothing_and_the_cli_runs_it(eng):
    path = write_log(eng)
    assert eng.import_log(path, dry_run=True, **W).startswith("dry run, nothing written: would import 4 entries")
    assert not (eng.root / "decisions").exists()
    files = lambda: sorted(p.relative_to(eng.root).as_posix() for p in eng.root.rglob("*"))  # noqa: E731
    before = files()
    assert main(["--root", str(eng.root), "--session", S, "--actor", ACTOR, "decision", "import", path, "--dry-run"]) == 0
    assert files() == before  # CE-98: not even the lock file the write ops' batch would create
    assert main(["--root", str(eng.root), "--session", S, "--actor", ACTOR, "decision", "import", path]) == 0
    assert len(list((eng.root / "decisions").glob("D-*.md"))) == 6


# -- CE-98: the import never loses text silently -------------------------------------------------

SHAPED = """# A log in groups

Intro, not an entry.

## 2026-10-02

### D-3 -- three *(owner, 2026-10-02)*

Body three.

## 1. An inner section

Inner text of three.

```bash
# a comment in a fence
### D-9 -- in a fence, so not an entry *(owner, 2026-01-01)*
```

```a span``` at a line's start opens no fence

<!--
### D-8 -- a draft in a comment, so not an entry *(owner, 2026-01-01)*
-->

## 2026-10-01

### D-2 -- two *(unrecorded, 2026-10-01)*

Body two.

## Amendments

### D-2 FIX (2026-10-03) -- folded under its parent's amendments

Fix text.

### D-1 -- one *(agent, 2026-09-30)*

Body one.

## 1. The last entry's own section

Its text.

## Amendments

### D-1 FIX -- under the last entry's own amendments

Fix of one.

## 2026-09
"""


@pytest.mark.criterion("AC-42")
def test_an_inner_heading_stays_in_its_entry_and_every_line_left_out_is_named(eng):
    parsed = D.parse_log(SHAPED)
    lines = SHAPED.split("\n")
    held = [lines[e.line - 1] for e in parsed.entries] + [ln for e in parsed.entries for ln in e.body.split("\n")]
    held += [ln for x in parsed.excluded for ln in lines[x.first - 1 : x.last]]
    assert sorted(ln for ln in held if ln.strip()) == sorted(ln for ln in lines if ln.strip())  # every line is somewhere
    out = eng.import_log(write_log(eng, SHAPED), **W)
    assert "\n" not in out and "1 with actor `unrecorded`" in out and "2 entries' own `## Amendments` kept" in out and "4 `#`/`## ` headings kept inside 3 entries" in out
    assert "not imported: lines 1-5 (before the first entry, from '# A log in groups'), 2 headings with no text of their own (lines 26, 52)" in out
    get = lambda i: eng.store.get(i).doc  # noqa: E731
    three = okf.canonical(get("D-3").body)
    assert three.startswith("Body three.\n\n## 1. An inner section\n\nInner text of three.\n\n```bash\n# a comment in a fence\n### D-9") and "2026-10-01" not in three
    assert "```a span``` at a line's start opens no fence\n\n<!--\n### D-8 -- a draft in a comment" in three
    d2 = get("D-2")
    assert okf.canonical(d2.body) == "Body two.\n" and d2.get("actor") == "unrecorded" and d2.get("decided") == dt.date(2026, 10, 1)
    assert "### D-2 FIX (2026-10-03)" in okf.get_section(d2.body, "Amendments") and "Fix text." in d2.body
    d1 = get("D-1")  # the last entry runs to the end of the log, like every entry: its own sections and `## Amendments` stay its
    assert okf.canonical(d1.body) == "Body one.\n\n## 1. The last entry's own section\n\nIts text.\n"
    assert "### D-1 FIX -- under the last entry's own amendments\n\nFix of one." in okf.get_section(d1.body, "Amendments") and "2026-09" not in d1.body
    assert {p.name.split("-")[1] for p in (eng.root / "decisions").glob("D-*.md")} == {"1", "2", "3"}  # no D-8 (in a comment), no D-9 (in a fence)
    assert eng.store.lint() == []


@pytest.mark.criterion("AC-42")
def test_a_rejected_table_inside_an_entry_stays_that_entrys_text(eng):
    text = "### D-2 -- two *(owner, 2026-10-02)*\n\nBody two.\n\n## 6. What was rejected\n\n| thing | verdict |\n|---|---|\n| x | **rejected** (2026-10-02) |\n\n### D-1 -- one *(owner, 2026-10-01)*\n\nBody one.\n"
    out = eng.import_log(write_log(eng, text), **W)
    assert out.startswith("imported 2 entries (D-1..D-2, ids kept); 1 `#`/`## ` headings kept inside 1 entries") and "rejected rows" not in out
    assert "## 6. What was rejected\n\n| thing | verdict |\n|---|---|\n| x | **rejected** (2026-10-02) |\n" in eng.store.get("D-2").doc.body


FENCED = """# Log

How to write a rejected table:

```md
## Rejected (example)

| thing | verdict |
|---|---|
| EXAMPLE | **rejected** (2026-01-01) |
```

### D-2 -- two *(owner, 2026-10-02)*

Body two.

### D-1 -- one *(owner, 2026-10-01)*

Body one.

## 6. What was rejected and why

| thing | verdict |
|---|---|
| y | **rejected** (2026-10-01) |

## 7. Consequences

Consequence text of one.
"""


@pytest.mark.criterion("AC-42")
def test_the_rejected_table_is_read_only_before_the_first_entry_and_outside_fences(eng):
    out = eng.import_log(write_log(eng, FENCED), **W)
    assert out.startswith("imported 2 entries (D-1..D-2, ids kept); 2 `#`/`## ` headings kept inside 1 entries") and "rejected rows" not in out
    assert "not imported: lines 1-11 (before the first entry, from '# Log')" in out
    assert {p.name.split("-")[1] for p in (eng.root / "decisions").glob("D-*.md")} == {"1", "2"}  # no REJECTED record
    assert okf.canonical(eng.store.get("D-1").doc.body) == "Body one.\n\n" + FENCED.split("Body one.\n\n")[1]  # the last entry's rejected section and all after it
    assert eng.store.lint() == []


@pytest.mark.criterion("AC-42")
def test_a_refusal_names_every_line_the_import_cannot_read_at_once_in_line_order(eng):
    text = LOG.replace("### D-4 -- the new way", "### D-4a -- the new way").replace("*(agent, 2026-10-05)*", "*(2026-10-05)*").replace("### D-1 – the first", "### D-1b – the first")
    with pytest.raises(Refusal) as r:
        eng.import_log(write_log(eng, text), **W)
    assert r.value.message.startswith("line 14: '### D-4a -- the new way")  # the first by line, not by the order found
    assert r.value.message.endswith("; 3 lines in all that the import cannot read: letter id x2 (lines 14, 32); date as actor x1 (line 20)")
    assert not (eng.root / "decisions").exists()


@pytest.mark.criterion("AC-42")
def test_the_dry_run_doc_names_each_line_left_out_and_each_heading_kept_inside_an_entry(eng):
    doc = eng.import_log(write_log(eng, SHAPED), dry_run=True, **W).split("then import:\n\n")[1]
    no_text = D.EMPTY_HEADING
    assert f"## Not imported\n\n- lines 1-5: before the first entry: '# A log in groups'\n- line 26: {no_text}: '## 2026-10-01'\n- line 52: {no_text}: '## 2026-09'\n" in doc
    assert "## Headings kept inside entries\n\n- line 11, in D-3: '## 1. An inner section'\n- line 32, in D-2: '## Amendments'\n- line 42, in D-1: \"## 1. The last entry's own section\"\n- line 46, in D-1: '## Amendments'\n" in doc


# -- DEC-37: an import renames to the framework's form, and each old id stays an alias --------------

DEC_CONFIG = {**CONFIG, "kinds": {**CONFIG["kinds"], "decision": {**CONFIG["kinds"]["decision"], "prefix": "DEC"}}}


@pytest.fixture
def deng(tmp_path):
    """A repo whose decision kind is DEC-n, adopting a log written as D-n (adhoc's case)."""
    (tmp_path / "context.toml").write_text(_toml(DEC_CONFIG), encoding="utf-8")
    (tmp_path / "criteria.md").write_text("| id | criterion |\n| --- | --- |\n| AC-7 | a criterion |\n", encoding="utf-8")
    return Engine(tmp_path, today=lambda: dt.date(2026, 10, 12))


@pytest.mark.criterion("AC-42")
def test_import_renames_a_foreign_prefix_keeping_each_number_and_the_old_id_as_an_alias(deng):
    path = write_log(deng)
    dry = deng.import_log(path, dry_run=True, **W)
    assert not (deng.root / "decisions").exists()
    assert "| D-3 | DEC-3 | SUPERSEDED | the gate is X |" in dry and "| D-1 | DEC-1 | BUILT | the first |" in dry
    assert "| (rejected table row 1) | DEC-5 | REJECTED |" in dry  # no id in the log: a new number, no alias
    doc = dry.split("Save everything below this line as the id map's evidence doc, then import:\n\n")[1]
    assert doc.startswith("# Decision id map: decisions-copy.md into decisions\n\nFROZEN. ")  # a doc ready to save: a title and its liveness
    assert dry.splitlines()[0].endswith("review each and `decision set <id> --set decision_status=<status>` any that was parked, deferred or not built")
    out = deng.import_log(path, **W)
    assert "\n" not in out and "4 entries (D-1..D-4 as DEC-1..DEC-4, numbers kept, 4 old ids kept as aliases); 2 rejected rows as DEC-5..DEC-6" in out
    assert "3 set BUILT by default, as the log gives no status: review each" in out  # F22: the defaulted statuses are named, not silent
    get = lambda i: deng.store.get(i).doc  # noqa: E731
    assert [get(f"DEC-{n}").get("aliases") for n in range(1, 7)] == [["D-1"], ["D-2"], ["D-3"], ["D-4"], None, None]
    assert (get("DEC-3").get("superseded_by"), get("DEC-4").get("supersedes"), get("DEC-4").get("relaxes"), get("DEC-2").get("narrowed_by")) == (["DEC-4"], ["DEC-3"], ["DEC-2"], ["DEC-4"])
    assert get("DEC-5").get("refs") == ["DEC-3"] and get("DEC-5").get("attribution").endswith("the reasoning is under DEC-3")
    assert "imported heading note: **SUPERSEDED by D-4 (for X); the rest stands**" in okf.get_section(get("DEC-3").body, "Amendments")  # history keeps the old id
    assert not list((deng.root / "decisions").glob("D-*.md"))
    assert deng.store.lint() == [] and G.ids(deng) == []


@pytest.mark.criterion("AC-42")
def test_a_reimport_refuses_an_old_id_already_imported_or_a_number_already_taken(deng):
    deng.import_log(write_log(deng), **W)
    before = sorted(p.name for p in (deng.root / "decisions").iterdir())
    with pytest.raises(Refusal, match="D-4 was imported already: it is an alias of DEC-4") as r:
        deng.import_log(write_log(deng), **W)
    assert "import a copy holding only them" in r.value.remedy
    # F21: the log gained D-5 by hand after the import, but DEC-5 is already a rejected row's record
    later = "### D-5 -- written by hand after the import *(owner, 2026-10-13)*\n\nNew words.\n"
    with pytest.raises(Refusal, match="D-5 would become DEC-5, which is already a record") as r:
        deng.import_log(write_log(deng, later), **W)
    assert "record new decision ... --set aliases=[<old id>]" in r.value.remedy
    assert sorted(p.name for p in (deng.root / "decisions").iterdir()) == before
    rid = deng.record_new("decision", "written by hand after the import", "New words.", {"actor": "owner", "decision_status": "BUILT", "aliases": "[D-5]"}, **W).id
    assert rid == "DEC-7" and deng.decision_show("D-5").startswith("D-5 is an alias of DEC-7\nDEC-7 · BUILT")


@pytest.mark.criterion("AC-40")
def test_show_why_link_and_supersede_resolve_an_alias_and_say_which_record_it_named(deng):
    deng.import_log(write_log(deng), **W)
    task = deng.new("task", "Estimate the activity", **W).id
    assert deng.set(task, {"aliases": "[1h, est-activity]"}, **W) == f"{task}: set aliases"
    assert deng.show("1h").startswith(f"1h is an alias of {task}\n{task} · LATER · open · Estimate the activity\naliases: 1h, est-activity\n")
    assert deng.decision_show("D-3").startswith("D-3 is an alias of DEC-3\nDEC-3 · SUPERSEDED · the gate is X\n")
    assert "aliases: D-3\n" in deng.decision_show("DEC-3")
    assert deng.link("D-1", "est-activity", **W) == f"DEC-1: tasks + {task} (D-1 is an alias of DEC-1) (est-activity is an alias of {task})"
    assert deng.store.get("DEC-1").doc.get("tasks") == [task]  # the live id is written, never the alias
    assert deng.why("1h") == [f"1h is an alias of {task}", f"{deng._row(deng.store.get('DEC-1'))}  via tasks"]
    assert deng.why("D-2")[0] == "D-2 is an alias of DEC-2" and "DEC-4" in deng.why("D-2")[1]
    assert deng.why("AC-7") == []  # a criterion is taken as given
    assert deng.supersede("D-1", "D-4", **W).endswith("(D-1 is an alias of DEC-1) (D-4 is an alias of DEC-4)")
    assert "DEC-2" in [ln.split()[0] for ln in deng.find("D-2")]  # its title and text never say D-2: find's text searches aliases too
    with pytest.raises(Refusal, match="no record Q9: it is not an id of a configured series"):
        deng.show("Q9")
    assert main(["--root", str(deng.root), "task", "show", "est-activity"]) == 0


@pytest.mark.criterion("AC-40")
def test_the_mcp_operations_resolve_an_alias(deng):
    deng.import_log(write_log(deng), **W)
    c = engine_ops.Caller(S, ACTOR)
    assert engine_ops.OPS["decision_show"].call(deng, c, id="D-4")[1].startswith("D-4 is an alias of DEC-4\n")
    assert engine_ops.OPS["why"].call(deng, c, target="D-3")[1].startswith("D-3 is an alias of DEC-3\n")


def _hand_alias(e, rid, aliases):
    """Write `aliases:` into a record's frontmatter by hand, as an editor would, past the engine's checks."""
    path = e.store.find(rid)
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(f"id: {rid}\n", f"id: {rid}\naliases: {aliases}\n", 1), encoding="utf-8", newline="\n")


@pytest.mark.parametrize(
    "aliases, match",
    [
        ("[CE-1]", "lists its own id CE-1 as an alias"),
        ("[ce-1]", "lists its own id ce-1 as an alias"),
        ("[DEC-9]", "has alias DEC-9, which reads as an id of the decision series"),
        ("[CE-7]", "has alias CE-7, which reads as an id of the task series"),
        ("[dec-3]", "has alias dec-3, which reads as an id of the decision series"),  # case aside
        ("[CE-014]", "has alias CE-014, which reads as an id of the task series"),  # leading zeros aside
        ("[AC-7]", "has alias AC-7, which reads as a criterion id"),  # a criterion row
        ("[AC-99]", "has alias AC-99, which reads as a criterion id"),  # the criteria's series, before the row exists
        ("[2h, 2h]", "lists alias 2h twice"),
        ("[2h, 2H]", "lists alias 2H twice"),
        ("[two words]", "has alias 'two words', which is not one word"),
        ("[a/b]", "has alias 'a/b', which is not one word"),
        ("[D‐27]", "which is not one word of printable ASCII"),  # a look-alike hyphen
        ("[1h]", "has alias 1h, which CE-2 also carries"),
        ("[1H]", "has alias 1H, which CE-2 also carries"),
    ],
)
def test_every_write_and_lint_g_d2_refuse_an_alias_that_does_not_name_one_record(deng, aliases, match):
    deng.new("task", "First", **W)
    deng.new("task", "Second", **W)
    deng.set("CE-2", {"aliases": "[1h]"}, **W)
    before = deng.store.find("CE-1").read_bytes()
    with pytest.raises(Refusal, match=match):
        deng.set("CE-1", {"aliases": aliases}, **W)
    assert deng.store.find("CE-1").read_bytes() == before and G.ids(deng) == []
    _hand_alias(deng, "CE-1", aliases)
    assert any(f.guard == "G-D2" and re.search(match, f.message) and f.path.startswith("tasks/CE-1") for f in G.ids(deng)), G.ids(deng)


def test_an_alias_two_records_carry_is_refused_on_lookup_and_a_decision_keeps_its_aliases(deng):
    deng.import_log(write_log(deng), **W)
    deng.new("task", "First", **W)
    _hand_alias(deng, "CE-1", "[D-2]")  # by hand: every write refuses it (above)
    with pytest.raises(Refusal, match=r"D-2 is an alias of 2 records \((DEC-2, CE-1|CE-1, DEC-2)\)"):
        deng.decision_show("D-2")
    with pytest.raises(Refusal, match="`decision set` does not change a decision's `aliases`"):
        deng.decision_set("DEC-1", {"aliases": "[D-01]"}, **W)
    with pytest.raises(Refusal, match="has alias D-3, which DEC-3 also carries"):
        deng.record_new("decision", "A copy", "Words.", {"actor": "owner", "decision_status": "BUILT", "aliases": "[D-3]"}, **W)


def test_task_new_and_ask_new_keep_an_imported_number(deng):
    assert deng.ask_new("Which way?", rid="ASK-8", **W).id == "ASK-8"  # Q8 keeps its number
    assert deng.ask_new("And then?", **W).id == "ASK-9"
    with pytest.raises(Refusal, match="ASK-8 is already in use"):
        deng.ask_new("Again", rid="ASK-8", **W)
    with pytest.raises(Refusal, match="CE-3 is not an id of the question series"):
        deng.ask_new("Wrong series", rid="CE-3", **W)
    assert main(["--root", str(deng.root), "--session", S, "--actor", ACTOR, "task", "new", "Kept", "--id", "CE-14"]) == 0
    assert deng.store.find("CE-14").name.startswith("CE-14-kept")
    for bad, want in (("CE-014", "give CE-14: no leading zeros"), ("CE-0", "give CE-n, n from 1")):
        with pytest.raises(Refusal, match=want):
            deng.new("task", "Padded", rid=bad, **W)
    deng.store.find("CE-14").unlink()  # the file is gone, but the op log shows CE-14 was created
    with pytest.raises(Refusal, match=r"CE-14 is already in use \(the op log shows it was created before\)"):
        deng.new("task", "Again", rid="CE-14", **W)


# -- the design review's findings (CE-74) ----------------------------------------------------------


def test_a_write_that_leaves_aliases_alone_is_not_refused_for_a_clash_made_elsewhere(deng):
    deng.new("task", "First", **W)
    deng.new("task", "Second", **W)
    deng.set("CE-1", {"aliases": "[1h]"}, **W)
    _hand_alias(deng, "CE-2", "[1h]")  # by hand, on the other record: lint is red, and says so
    assert deng.set("CE-1", {"brief": "still writable"}, **W) == "CE-1: set brief"
    assert any(f.guard == "G-D2" and "1h" in f.message for f in G.ids(deng))
    with pytest.raises(Refusal, match="which CE-2 also carries"):
        deng.set("CE-1", {"aliases": "[1h, 1i]"}, **W)  # a write that sets aliases is checked


def test_setting_aliases_names_the_ones_it_drops(deng):
    deng.new("task", "First", **W)
    deng.set("CE-1", {"aliases": "[1h, est-activity]"}, **W)
    assert deng.set("CE-1", {"aliases": "1h"}, **W) == "CE-1: set aliases; dropped alias est-activity, which no longer resolves"
    assert deng.set("CE-1", {}, unset=("aliases",), **W) == "CE-1: set aliases; dropped alias 1h, which no longer resolves"


@pytest.mark.criterion("AC-40")
def test_find_links_to_resolves_an_alias_and_a_refusal_names_the_alias_it_followed(deng):
    deng.import_log(write_log(deng), **W)
    via_alias = deng.find(links_to="D-3")
    assert via_alias[0] == "D-3 is an alias of DEC-3" and via_alias[1:] == deng.find(links_to="DEC-3") != []
    assert deng.find(links_to="D-1")[0] == "D-1 is an alias of DEC-1"
    deng.new("task", "First", **W)
    deng.set("CE-1", {"aliases": "[1h]"}, **W)
    with pytest.raises(Refusal, match="1h is an alias of CE-1, which is not a decision") as r:
        deng.decision_show("1h")
    assert "`task show 1h` shows it" in r.value.remedy


@pytest.mark.criterion("AC-42")
def test_a_reimport_refuses_a_rejected_row_already_imported(deng):
    deng.import_log(write_log(deng), **W)
    later = LOG.split("## Entries")[0] + "## Entries\n\n### D-9 -- added later *(owner, 2026-10-13)*\n\nNew words.\n"
    before = sorted(p.name for p in (deng.root / "decisions").iterdir())
    with pytest.raises(Refusal, match=r"the rejected row '`tool -x` for three papers' was imported already, as DEC-5") as r:
        deng.import_log(write_log(deng, later), **W)
    assert "drop the `## Built and rejected, or decided against evidence` table from the copy" in r.value.remedy
    assert sorted(p.name for p in (deng.root / "decisions").iterdir()) == before


@pytest.mark.criterion("AC-42")
@pytest.mark.parametrize(
    "edit, match",
    [
        (("D-", "US-"), "the log's entry US-4 would become DEC-4, whose old id US-4, which reads as an id of the story series"),  # a kind's prefix here
        (("### D-1 ", "### DEC-01 "), "the log's entry DEC-01 is in the kind's own prefix but not written as the engine writes it"),
    ],
)
def test_the_dry_run_refuses_what_the_import_would(deng, edit, match):
    path = write_log(deng, LOG.replace(*edit))
    for dry in (True, False):
        with pytest.raises(Refusal, match=match):
            deng.import_log(path, dry_run=dry, **W)
    assert not (deng.root / "decisions").exists()


def test_an_import_names_another_kinds_record_carrying_an_old_id(deng):
    deng.new("task", "First", **W)
    deng.set("CE-1", {"aliases": "[D-4]"}, **W)
    with pytest.raises(Refusal, match="D-4 is already an alias of CE-1"):
        deng.import_log(write_log(deng), **W)


# -- CE-76: `decision find <text>` (adhoc dry run F24) ---------------------------------------------


@pytest.mark.criterion("AC-40")
def test_decision_find_takes_its_text_as_a_positional_argument(eng, capsys):
    dec(eng, "Meet on Monday")
    dec(eng, "Something else", body="Unrelated words.\n")
    root = ["--root", str(eng.root)]
    assert main([*root, "decision", "find", "monday"]) == 0
    positional = capsys.readouterr().out
    assert main([*root, "decision", "find", "--text", "monday"]) == 0
    assert positional == capsys.readouterr().out and positional.split()[0] == "D-1" and "D-2" not in positional
    assert main([*root, "decision", "find", "monday", "--text", "monday"]) == 0  # the same text twice is one text
    capsys.readouterr()
    assert main([*root, "decision", "find", "monday", "--text", "tuesday"]) == 2
    assert "two search texts" in capsys.readouterr().err
