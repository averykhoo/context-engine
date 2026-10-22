"""The engine commits its writes by path (FRAMEWORK §5.5 rule 4, CE-45): every op log line HEAD
lacks, with the files those lines name (only the committing session's lines by default, CE-125;
`sweep` takes all), so a clean checkout of any commit passes lint on its own, and nothing
another session staged or left untracked goes into the commit. When it commits is the
`[engine] commit` policy (DEC-36, CE-55): at milestones by default, after every write, or only a
pause. The session's own commits take lines the same way (`context-engine commit`).

The sweep's own tests run under `every-write`, where each write commits, so each pins one case;
the policy's tests below them run under the default."""

import copy
import dataclasses
import json
import re
import shutil
import subprocess
import time
import types
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

EVERY = {**CONFIG, "engine": {**CONFIG["engine"], "commit": "every-write"}}  # the sweep's tests: each write commits


def git(root, *args, check=True):
    p = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8")
    if check and p.returncode != 0:
        raise AssertionError(f"git {' '.join(args)}: {p.stderr}")
    return p.stdout


def _write_target(root: Path, config: dict = EVERY) -> None:
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


def run(root, name, c, /, **kw):
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
    git(repo, "add", task_file)  # a no-op when the engine committed it; else the old procedure's add
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


def test_an_operation_that_writes_twice_and_is_no_milestone_makes_one_commit(repo):
    """`record stamp` of two ids is two writes, each under its own lock, and no milestone (no
    batch of its own): the one commit is `Op.call`'s batch, which the milestone `ask answer`
    above no longer shows, its own batch covering it (CE-66)."""
    for n in (1, 2):
        (repo / "decisions").mkdir(exist_ok=True)
        (repo / "decisions" / f"DEC-{n}-by-hand.md").write_text(
            f"---\ntype: Decision\nid: DEC-{n}\ntitle: By hand {n}\nactor: owner\ndecided: 2026-10-08\n"
            f"session: 2026-10-08a\ndecision_status: BUILT\n---\n\nWords {n}.\n", encoding="utf-8")
    git(repo, "add", "decisions")
    git(repo, "commit", "-q", "-m", "two decisions by hand")
    c = start(repo)
    before = count(repo)
    _, line = run(repo, "record_stamp", c, ids=["DEC-1", "DEC-2"])
    assert count(repo) == before + 1, line
    names = files_at(repo)
    assert "decisions/DEC-1-by-hand.md" in names and "decisions/DEC-2-by-hand.md" in names, names


def test_the_session_ledger_is_committed_at_start_and_close(repo):
    c = start(repo)
    assert files_at(repo) == ["ledger.md", "ops.jsonl"]
    run(repo, "session_close", c, rows="none", summary=["nothing"], guards="gate green", read="board")
    assert files_at(repo) == ["ledger.md", "ops.jsonl"]
    assert git(repo, "log", "-1", "--format=%s").strip() == f"engine: session.close {c.session}"
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
    assert "not committed: context.toml is not committed in this repo" in line and "procedures § Bootstrap" in line, line
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


@pytest.mark.parametrize("off", ["off", False])  # False: CE-45's spelling, still read
def test_commit_off_leaves_every_commit_but_a_pauses_to_the_session(repo, off):
    (repo / "context.toml").write_text(_toml({**CONFIG, "engine": {**CONFIG["engine"], "commit": off}}), encoding="utf-8")
    git(repo, "commit", "-q", "-am", "commit = off")
    before = count(repo)
    c = start(repo)
    _, line = run(repo, "task_new", c, title="Not committed")
    assert count(repo) == before and "; committed" not in line and "not committed" not in line
    _, line = run(repo, "task_close", c, id="CE-1", msg="done")  # a milestone, but the policy is off
    assert count(repo) == before and "; committed" not in line, line
    _, line = run(repo, "pause_open", c, in_flight="half done", resume="finish it")
    assert count(repo) == before + 1 and "; committed" in line  # AC-14: a pause commits regardless
    assert git(repo, "status", "--porcelain").strip() == ""  # and carries what the others left


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


def _hook(repo, body: str, name: str = "pre-commit") -> None:
    hooks = Path(git(repo, "rev-parse", "--absolute-git-dir").strip()) / "hooks"
    hooks.mkdir(exist_ok=True)
    path = hooks / name
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
    # the engine's own `time`, not the module: on Linux `subprocess` waits for git with `time.sleep`,
    # and a patched module unlinks git's own live lock mid-write (CE-67)
    monkeypatch.setattr(C, "time", types.SimpleNamespace(**{**vars(time), "sleep": lambda s: (waits.append(s), lock.unlink(missing_ok=True))}))
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


def test_a_post_commit_hook_timeout_after_head_moved_is_a_commit_with_a_warning(repo, monkeypatch):
    """CE-127: HEAD moved to the commit before a slow post-commit hook made git time out. That is
    a commit: the reply says so, and the new record's `git add` is not taken back (that left the
    index without a file HEAD has, so a plain commit would delete it)."""
    c = start(repo)
    _hook(repo, "sleep 6", name="post-commit")
    monkeypatch.setattr(C, "GIT_TIMEOUT", 2)
    before = head(repo)
    t = time.monotonic()
    _, line = run(repo, "task_new", c, title="Slow post-commit hook")
    assert time.monotonic() - t < 5.5, line
    assert head(repo) != before and f"; committed {head(repo)}" in line, line
    assert "WARNING: git took over 2s after the commit landed (a post-commit hook?)" in line, line
    assert any(n.startswith("tasks/CE-1") for n in files_at(repo))
    assert git(repo, "status", "--porcelain", "--untracked-files=all").strip() == ""  # the index is HEAD's


@pytest.mark.criterion("AC-78")
def test_a_post_commit_hook_timeout_after_a_partial_commit_resets_the_index(repo, monkeypatch):
    """CE-127 on the partial path (CE-125): the real index's reset runs after git's commit, so a
    timeout there skipped it and the index kept the old op log and lacked the new file."""
    a, b, key, theirs = _two(repo)
    _hook(repo, "sleep 6", name="post-commit")
    monkeypatch.setattr(C, "GIT_TIMEOUT", 2)
    (repo / "a.py").write_text("a = 1\n", encoding="utf-8")
    _, line = run(repo, "commit", a, paths=["a.py"], message="CE-9: a")
    assert line.startswith(f"committed {head(repo)}") and "WARNING: git took over 2s after the commit landed" in line, line
    assert "a.py" in files_at(repo) and f"left uncommitted: 2 op lines of {key}" in line, line
    status = git(repo, "status", "--porcelain", "--untracked-files=all").splitlines()
    assert sorted(status) == sorted([" M ops.jsonl", " M ledger.md", f"?? {theirs}"]), status  # nothing staged: the index is HEAD's


def test_a_timeout_counts_as_landed_only_for_this_commit_on_the_head_before(repo, tmp_path):
    """`_landed` names HEAD only when its parent is the HEAD before and its message is this
    one: HEAD unmoved, or moved by another commit, is a timeout before the commit."""
    g = C._Git(repo)
    before = C._rev(g, "HEAD")
    msg = tmp_path / "message"
    msg.write_bytes(b"CE-9: mine\n\nSession: 2026-10-22b\n")
    assert C._landed(g, before, msg) == ""  # HEAD did not move
    git(repo, "commit", "-q", "--allow-empty", "-F", str(msg))
    assert C._landed(g, before, msg) == head(repo)
    git(repo, "commit", "-q", "--allow-empty", "-F", str(msg))
    assert C._landed(g, before, msg) == ""  # the same message, but its parent is not the HEAD before
    git(repo, "reset", "-q", "--hard", before)
    git(repo, "commit", "-q", "--allow-empty", "-m", "someone else")
    assert C._landed(g, before, msg) == ""  # another message


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
    (repo / "notes").mkdir(exist_ok=True)  # not a record directory: the commit lints none of them
    with open(repo / "ops.jsonl", "a", encoding="utf-8", newline="\n") as f:
        for n in range(700):  # 700 paths of 57 characters: 39k, over the cap
            rel = f"notes/leftover-{n:04d}-with-a-name-long-enough-to-matter.txt"
            (repo / rel).write_text("x\n", encoding="utf-8")
            f.write(json.dumps({"session": "2026-10-01a", "op": "set", "id": f"X-{n}", "path": rel, "fields": []}) + "\n")
    _, line = run(repo, "commit", c, message="Adopt a dead session's lines", sweep=True)
    assert line.startswith("committed ") and "including op lines that 2026-10-01a left uncommitted" in line, line
    assert len(files_at(repo)) == 701


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


# -- the policy: commit at milestones (DEC-36, CE-55) ---------------------------------------------

STORY = {"type": "Story", "prefix": "US", "dir": "stories", "mode": "append-only", "required": ["title", "actor", "date", "story_status"],
         "enums": {"story_status": ["live", "unspecified", "unconfirmed", "retired"]}, "types": {"date": "date"}}
MILESTONE_CONFIG = copy.deepcopy(CONFIG)  # no `commit` key: the default policy
MILESTONE_CONFIG["kinds"]["story"] = STORY
MILESTONE_CONFIG["kinds"]["decision"]["enums"]["decision_status"].append("SUPERSEDED")
MILESTONE_CONFIG["guards"] = {**CONFIG["guards"], "stories": "story"}
MILESTONE_CONFIG["working"] = {**CONFIG["working"], "decision_index": "decisions/index.md", "baton_max_age": 0}  # 0: expiry has work at once
# DEC-36's milestones: a task's close, the owner-words writes, a hand-off (baton, pause) and the
# session's own close or pause; and the banner, which a clean close writes after the session's
# close (CE-55's call: DEC-36 names it in neither list). Every other write stays uncommitted until the next commit.
MILESTONES = {"task_close", "ask_answer", "record_new", "record_amend", "record_retire", "record_confirm", "decision_supersede",
              "baton_add", "pause_open", "session_close", "session_pause", "session_abandon", "banner_set"}
OWNER = {"actor": "owner", "story_status": "live"}


@pytest.fixture
def mrepo(tmp_path):
    root = tmp_path / "repo"
    _write_target(root, MILESTONE_CONFIG)
    _init(root)
    return root


def trailers(root, rev="HEAD") -> list[str]:
    msg = git(root, "log", "-1", "--format=%B", rev)
    # bytes, not text: text mode on Windows sends `\r\n`, and git then unfolds no continuation line (CE-67)
    p = subprocess.run(["git", "interpret-trailers", "--parse"], cwd=root, input=msg.encode("utf-8"), capture_output=True, check=True)
    return p.stdout.decode("utf-8").splitlines()


@pytest.mark.criterion("AC-76")
def test_the_milestones_are_dec_36s_and_every_other_write_rides_along(mrepo):
    """Every write operation, walked once under the default policy: exactly DEC-36's milestones
    commit, each carrying what rode along, and a new write operation must be placed here."""
    committed, walked = set(), []
    c = ops.Caller(actor=ACTOR)

    def lines() -> int:
        return len((mrepo / "ops.jsonl").read_text(encoding="utf-8").splitlines()) if (mrepo / "ops.jsonl").exists() else 0

    def w(op, /, **kw):
        before, logged = count(mrepo), lines()
        _, line = run(mrepo, op, c, **kw)
        walked.append(op)
        assert lines() > logged, (op, "wrote nothing, so the walk cannot place it")
        if count(mrepo) != before:
            committed.add(op)
            assert re.search(rf"; committed {head(mrepo)}( \(including op lines that \S+ left uncommitted\))?$", line), (op, line)
            left = [ln for ln in git(mrepo, "status", "--porcelain").splitlines() if ln[3:] not in ("a.py", "b.py", "log.md")]
            assert left == [], (op, "a milestone carries every write before it")
        else:
            assert "committed" not in line, (op, line)  # riding along says nothing
        return line

    w("session_start")
    w("task_new", title="One", pri="NOW")
    w("task_new", title="Two")
    w("task_set", id="CE-2", fields={"brief": "b"})
    w("task_promote", id="CE-2", pri="NEXT")
    w("task_dep", id="CE-2", add=["CE-1"])
    w("task_comment", id="CE-2", text="a note")
    w("task_touch", id="CE-2")
    w("task_section", id="CE-2", name="Traps", text="- one")
    w("task_close", id="CE-2", msg="done")
    w("task_reopen", id="CE-2", msg="not yet")
    (mrepo / "notes.md").write_text("# Notes\n\nACTIVE-PLAN until the trial ends.\n", encoding="utf-8")
    w("doc_freeze", path="notes.md")
    (mrepo / "old.md").write_text("# Old\n\nLIVING.\n", encoding="utf-8")
    git(mrepo, "add", "old.md")
    git(mrepo, "commit", "-q", "-m", "old.md, to archive")
    w("doc_archive", path="old.md", to="archive")
    w("ask_new", title="Which way?")
    w("ask_raised", ids=["ASK-1"])
    w("ask_later", id="ASK-1")
    w("ask_answer", id="ASK-1", words="this way", title="This way")
    w("record_new", kind="decision", title="Kept", body="Owner words.", fields={"actor": "owner", "decision_status": "BUILT"})
    w("record_amend", id="DEC-2", text="widened")
    w("record_correct", id="DEC-2", after="Owner", text="sic")
    w("decision_link", id="DEC-2", target="CE-1")
    for f in ("a.py", "b.py"):
        (mrepo / f).write_text("def f():\n    pass\n", encoding="utf-8")
    w("decision_link", id="DEC-2", target="a.py::f")
    w("decision_relink", id="DEC-2", old="a.py::f", new="b.py::f")
    w("decision_set", id="DEC-2", fields={"tags": "a, b"})
    w("decision_supersede", old="DEC-1", new="DEC-2")
    (mrepo / "decisions" / "index.md").write_text("stale\n", encoding="utf-8")  # so the regeneration writes
    w("hk_regen_index")
    w("record_new", kind="story", title="A story", body="the owner's words", fields=OWNER)
    w("record_new", kind="story", title="Again", body="the owner's words", fields=OWNER)
    w("record_retire", id="US-1", why="recorded again", by="agent", superseded_by="US-2")
    w("record_new", kind="story", title="Rebuilt", body="the agent's reading", fields={"actor": "agent (x, reconstructed from notes)", "story_status": "unconfirmed"})
    w("record_confirm", id="US-3", words="yes, that is it")
    w("baton_add", step="a step", why="no time")
    w("baton_done", id="BTN-1", evidence="did it")
    w("pause_open", in_flight="half done", resume="finish it")
    w("pause_resume", id="PAU-1")
    w("baton_add", step="left open", why="for the expiry")
    w("hk_expire_batons")
    sha = run(mrepo, "banner_show", c)[1].split()[3]
    w("banner_set", text="- Where things stand.", seen=sha)
    w("session_close", rows="CE-1, CE-2", summary=["built it"], guards="green", read="board")
    w("session_start")
    w("session_pause", rows="none", deferred="everything")
    dead = ops.Caller(actor=ACTOR)
    run(mrepo, "session_start", dead)
    w("session_start")
    w("session_abandon", key=dead.session, force=True)
    (mrepo / "log.md").write_text("### DEC-91 -- Old *(owner, 2026-01-01)*\n\nwords\n", encoding="utf-8")
    w("decision_import", path="log.md")
    hand = "---\ntype: Decision\nid: DEC-90\ntitle: By hand\nactor: owner\ndecided: 2026-10-08\nsession: 2026-10-08a\ndecision_status: BUILT\n---\n\nwords\n"
    (mrepo / "decisions" / "DEC-90-by-hand.md").write_text(hand, encoding="utf-8")
    w("record_stamp", ids=["DEC-90"])
    assert committed == MILESTONES
    writes = {o.name for o in ops.OPS.values() if o.write}
    assert writes - set(walked) == {"init", "commit"}  # init commits nothing; commit is the session's own (below)


@pytest.mark.criterion("AC-77")
def test_a_task_close_commits_with_closes_its_body_and_what_rode_along(mrepo):
    c = start(mrepo)
    run(mrepo, "task_new", c, title="Build the parser")
    run(mrepo, "task_comment", c, id="CE-1", text="half way")
    sabotage = "Sabotage: dropped the check -> test_parser red\nSabotage: cut the cap -> test_cap red"
    _, line = run(mrepo, "task_close", c, id="CE-1", msg="done in abc1234", body=sabotage)
    assert line.endswith(f"; committed {head(mrepo)}"), line
    msg = git(mrepo, "log", "-1", "--format=%B")
    assert msg.splitlines()[0] == "CE-1: close; done in abc1234", msg
    assert f"Ops: close CE-1, session.start {c.session}, new CE-1, comment CE-1" in msg, msg
    assert sabotage in msg
    assert trailers(mrepo) == ["Closes: CE-1", f"Session: {c.session}"], msg
    assert git(mrepo, "status", "--porcelain").strip() == ""


@pytest.mark.criterion("AC-77")
def test_a_long_close_message_is_cut_in_the_title_and_kept_whole_in_the_body(mrepo):
    c = start(mrepo)
    run(mrepo, "task_new", c, title="Long")
    words = "done in abc1234, with the parser, the lexer, the printer and the docs all reviewed twice over"
    run(mrepo, "task_close", c, id="CE-1", msg=words)
    msg = git(mrepo, "log", "-1", "--format=%B")
    title = msg.splitlines()[0]
    assert len(title) <= C.TITLE_MAX and title.startswith("CE-1: close; done in abc1234, with") and title.endswith("..."), title
    assert words in msg


@pytest.mark.criterion("AC-77")
def test_a_close_refused_after_its_write_commits_the_write_without_closes(mrepo, monkeypatch):
    """`Closes:` is set after the close's write: a close that refuses partway still commits what
    it wrote (the op log at HEAD must not lag), but never claims the item closed."""
    c = start(mrepo)
    run(mrepo, "task_new", c, title="Half")
    real = Engine._board_set

    def writes_then_refuses(self, *a, **kw):
        real(self, *a, **kw)
        raise Refusal("after the write", "retry")

    monkeypatch.setattr(Engine, "_board_set", writes_then_refuses)
    before = count(mrepo)
    with pytest.raises(Refusal, match=r"what it wrote before the refusal was committed"):
        run(mrepo, "task_close", c, id="CE-1", msg="done")
    assert count(mrepo) == before + 1
    assert not [t for t in trailers(mrepo) if t.startswith("Closes:")], trailers(mrepo)
    assert git(mrepo, "log", "-1", "--format=%s").startswith("engine: close CE-1")


@pytest.mark.criterion("AC-77")
def test_a_milestones_settings_are_spent_by_its_own_commit_or_refusal(mrepo):
    """One Engine for every call, as a library user holds it (the CLI and MCP make one per call):
    a close's title, `Closes:` and milestone mark never reach a later write's commit."""
    e = eng(mrepo)
    key = e.session_start(actor=ACTOR)
    e.new("task", "One", session=key, actor=ACTOR)
    e.close("CE-1", "done", session=key, actor=ACTOR, body="Sabotage: x -> y red")
    before = count(mrepo)
    e.new("task", "Two", session=key, actor=ACTOR)  # stays uncommitted: no commit, and nothing of the close's
    with pytest.raises(Refusal, match="already closed"):
        e.close("CE-1", "again", session=key, actor=ACTOR)  # its milestone mark is spent by its own lock exit
    e.new("task", "Three", session=key, actor=ACTOR)
    assert count(mrepo) == before
    e.baton_add("a step", "no time", session=key, actor=ACTOR)
    msg = git(mrepo, "log", "-1", "--format=%B")
    assert msg.startswith("engine: new BTN-1") and "Closes:" not in msg and "Sabotage:" not in msg, msg


@pytest.mark.criterion("AC-76")
@pytest.mark.parametrize("value,policy", [(True, "milestones"), (False, "off"), ("every-write", "every-write"), ("milestones", "milestones"), ("off", "off")])
def test_the_policy_reads_its_three_values_and_ce_45s_bools(tmp_path, value, policy):
    _write_target(tmp_path, {**CONFIG, "engine": {**CONFIG["engine"], "commit": value}})
    assert load(tmp_path).commit == policy
    _write_target(tmp_path, CONFIG)
    assert load(tmp_path).commit == "milestones"  # the default


@pytest.mark.criterion("AC-76")
def test_an_unknown_policy_refuses_naming_the_three(tmp_path):
    _write_target(tmp_path, {**CONFIG, "engine": {**CONFIG["engine"], "commit": "sometimes"}})
    with pytest.raises(Refusal, match=r'`commit` is .sometimes.*"milestones", "every-write", "off"'):
        load(tmp_path)


def test_an_upgraded_repo_saying_commit_true_commits_at_milestones(mrepo):
    """CE-45's kit wrote `commit = true` into every repo it set up: that repo now commits at
    milestones, as a new one does."""
    cfg = copy.deepcopy(MILESTONE_CONFIG)
    cfg["engine"]["commit"] = True
    (mrepo / "context.toml").write_text(_toml(cfg), encoding="utf-8")
    git(mrepo, "commit", "-q", "-am", "commit = true")
    before = count(mrepo)
    c = start(mrepo)
    run(mrepo, "task_new", c, title="Rides")
    assert count(mrepo) == before
    run(mrepo, "task_close", c, id="CE-1", msg="done")
    assert count(mrepo) == before + 1


# -- the session's own commit (`context-engine commit`) ------------------------------------------


@pytest.mark.criterion("AC-78")
def test_the_session_commit_carries_its_paths_with_the_op_log_and_the_records_it_names(mrepo, tmp_path):
    """The defect a milestone policy would bring back: the session commits its code mid-task
    while board writes stay uncommitted until the next commit; a commit of a record without its line fails
    lint on a clean checkout. `commit` sweeps them in, so every commit lints on its own."""
    c = start(mrepo)
    run(mrepo, "task_new", c, title="Build the parser")
    run(mrepo, "task_comment", c, id="CE-1", text="half way")
    (mrepo / "parser.py").write_text("x = 1\n", encoding="utf-8")  # new: added by the commit
    (mrepo / "CLAUDE.md").write_text("# contract\n\nframework: " + FRAMEWORK + "\n\nmore\n", encoding="utf-8")
    (mrepo / "HANDOFF.md").write_text("# HANDOFF\n\n## Banner (2026-10-07b)\n\n- staged by someone else\n", encoding="utf-8")
    git(mrepo, "add", "HANDOFF.md")  # another session's staged edit: stays staged
    (mrepo / "wip.py").write_text("y = 2\n", encoding="utf-8")  # untracked and not named: stays untracked
    _, line = run(mrepo, "commit", c, paths=["parser.py", "CLAUDE.md"], message="CE-1: the parser\n\nSabotage: x -> test_y red")
    task_file = next((mrepo / "tasks").glob("CE-1-*.md")).relative_to(mrepo).as_posix()
    assert line == f"committed {head(mrepo)}: 5 paths", line
    assert files_at(mrepo) == sorted(["CLAUDE.md", "parser.py", "ops.jsonl", "ledger.md", task_file])
    msg = git(mrepo, "log", "-1", "--format=%B")
    assert msg.startswith(f"CE-1: the parser\n\nOps: session.start {c.session}, new CE-1, comment CE-1\n\nSabotage: x -> test_y red\nSession: {c.session}\n"), msg
    assert trailers(mrepo) == ["Sabotage: x -> test_y red", f"Session: {c.session}"], msg  # a trailer-shaped last paragraph takes the trailer
    status = git(mrepo, "status", "--porcelain")
    assert status.splitlines() == ["M  HANDOFF.md", "?? wip.py"], status
    clone = tmp_path / "clone"
    git(tmp_path, "-c", "core.autocrlf=false", "clone", "-q", str(mrepo), str(clone))
    assert [str(f) for f in Engine(clone, today=lambda: TODAY).lint() if f.guard == "G-W7"] == []


@pytest.mark.criterion("AC-78")
def test_the_session_commit_keeps_its_trailer_block_and_adds_session_to_it(mrepo):
    c = start(mrepo)
    (mrepo / "a.py").write_text("a = 1\n", encoding="utf-8")
    run(mrepo, "commit", c, paths=["a.py"], message="CE-1: a\n\nCo-Authored-By: Someone <s@example.com>\n")
    assert trailers(mrepo) == ["Co-Authored-By: Someone <s@example.com>", f"Session: {c.session}"]
    msg = git(mrepo, "log", "-1", "--format=%B")
    assert msg.index("Ops: session.start") < msg.index("Co-Authored-By")  # what the engine adds goes before the trailers
    (mrepo / "a.py").write_text("a = 2\n", encoding="utf-8")
    run(mrepo, "commit", c, paths=["a.py"], message=f"CE-1: again\n\nSession: {c.session}\n\nCo-Authored-By: Someone <s@example.com>")
    assert f"Session: {c.session}" in trailers(mrepo)  # a Session line outside the last paragraph is no trailer to git
    (mrepo / "a.py").write_text("a = 3\n", encoding="utf-8")
    run(mrepo, "commit", c, paths=["a.py"], message=f"CE-1: three\n\nSession: {c.session}\nCloses: CE-1")
    assert git(mrepo, "log", "-1", "--format=%B").count("Session:") == 1  # the session's own trailer stands
    (mrepo / "a.py").write_text("a = 4\n", encoding="utf-8")
    run(mrepo, "commit", c, paths=["a.py"], message="CE-1: four\n\nSession: 2026-01-01a was the old key, in prose\n\nCloses: CE-1\n  continued")
    assert trailers(mrepo) == ["Closes: CE-1 continued", f"Session: {c.session}"], trailers(mrepo)  # the prose line is no trailer
    (mrepo / "a.py").write_text("a = 5\n", encoding="utf-8")
    run(mrepo, "commit", c, paths=["a.py"], message="CE-1: five\n\nSession: 2026-01-01a was the old key,\nso say it in prose")  # prose, not a trailer
    assert trailers(mrepo) == [f"Session: {c.session}"], trailers(mrepo)


def test_the_session_commit_with_no_paths_commits_the_op_log_and_what_it_names(mrepo):
    c = start(mrepo)
    run(mrepo, "task_new", c, title="Board only")
    _, line = run(mrepo, "commit", c, message="Board: file CE-1")
    assert line.startswith("committed ") and git(mrepo, "status", "--porcelain").strip() == "", line


@pytest.mark.criterion("AC-78")
def test_the_session_commit_takes_directories_and_absolute_paths(mrepo):
    c = start(mrepo)
    (mrepo / "src" / "deep").mkdir(parents=True)
    (mrepo / "src" / "old.py").write_text("old = 1\n", encoding="utf-8")
    git(mrepo, "add", "src/old.py")
    git(mrepo, "commit", "-q", "-m", "old")
    (mrepo / "src" / "old.py").write_text("old = 2\n", encoding="utf-8")  # a tracked change
    (mrepo / "src" / "new.py").write_text("new = 1\n", encoding="utf-8")  # and new files beside it, never added
    (mrepo / "src" / "deep" / "newer.py").write_text("newer = 1\n", encoding="utf-8")
    (mrepo / "README.md").write_text("readme\n", encoding="utf-8")
    _, line = run(mrepo, "commit", c, paths=["src", str(mrepo / "README.md")], message="CE-1: both")
    assert {"src/old.py", "src/new.py", "src/deep/newer.py", "README.md"} <= set(files_at(mrepo))
    assert line == f"committed {head(mrepo)}: {len(files_at(mrepo))} paths", line  # what git committed
    assert git(mrepo, "status", "--porcelain").strip() == ""


@pytest.mark.criterion("AC-78")
@pytest.mark.parametrize("policy", ["milestones", "every-write", "off"])
def test_the_session_commit_sweeps_whatever_the_policy(tmp_path, policy):
    root = tmp_path / "repo"
    _write_target(root, {**MILESTONE_CONFIG, "engine": {**MILESTONE_CONFIG["engine"], "commit": policy}})
    _init(root)
    c = start(root)
    run(root, "task_new", c, title="Rides, or not")
    (root / "a.py").write_text("a = 1\n", encoding="utf-8")
    _, line = run(root, "commit", c, paths=["a.py"], message="CE-1: a")
    assert line.startswith(f"committed {head(root)}") and "a.py" in files_at(root), line
    assert git(root, "status", "--porcelain").strip() == ""  # nothing of the engine's left behind


@pytest.mark.criterion("AC-76")
def test_a_milestone_never_commits_a_record_whose_frontmatter_does_not_parse(mrepo, tmp_path):
    """Another session's half-done hand edit to a record riding along: the next milestone, made
    by any session, would carry it as it stands and its clean checkout would not lint. It stops
    instead, naming the file; the edit finished, the next milestone carries it."""
    a = start(mrepo)
    run(mrepo, "task_new", a, title="Being edited")
    task = next((mrepo / "tasks").glob("CE-1-*.md"))
    good = task.read_bytes()
    task.write_bytes(good.replace(b"pri: LATER", b"pri: LATER\nlabels: [half"))  # mid-edit, by hand
    b = start(mrepo)
    before = count(mrepo)
    _, line = run(mrepo, "baton_add", b, step="a step", why="no time")
    assert count(mrepo) == before and f"not committed: tasks/{task.name} does not parse" in line, line
    task.write_bytes(good)  # the edit is finished (here: undone)
    _, line = run(mrepo, "baton_add", b, step="another", why="no time")
    assert "; committed" in line and f"tasks/{task.name}" in files_at(mrepo), line


@pytest.mark.criterion("AC-78")
@pytest.mark.parametrize("paths,message,why", [
    (["a.py"], "", "a commit with no message"),
    (["a.py"], "CE-1: x\n\nSession: 2026-01-01a", "names 2026-01-01a, not this session"),
    (["."], "CE-1: x", "is the whole repo"),
    ([":/"], "CE-1: x", "pathspec magic"),
    (["a.py", "ignored.log"], "CE-1: x", "ignored.log is gitignored"),
    ([], "CE-1: x", "nothing to commit"),
    (["a.py", "missing.py"], "CE-1: x", "did not match"),  # a.py is added, then the add is taken back
    (["../outside.py"], "CE-1: x", "outside this repo's root"),
    ([".gitignore"], "CE-1: x", "nothing to commit: no path given has a change"),
], ids=["no-message", "other-session", "whole-repo", "magic", "ignored", "nothing", "missing", "outside", "unchanged"])
def test_the_session_commit_refuses_what_it_cannot_commit_and_commits_nothing(mrepo, paths, message, why):
    (mrepo / ".gitignore").write_text("*.log\n", encoding="utf-8")
    git(mrepo, "add", ".gitignore")
    git(mrepo, "commit", "-q", "-m", "ignore logs")
    (mrepo / "ignored.log").write_text("x\n", encoding="utf-8")
    (mrepo / "a.py").write_text("a = 1\n", encoding="utf-8")
    c = ops.Caller("2026-10-13a", ACTOR)
    before = count(mrepo)
    with pytest.raises(Refusal, match=re.escape(why)):
        run(mrepo, "commit", c, paths=paths, message=message)
    assert count(mrepo) == before
    assert "?? a.py" in git(mrepo, "status", "--porcelain")  # an add is taken back


@pytest.mark.criterion("AC-78")
def test_the_session_commit_outside_git_refuses(tmp_path):
    root = tmp_path / "plain"
    _write_target(root, MILESTONE_CONFIG)
    (root / "a.py").write_text("a = 1\n", encoding="utf-8")
    with pytest.raises(Refusal, match="not inside a git work tree"):
        run(root, "commit", ops.Caller("2026-10-13a", ACTOR), paths=["a.py"], message="CE-1: a")


@pytest.mark.criterion("AC-78")
def test_the_session_commit_through_the_cli_and_the_mcp_tool(mrepo, capsys):
    from context_engine.cli import main

    c = start(mrepo)
    (mrepo / "a.py").write_text("a = 1\n", encoding="utf-8")
    (mrepo / "msg.txt").write_bytes("﻿CE-1: from a file\r\n\r\nits body\r\n".encode())  # PowerShell 5.1: a BOM, CRLF
    argv = ["--root", str(mrepo), "--session", c.session, "--actor", ACTOR]
    assert main([*argv, "commit", "a.py", "-F", str(mrepo / "msg.txt")]) == 0
    assert capsys.readouterr().out.strip().startswith(f"committed {head(mrepo)}")
    assert git(mrepo, "log", "-1", "--format=%B").startswith("CE-1: from a file\n\nits body\n")
    (mrepo / "a.py").write_text("a = 2\n", encoding="utf-8")
    assert main([*argv, "commit", "a.py", "-m", "CE-1: two", "-m", "para"]) == 0
    assert git(mrepo, "log", "-1", "--format=%B").startswith("CE-1: two\n\npara\n")
    assert main([*argv, "commit", "a.py", "-m", "CE-1: nothing changed"]) == 2
    assert "not committed" in capsys.readouterr().err
    (mrepo / "utf16.txt").write_bytes("CE-1: saved by Out-File\r\n".encode("utf-16"))  # PowerShell 5.1's default
    assert main([*argv, "commit", "a.py", "-F", str(mrepo / "utf16.txt")]) == 2
    assert "utf16.txt is not UTF-8" in capsys.readouterr().err
    (mrepo / "a.py").write_text("a = 3\n", encoding="utf-8")
    state = ops.Caller(c.session, ACTOR)
    line = mcp.make_tool(ops.OPS["commit"], mrepo, state)(paths=["a.py"], message="CE-1: over MCP")
    assert line == f"committed {head(mrepo)}: 1 path", line
    run(mrepo, "task_new", c, title="Closed from the CLI")
    (mrepo / "lines.md").write_bytes("\ufeffSabotage: a -> test_b red\r\n".encode())
    assert main([*argv, "task", "close", "CE-1", "-m", "done", "--body-file", str(mrepo / "lines.md")]) == 0
    assert "\n\nSabotage: a -> test_b red\n\nCloses: CE-1\n" in git(mrepo, "log", "-1", "--format=%B")


def test_a_new_repo_commits_its_kit_through_the_session_commit(tmp_path):
    """Bootstrap: a session that started before the kit was committed commits the kit with
    `commit`, its op lines riding along; the kit's own `context.toml` is in that commit."""
    root = tmp_path / "fresh"
    _write_target(root, MILESTONE_CONFIG)
    _init(root, commit=False)
    c = start(root)
    _, line = run(root, "commit", c, paths=["context.toml", "CLAUDE.md", "HANDOFF.md"], message="Adopt the framework")
    assert line.startswith("committed "), line
    assert files_at(root) == ["CLAUDE.md", "HANDOFF.md", "context.toml", "ledger.md", "ops.jsonl"]


# -- whose op lines a commit takes (CE-125) ---------------------------------------------------


def _two(root):
    """Session A through the ops, and B as a library engine that commits nothing on its own:
    B's lines stay uncommitted, as a live session's between its milestones or a dead one's."""
    a = start(root)
    b = eng(root, commit="off")
    key = b.session_start(actor=ACTOR)
    rec = b.new("task", "B's half-done work", session=key, actor=ACTOR)
    return a, b, key, rec.path.relative_to(root).as_posix()


@pytest.mark.criterion("AC-78")
def test_a_commit_leaves_another_sessions_lines_out_and_names_them(repo, tmp_path):
    """Adhoc AAR entry 22: a dead or concurrent session's op lines rode into the next session's
    commit. Now they stay in the tree, uncommitted, and the reply says whose and how many."""
    a, b, key, theirs = _two(repo)
    working_before = (repo / "ops.jsonl").read_bytes()
    (repo / "a.py").write_text("a = 1\n", encoding="utf-8")
    _, line = run(repo, "commit", a, paths=["a.py"], message="CE-9: a")
    assert line.startswith(f"committed {head(repo)}"), line
    assert f"left uncommitted: 2 op lines of {key}" in line and "--sweep" in line, line  # its session.start and its new
    assert theirs not in files_at(repo) and "ledger.md" not in files_at(repo)
    at_head = git(repo, "show", "HEAD:ops.jsonl")
    assert key not in at_head and f'"session": "{a.session}"' in at_head
    assert (repo / "ops.jsonl").read_bytes() == working_before  # the working op log is never rewritten
    status = git(repo, "status", "--porcelain", "--untracked-files=all").splitlines()
    assert sorted(status) == sorted([" M ops.jsonl", " M ledger.md", f"?? {theirs}"]), status  # a.py's index entry is HEAD's: nothing staged
    clone = tmp_path / "clone"
    git(tmp_path, "-c", "core.autocrlf=false", "clone", "-q", str(repo), str(clone))
    assert [str(f) for f in Engine(clone, today=lambda: TODAY).lint() if f.guard == "G-W7"] == []
    # B commits its own later: nothing is left behind, so the op log goes in whole and converges
    _, line = run(repo, "commit", ops.Caller(actor=ACTOR, session=key), message="CE-9: B's")
    assert "left uncommitted" not in line and theirs in files_at(repo), line
    assert git(repo, "show", "HEAD:ops.jsonl").encode() == (repo / "ops.jsonl").read_bytes()
    assert git(repo, "status", "--porcelain").strip() == ""


@pytest.mark.criterion("AC-78")
def test_a_line_of_another_session_on_a_file_the_commit_carries_goes_in_with_it(repo, tmp_path):
    """The file holds that write, so its line must go too, or G-W7 fails on a clean checkout."""
    a, b, key, theirs = _two(repo)
    rid = theirs.split("/")[1].split("-")[0] + "-" + theirs.split("/")[1].split("-")[1]
    _, line = run(repo, "task_comment", a, id=rid, text="A comments on B's item")  # A's line names B's file; it commits (every-write)
    assert f"; committed {head(repo)}" in line and theirs in files_at(repo) and f"including op lines that {key} left uncommitted" in line, line
    assert f"left uncommitted: 1 op line of {key}" in line, line  # its session.start, on the ledger
    clone = tmp_path / "clone"
    git(tmp_path, "-c", "core.autocrlf=false", "clone", "-q", str(repo), str(clone))
    assert [str(f) for f in Engine(clone, today=lambda: TODAY).lint() if f.guard == "G-W7"] == []


@pytest.mark.criterion("AC-78")
def test_sweep_takes_every_line_as_ce_45_did(repo):
    a, b, key, theirs = _two(repo)
    _, line = run(repo, "commit", a, message="Adopt a dead session's lines", sweep=True)
    assert theirs in files_at(repo) and "ledger.md" in files_at(repo) and "left uncommitted:" not in line, line
    assert f"left uncommitted by session {key}" in git(repo, "log", "-1", "--format=%B")
    assert git(repo, "status", "--porcelain").strip() == ""


@pytest.mark.criterion("AC-78")
def test_a_commit_with_only_another_sessions_lines_and_no_path_says_so(repo):
    a, b, key, theirs = _two(repo)
    before = count(repo)
    with pytest.raises(Refusal, match=rf"every uncommitted line in ops.jsonl is another session's.*2 op lines of {key}"):
        run(repo, "commit", a, message="nothing of mine")
    assert count(repo) == before


def test_a_milestone_leaves_another_sessions_lines_out_too(repo):
    """The adhoc case was an engine commit (`a24d18d`), not the session's own: the default is the same."""
    a, b, key, theirs = _two(repo)
    _, line = run(repo, "task_new", a, title="Mine")
    assert f"; committed {head(repo)}" in line and f"left uncommitted: 2 op lines of {key}" in line, line
    assert theirs not in files_at(repo)
    at_head = git(repo, "show", "HEAD:ops.jsonl")
    assert key not in at_head and '"op": "new", "id": "CE-2"' in at_head  # a partial op log: A's line, not B's


def test_a_failed_partial_commit_leaves_the_index_and_the_op_log_as_they_were(repo):
    a, b, key, theirs = _two(repo)
    _hook(repo, 'echo "hook says no" >&2\nexit 1')
    (repo / "a.py").write_text("a = 1\n", encoding="utf-8")
    before = ((repo / "ops.jsonl").read_bytes(), git(repo, "status", "--porcelain"), head(repo))
    with pytest.raises(Refusal, match=r"`git commit` failed \(hook says no\)"):
        run(repo, "commit", a, paths=["a.py"], message="CE-9: a")
    assert ((repo / "ops.jsonl").read_bytes(), git(repo, "status", "--porcelain"), head(repo)) == before
    _hook(repo, 'touch hook-ran\nexit 0')
    _, line = run(repo, "commit", a, paths=["a.py"], message="CE-9: a")
    assert "left uncommitted" in line and (repo / "hook-ran").exists(), line  # the partial commit runs hooks too


def test_select_takes_own_lines_lines_on_carried_paths_and_unreadable_ones():
    mine = json.dumps({"session": "2026-10-22b", "op": "new", "id": "CE-1", "path": "tasks/CE-1.md"})
    shared = json.dumps({"session": "2026-10-22a", "op": "comment", "id": "CE-1", "path": "tasks/CE-1.md"})
    under = json.dumps({"session": "2026-10-22a", "op": "set", "id": "CE-2", "path": "src/x.md"})
    elsewhere = json.dumps({"session": "2026-10-22a", "op": "set", "id": "CE-3", "path": "tasks/CE-3.md"})
    lines = [shared, mine, "not json", under, elsewhere]
    assert C.select(lines, "2026-10-22b", given=("src",)) == ([shared, mine, "not json", under], [elsewhere])
    assert C.select(lines, "2026-10-22b") == ([shared, mine, "not json"], [under, elsewhere])
    assert C.select(lines, "2026-10-22b", sweep=True) == (lines, [])


def test_select_leaves_an_unparseable_line_that_names_another_session_with_it():
    """CE-128: a line cut short or hand-broken still names its session in its text; it is that
    session's, so it stays out with its lines. One naming this session, or none, goes in."""
    theirs = '{"at": "2026-10-22T10:00:00+08:00", "session": "2026-10-22a", "op": "new", "id": "CE-4", "pa'
    mine = '{"session": "2026-10-22b", "op": "set", "id": "CE-5"'
    lines = [theirs, mine, "not json"]
    assert C.select(lines, "2026-10-22b") == ([mine, "not json"], [theirs])
    assert C.select(lines, "2026-10-22b", sweep=True) == (lines, [])
    assert [C.session_of(x) for x in lines] == ["2026-10-22a", "2026-10-22b", None]
    assert C._whose([theirs]) == (("2026-10-22a", 1),)
    assert C.unparseable([theirs, json.dumps({"session": "x"}), "[1]"]) == [theirs, "[1]"]


@pytest.mark.criterion("AC-78")
def test_another_sessions_unparseable_line_stays_out_of_the_commit(repo, tmp_path):
    """CE-128: another session's broken op line rode into every commit, so the op log at HEAD
    failed G-W7 and the CE-63 lint before `context-engine commit` refused every commit that took
    an op line. Now it stays in the tree, named as that session's, and HEAD's op log parses."""
    a = start(repo)
    broken = '{"at": "2026-10-07T10:00:00+08:00", "session": "2026-10-07z", "op": "new", "id": "CE-40", "pa'
    with open(repo / "ops.jsonl", "a", encoding="utf-8", newline="\n") as f:
        f.write(broken + "\n")
    assert C.unparseable(C.taken_lines(repo, "ops.jsonl", a.session)) == []  # what the commit lint can rely on
    assert C.unparseable(C.taken_lines(repo, "ops.jsonl", a.session, sweep=True)) == [broken]
    _, line = run(repo, "task_new", a, title="Mine")
    assert f"; committed {head(repo)}" in line and "left uncommitted: 1 op line of 2026-10-07z" in line, line
    assert broken not in git(repo, "show", "HEAD:ops.jsonl") and broken in (repo / "ops.jsonl").read_text(encoding="utf-8")
    clone = tmp_path / "clone"
    git(tmp_path, "-c", "core.autocrlf=false", "clone", "-q", str(repo), str(clone))
    assert [str(f) for f in Engine(clone, today=lambda: TODAY).lint() if f.guard == "G-W7"] == []


def test_a_pause_lists_another_sessions_paths_as_uncommitted(repo):
    """Its own commit leaves another session's lines out, so the files they name stay
    uncommitted, and the pause record says so (INV-45's list, with `pending(session)`)."""
    a, b, key, theirs = _two(repo)
    run(repo, "pause_open", a, in_flight="half done", resume="finish it")
    rec = next(Engine(repo, today=lambda: TODAY).store.records("pause"))
    assert theirs in rec.doc.get("uncommitted") and "ledger.md" in rec.doc.get("uncommitted"), rec.doc.get("uncommitted")
    assert theirs not in files_at(repo)


def test_a_partial_commit_in_a_root_below_the_top_of_the_work_tree(tmp_path):
    """The partial op log's index entry is a path from the top of the work tree."""
    top = tmp_path / "mono"
    _write_target(top / "svc")
    _init(top)
    a, b, key, theirs = _two(top / "svc")
    _, line = run(top / "svc", "task_new", a, title="Mine, in a subdirectory")
    assert "; committed" in line and "left uncommitted" in line, line
    names = files_at(top)
    assert "svc/ops.jsonl" in names and "ops.jsonl" not in names and f"svc/{theirs}" not in names, names
    assert key not in git(top, "show", "HEAD:svc/ops.jsonl")
    assert git(top, "status", "--porcelain", "--", "ops.jsonl").strip() == ""


def test_a_carried_decision_index_brings_every_decision_line_it_reflects(tmp_path):
    """The index is generated from every decision on disk, so a commit carrying it carries the
    decision lines it reflects, another session's too, or G-D6 fails at HEAD (CE-125 review)."""
    cfg = copy.deepcopy(CONFIG)
    cfg["working"]["decision_index"] = "decisions/index.md"
    root = tmp_path / "r"
    _write_target(root, cfg)
    _init(root)
    a = start(root)
    for title in ("One", "Two"):
        run(root, "record_new", a, kind="decision", title=title, body="x", fields={"actor": "owner", "decision_status": "PROVISIONAL"})
    b = eng(root, commit="off")
    key = b.session_start(actor=ACTOR)
    b.decision_set("DEC-1", {"decision_status": "BUILT"}, session=key, actor=ACTOR)
    run(root, "decision_set", a, id="DEC-2", fields={"decision_status": "BUILT"})
    _, line = run(root, "commit", a, message="CE-1: mine")
    assert f"including op lines that {key} left uncommitted" in line and "left uncommitted: 1 op line" in line, line  # only its session.start stays
    clone = tmp_path / "clone"
    git(tmp_path, "-c", "core.autocrlf=false", "clone", "-q", str(root), str(clone))
    assert [str(f) for f in Engine(clone, today=lambda: TODAY).lint() if f.guard in ("G-D6", "G-W7")] == []


def test_a_partial_commit_whose_index_update_fails_says_so(repo):
    """Committed, but a post-commit hook holds git's index lock, so the real index keeps the old
    entries and a plain commit would undo the work: the reply warns and names the command."""
    a, b, key, theirs = _two(repo)
    _hook(repo, 'touch "$(git rev-parse --git-common-dir)/index.lock"\nexit 0', name="post-commit")
    (repo / "a.py").write_text("a = 1\n", encoding="utf-8")
    _, line = run(repo, "commit", a, paths=["a.py"], message="CE-9: a")
    assert line.startswith(f"committed {head(repo)}") and "WARNING: the index was not updated" in line and "git reset -q HEAD -- ops.jsonl a.py" in line, line


# -- the session commit lints what it carries (CE-63) ------------------------------------------


@pytest.mark.criterion("AC-78")
def test_the_session_commit_refuses_a_path_lint_fails_and_commits_the_rest(mrepo):
    """Adhoc AAR entry 18: a close-docs commit went in with lint red, since `commit` ran no
    check. It now runs lint and refuses when a failure sits on a path it would carry, a given
    path or one its op lines name; a failure elsewhere is not this commit's."""
    c = start(mrepo)
    note = mrepo / "HANDOFF.md"
    note.write_text(note.read_text(encoding="utf-8") + "\n## Banner (2026-10-07a)\n\n- stacked\n", encoding="utf-8")  # G-D8
    before = count(mrepo)
    with pytest.raises(Refusal, match=r"lint fails on what this commit carries: G-D8 HANDOFF\.md: 2 banner headings.*keep the newest"):
        run(mrepo, "commit", c, paths=["HANDOFF.md"], message="Note: by hand")
    assert count(mrepo) == before
    (mrepo / "a.py").write_text("a = 1\n", encoding="utf-8")
    _, line = run(mrepo, "commit", c, paths=["a.py"], message="CE-1: a")  # HANDOFF.md is not carried
    assert line.startswith(f"committed {head(mrepo)}"), line


@pytest.mark.criterion("AC-78")
def test_the_session_commit_lints_the_records_its_op_lines_name(mrepo):
    c = start(mrepo)
    run(mrepo, "task_new", c, title="Hand-edited")
    rec = next((mrepo / "tasks").glob("CE-1-*.md"))
    rec.write_text(rec.read_text(encoding="utf-8").replace(f"moved: {c.session}", "moved: 2026-10-07a"), encoding="utf-8")  # G-W7
    before = count(mrepo)
    with pytest.raises(Refusal, match=rf"lint fails on what this commit carries: G-W7 {re.escape(rec.relative_to(mrepo).as_posix())}"):
        run(mrepo, "commit", c, message="Board: file CE-1")
    assert count(mrepo) == before
