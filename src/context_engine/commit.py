"""The engine commits its own writes by path (FRAMEWORK §5.5 rule 4).

A commit carries **every op log line the working tree has and HEAD lacks, every file those lines
name, and the op log itself**. So the op log at HEAD never runs ahead of, or behind, the records
it names, and a clean checkout of any commit passes G-W7 on its own. A session that dies leaves
nothing for another session's close to sweep up. Lines another session left uncommitted (its
own commit failed, or it ran by hand or on an older engine) go in too, with the files they name:
that is the commit its own close would have made. The message and the operation's line both say
whose they were.

It runs while the engine lock is held, so no engine operation is half-written in the tree when
it reads. It runs ``git commit --only`` on those paths, after a ``git add`` only for paths git
has never seen (undone if the commit fails). What another session staged on other paths stays
staged; nothing is unstaged, reset or stashed; hooks run.

It never undoes the write it follows. When it cannot commit, the operation's line says why, and
the session commits those paths by hand (manual-mode § What every write does):
- it says nothing when the root is in no git work tree (no ``.git`` in it or above it), or
  ``[engine] commit`` is false;
- otherwise the line reads "not committed: ...". That covers: git missing beside a ``.git``; git
  refusing the repo; a merge, rebase, cherry-pick, revert or bisect in progress; a detached HEAD;
  ``GIT_DIR``-style variables set (inside a git hook); ``context.toml`` not tracked by the
  enclosing repo; the op log gitignored, or missing lines HEAD has; and git refusing the commit
  (a hook, the identity, ``index.lock`` held past its retries, a timeout).

Output, the message and the paths go through temporary files, never pipes. On Windows a hook's
child process can hold a pipe open after git is killed, so a timeout would not bound the time
the engine lock is held.

Deliberately not handled: a path named by a line that another session is still editing by hand.
Its half-edit is committed as it stands, and nothing is lost from the tree; the line names the
other session whose lines were carried.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

TITLE_MAX = 72
# Seconds. Provenance: JUDGEMENT, a hook may run a check. Wrong if a normal hook takes longer. It is
# longer than the engine lock's own 30 s default, so a hook slower than that makes another
# session's write refuse (before it writes anything) while this one waits.
GIT_TIMEOUT = 120
LOCK_RETRIES = 10  # git's own index.lock or HEAD ref lock, held for a moment by a session's own git command
BUSY = ("index.lock", "cannot lock ref")
STATUS_CHUNK = 200  # paths per `git status` call: it has no --pathspec-from-file, and Windows caps a command line
CONFIG = "context.toml"
# Set by git for a hook, or by hand: a commit would use that repo or index, not this tree's.
GIT_ENV = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR", "GIT_OBJECT_DIRECTORY")
IN_PROGRESS = (
    ("MERGE_HEAD", "a merge"),
    ("rebase-merge", "a rebase"),
    ("rebase-apply", "a rebase or `git am`"),
    ("CHERRY_PICK_HEAD", "a cherry-pick"),
    ("REVERT_HEAD", "a revert"),
    ("BISECT_LOG", "a bisect"),
)
SHA_RE = re.compile(r"^\[[^\]]*?\b([0-9a-f]{7,40})\]", re.MULTILINE)  # `[main (root-commit) abc1234] title`


@dataclass
class Outcome:
    """What the commit after a write did. ``sha`` is set when it committed and ``note`` when it
    could not (the note names the by-hand step); both are empty when there was nothing to do or
    no git repo. ``left_out`` lists named paths that git ignores, and ``carried`` lists the other
    sessions whose lines went in."""

    sha: str = ""
    note: str = ""
    paths: tuple[str, ...] = field(default_factory=tuple)
    left_out: tuple[str, ...] = field(default_factory=tuple)
    carried: tuple[str, ...] = field(default_factory=tuple)

    def line(self) -> str:
        """The suffix for the operation's one line."""
        if self.sha:
            extra = []
            if self.carried:
                extra.append(f"carrying lines left uncommitted by {', '.join(self.carried)}")
            if self.left_out:
                extra.append(f"left out as gitignored: {', '.join(self.left_out)}")
            return f"; committed {self.sha}" + (f" ({'; '.join(extra)})" if extra else "")
        if self.note:
            return f"; not committed: {self.note}"
        return ""


def _in_git_tree(root: Path) -> bool:
    """A cheap look for ``.git`` (a directory, or a worktree's file) in root or a parent, so a
    target that is not a repo costs no git process."""
    return any((p / ".git").exists() for p in (root, *root.parents))


class _Git:
    def __init__(self, root: Path):
        self.root = root
        self.env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}

    def run(self, *args: str) -> subprocess.CompletedProcess:
        """Git with stdin closed and its output in temporary files. A pipe held open by a
        hook's child would make ``subprocess.run`` wait past its timeout on Windows."""
        with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
            p = subprocess.run(["git", *args], cwd=self.root, stdin=subprocess.DEVNULL, stdout=out, stderr=err, timeout=GIT_TIMEOUT, env=self.env)
            out.seek(0)
            err.seek(0)
            dec = lambda f: f.read().decode("utf-8", errors="replace")
            return subprocess.CompletedProcess(p.args, p.returncode, dec(out), dec(err))

    def write(self, *args: str) -> subprocess.CompletedProcess:
        """A command that takes git's ``index.lock`` (and for a commit, HEAD's ref lock), retried
        while another git command holds it."""
        for attempt in range(LOCK_RETRIES):
            p = self.run(*args)
            if p.returncode == 0 or not any(b in p.stderr for b in BUSY):
                return p
            time.sleep(0.05 * (attempt + 1))
        return p


def _first_error(p: subprocess.CompletedProcess) -> str:
    """git's own `fatal:` or `error:` line if it printed one, else the first line (a hook's)."""
    lines = [ln.strip() for ln in (p.stderr + "\n" + p.stdout).splitlines()]
    useful = [ln for ln in lines if ln and not ln.startswith("warning: in the working copy")]
    own = [ln for ln in useful if ln.startswith(("fatal:", "error:"))]
    return ((own or useful)[0] if useful else f"exit {p.returncode}")[:200]


def new_lines(working: str, head: str) -> list[str]:
    """The op log lines in ``working`` that ``head`` lacks, as a multiset difference in working
    order (a line written twice is new twice). ``splitlines`` drops CRLF and LF endings alike,
    so a CRLF checkout does not make every line new."""
    have = Counter(ln for ln in head.splitlines() if ln.strip())
    out = []
    for ln in working.splitlines():
        if not ln.strip():
            continue
        if have[ln]:
            have[ln] -= 1
        else:
            out.append(ln)
    return out


def message(lines: list[dict], session: str, title: str | None) -> str:
    """The commit message. The title is ``engine: <op> <id>, ...``, naming the session's own ops;
    a mechanical index line is named only when it is alone. Then a paragraph naming any other
    session whose lines ride along, then the trailer."""
    own = [o for o in lines if o.get("session") == session] or lines
    named = [o for o in own if o.get("op") != "index"] or own
    if not title:
        parts = list(dict.fromkeys(f"{o.get('op')} {o.get('id')}" for o in named))
        title = "engine: "
        for n, p in enumerate(parts):
            more = f" (+{len(parts) - n} more)"
            sep = ", " if n else ""
            if len(title) + len(sep) + len(p) + (len(more) if n < len(parts) - 1 else 0) > TITLE_MAX:
                title += more
                break
            title += sep + p
    others = _others(lines, session)
    body = ""
    if others:
        n = sum(o.get("session") != session for o in lines)
        body = (f"Also carries {n} op log line{'s' if n != 1 else ''} left uncommitted by "
                f"session{'s' if len(others) != 1 else ''} {', '.join(others)}, with the files they name.\n\n")
    return f"{title}\n\n{body}Session: {session}\n"


def _others(lines: list[dict], session: str) -> tuple[str, ...]:
    return tuple(sorted({str(o.get("session")) for o in lines if o.get("session") != session}))


def commit(root: Path, oplog: str, session: str, *, title: str | None = None) -> Outcome:
    """Commit the op log's uncommitted lines with the files they name. Call it holding the lock."""
    remedy = (f"commit by hand: `git commit -o {oplog} <the paths its uncommitted lines name>` with a "
              f"`Session: {session}` trailer (manual-mode § What every write does)")
    set_env = [v for v in GIT_ENV if os.environ.get(v)]
    if set_env:
        return Outcome(note=f"{', '.join(set_env)} is set (inside a git hook?), so a commit would go to that repo or index; outside it, {remedy}")
    if not _in_git_tree(root):
        return Outcome()
    git = _Git(root)
    try:
        p = git.run("rev-parse", "--absolute-git-dir", "--show-prefix")
    except FileNotFoundError:
        return Outcome(note=f"git is not installed; {remedy}")
    except subprocess.TimeoutExpired:
        return Outcome(note=f"git did not answer in {GIT_TIMEOUT}s; {remedy}")
    if p.returncode != 0:
        if "not a git repository" in p.stderr:
            return Outcome()  # a `.git` above that is not a repo of this tree: nothing to commit to
        return Outcome(note=f"git refuses this repo ({_first_error(p)}); {remedy}")
    gitdir, prefix = (p.stdout.splitlines() + ["", ""])[:2]
    gitdir = Path(gitdir.strip())
    for name, what in IN_PROGRESS:
        if (gitdir / name).exists():
            return Outcome(note=f"{what} is in progress; when it is done, {remedy}")
    if _detached(git, gitdir):
        return Outcome(note=f"HEAD is detached, so a commit would belong to no branch; on a branch, {remedy}")
    started = time.time()
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:  # a killed hook may still hold a file
        try:
            return _commit(git, root, oplog, session, title, remedy, prefix.strip(), Path(tmp))
        except subprocess.TimeoutExpired:
            lock = gitdir / "index.lock"
            left = f"; it left {lock} behind: remove it once no git command is running" if lock.exists() and lock.stat().st_mtime >= started - 1 else ""
            return Outcome(note=f"git took over {GIT_TIMEOUT}s (a hook?){left}; {remedy}")


def _pathspec(tmp: Path, name: str, paths: list[str]) -> str:
    f = tmp / name
    f.write_bytes(b"\0".join(p.encode("utf-8") for p in paths))
    return str(f)


def _detached(git: _Git, gitdir: Path) -> bool:
    """HEAD names no branch. Read from the worktree's own HEAD file, which saves a git process
    on every write; the reftable backend's placeholder HEAD file is asked of git instead."""
    try:
        text = (gitdir / "HEAD").read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        text = ""
    if text.startswith("ref: ") and text != "ref: refs/heads/.invalid":
        return False
    return git.run("symbolic-ref", "-q", "HEAD").returncode != 0


def _commit(git: _Git, root: Path, oplog: str, session: str, title: str | None, remedy: str, prefix: str, tmp: Path) -> Outcome:
    log = root / oplog
    if not log.exists():
        return Outcome()
    head = git.run("show", f"HEAD:./{oplog}")
    head_text = head.stdout if head.returncode == 0 else ""
    working = log.read_bytes().decode("utf-8", errors="replace")
    lost = new_lines(head_text, working)
    if lost:
        return Outcome(note=(f"{oplog} lacks {len(lost)} line{'s' if len(lost) != 1 else ''} HEAD has, so a commit would "
                             f"break G-W7 at HEAD; restore them (`git show HEAD:./{oplog}`), then {remedy}"))
    fresh = new_lines(working, head_text)
    if not fresh:
        return Outcome()
    ops: list[dict] = []
    for ln in fresh:
        try:
            o = json.loads(ln)
        except ValueError:
            continue  # G-W7 reports it; the line still rides with the op log
        if isinstance(o, dict):
            ops.append(o)
    wanted = list(dict.fromkeys([oplog, *(str(o["path"]) for o in ops if o.get("path"))]))
    codes: dict[str, str] = {}
    asked = [CONFIG, *wanted]
    for i in range(0, len(asked), STATUS_CHUNK):
        st = git.run("status", "--porcelain=v1", "-z", "--ignored", "--untracked-files=all", "--", *asked[i:i + STATUS_CHUNK])
        if st.returncode != 0:
            return Outcome(note=f"`git status` failed ({_first_error(st)}); {remedy}")
        for entry in st.stdout.split("\0"):
            if len(entry) > 3 and entry[2] == " ":
                codes[entry[3:]] = entry[:2]  # porcelain paths are from the top of the work tree
    if codes.get(prefix + CONFIG) in ("??", "!!") or not (root / CONFIG).exists():
        where = f" (this target is {prefix.rstrip('/')} inside a larger repo)" if prefix else ""
        return Outcome(note=(f"{CONFIG} is not committed in this repo{where}, so a clean checkout would lack it; "
                             f"commit the kit's files by path first (rituals § Bootstrap), then {remedy}"))
    if codes.get(prefix + oplog) == "!!":
        return Outcome(note=(f"{oplog} is gitignored, so no commit can carry it and G-W7 fails on every clone; "
                             f"un-ignore it, or set `[engine] commit = false` and commit by hand"))
    paths, untracked, left_out = [], [], []
    for rel in wanted:
        code = codes.get(prefix + rel)
        if code == "!!":
            left_out.append(rel)  # ignored: the repo keeps it out of git on purpose
            continue
        if code is None and not (root / rel).exists():
            continue  # gone, and git never knew it
        paths.append(rel)
        if code == "??":
            untracked.append(rel)
    if untracked:
        a = git.write("add", f"--pathspec-from-file={_pathspec(tmp, 'add', untracked)}", "--pathspec-file-nul")
        if a.returncode != 0:
            return Outcome(note=f"`git add` failed ({_first_error(a)}); {remedy}")
    msg = tmp / "message"
    msg.write_bytes(message(ops, session, title).encode("utf-8"))
    try:
        c = git.write("commit", "--only", "-F", str(msg), f"--pathspec-from-file={_pathspec(tmp, 'commit', paths)}", "--pathspec-file-nul")
    except subprocess.TimeoutExpired:
        _unstage(git, tmp, untracked)
        raise
    if c.returncode != 0:
        _unstage(git, tmp, untracked)
        return Outcome(note=f"`git commit` failed ({_first_error(c)}); {remedy}", paths=tuple(paths))
    m = SHA_RE.search(c.stdout)
    sha = m.group(1) if m else git.run("rev-parse", "--short", "HEAD").stdout.strip()
    return Outcome(sha=sha, paths=tuple(paths), left_out=tuple(left_out), carried=_others(ops, session))


def _unstage(git: _Git, tmp: Path, untracked: list[str]) -> None:
    """Take back the ``git add`` of paths git had never seen, so a later plain ``git commit`` by
    anyone cannot carry a record without its op line."""
    if untracked:
        try:
            git.run("rm", "-q", "--cached", "--ignore-unmatch", f"--pathspec-from-file={_pathspec(tmp, 'unstage', untracked)}", "--pathspec-file-nul")
        except subprocess.TimeoutExpired:
            pass
