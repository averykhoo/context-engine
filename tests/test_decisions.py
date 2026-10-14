"""Decision records (CE-5, FRAMEWORK §6.5): bracketed corrections, supersede and link in both
directions, decision set (CE-32), relink (CE-35), find, show and why(), the generated index
(G-D6), and the single-file log importer (AC-38 to AC-42, AC-53, AC-54)."""

import datetime as dt
import json
import re

import pytest

from context_engine import okf
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
    assert "Not an entry" not in get("D-1").body
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
        (("### D-1 – the first", "### X-1 – the first"), "prefix 'X'"),
        (("### D-1 – the first", "### D-2 – the first"), "two entries D-2"),
        (("*(owner, 2026-09-01; amended by evidence)*", "(owner, 2026-09-01)"), "has no `\\*\\(actor, date\\)\\*`"),
        (("*(agent, 2026-10-05)*", "*(agent, yesterday)*"), "no YYYY-MM-DD date"),
        (("**relaxes D-2**", "**relaxes D-9**"), "links D-9"),
        (("| keeping two duplicates | **removed**: duplicates | D-1 |", "| keeping two | duplicates | **removed** | D-1 |"), "has 4 cells"),
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
    assert main(["--root", str(eng.root), "--session", S, "--actor", ACTOR, "decision", "import", path]) == 0
    assert len(list((eng.root / "decisions").glob("D-*.md"))) == 6
