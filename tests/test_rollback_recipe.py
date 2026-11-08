"""The git recipe of procedures.md § Rollback and close (FRAMEWORK §6.13, US-13, CE-18).

The section is prose, but it makes claims about git that a rollback in a shared checkout leans
on: that the trailer query finds only the session's own commits, that a restore by path leaves
another writer's staged change in the index, that the same restore deletes a file the session
created, which then commits by path, and that a reversed hunk is checked before it is applied, a disjoint one
going through and an overlapping one refused with the file untouched. Each claim is run here in
a temporary repo, by the very command text the runbook gives (the constants below, which
``test_the_runbook_gives_the_commands_these_tests_run`` finds in the section), with
`core.autocrlf` off and on (Git for Windows turns it on, and a patch is made against the
repo's LF form)."""

from __future__ import annotations

import re
import shlex
import subprocess
from pathlib import Path

import pytest

from test_runbook import PROCEDURES, h2_sections, table_rows

SECTION = "Rollback and close (§6.13)"
A, B = "2026-01-01a", "2026-01-01b"  # the session rolling back, and another writer

# The runbook's command forms, word for word (placeholders as the section writes them).
FIND = "git log -F --grep=\"Session: <key>\" --format='%h %(trailers:key=Session,valueonly,separator=%x2C)' HEAD"
TOUCHED = "git log --format='%h %(trailers:key=Session,valueonly)' <first>^..HEAD -- <path>"
RESTORE = "git restore --source=<first>^ --worktree -- <path>"
CREATED = "git cat-file -e <first>^:<path>"
PATCH = "git diff --binary <c>^ <c> -- <path> > <patch>"
CHECK = "git apply -R --check <patch>"
APPLY = "git apply -R <patch>"
BACK_TO_HEAD = "git restore --source=HEAD --worktree -- <path>"
RECIPE = (FIND, TOUCHED, RESTORE, CREATED, PATCH, CHECK, APPLY, BACK_TO_HEAD)
# What no step's Engine or By hand cell may hold (the section's prose may forbid them by name).
FORBIDDEN = ("git stash", "git reset", "git clean", "git revert", "git checkout", "add -A", "--3way")


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8")
    assert not check or p.returncode == 0, f"git {' '.join(args)}: {p.stderr}"
    return p


def run(repo: Path, form: str, **subs: str) -> subprocess.CompletedProcess:
    """Run one of the runbook's command forms, its `<name>`s filled in; `> <file>` redirects."""
    for name, value in subs.items():
        form = form.replace(f"<{name}>", value)
    assert "<" not in form.replace("> ", ""), f"a placeholder left in {form!r}"
    cmd, _, out = form.partition(" > ")
    argv = shlex.split(cmd)
    assert argv[0] == "git"
    p = subprocess.run(["git", "-C", str(repo), *argv[1:]], capture_output=True)
    if out:
        assert p.returncode == 0, p.stderr
        Path(out).write_bytes(p.stdout)
    return p


class Repo:
    def __init__(self, root: Path, crlf: bool):
        self.root, self.crlf = root, crlf
        self.eol = "\r\n" if crlf else "\n"

    def write(self, rel: str, lines: list[str]) -> None:
        """Write a file as an editor on this checkout would: CRLF where autocrlf is on."""
        (self.root / rel).write_bytes(self.eol.join(lines + [""]).encode())

    def lines(self, rel: str) -> list[str]:
        return (self.root / rel).read_bytes().decode().replace("\r\n", "\n").splitlines()

    def commit(self, message: str, *paths: str) -> str:
        git(self.root, "add", "--", *paths)
        git(self.root, "commit", "-q", "-m", message, "--", *paths)
        return git(self.root, "rev-parse", "--short", "HEAD").stdout.strip()

    def staged(self) -> list[str]:
        return git(self.root, "diff", "--cached", "--name-only").stdout.split()


BASE = [f"line {i}" for i in range(1, 31)]  # far enough apart that lines 2, 15 and 28 are three hunks


def shared(**changed: str) -> list[str]:
    out = list(BASE)
    for at, text in changed.items():
        out[int(at[1:]) - 1] = text
    return out


@pytest.fixture(params=[False, True], ids=["lf", "autocrlf"])
def repo(request, tmp_path) -> Repo:
    """Two writers in one checkout. Session A (the one rolling back) changes a.txt, creates
    new.txt and changes shared.txt at lines 2 and 15; session B then changes shared.txt at line
    28, makes a commit whose body (not its trailers) mentions A's key, and leaves keep.txt staged."""
    r = Repo(tmp_path / "repo", request.param)
    r.root.mkdir()
    git(r.root, "init", "-q", "-b", "main")
    git(r.root, "config", "user.email", "t@example.com")
    git(r.root, "config", "user.name", "t")
    git(r.root, "config", "core.autocrlf", "true" if r.crlf else "false")
    r.write("a.txt", ["1", "2", "3"])
    r.write("shared.txt", BASE)
    r.write("keep.txt", ["k"])
    r.write("other.txt", ["o"])
    r.c0 = r.commit("base", "a.txt", "shared.txt", "keep.txt", "other.txt")
    r.write("a.txt", ["1", "A", "3"])
    r.write("new.txt", ["new"])
    r.write("shared.txt", shared(L2="line 2 by A", L15="line 15 by A"))
    r.c1 = r.commit(f"work\n\nSession: {A}", "a.txt", "new.txt", "shared.txt")
    r.write("shared.txt", shared(L2="line 2 by A", L15="line 15 by A", L28="line 28 by B"))
    r.c2 = r.commit(f"theirs\n\nSession: {B}", "shared.txt")
    r.write("other.txt", ["o", "by B"])
    r.mention = r.commit(f"note\n\nSession: {A} was asked about this.\n\nSession: {B}", "other.txt")
    r.write("other.txt", ["o", "by B", "by A"])
    r.c3 = r.commit(f"more\n\nSession: {A}\nCo-Authored-By: t <t@example.com>", "other.txt")
    r.write("keep.txt", ["k", "staged by B"])
    git(r.root, "add", "keep.txt")
    return r


def session_commits(r: Repo, key: str) -> list[str]:
    """Step 1: the --grep hits, kept only where the trailer list holds the key."""
    rows = run(r.root, FIND, key=key).stdout.decode().splitlines()
    return [sha for sha, _, keys in (row.partition(" ") for row in rows) if key in keys.split(",")]


def test_the_trailer_finds_only_the_sessions_own_commits(repo):
    hits = run(repo.root, FIND, key=A).stdout.decode().split("\n")
    assert any(h.startswith(repo.mention) for h in hits), "the --grep alone hits the commit that only mentions the key"
    assert session_commits(repo, A) == [repo.c3, repo.c1]


def test_the_touched_query_tells_a_restore_from_a_revert_by_hunk(repo):
    def rows(path: str) -> list[tuple[str, str]]:
        out = run(repo.root, TOUCHED, first=repo.c1, path=path).stdout.decode().split("\n")
        return [tuple(ln.split(" ", 1)) for ln in out if ln]

    assert rows("a.txt") == [(repo.c1, A)]  # every row the key: restore it
    assert rows("shared.txt") == [(repo.c2, B), (repo.c1, A)]  # another writer's row: revert by hunk


def test_a_restore_by_path_leaves_the_index_as_other_writers_staged_it(repo):
    assert repo.staged() == ["keep.txt"]
    p = run(repo.root, RESTORE, first=repo.c1, path="a.txt")
    assert p.returncode == 0, p.stderr
    assert repo.lines("a.txt") == ["1", "2", "3"]
    assert repo.staged() == ["keep.txt"], "the restore wrote the index"
    assert repo.lines("keep.txt") == ["k", "staged by B"]


def test_a_file_the_session_created_is_deleted_and_committed_by_path(repo):
    assert run(repo.root, CREATED, first=repo.c1, path="new.txt").returncode != 0, "new.txt was in c1's parent"
    assert run(repo.root, CREATED, first=repo.c1, path="a.txt").returncode == 0
    p = run(repo.root, RESTORE, first=repo.c1, path="new.txt")
    assert p.returncode == 0, p.stderr
    assert not (repo.root / "new.txt").exists(), "the restore left a file its source does not have"
    assert repo.staged() == ["keep.txt"], "the restore staged the delete"
    git(repo.root, "commit", "-q", "-o", "-m", f"Roll back session {A}", "--", "new.txt")
    assert "new.txt" not in git(repo.root, "ls-tree", "--name-only", "HEAD").stdout.split()
    assert git(repo.root, "show", "--name-only", "--format=", "HEAD").stdout.split() == ["new.txt"]
    assert repo.staged() == ["keep.txt"], "the other writer's staged change was committed or dropped"


def test_a_disjoint_hunk_reverts_and_leaves_the_other_writers_line(repo, tmp_path):
    patch = (tmp_path / "c1.patch").as_posix()  # shlex reads a backslash as an escape
    run(repo.root, PATCH, c=repo.c1, path="shared.txt", patch=patch)
    p = run(repo.root, CHECK, patch=patch)
    assert p.returncode == 0, p.stderr
    assert run(repo.root, APPLY, patch=patch).returncode == 0
    assert repo.lines("shared.txt") == shared(L28="line 28 by B")
    assert repo.staged() == ["keep.txt"]


def test_an_overlapping_hunk_is_refused_and_the_file_is_left_untouched(repo, tmp_path):
    repo.write("shared.txt", shared(L2="line 2 by B", L15="line 15 by A", L28="line 28 by B"))
    repo.commit(f"B again\n\nSession: {B}", "shared.txt")
    before = (repo.root / "shared.txt").read_bytes()
    patch = (tmp_path / "c1.patch").as_posix()  # shlex reads a backslash as an escape
    run(repo.root, PATCH, c=repo.c1, path="shared.txt", patch=patch)
    p = run(repo.root, CHECK, patch=patch)
    assert p.returncode != 0, "a reversed hunk over another writer's line applied"
    assert (repo.root / "shared.txt").read_bytes() == before, "a refused check changed the file (line 15's hunk went through alone)"
    assert b"patch does not apply" in p.stderr, p.stderr  # refused for the overlap, not for a patch it could not read
    assert sorted(p.name for p in repo.root.iterdir()) == [".git", "a.txt", "keep.txt", "new.txt", "other.txt", "shared.txt"]
    assert run(repo.root, BACK_TO_HEAD, path="shared.txt").returncode == 0
    assert (repo.root / "shared.txt").read_bytes() == before


def _section() -> str:
    return h2_sections(PROCEDURES)[SECTION]


def test_the_runbook_gives_the_commands_these_tests_run():
    flat = " ".join(_section().split())
    missing = [form for form in RECIPE if form not in flat]
    assert missing == [], f"procedures.md § {SECTION} no longer gives {missing}: change the tests with it"


def test_no_step_of_the_rollback_runs_a_command_the_shared_tree_forbids():
    rows = table_rows(_section())
    assert [r[0] for r in rows] == [str(i) for i in range(8)], [r[0] for r in rows]
    bad = [(r[0], f) for r in rows for cell in (r[2], r[3]) for f in FORBIDDEN if re.search(re.escape(f), cell)]
    assert bad == [], f"a step of § {SECTION} runs what FRAMEWORK §6.13 forbids: {bad}"
