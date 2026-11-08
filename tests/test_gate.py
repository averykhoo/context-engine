"""The scoped gate (FRAMEWORK §8.5 G-V1, CE-78): each gate run's result is recorded against a
content id of each scope's files, so the code gate re-runs only when its inputs changed, and
`context-engine commit` refuses a code path that no green run covers.

The traps pinned here are the ones graph-reachability-zanzibar-index paid for (its
scripts/gate_status.py): the id must survive `git add`, `git commit` and a committed deletion or
rename; it must see untracked files; it must never be invented; and the run ledger must be
gitignored, or it sits inside its own id."""

import dataclasses
import json
import os
import re
import sys
import shutil
import subprocess

import pytest

from context_engine import gate as G
from context_engine.cli import main
from context_engine.config import load
from context_engine.errors import Refusal
from context_engine.working import Engine

from conftest import _toml
from test_commit import _init, git
from test_working import ACTOR, CONFIG, FRAMEWORK, LEDGER, NOTE, TODAY

OK = ["{python}", "-c", "print('1 passed')"]
RED = ["{python}", "-c", "import sys; print('1 failed'); sys.exit(1)"]
EXCLUDE = ["tasks/**", "ledger.md", "ops.jsonl", "HANDOFF.md", "notes/**"]  # the records, as this repo's code scope leaves them out
SCOPES = {"code": {"exclude": EXCLUDE}, "all": {}}


def _config(command=OK, require="code", scopes=SCOPES, parts=None) -> dict:
    gate = {"command": command, "scopes": scopes} if parts is None else {"parts": parts, "scopes": scopes}
    if require:
        gate["require"] = require
    return {**CONFIG, "gate": gate}


def _target(root, config) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "context.toml").write_text(_toml(config), encoding="utf-8")
    (root / "ledger.md").write_text(LEDGER, encoding="utf-8")
    (root / "HANDOFF.md").write_text(NOTE.format(key="2026-10-07b"), encoding="utf-8")
    (root / "CLAUDE.md").write_text(f"# contract\n\nframework: {FRAMEWORK}\n", encoding="utf-8")
    (root / "src").mkdir(exist_ok=True)
    (root / "src" / "a.py").write_text("a = 1\n", encoding="utf-8")
    (root / "src" / "b.py").write_text("b = 1\n", encoding="utf-8")


@pytest.fixture(scope="module")
def _template(tmp_path_factory):
    root = tmp_path_factory.mktemp("gate-template") / "repo"
    _target(root, _config())
    _init(root)
    return root


@pytest.fixture
def repo(tmp_path, _template):
    root = tmp_path / "repo"
    shutil.copytree(_template, root)
    return root


def gate_of(root, **edits) -> G.Gate:
    if edits:
        (root / "context.toml").write_text(_toml(_config(**edits)), encoding="utf-8")
    return load(root).gate


def code_id(root) -> str:
    g = gate_of(root)
    return G.scope_id(root, g.scopes["code"], G.listing(root, g))


# -- the id: content, not commits (zanzibar GS-1) -------------------------------------------


def test_the_id_survives_git_add_and_git_commit_and_moves_on_an_edit(repo):
    (repo / "src" / "c.py").write_text("c = 1\n", encoding="utf-8")  # untracked: still read
    before = code_id(repo)
    git(repo, "add", "src/c.py")
    assert code_id(repo) == before, "git add moved the id"
    git(repo, "commit", "-q", "-m", "c")
    assert code_id(repo) == before, "git commit moved the id"
    (repo / "src" / "c.py").write_text("c = 2\n", encoding="utf-8")
    assert code_id(repo) != before, "an edit to a file in scope left the id where it was"


def test_the_id_survives_a_commit_of_a_deletion_or_rename(repo):
    """zanzibar's 2026-09-05b defect: a pending deletion hashed differently from a committed one,
    so a green row went stale on the commit of a rename."""
    (repo / "src" / "b.py").unlink()  # pending: still in the index
    (repo / "src" / "a.py").rename(repo / "src" / "a2.py")  # pending: a in the index, a2 untracked
    pending = code_id(repo)
    git(repo, "add", "-A", "src")
    git(repo, "commit", "-q", "-m", "delete and rename")
    assert code_id(repo) == pending


def test_control_a_deletion_or_a_rename_does_move_the_id(repo):
    """The control for the pin above: skipping a deleted path must not hide the deletion."""
    start = code_id(repo)
    (repo / "src" / "b.py").unlink()
    deleted = code_id(repo)
    assert deleted != start
    (repo / "src" / "a.py").rename(repo / "src" / "a2.py")
    assert code_id(repo) not in (start, deleted)


def test_an_excluded_file_does_not_move_the_scope_id_and_does_move_the_whole_tree_s(repo):
    g = gate_of(repo)
    before = G.scope_ids(repo, g)
    (repo / "tasks").mkdir()
    (repo / "tasks" / "CE-9-x.md").write_text("---\ntitle: x\n---\n", encoding="utf-8")
    after = G.scope_ids(repo, g)
    assert after["code"] == before["code"] and after["all"] != before["all"]


def test_a_changed_scope_definition_matches_no_old_row(repo):
    before = code_id(repo)
    g = gate_of(repo, scopes={"code": {"exclude": [*EXCLUDE, "nothing/**"]}})
    assert G.scope_id(repo, g.scopes["code"]) != before


def test_the_id_is_never_invented(repo, tmp_path):
    g = gate_of(repo)
    with pytest.raises(Refusal, match="covers no file"):
        G.scope_id(repo, G.Scope("none", include=("nowhere/**",)))
    bare = tmp_path / "bare"
    bare.mkdir()
    (bare / "a.py").write_text("a\n", encoding="utf-8")
    with pytest.raises(Refusal, match="git"):
        G.scope_id(bare, g.scopes["code"])


@pytest.mark.parametrize(
    "glob,path,hit",
    [
        ("**", "a/b/c.py", True), ("tasks/**", "tasks/x.md", True), ("tasks/**", "tasks/closed/x.md", True),
        ("tasks/**", "tasksx/y.md", False), ("**/*.md", "README.md", True), ("**/*.md", "a/b.md", True),
        ("*.md", "a/b.md", False), ("*.md", "b.md", True), ("docs/?.md", "docs/a.md", True), ("docs/?.md", "docs/ab.md", False),
        ("HANDOFF.md", "HANDOFF.md", True), ("HANDOFF.md", "x/HANDOFF.md", False), ("a.b", "axb", False),
    ],
)
def test_globs_span_directories_only_with_two_stars(glob, path, hit):
    assert bool(G._glob(glob).fullmatch(path)) is hit


@pytest.mark.parametrize(
    "gate,match",
    [
        ({"comand": []}, r"\[gate\] has unknown key 'comand'"),
        ({"command": "pytest"}, r"`command` is 'pytest'"),
        ({"scopes": {"Code": {}}}, r"names a scope 'Code'"),
        ({"scopes": {"code": {"exclude": "tasks/**"}}}, r"`exclude` is 'tasks/\*\*'"),
        ({"scopes": {"code": {"exclud": []}}}, r"unknown key 'exclud'"),
        ({"scopes": {"code": {"exclude": ["../x"]}}}, r"not a path relative"),
        ({"command": ["x"], "require": "code"}, r"`require` names scope 'code', which is not declared"),
        ({"scopes": {"code": {}}, "require": "code"}, r"sets `require` but no `command`"),
        ({"ledger": "C:/runs.jsonl"}, r"not a path relative"),
        # [gate.parts] (CE-181)
        ({"command": ["x"], "parts": {"a": {"command": ["x"], "scope": "s"}}, "scopes": {"s": {}}}, r"either `command` or `parts`"),
        ({"parts": {"a": {"command": [], "scope": "s"}}, "scopes": {"s": {}}}, r"\[gate\.parts\.a\] `command` is \[\]"),
        ({"parts": {"a": {"command": ["x"]}}, "scopes": {"s": {}}}, r"\[gate\.parts\.a\] names no `scope`"),
        ({"parts": {"a": {"command": ["x"], "scope": "nope"}}, "scopes": {"s": {}}}, r"scope 'nope', which is not declared"),
        ({"parts": {"a": {"command": ["x"], "scope": "s", "timeout": 5}}, "scopes": {"s": {}}}, r"unknown key 'timeout'"),
        ({"parts": {"readers": {"command": ["x"], "scope": "s"}}, "scopes": {"s": {}}}, r"'readers', which is reserved"),
        ({"parts": {"all": {"command": ["x"], "scope": "s"}}, "scopes": {"s": {}}}, r"'all', which is reserved"),
        ({"parts": {"A": {"command": ["x"], "scope": "s"}}, "scopes": {"s": {}}}, r"names a part 'A'"),
        ({"parts": "x"}, r"`parts` is not a table"),
        ({"parts": {"a": {"command": ["x"], "scope": "s"}}, "scopes": {"s": {"readers": ["t::r"]}}}, r"`parts` and a scope with `readers`"),
    ],
)
def test_the_gate_table_refuses_what_it_does_not_know(gate, match):
    with pytest.raises(Refusal, match=match):
        G.from_dict(gate)


def test_a_gate_of_parts_parses_in_declared_order_with_require_and_no_command():
    g = G.from_dict({"parts": {"b": {"command": ["x"], "scope": "s"}, "a": {"command": ["{python}", "y"], "scope": "s"}}, "scopes": {"s": {}}, "require": "s"})
    assert [p.name for p in g.parts] == ["b", "a"] and g.parts[0].command == ("x",) and g.parts[0].scope == "s" and g.command == ()
    assert g.parts[1].argv() == [sys.executable, "y"]
    assert G.from_dict({"command": [], "parts": {"a": {"command": ["x"], "scope": "s"}}, "scopes": {"s": {}}}).parts, "an empty `command`, as the kit's template ships it, is no command"


# -- the run ledger --------------------------------------------------------------------------


def test_a_green_run_covers_its_scopes_until_a_file_in_scope_changes(repo):
    g = gate_of(repo)
    assert G.status(repo, g, require="code")[0] == 1
    code, line = G.run(repo, g, session="2026-10-14g", actor=ACTOR)
    assert code == 0 and line.startswith("gate PASSED in ") and "(1 passed)" in line, line
    (row,) = G.read_rows(repo / g.ledger)
    assert row["status"] == "PASSED" and row["session"] == "2026-10-14g" and set(row["scopes"]) == {"all", "code"}
    assert G.status(repo, g, require="code")[0] == 0
    (repo / "HANDOFF.md").write_text("# HANDOFF\n\nedited\n", encoding="utf-8")  # out of the code scope
    code, text = G.status(repo, g, require="code")
    assert code == 0 and "all: NOT covered" in text and "code: covered" in text, text
    (repo / "src" / "a.py").write_text("a = 2\n", encoding="utf-8")
    code, text = G.status(repo, g, require="code")
    assert code == 1 and "code: NOT covered" in text and "(no run on it)" in text, text


def test_a_red_run_after_a_green_one_on_the_same_files_uncovers_them(repo):
    """The command changes in the Gate, not in context.toml: a context.toml edit would move the
    code scope's id (it is in the scope) and test nothing about the rows."""
    g = gate_of(repo)
    assert G.run(repo, g)[0] == 0
    red = dataclasses.replace(g, command=tuple(RED))
    assert G.run(repo, red)[0] == 1
    assert G.status(repo, red, require="code")[0] == 1
    assert G.status(repo, g, require="code")[0] == 1, "the newest row on these files is red, whatever its command"


def test_a_row_counts_only_for_the_command_configured_now(repo):
    g = gate_of(repo)
    assert G.run(repo, g)[0] == 0
    assert G.status(repo, g, require="code")[0] == 0
    other = dataclasses.replace(g, command=("{python}", "-c", "pass"))  # the same files: only the command differs
    code, text = G.status(repo, other, require="code")
    assert code == 1 and "code: NOT covered" in text, text


def test_a_run_whose_files_change_while_it_runs_counts_for_nothing(repo):
    touch = ["{python}", "-c", "open('src/a.py', 'a').write(chr(35))"]  # no backslash: conftest's _toml does not escape one
    g = gate_of(repo, command=touch)
    code, line = G.run(repo, g)
    assert code == 1 and line.startswith("gate INCONSISTENT") and "code" in line, line
    (row,) = G.read_rows(repo / g.ledger)
    assert row["scopes"] == {} and row["moved"] == ["all", "code"]
    assert G.status(repo, g, require="code")[0] == 1


def test_a_run_records_each_scope_whose_files_did_not_move_while_it_ran(repo):
    """A change outside a scope during a run (another session's op-log line) moves only the ids
    that cover it: the run is recorded on the rest, and names the moved ones, so a concurrent
    engine write never voids the code scope's result (review of 2026-10-14g, F2)."""
    oplog = ["{python}", "-c", "open('ops.jsonl', 'a').write(chr(123) + chr(125) + chr(10)); print('1 passed')"]
    g = gate_of(repo, command=oplog)
    code, line = G.run(repo, g)
    assert code == 0 and line.startswith("gate PASSED") and "not recorded on all: their files changed while it ran" in line, line
    (row,) = G.read_rows(repo / g.ledger)
    assert row["status"] == "PASSED" and set(row["scopes"]) == {"code"} and row["moved"] == ["all"], row
    code, text = G.status(repo, g, require="code")
    assert code == 0 and "code: covered" in text and "all: NOT covered" in text, text


def test_the_run_ledger_is_gitignored_and_a_tracked_one_is_refused(repo):
    g = gate_of(repo)
    G.run(repo, g)
    assert (repo / ".context" / "gate" / ".gitignore").read_text(encoding="utf-8") == "*\n"
    assert git(repo, "status", "--porcelain", "--untracked-files=all", ".context") == ""
    (repo / "context.toml").write_text(_toml({**_config(), "gate": {**_config()["gate"], "ledger": "runs.jsonl"}}), encoding="utf-8")
    with pytest.raises(Refusal, match="runs.jsonl is tracked or not gitignored"):
        G.run(repo, load(repo).gate)


def test_no_command_is_refused_with_its_remedy(repo):
    with pytest.raises(Refusal, match=r"\[gate\] has no `command`"):
        G.run(repo, gate_of(repo, command=[], require=""))


# -- the commit refusal (P7) -----------------------------------------------------------------


def _engine(root) -> tuple[Engine, str]:
    e = Engine(root, today=lambda: TODAY)
    return e, e.session_start(actor=ACTOR)


def test_commit_refuses_a_code_path_no_green_run_covers_and_takes_a_records_path(repo):
    e, key = _engine(repo)
    (repo / "src" / "a.py").write_text("a = 2\n", encoding="utf-8")
    with pytest.raises(Refusal, match=r"src/a.py is in gate scope 'code', which no green gate run covers") as r:
        e.commit(["src/a.py"], "CE-1: code", session=key, actor=ACTOR)
    assert "context-engine gate run" in r.value.remedy
    with pytest.raises(Refusal, match="src is in gate scope 'code'"):
        e.commit(["src"], "CE-1: code", session=key, actor=ACTOR)
    (repo / "HANDOFF.md").write_text(NOTE.format(key=key), encoding="utf-8")
    assert e.commit(["HANDOFF.md"], "records only", session=key, actor=ACTOR).startswith("committed ")
    assert G.run(repo, gate_of(repo))[0] == 0
    assert e.commit(["src/a.py"], "CE-1: code", session=key, actor=ACTOR).startswith("committed ")


def test_commit_refuses_a_deleted_code_path_too_and_checks_nothing_without_require(repo):
    e, key = _engine(repo)
    git(repo, "rm", "-q", "src/b.py")
    with pytest.raises(Refusal, match="src/b.py is in gate scope 'code'"):
        e.commit(["src/b.py"], "CE-1: delete", session=key, actor=ACTOR)
    gate_of(repo, require="")
    e = Engine(repo, today=lambda: TODAY)
    assert e.commit(["src/b.py", "context.toml"], "CE-1: delete", session=key, actor=ACTOR).startswith("committed ")


# -- the CLI ---------------------------------------------------------------------------------


def test_the_cli_runs_the_gate_and_requires_green(repo, capsys, monkeypatch):
    monkeypatch.chdir(repo)
    assert main(["gate", "status", "--require", "code"]) == 1
    assert "code: NOT covered" in capsys.readouterr().out
    assert main(["gate", "run"]) == 0
    assert capsys.readouterr().out.startswith("gate PASSED")
    assert main(["gate", "status", "--require", "code"]) == 0
    assert "require code: green" in capsys.readouterr().out
    assert main(["gate", "status", "--require", "nope"]) == 2
    assert "no gate scope named 'nope'" in capsys.readouterr().err
    p = subprocess.run(["git", "check-ignore", "-q", ".context/gate/runs.jsonl"], cwd=repo)
    assert p.returncode == 0
    rows = [json.loads(x) for x in (repo / ".context/gate/runs.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [r["status"] for r in rows] == ["PASSED"]


def test_manual_mode_s_by_hand_id_is_the_engine_s(repo):
    """manual-mode § The scoped gate computes the id by hand (DEC-20): its recipe, followed with
    nothing but git and hashlib, gives the engine's id."""
    import hashlib

    (repo / "src" / "b.py").unlink()  # step 1: a listed file the tree lacks is skipped
    (repo / "notes").mkdir()
    (repo / "notes" / "n.md").write_text("excluded\n", encoding="utf-8")
    scope = gate_of(repo).scopes["code"]
    raw = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=repo, capture_output=True).stdout
    listed = sorted({p for p in raw.split(b"\0") if p})
    spec = json.dumps({"include": sorted(scope.include), "exclude": sorted(scope.exclude), "readers": sorted(scope.readers)}, sort_keys=True)
    h = hashlib.sha256(f"context-engine-gate/g1/code/{spec}".encode() + b"\0")
    for rel in listed:
        if not scope.matches(rel.decode()) or not (repo / rel.decode()).exists():
            continue
        data = (repo / rel.decode()).read_bytes()
        h.update(rel + b"\0" + f"{len(data)}:{hashlib.sha256(data).hexdigest()}".encode() + b"\0")
    assert G.scope_id(repo, scope) == f"g1/code:{h.hexdigest()[:16]}"


# -- the guard on the exclusions (scope_guard) -------------------------------------------------

GUARDED = '''
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def test_reads_code():
    assert (ROOT / "src" / "a.py").read_text()


def test_reads_a_record():
    assert (ROOT / "HANDOFF.md").read_text()


def test_lists_the_records():
    assert list((ROOT / "notes").iterdir())


def test_starts_a_process_in_the_repo():
    subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True)


def test_starts_a_process_elsewhere(tmp_path):
    subprocess.run(["git", "--version"], cwd=tmp_path, capture_output=True)


def test_the_reader():
    assert (ROOT / "notes" / "n.md").read_text()
'''


@pytest.mark.parametrize("guard", ["on", "off"])
def test_the_scope_guard_fails_a_test_that_reads_an_excluded_path_unless_it_is_a_reader(repo, guard):
    """The exclusions fail open, so a survey is not enough: the guard fails, in the suite itself,
    any test that opens or lists an excluded path or starts a process in the repo; a reader
    passes. With the guard off (the control), every one of them passes."""
    (repo / "notes").mkdir()
    (repo / "notes" / "n.md").write_text("a note\n", encoding="utf-8")
    scopes = {"code": {"exclude": EXCLUDE, "readers": ["test_guarded.py::test_the_reader"]}}
    gate_of(repo, scopes=scopes)
    (repo / "conftest.py").write_text("from context_engine.scope_guard import pytest_runtest_makereport, pytest_runtest_protocol  # noqa: F401\n", encoding="utf-8")
    (repo / "test_guarded.py").write_text(GUARDED, encoding="utf-8")
    env = {**os.environ, "CE_SCOPE_GUARD": guard}
    p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rfE", "test_guarded.py"],
                       cwd=repo, capture_output=True, text=True, env=env, timeout=300)
    failed = sorted(set(re.findall(r"^FAILED test_guarded.py::(\w+)", p.stdout, re.MULTILINE)))
    if guard == "off":
        assert failed == [] and p.returncode == 0, p.stdout
        return
    assert p.returncode == 1 and failed == ["test_lists_the_records", "test_reads_a_record", "test_starts_a_process_in_the_repo"], p.stdout
    assert "opened HANDOFF.md" in p.stdout and "listed notes/" in p.stdout and "started a process in ./" in p.stdout, p.stdout


def test_readers_are_a_part_keyed_on_every_file_so_a_change_outside_the_scope_re_runs_only_them(repo):
    """A reader reads what its scope excludes, so a change there leaves the scope covered and its
    readers not: `gate status --require code+readers` says so, and `gate run --readers` re-runs
    just them (their names appended to the command)."""
    echo = ["{python}", "-c", "import sys; print(' '.join(sys.argv[1:]) or 'all')"]
    scopes = {"code": {"exclude": EXCLUDE, "readers": ["tests/test_r.py::test_reads"]}}
    g = gate_of(repo, command=echo, scopes=scopes)
    assert G.run(repo, g)[0] == 0
    assert G.status(repo, g, require="code+readers")[0] == 0
    (repo / "HANDOFF.md").write_text("# HANDOFF\n\nedited\n", encoding="utf-8")
    code, text = G.status(repo, g, require="code")
    assert code == 0 and "code: covered" in text and "require code: green" in text, text
    code, text = G.status(repo, g, require="code+readers")
    assert code == 1 and "code: covered" in text and "code+readers: NOT covered" in text and "gate run --readers" in text, text
    code, line = G.run(repo, g, readers=True)
    assert code == 0 and line.startswith("gate readers PASSED") and "(tests/test_r.py::test_reads)" in line, line
    rows = G.read_rows(repo / g.ledger)
    assert rows[-1]["part"] == "readers" and set(rows[-1]["scopes"]) == {"code+readers"} and rows[-1]["args"] == ["tests/test_r.py::test_reads"]
    assert G.status(repo, g, require="code+readers")[0] == 0
    (repo / "src" / "a.py").write_text("a = 3\n", encoding="utf-8")
    code, text = G.status(repo, g, require="code+readers")
    assert code == 1 and "require code+readers: red: run `context-engine gate run`" in text, "a readers run never covers the scope itself"
    with pytest.raises(Refusal, match="no gate scope named 'all\\+readers'"):
        G.status(repo, g, require="all+readers")
    with pytest.raises(Refusal, match="no gate scope names `readers`"):
        G.run(repo, gate_of(repo, scopes=SCOPES), readers=True)


def test_commit_checks_only_the_scope_so_an_engine_write_after_the_gate_run_does_not_refuse_it(repo):
    """The readers' id covers every file, the op log included, so every engine write moves it (this
    session's or a concurrent one's). The commit of a code path is checked on the scope alone: a
    green whole-gate run on exactly these code files still counts after an op-log line lands
    (review of 2026-10-14g, F1); a change to the code itself is still refused."""
    scopes = {"code": {"exclude": EXCLUDE, "readers": ["tests/test_r.py::test_reads"]}}
    g = gate_of(repo, scopes=scopes)
    (repo / "src" / "a.py").write_text("a = 2\n", encoding="utf-8")
    assert G.run(repo, g)[0] == 0
    e, key = _engine(repo)  # an engine write: an op-log line moves the readers' id, not the scope's
    code, text = G.status(repo, g, require="code+readers")
    assert code == 1 and "code: covered" in text and "code+readers: NOT covered" in text, text
    assert e.commit(["src/a.py"], "CE-1: code", session=key, actor=ACTOR).startswith("committed ")
    (repo / "src" / "a.py").write_text("a = 3\n", encoding="utf-8")
    with pytest.raises(Refusal, match="src/a.py is in gate scope 'code', which no green gate run covers"):
        e.commit(["src/a.py"], "CE-1: code", session=key, actor=ACTOR)


def test_a_close_s_own_writes_leave_step_2_s_run_covering_the_code_and_a_code_change_does_not(repo):
    """Clean close step 7 (procedures.md, CE-92) checks `gate status --require <scope>` instead of
    a second test run: the close's writes after step 2 (the ledger entry, the banner) are records,
    outside the code scope, so step 2's run still covers it; a code change after step 2 moves the
    id, so status is red and step 7 runs the gate again. The readers read those records (HANDOFF.md,
    the op log), so the close's writes leave `<scope>+readers` red: step 7 re-runs them
    (`gate run --readers`), as the full second run once did (review of 2026-10-16a)."""
    g = gate_of(repo, scopes={"code": {"exclude": EXCLUDE, "readers": ["tests/test_r.py::test_reads"]}, "all": {}})
    e, key = _engine(repo)
    assert G.run(repo, g, session=key, actor=ACTOR)[0] == 0  # step 2's gate
    assert G.status(repo, g, require="code+readers")[0] == 0  # step 2's run covered the readers too
    e.session_close(key, actor=ACTOR, rows="CE-1 (closed)", summary=["built it"], receipts={"guards": "gate 3 passed", "read": "board only"})
    e.banner_set("- my banner", e.banner().sha, session=key, actor=ACTOR)  # step 3
    code, text = G.status(repo, g, require="code")
    assert code == 0 and "code: covered" in text and "all: NOT covered" in text, text  # all moved: the close did write
    code, text = G.status(repo, g, require="code+readers")
    assert code == 1 and "code+readers: NOT covered" in text and "gate run --readers" in text, text  # the readers must re-run
    assert G.run(repo, g, readers=True, session=key, actor=ACTOR)[0] == 0
    assert G.status(repo, g, require="code+readers")[0] == 0
    (repo / "src" / "a.py").write_text("a = 2\n", encoding="utf-8")  # a code change after step 2
    code, text = G.status(repo, g, require="code")
    assert code == 1 and "code: NOT covered" in text, text


# -- a gate split into parts ([gate.parts], CE-181) ------------------------------------------

PARTS = {"unit": {"command": OK, "scope": "code"}, "docs": {"command": OK, "scope": "all"}}  # one command each: only the name tells their rows apart


def _parts(root) -> list[str]:
    return [r["part"] for r in G.read_rows(root / ".context/gate/runs.jsonl")]


def test_a_scope_is_covered_only_when_every_part_passed_on_its_files(repo):
    g = gate_of(repo, parts=PARTS)
    assert G.status(repo, g, require="code")[0] == 1
    code, out = G.run(repo, g, parts=["unit"])
    assert code == 0 and out.startswith("gate part unit PASSED in ") and out.endswith("gate: 1 part run: 1 PASSED"), out
    code, text = G.status(repo, g, require="code")
    assert code == 1 and "code: NOT covered" in text and "(part docs: no run on it)" in text and "part unit:" not in text, text
    assert G.run(repo, g, parts=["docs"])[0] == 0
    for key in ("code", "all", "code+parts", "all+parts"):
        code, text = G.status(repo, g, require=key)
        assert code == 0 and f"require {key}: green" in text, text
    rows = G.read_rows(repo / g.ledger)
    assert [r["part"] for r in rows] == ["unit", "docs"] and all(set(r["scopes"]) == {"all", "code"} for r in rows), rows


def test_a_close_stales_only_the_parts_that_read_its_writes_and_stale_re_runs_just_them(repo):
    """CE-181 (b): the close's writes (the ledger entry, the banner, HANDOFF.md) are outside the
    code scope, so a part keyed on it stays fresh; a part keyed on every file goes stale, and
    `gate run --stale` re-runs that part alone. Nothing in the close or the banner changes."""
    g = gate_of(repo, parts=PARTS)
    e, key = _engine(repo)
    assert G.run(repo, g, session=key, actor=ACTOR)[0] == 0  # step 2's gate: every part
    assert G.status(repo, g, require="code+parts")[0] == 0
    e.session_close(key, actor=ACTOR, rows="CE-1 (closed)", summary=["built it"], receipts={"guards": "gate 3 passed", "read": "board only"})
    e.banner_set("- my banner", e.banner().sha, session=key, actor=ACTOR)  # step 3: HANDOFF.md
    code, text = G.status(repo, g, require="code")
    assert code == 0 and "code: covered" in text, text  # the code is covered: docs's row recorded the code id too
    assert "part unit (scope code): fresh on " in text and "part docs (scope all): STALE on " in text, text
    code, text = G.status(repo, g, require="code+parts")
    assert code == 1 and text.splitlines()[-1] == "require code+parts: red: run `context-engine gate run --stale` (parts docs)", text
    n = len(G.read_rows(repo / g.ledger))
    code, out = G.run(repo, g, stale=True, session=key, actor=ACTOR)
    assert code == 0 and out.startswith("gate part docs PASSED") and "gate part unit" not in out, out
    assert _parts(repo)[n:] == ["docs"]
    assert G.status(repo, g, require="code+parts")[0] == 0
    code, out = G.run(repo, g, stale=True)
    assert code == 0 and out == "gate: every part is fresh and covers code: nothing to run", out
    assert len(_parts(repo)) == n + 1, "a --stale run with nothing stale wrote a row"


def test_a_code_change_stales_every_part(repo):
    g = gate_of(repo, parts=PARTS)
    assert G.run(repo, g)[0] == 0
    (repo / "src" / "a.py").write_text("a = 2\n", encoding="utf-8")
    code, text = G.status(repo, g, require="code")
    assert code == 1 and "(part unit: no run on it; part docs: no run on it)" in text, text
    assert G.run(repo, g, stale=True)[0] == 0
    assert _parts(repo) == ["unit", "docs", "unit", "docs"]
    assert G.status(repo, g, require="code+parts")[0] == 0


def test_a_part_whose_scope_misses_the_require_scope_is_stale_until_it_covers_that_too(repo):
    """A part keyed on a scope narrower than `require` (docs/** only) stays fresh on its own files
    when the code changes, but no longer covers the code: --stale must run it, or the require
    scope could never go green again by `--stale` alone."""
    (repo / "docs").mkdir()
    (repo / "docs" / "d.md").write_text("d\n", encoding="utf-8")
    scopes = {"code": {"exclude": EXCLUDE}, "all": {}, "prose": {"include": ["docs/**"]}}
    g = gate_of(repo, scopes=scopes, parts={"unit": {"command": OK, "scope": "code"}, "prose": {"command": OK, "scope": "prose"}})
    assert G.run(repo, g)[0] == 0
    (repo / "src" / "a.py").write_text("a = 2\n", encoding="utf-8")
    code, text = G.status(repo, g, require="code")
    assert code == 1 and "part prose (scope prose): STALE: it passed on g1/prose:" in text, text
    assert [p.name for p in G.stale_parts(G.read_rows(repo / g.ledger), g, G.scope_ids(repo, g))] == ["unit", "prose"]
    assert G.run(repo, g, stale=True)[0] == 0
    assert G.status(repo, g, require="code+parts")[0] == 0


def test_a_part_row_counts_only_for_that_part_and_its_command_now(repo):
    g = gate_of(repo, parts=PARTS)
    assert G.run(repo, g, parts=["unit"])[0] == 0
    ok, missing = G.covered(G.read_rows(repo / g.ledger), g, "code", code_id(repo))
    assert not ok and missing == ["docs"], "unit's row, of the same command, counted for docs"
    unit, docs = g.parts
    other = dataclasses.replace(g, parts=(dataclasses.replace(unit, command=("{python}", "-c", "pass")), docs))
    code, text = G.status(repo, other, require="code")
    assert code == 1 and "part unit: its newest run on it ran another command" in text, text
    assert G.run(repo, g, parts=["docs"])[0] == 0 and G.status(repo, g, require="code")[0] == 0
    red = dataclasses.replace(g, parts=(dataclasses.replace(unit, command=tuple(RED)), docs))
    assert G.run(repo, red, parts=["unit"])[0] == 1
    code, text = G.status(repo, g, require="code")
    assert code == 1 and "part unit: its newest run on it FAILED" in text, "the newest row of unit on these files is red, whatever its command"


def test_a_failing_part_does_not_stop_the_others_and_each_row_is_kept(repo):
    g = gate_of(repo, parts={"a": {"command": RED, "scope": "code"}, "b": {"command": OK, "scope": "code"}})
    code, out = G.run(repo, g)
    assert code == 1 and out.splitlines()[0].startswith("gate part a FAILED") and out.splitlines()[-1] == "gate: 2 parts run: 1 PASSED; FAILED: a", out
    assert [(r["part"], r["status"]) for r in G.read_rows(repo / g.ledger)] == [("a", "FAILED"), ("b", "PASSED")]
    code, text = G.status(repo, g, require="code")
    assert code == 1 and "(part a: its newest run on it FAILED)" in text and "part b (scope code): fresh" in text, text


def test_a_part_whose_files_move_while_it_runs_is_inconsistent_alone(repo):
    touch = ["{python}", "-c", "open('src/a.py', 'a').write(chr(35))"]  # no backslash: conftest's _toml does not escape one
    g = gate_of(repo, parts={"touch": {"command": touch, "scope": "code"}, "ok": {"command": OK, "scope": "code"}})
    code, out = G.run(repo, g)
    assert code == 1 and out.splitlines()[0].startswith("gate part touch INCONSISTENT") and out.endswith("; INCONSISTENT: touch"), out
    first, second = G.read_rows(repo / g.ledger)
    assert first["scopes"] == {} and first["moved"] == ["all", "code"] and first["part"] == "touch"
    assert second["status"] == "PASSED" and second["scopes"]["code"] == code_id(repo), "the next part ran on the new files"
    code, text = G.status(repo, g, require="code")
    assert code == 1 and "(part touch: no run on it)" in text, text


def test_commit_refuses_a_code_path_until_every_part_passed_on_it_and_never_checks_freshness(repo):
    """The commit check is the require scope's coverage, as with one command: an op-log write
    after the run stales the part keyed on every file, and the commit still goes through; a code
    change is refused until every part passed on it."""
    g = gate_of(repo, parts=PARTS)
    (repo / "src" / "a.py").write_text("a = 2\n", encoding="utf-8")
    assert G.run(repo, g)[0] == 0
    e, key = _engine(repo)  # an engine write: an op-log line moves `all`, so docs goes stale
    code, text = G.status(repo, g, require="code+parts")
    assert code == 1 and "code: covered" in text and "part docs (scope all): STALE" in text, text
    assert e.commit(["src/a.py"], "CE-1: code", session=key, actor=ACTOR).startswith("committed ")
    (repo / "src" / "a.py").write_text("a = 3\n", encoding="utf-8")
    assert G.run(repo, g, parts=["unit"])[0] == 0
    with pytest.raises(Refusal, match=r"src/a.py is in gate scope 'code', which no green gate run covers \(g1/code:\w+\); parts not passed on it: docs") as r:
        e.commit(["src/a.py"], "CE-1: code", session=key, actor=ACTOR)
    assert "context-engine gate run --stale" in r.value.remedy
    assert G.run(repo, g, stale=True)[0] == 0
    assert e.commit(["src/a.py"], "CE-1: code", session=key, actor=ACTOR).startswith("committed ")


def test_the_cli_runs_parts_and_requires_them(repo, capsys, monkeypatch):
    monkeypatch.chdir(repo)
    assert main(["gate", "run", "--stale"]) == 2 and "declares no parts" in capsys.readouterr().err  # one command: no parts
    assert main(["gate", "run", "--part", "x"]) == 2 and "declares no parts" in capsys.readouterr().err
    assert main(["gate", "status", "--require", "code+parts"]) == 2
    assert "no gate scope named 'code+parts'" in capsys.readouterr().err
    gate_of(repo, parts=PARTS)
    assert main(["gate", "run", "--part", "unit"]) == 0
    assert capsys.readouterr().out.startswith("gate part unit PASSED")
    assert main(["gate", "run", "--part", "nope"]) == 2
    assert "no gate part named 'nope'" in capsys.readouterr().err
    assert main(["gate", "run", "--stale"]) == 0
    assert capsys.readouterr().out.startswith("gate part docs PASSED")
    assert main(["gate", "status", "--require", "code+parts"]) == 0
    assert "require code+parts: green" in capsys.readouterr().out
    assert main(["gate", "run", "--part", "unit", "--part", "docs"]) == 0
    assert capsys.readouterr().out.splitlines()[-1] == "gate: 2 parts run: 2 PASSED"
    assert main(["gate", "run", "--readers"]) == 2 and "take no `--readers`" in capsys.readouterr().err
    assert main(["gate", "run", "--part", "unit", "--stale"]) == 2 and "`--part` with `--stale`" in capsys.readouterr().err
    assert main(["gate", "status", "--require", "code+readers"]) == 2 and "no gate scope named 'code+readers'" in capsys.readouterr().err


PART_LEAN = '''
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def test_reads_a_record():
    assert (ROOT / "HANDOFF.md").read_text()


def test_starts_a_process_in_the_repo():
    subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True)
'''


def test_the_scope_guard_keys_on_the_running_part_s_scope_not_require_s(repo):
    """A part is fresh on its own scope's id, so the guard checks its tests against that scope:
    a part keyed on every file may read the records (parts take no `readers`, so require's scope
    would leave it no remedy), and a part keyed on the code may not, whatever `require` is. Run
    outside `gate run` (no CE_GATE_PART), the guard keys on require and says so."""
    pytest_ = ["{python}", "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rfE"]
    parts = {"unit": {"command": pytest_ + ["test_unit.py"], "scope": "code"}, "lean": {"command": pytest_ + ["test_lean.py"], "scope": "all"}}
    g = gate_of(repo, parts=parts)  # require = code
    with open(repo / ".gitignore", "a", encoding="utf-8") as f:
        f.write("\n__pycache__/\n")  # the parts' own bytecode, or each run moves the ids it runs on
    (repo / "conftest.py").write_text("from context_engine.scope_guard import pytest_runtest_makereport, pytest_runtest_protocol  # noqa: F401\n", encoding="utf-8")
    (repo / "test_lean.py").write_text(PART_LEAN, encoding="utf-8")
    (repo / "test_unit.py").write_text("def test_code():\n    assert open('src/a.py').read()\n", encoding="utf-8")
    code, out = G.run(repo, g)
    assert code == 0 and out.splitlines()[-1] == "gate: 2 parts run: 2 PASSED", out
    (repo / "test_unit.py").write_text(PART_LEAN, encoding="utf-8")  # the code's part now reads a record
    code, out = G.run(repo, g, parts=["unit"])
    log = (repo / G.read_rows(repo / g.ledger)[-1]["log"]).read_text(encoding="utf-8", errors="replace")
    assert code == 1 and "in gate part 'unit'" in log and "opened HANDOFF.md" in log and "started a process in ./" in log, log
    assert "move the test to a part keyed on a scope that holds the path" in log and "`readers`, which" not in log, log
    env = {k: v for k, v in os.environ.items() if k not in (G.PART_ENV, "CE_SCOPE_GUARD")}
    p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rfE", "test_lean.py"],
                       cwd=repo, capture_output=True, text=True, env=env, timeout=300)
    assert p.returncode == 1 and "run outside `context-engine gate run`" in p.stdout and "gate run --part <name>" in p.stdout, p.stdout
