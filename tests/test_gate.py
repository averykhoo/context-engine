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


def _config(command=OK, require="code", scopes=SCOPES) -> dict:
    gate = {"command": command, "scopes": scopes}
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
    ],
)
def test_the_gate_table_refuses_what_it_does_not_know(gate, match):
    with pytest.raises(Refusal, match=match):
        G.from_dict(gate)


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
    e.session_close(key, actor=ACTOR, rows="CE-1 (closed)", summary=["built it"], receipts={"guards": "gate green", "read": "board only"})
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
