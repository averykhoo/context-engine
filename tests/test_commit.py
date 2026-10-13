"""The engine commits its own writes by path (FRAMEWORK §5.5 rule 4, CE-45): every op log line
HEAD lacks, with the files those lines name, so a clean checkout of any commit passes lint on
its own, and nothing another session staged or left untracked rides along."""

import dataclasses
import json
import re
import shutil
import subprocess
import time
from pathlib import Path

import pytest

from context_engine import commit as C
from context_engine import mcp, ops
from context_engine.config import load
from context_engine.errors import Refusal
from context_engine.lock import FileLock
from context_engine.working import Engine

from test_working import ACTOR, CONFIG, FRAMEWORK, LEDGER, NOTE, TODAY
from conftest import _toml


def git(root, *args, check=True):
    p = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8")
    if check and p.returncode != 0:
        raise AssertionError(f"git {' '.join(args)}: {p.stderr}")
    return p.stdout


def _write_target(root: Path, config: dict = CONFIG) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "context.toml").write_text(_toml(config), encoding="utf-8")
    (root / "ledger.md").write_text(LEDGER, encoding="utf-8")
    (root / "HANDOFF.md").write_text(NOTE.format(key="2026-10-07b"), encoding="utf-8")
    (root / "CLAUDE.md").write_text(f"# contract\n\nframework: {FRAMEWORK}\n", encoding="utf-8")


def _init(root: Path, commit: bool = True) -> None:
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.email", "t@example.com")
    git(root, "config", "user.name", "t")
    git(root, "config", "core.autocrlf", "false")
    if commit:
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "base")


@pytest.fixture(scope="module")
def _template(tmp_path_factory):
    root = tmp_path_factory.mktemp("template") / "repo"
    _write_target(root)
    _init(root)
    return root


@pytest.fixture
def repo(tmp_path, _template):
    """A target repo under git with one base commit: a copy of one made once per module, which
    saves six git processes a test."""
    root = tmp_path / "repo"
    shutil.copytree(_template, root)
    return root


def eng(root, **config) -> Engine:
    cfg = load(root)
    return Engine(root, config=dataclasses.replace(cfg, **config) if config else cfg, today=lambda: TODAY)


def run(root, name, c, **kw):
    """An operation as the CLI and the MCP server run it (``Op.call``)."""
    o = ops.OPS[name]
    return o.call(o.target(root), c, **kw)


def start(root) -> ops.Caller:
    c = ops.Caller(actor=ACTOR)
    run(root, "session_start", c)
    return c


def head(root) -> str:
    return git(root, "rev-parse", "--short", "HEAD").strip()


def files_at(root, rev="HEAD") -> list[str]:
    return sorted(git(root, "show", "--name-only", "--format=", rev).split())


def count(root) -> int:
    return int(git(root, "rev-list", "--count", "HEAD"))


# -- what a commit carries -------------------------------------------------------------------


def test_a_mid_session_commit_passes_lint_on_its_own(repo, tmp_path):
    """The defect CE-45 fixes: the session commits its work by path, and a clean checkout of
    that commit must pass G-W7 without the op log lines still sitting in the shared tree."""
    c = start(repo)
    run(repo, "task_new", c, title="Build the parser")
    run(repo, "session_close", c, rows="CE-1 (filed)", summary=["filed"], guards="gate green", read="board")
    c = start(repo)
    run(repo, "task_touch", c, id="CE-1")
    (repo / "parser.py").write_text("x = 1\n", encoding="utf-8")
    git(repo, "add", "parser.py")
    task_file = next((repo / "tasks").glob("CE-1-*.md")).relative_to(repo).as_posix()
    git(repo, "add", task_file)  # a no-op when the engine committed it; else the old ritual's add
    # the per-task commit a session makes by path: its code and the board item, never `-A`
    git(repo, "commit", "-q", "-o", "parser.py", task_file, "-m", "CE-1: the parser", "-m", f"Session: {c.session}")
    clone = tmp_path / "clone"
    git(tmp_path, "-c", "core.autocrlf=false", "clone", "-q", str(repo), str(clone))
    assert [str(f) for f in Engine(clone, today=lambda: TODAY).lint() if f.guard == "G-W7"] == []
    assert git(repo, "status", "--porcelain").strip() == ""  # nothing of the engine's left dirty


def test_a_write_commits_its_record_with_its_op_line_and_nothing_else(repo):
    c = start(repo)
    (repo / "HANDOFF.md").write_text("# HANDOFF\n\n## Banner (2026-10-07b)\n\n- staged by someone else\n", encoding="utf-8")
    git(repo, "add", "HANDOFF.md")  # another session's staged edit: must stay staged, uncommitted
    (repo / "wip.py").write_text("y = 2\n", encoding="utf-8")  # untracked work: must stay untracked
    _, line = run(repo, "task_new", c, title="Build the parser")
    task_file = next((repo / "tasks").glob("CE-1-*.md")).relative_to(repo).as_posix()
    assert line.endswith(f"; committed {head(repo)}"), line
    assert files_at(repo) == sorted(["ops.jsonl", task_file])
    status = git(repo, "status", "--porcelain")
    assert "M  HANDOFF.md" in status and "?? wip.py" in status
    msg = git(repo, "log", "-1", "--format=%B")
    assert msg.splitlines()[0] == "engine: new CE-1"
    trailers = subprocess.run(["git", "interpret-trailers", "--parse"], cwd=repo, input=msg, capture_output=True, text=True, check=True).stdout
    assert trailers.splitlines() == [f"Session: {c.session}"]


def test_a_library_call_commits_too(repo):
    """Not only the CLI and MCP path: any write through the store commits when its lock is let go."""
    e = eng(repo)
    key = e.session_start(actor=ACTOR)
    before = count(repo)
    rec = e.new("task", "Straight from the library", session=key, actor=ACTOR)
    assert count(repo) == before + 1 and e.store.last_commit.sha == head(repo)
    assert files_at(repo) == sorted(["ops.jsonl", rec.path.relative_to(repo).as_posix()])


def test_one_operation_that_writes_twice_makes_one_commit(repo):
    """`ask answer` writes a decision, then closes the question: one operation, one commit."""
    c = start(repo)
    run(repo, "ask_new", c, title="Red or blue?")
    before = count(repo)
    _, line = run(repo, "ask_answer", c, id="ASK-1", words="blue", title="Blue it is")
    assert count(repo) == before + 1, line
    names = files_at(repo)
    assert "ops.jsonl" in names and any(n.startswith("decisions/DEC-1") for n in names) and any(n.startswith("tasks/ASK-1") for n in names)
    assert git(repo, "log", "-1", "--format=%s").strip() == "engine: new DEC-1, ask.answer ASK-1"


def test_the_session_ledger_is_committed_at_start_and_close(repo):
    c = start(repo)
    assert files_at(repo) == ["ledger.md", "ops.jsonl"]
    run(repo, "session_close", c, rows="none", summary=["nothing"], guards="gate green", read="board")
    assert files_at(repo) == ["ledger.md", "ops.jsonl"]
    assert git(repo, "log", "-1", "--format=%s").strip() == f"engine: session.close {c.session}"
    assert git(repo, "status", "--porcelain").strip() == ""


def test_another_sessions_leftover_lines_ride_along_with_the_files_they_name(repo):
    """A session whose commit never happened (an older engine, a by-hand op, a crash) leaves
    op lines and records in the tree; the next engine commit carries them, and says whose."""
    c = start(repo)
    other = eng(repo, commit=False)  # the leftover: written, never committed
    key = other.session_start(actor=ACTOR)
    other.new("task", "Left behind", session=key, actor=ACTOR)
    assert "tasks/" in git(repo, "status", "--porcelain")
    run(repo, "task_new", c, title="Mine")
    names = files_at(repo)
    assert any(n.startswith("tasks/CE-1") for n in names) and any(n.startswith("tasks/CE-2") for n in names)
    assert "ledger.md" in names and "ops.jsonl" in names
    msg = git(repo, "log", "-1", "--format=%B")
    assert f"left uncommitted by session {key}" in msg and msg.rstrip().endswith(f"Session: {c.session}")
    assert git(repo, "status", "--porcelain").strip() == ""


def test_the_mcp_tool_commits_as_the_cli_does(repo):
    state = ops.Caller(actor=ACTOR)
    mcp.make_tool(ops.OPS["session_start"], repo, state)()
    line = mcp.make_tool(ops.OPS["task_new"], repo, state)(title="Over MCP")
    assert line.endswith(f"; committed {head(repo)}"), line
    assert any(n.startswith("tasks/CE-1") for n in files_at(repo))


def test_a_root_below_the_top_of_the_work_tree_commits_its_own_paths(tmp_path):
    top = tmp_path / "mono"
    _write_target(top / "svc")
    _init(top)
    c = start(top / "svc")
    _, line = run(top / "svc", "task_new", c, title="In a subdirectory")
    assert "; committed" in line, line
    names = files_at(top)
    assert "svc/ops.jsonl" in names and any(n.startswith("svc/tasks/CE-1") for n in names)


def test_a_fresh_repo_commits_once_its_config_is_committed_or_staged(tmp_path):
    """A clean checkout of an engine commit that lacks context.toml would not lint: until the kit
    is committed (or staged) the engine says so instead of committing."""
    root = tmp_path / "fresh"
    _write_target(root)
    _init(root, commit=False)
    c = ops.Caller(actor=ACTOR)
    _, line = run(root, "session_start", c)
    assert "not committed: context.toml is not committed in this repo" in line and "rituals § Bootstrap" in line, line
    git(root, "add", "context.toml", "CLAUDE.md", "HANDOFF.md")  # the bootstrap's kit commit, staged
    _, line = run(root, "task_new", c, title="First")
    assert "; committed" in line, line
    task_file = next((root / "tasks").glob("CE-1-*.md")).relative_to(root).as_posix()
    assert files_at(root) == sorted(["ledger.md", "ops.jsonl", task_file])  # --only: the staged kit stays staged
    assert "A  context.toml" in git(root, "status", "--porcelain")


def test_a_target_inside_an_unrelated_repo_never_commits_into_it(tmp_path):
    outer = tmp_path / "outer"
    outer.mkdir()
    (outer / "README.md").write_text("outer\n", encoding="utf-8")
    _init(outer)
    _write_target(outer / "inner")
    before = head(outer)
    _, line = run(outer / "inner", "session_start", ops.Caller(actor=ACTOR))
    assert "not committed: context.toml is not committed in this repo (this target is inner inside a larger repo)" in line, line
    assert head(outer) == before


# -- when it does not commit -------------------------------------------------------------------


def test_a_target_that_is_not_a_git_repo_is_written_and_says_nothing(tmp_path):
    root = tmp_path / "plain"
    _write_target(root)
    assert not any((p / ".git").exists() for p in (root, *root.parents))
    c = start(root)
    code, line = run(root, "task_new", c, title="No git here")
    assert code == 0 and "; committed" not in line and "not committed" not in line, line
    assert next((root / "tasks").glob("CE-1-*.md")).exists()


def test_commit_false_leaves_every_commit_but_a_pauses_to_the_session(repo):
    (repo / "context.toml").write_text(_toml({**CONFIG, "engine": {**CONFIG["engine"], "commit": False}}), encoding="utf-8")
    git(repo, "commit", "-q", "-am", "commit = false")
    before = count(repo)
    c = start(repo)
    _, line = run(repo, "task_new", c, title="Not committed")
    assert count(repo) == before and "; committed" not in line and "not committed" not in line
    _, line = run(repo, "pause_open", c, in_flight="half done", resume="finish it")
    assert count(repo) == before + 1 and "; committed" in line  # AC-14: a pause commits regardless


@pytest.mark.parametrize("marker,what", [(m, w) for m, w in C.IN_PROGRESS])
def test_an_operation_in_progress_in_git_skips_the_commit_and_says_so(repo, marker, what):
    gitdir = Path(git(repo, "rev-parse", "--absolute-git-dir").strip())
    c = start(repo)
    before = head(repo)
    p = gitdir / marker
    p.mkdir() if marker.startswith("rebase") else p.write_text("0" * 40 + "\n", encoding="utf-8")
    _, line = run(repo, "task_new", c, title="During it")
    assert f"; not committed: {what} is in progress" in line and "git commit -o ops.jsonl" in line, line
    assert head(repo) == before
    assert next((repo / "tasks").glob("CE-1-*.md")).exists()  # the write itself stands


def test_a_real_merge_conflict_skips_the_commit(repo):
    (repo / "code.py").write_text("a = 0\n", encoding="utf-8")
    git(repo, "add", "code.py")
    git(repo, "commit", "-q", "-m", "code")
    git(repo, "checkout", "-q", "-b", "other")
    (repo / "code.py").write_text("a = 1\n", encoding="utf-8")
    git(repo, "commit", "-q", "-am", "one")
    git(repo, "checkout", "-q", "main")
    (repo / "code.py").write_text("a = 2\n", encoding="utf-8")
    git(repo, "commit", "-q", "-am", "two")
    assert git(repo, "merge", "other", check=False) is not None
    c = start(repo)
    _, line = run(repo, "task_new", c, title="Mid-merge")
    assert "; not committed: a merge is in progress" in line, line
    assert git(repo, "rev-parse", "-q", "--verify", "MERGE_HEAD", check=False).strip()  # the merge is untouched


def test_a_detached_head_skips_the_commit(repo):
    git(repo, "checkout", "-q", "--detach")
    c = start(repo)
    assert "not committed: HEAD is detached" in run(repo, "task_new", c, title="Detached")[1]


def _hook(repo, body: str) -> None:
    hooks = Path(git(repo, "rev-parse", "--absolute-git-dir").strip()) / "hooks"
    hooks.mkdir(exist_ok=True)
    path = hooks / "pre-commit"
    path.write_bytes(("#!/bin/sh\n" + body + "\n").encode())
    path.chmod(0o755)


def test_hooks_run_and_a_refusing_hook_leaves_the_write_uncommitted(repo):
    _hook(repo, 'echo "hook says no" >&2\nexit 1')
    c = start(repo)  # refused too
    before = head(repo)
    _, line = run(repo, "task_new", c, title="Hooked")
    assert "not committed: `git commit` failed (hook says no)" in line, line
    assert head(repo) == before
    # its `git add` is taken back: a later plain `git commit` cannot carry the record without its line
    assert re.search(r"^\?\? tasks/", git(repo, "status", "--porcelain", "--untracked-files=all"), re.MULTILINE)
    _hook(repo, 'touch hook-ran\nexit 0')
    _, line = run(repo, "task_new", c, title="Hook passes")
    assert "; committed" in line and (repo / "hook-ran").exists()  # never `--no-verify`
    names = files_at(repo)
    assert any(n.startswith("tasks/CE-1") for n in names) and any(n.startswith("tasks/CE-2") for n in names)  # the refused one rode along


def test_a_held_index_lock_is_waited_for(repo, monkeypatch):
    """Deterministic: the lock goes away at the first retry's wait, so only a retry commits."""
    c = start(repo)
    lock = Path(git(repo, "rev-parse", "--absolute-git-dir").strip()) / "index.lock"
    lock.write_text("", encoding="utf-8")
    waits = []
    monkeypatch.setattr(C.time, "sleep", lambda s: (waits.append(s), lock.unlink(missing_ok=True)))
    _, line = run(repo, "task_new", c, title="Waited")
    assert "; committed" in line and waits, (line, waits)


def test_a_timed_out_git_returns_on_time_and_names_the_lock_it_left(repo, monkeypatch):
    """The output goes to files, not pipes: a hook's child holding a pipe would keep a Windows
    `subprocess.run` waiting long past its timeout, and the engine lock with it."""
    c = start(repo)
    _hook(repo, "sleep 6")
    monkeypatch.setattr(C, "GIT_TIMEOUT", 2)
    t = time.monotonic()
    _, line = run(repo, "task_new", c, title="Slow hook")
    assert time.monotonic() - t < 5.5, line
    assert "not committed: git took over 2s (a hook?)" in line, line


@pytest.mark.parametrize("var", ["GIT_DIR", "GIT_INDEX_FILE"])
def test_git_environment_variables_skip_the_commit_loudly(repo, tmp_path, monkeypatch, var):
    """Inside a git hook git sets these; a commit would go to that repo or index, not this tree."""
    c = start(repo)
    before = head(repo)
    monkeypatch.setenv(var, str(tmp_path / "elsewhere"))
    _, line = run(repo, "task_new", c, title="From a hook")
    monkeypatch.delenv(var)
    assert f"; not committed: {var} is set (inside a git hook?)" in line, line
    assert head(repo) == before


def test_a_repo_git_refuses_says_so(repo, monkeypatch):
    c = start(repo)
    monkeypatch.setenv("GIT_TEST_ASSUME_DIFFERENT_OWNER", "1")  # what a `safe.directory` refusal looks like
    _, line = run(repo, "task_new", c, title="Not mine")
    monkeypatch.delenv("GIT_TEST_ASSUME_DIFFERENT_OWNER")
    assert "; not committed: git refuses this repo (" in line and "dubious ownership" in line, line


def test_an_op_log_missing_lines_head_has_is_not_committed(repo):
    c = start(repo)
    run(repo, "task_new", c, title="One")
    log = repo / "ops.jsonl"
    log.write_text(log.read_text(encoding="utf-8").splitlines(keepends=True)[0], encoding="utf-8")  # cut by hand
    before = head(repo)
    _, line = run(repo, "task_new", c, title="Two")
    assert "; not committed: ops.jsonl lacks 1 line HEAD has" in line, line
    assert head(repo) == before


def test_a_line_naming_a_file_git_never_saw_and_a_bad_line_do_not_block_the_commit(repo):
    c = start(repo)
    with open(repo / "ops.jsonl", "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({"session": c.session, "op": "new", "id": "CE-90", "path": "tasks/CE-90-gone.md", "fields": []}) + "\n")
        f.write("not json\n")
    _, line = run(repo, "task_new", c, title="After them")
    assert "; committed" in line, line
    assert "not json" in git(repo, "show", "HEAD:ops.jsonl")


def test_a_refusal_after_a_write_says_what_became_of_the_write(repo):
    c = start(repo)

    def writes_then_refuses(e, c):
        e.baton_add("stamp it", "ran out of time", session=c.session, actor=c.actor)
        raise Refusal("something after the write", "retry")

    o = ops.Op("probe", writes_then_refuses, True)
    with pytest.raises(Refusal, match=r"retry \(what it wrote before the refusal was committed [0-9a-f]{7,}\)"):
        o.call(o.target(repo), c)
    assert any(n.startswith("working/BTN-1") for n in files_at(repo))


def test_an_operation_holds_the_lock_from_its_first_write_to_its_commit(repo):
    """So no other session's write lands between an operation's writes, and no other session's
    commit carries half of it."""
    e = eng(repo)
    key = e.session_start(actor=ACTOR)
    lockfile = repo / e.store.config.lockfile
    with e.store.batch():
        e.new("task", "First write", session=key, actor=ACTOR)
        with pytest.raises(Refusal, match="was held"):
            with FileLock(lockfile, timeout=0.2):
                pass
        e.new("task", "Second write", session=key, actor=ACTOR)
    assert len([n for n in files_at(repo) if n.startswith("tasks/")]) == 2


def test_thousands_of_named_paths_fit_no_command_line(repo):
    """Paths go to git through a file: Windows caps a command line at 32k characters."""
    c = start(repo)
    (repo / "tasks").mkdir(exist_ok=True)
    with open(repo / "ops.jsonl", "a", encoding="utf-8", newline="\n") as f:
        for n in range(700):  # 700 paths of 56 characters: 39k, over the cap
            rel = f"tasks/leftover-{n:04d}-with-a-name-long-enough-to-matter.md"
            (repo / rel).write_text("x\n", encoding="utf-8")
            f.write(json.dumps({"session": "2026-10-01a", "op": "set", "id": f"X-{n}", "path": rel, "fields": []}) + "\n")
    _, line = run(repo, "task_new", c, title="After many")
    assert "; committed" in line and "carrying lines left uncommitted by 2026-10-01a" in line, line
    assert len(files_at(repo)) == 702


def test_a_pause_that_cannot_be_committed_refuses_and_keeps_its_record(repo):
    """AC-14: a pause is committed at once, or the session is told to do it by hand."""
    c = start(repo)
    git(repo, "checkout", "-q", "--detach")
    with pytest.raises(Refusal, match=r"the pause record was written but not committed \(HEAD is detached"):
        run(repo, "pause_open", c, in_flight="half done", resume="finish it")
    assert next((repo / "working").glob("PAU-1-*.md")).exists()


def test_an_ignored_op_log_is_never_committed_and_says_so(repo):
    (repo / ".gitignore").write_text("ops.jsonl\n", encoding="utf-8")
    git(repo, "add", ".gitignore")
    git(repo, "commit", "-q", "-m", "ignore the op log")
    before = count(repo)
    c = start(repo)
    _, line = run(repo, "task_new", c, title="Kept out")
    assert count(repo) == before and "; not committed: ops.jsonl is gitignored" in line, line


def test_an_ignored_record_is_named_as_left_out(repo):
    (repo / ".gitignore").write_text("tasks/\n", encoding="utf-8")
    git(repo, "add", ".gitignore")
    git(repo, "commit", "-q", "-m", "ignore the board")
    c = start(repo)
    _, line = run(repo, "task_new", c, title="Hidden")
    assert re.search(r"; committed [0-9a-f]{7,} \(left out as gitignored: tasks/CE-1-hidden\.md\)$", line), line
    assert files_at(repo) == ["ops.jsonl"]


# -- the pieces ---------------------------------------------------------------------------------


def test_new_lines_is_a_multiset_difference_blind_to_line_endings():
    assert C.new_lines("a\r\nb\nb\nc\n", "a\nb\n") == ["b", "c"]
    assert C.new_lines("a\n", "a\r\n") == []
    assert C.new_lines("x\n\n", "") == ["x"]


def test_the_title_stays_short_and_names_the_rest():
    lines = [{"session": "2026-10-08a", "op": "touch", "id": f"CE-{n}"} for n in range(30)]
    title = C.message(lines, "2026-10-08a", None).splitlines()[0]
    assert len(title) <= C.TITLE_MAX and title.startswith("engine: touch CE-0, touch CE-1") and title.endswith("more)")
