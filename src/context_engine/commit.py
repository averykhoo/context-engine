"""The engine commits its own writes by path (FRAMEWORK §5.5 rule 4).

A commit carries **every op log line the working tree has and HEAD lacks, every file those lines
name, and the op log itself**. So the op log at HEAD never runs ahead of, or behind, the records
it names: a clean checkout of any commit passes G-W7 on its own, and a session that dies leaves
nothing for another session's close to sweep up. Another session's leftover lines (its own
commit failed, it ran by hand or an older engine) are carried too, with the files they name:
that is the commit its own close would have made, and the message says whose they were.

It runs holding the engine lock, so no engine operation is half-written in the tree while it
reads. It is ``git commit --only`` on those paths (``git add`` first only for a path git has
never seen): what another session staged on other paths stays staged, nothing is unstaged,
reset or stashed, and hooks run.

It never refuses the write it follows. When it cannot commit it says why on the operation's
line, and the session commits those paths by hand (manual-mode § What every write does):
- quietly nothing, when the root is not in a git work tree (no ``.git``), or ``[engine] commit``
  is false;
- "not committed: ..." when git is missing beside a ``.git``, a merge, rebase, cherry-pick,
  revert or bisect is in progress, HEAD is detached, or git (a hook, identity, ``index.lock``
  held past its retries) refuses the commit.

Deliberately not handled: a hook that itself runs an engine write (it waits on the lock this
holds), and a path named by a line that another session is still editing by hand (its
half-edit is committed as it stands; nothing is lost from the tree).
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

TITLE_MAX = 72
GIT_TIMEOUT = 120  # seconds; provenance: JUDGEMENT, a hook may run a check; wrong if a normal hook takes longer
LOCK_RETRIES = 10  # git's own index.lock, held by a session's own git command for a moment
IN_PROGRESS = (
    ("MERGE_HEAD", "a merge"),
    ("rebase-merge", "a rebase"),
    ("rebase-apply", "a rebase or `git am`"),
    ("CHERRY_PICK_HEAD", "a cherry-pick"),
    ("REVERT_HEAD", "a revert"),
    ("BISECT_LOG", "a bisect"),
)


@dataclass
class Outcome:
    """What the commit after a write did: ``sha`` when it committed, ``note`` when it could not
    (with the by-hand step), both empty when there was nothing to do or no git repo."""

    sha: str = ""
    note: str = ""
    paths: tuple[str, ...] = field(default_factory=tuple)

    def line(self) -> str:
        """The suffix for the operation's one line."""
        if self.sha:
            return f"; committed {self.sha}"
        if self.note:
            return f"; not committed: {self.note}"
        return ""


def _in_git_tree(root: Path) -> bool:
    """A cheap look for ``.git`` (a directory, or a worktree's file) in root or a parent, so a
    target that is not a repo costs no git process."""
    if os.environ.get("GIT_DIR"):
        return True
    return any((p / ".git").exists() for p in (root, *root.parents))


class _Git:
    def __init__(self, root: Path):
        self.root = root

    def run(self, *args: str, input: str | None = None) -> subprocess.CompletedProcess:
        env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
        return subprocess.run(
            ["git", *args], cwd=self.root, input=input, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=GIT_TIMEOUT, env=env,
        )

    def write(self, *args: str, input: str | None = None) -> subprocess.CompletedProcess:
        """A command that takes git's ``index.lock``, retried while another git command holds it."""
        for attempt in range(LOCK_RETRIES):
            p = self.run(*args, input=input)
            if p.returncode == 0 or "index.lock" not in p.stderr:
                return p
            time.sleep(0.05 * (attempt + 1))
        return p


def _first_error(p: subprocess.CompletedProcess) -> str:
    lines = [ln.strip() for ln in (p.stderr + "\n" + p.stdout).splitlines()]
    useful = [ln for ln in lines if ln and not ln.startswith("warning: in the working copy")]
    return (useful[0] if useful else f"exit {p.returncode}")[:200]


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
    """``engine: <op> <id>, ...`` (the session's own ops; a mechanical index line only when it is
    alone), a paragraph naming any other session whose lines ride along, then the trailer."""
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
    others = sorted({str(o.get("session")) for o in lines if o.get("session") != session})
    body = ""
    if others:
        n = sum(o.get("session") != session for o in lines)
        body = (f"Also carries {n} op log line{'s' if n != 1 else ''} left uncommitted by "
                f"session{'s' if len(others) != 1 else ''} {', '.join(others)}, with the files they name.\n\n")
    return f"{title}\n\n{body}Session: {session}\n"


def commit(root: Path, oplog: str, session: str, *, title: str | None = None) -> Outcome:
    """Commit the op log's uncommitted lines with the files they name. Call it holding the lock."""
    if not _in_git_tree(root):
        return Outcome()
    git = _Git(root)
    remedy = f"commit by hand: `git commit -o {oplog} <the paths its new lines name>` with a `Session: {session}` trailer"
    try:
        p = git.run("rev-parse", "--absolute-git-dir", "--show-prefix")
    except FileNotFoundError:
        return Outcome(note=f"git is not installed; {remedy}")
    except subprocess.TimeoutExpired:
        return Outcome(note=f"git did not answer; {remedy}")
    if p.returncode != 0:
        return Outcome()  # inside .git, or a bare repo: no work tree to commit from
    gitdir, prefix = (p.stdout.splitlines() + ["", ""])[:2]
    gitdir = Path(gitdir.strip())
    for name, what in IN_PROGRESS:
        if (gitdir / name).exists():
            return Outcome(note=f"{what} is in progress; when it is done, {remedy}")
    try:
        return _commit(git, root, oplog, session, title, remedy, prefix.strip())
    except subprocess.TimeoutExpired:
        return Outcome(note=f"git took over {GIT_TIMEOUT}s (a hook?); {remedy}")


def _commit(git: _Git, root: Path, oplog: str, session: str, title: str | None, remedy: str, prefix: str) -> Outcome:
    if git.run("symbolic-ref", "-q", "HEAD").returncode != 0:
        return Outcome(note=f"HEAD is detached, so a commit would belong to no branch; on a branch, {remedy}")
    log = root / oplog
    if not log.exists():
        return Outcome()
    head = git.run("show", f"HEAD:./{oplog}")
    fresh = new_lines(log.read_bytes().decode("utf-8", errors="replace"), head.stdout if head.returncode == 0 else "")
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
    st = git.run("status", "--porcelain=v1", "-z", "--ignored", "--untracked-files=all", "--", *wanted)
    if st.returncode != 0:
        return Outcome(note=f"`git status` failed ({_first_error(st)}); {remedy}")
    codes = {}
    for entry in st.stdout.split("\0"):
        if len(entry) > 3 and entry[2] == " ":
            codes[entry[3:]] = entry[:2]  # porcelain paths are from the top of the work tree
    paths, untracked = [], []
    for rel in wanted:
        code = codes.get(prefix + rel)
        if code == "!!":
            continue  # ignored: the repo keeps it out of git on purpose
        if code is None and not (root / rel).exists():
            continue  # gone, and git never knew it
        paths.append(rel)
        if code == "??":
            untracked.append(rel)
    if oplog not in paths:
        return Outcome()  # the op log itself is ignored: this repo does not keep it in git
    if untracked:
        a = git.write("add", "--", *untracked)
        if a.returncode != 0:
            return Outcome(note=f"`git add` failed ({_first_error(a)}); {remedy}")
    c = git.write("commit", "-q", "--only", "-F", "-", "--", *paths, input=message(ops, session, title))
    if c.returncode != 0:
        return Outcome(note=f"`git commit` failed ({_first_error(c)}); {remedy}", paths=tuple(paths))
    return Outcome(sha=git.run("rev-parse", "--short", "HEAD").stdout.strip(), paths=tuple(paths))
