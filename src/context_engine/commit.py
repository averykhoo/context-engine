"""The engine commits its writes by path, at milestones (FRAMEWORK §5.5 rule 4, DEC-36).

``[engine] commit`` says when (``store.Store._commit``): at a milestone (task close, the
owner-words writes, a baton or pause, session close or pause, the banner), after every write, or
never but a pause. A write that is not a milestone stays uncommitted and goes into the next
commit, which carries it whole. The session's own commits go through ``commit`` too
(``context-engine commit <paths> -m ...``), so they never split a record from its op line.

A commit carries **the committing session's op log lines that HEAD lacks, every file those lines
name, and the op log itself**. So the op log at HEAD never runs ahead of, or behind, the records
it names, and a clean checkout of any commit passes G-W7 on its own. Another session's
uncommitted lines (it is still working, its commit failed, it died, or it ran by hand or on an
older engine) stay out by default (CE-125, superseding CE-45's sweep for the default; adhoc AAR
entry 22): with two live sessions on one tree, a sweep commits one session's half-done work
under the other's name. Two kinds go in anyway: another session's line naming a file this
commit carries (the file holds that write, so its line goes with it, or G-W7 fails at HEAD),
and a line that does not parse unless its text names another session (``session_of``; then it
stays out with that session's lines, CE-128). The reply names the lines left behind,
whose and how many; ``sweep`` takes every line, for a session known dead. When lines are left
behind, the op log at HEAD is HEAD's own lines plus the taken ones, in working order, built in
a temporary index; the working file is never rewritten, and once nothing is left behind a commit
carries it whole again, so the two converge. Before the first commit every line goes in (there
is no HEAD op log to build on). The message and the reply say whose lines went in.

It runs while the engine lock is held, so no engine operation is half-written in the tree when
it reads. With no line left behind it runs ``git commit --only`` on those paths (with lines left, a
temporary index, below), after a ``git add`` only for paths git
has never seen (undone if the commit fails). What another session staged on other paths stays
staged; nothing is unstaged, reset or stashed; hooks run.

It never undoes the write it follows. When it cannot commit, the operation's reply says why, and
the session commits those paths by hand (manual-mode § What every write does):
- it says nothing when the root is not inside a git work tree (no ``.git`` in it or above it), or
  the policy makes no commit now (the session's own commit says so instead: it was asked for);
- otherwise the reply reads "not committed: ...". That covers: a ``.git`` directory present but
  no git executable; git refusing the repo; a merge, rebase, cherry-pick, revert or bisect in
  progress; a detached HEAD; ``GIT_DIR``-style variables set (inside a git hook);
  ``context.toml`` not tracked by the enclosing repo; the op log gitignored, or missing lines HEAD has; a named record whose
  frontmatter does not parse (a hand edit in progress); and git refusing the commit (a hook,
  the identity, ``index.lock`` held past its retries, a timeout).

Output, the message and the paths go through temporary files, never pipes. On Windows a hook's
child process can hold a pipe open after git is killed, so a timeout would not bound the time
the engine lock is held.

Deliberately not handled: a path named by a line that another session is still editing by hand,
when the half-edit still parses. It is committed as it stands, and nothing is lost from the
tree; the reply names the other session whose lines were carried. Under the milestone policy a
record stays uncommitted until the next milestone, whoever makes it, so that window is wide; a
half-edit that breaks the frontmatter stops the commit instead (INV-42).
"""

from __future__ import annotations

import dataclasses
import json
import os
import re
import subprocess
import tempfile
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from . import okf

TITLE_MAX = 72
OPS_MAX = 400  # characters of the `Ops:` line naming the op log lines a commit carries, when its title does not
TRAILER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]*: \S")  # `Token: value`, as git reads a trailer
NOTHING = ("nothing to commit", "no changes added to commit", "nothing added to commit")  # git's own words
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
    left: tuple[tuple[str, int], ...] = field(default_factory=tuple)  # (session, op lines) left uncommitted (CE-125)
    warn: str = ""  # committed, but something after it failed and needs a hand step

    def line(self) -> str:
        """The suffix for the operation's one-line reply."""
        if self.sha:
            extra = []
            if self.carried:
                extra.append(f"including op lines that {', '.join(self.carried)} left uncommitted")
            if self.left_out:
                extra.append(f"left out as gitignored: {', '.join(self.left_out)}")
            if self.left:
                extra.append(left_behind(self.left))
            if self.warn:
                extra.append(f"WARNING: {self.warn}")
            return f"; committed {self.sha}" + (f" ({'; '.join(extra)})" if extra else "")
        if self.note:
            return f"; not committed: {self.note}"
        return ""


def left_behind(left: tuple[tuple[str, int], ...]) -> str:
    """What a reply says of the lines a commit left out: whose, how many, and how to take them."""
    each = ", ".join(f"{n} op line{'s' if n != 1 else ''} of {k}" for k, n in left)
    return (f"left uncommitted: {each}, with the files they name; that session commits them, "
            f"or once it is known dead, `context-engine commit --sweep` takes them")


def select(lines: list[str], session: str, given: tuple[str, ...] = (), sweep: bool = False,
           derived: dict[str, tuple[str, ...]] | None = None) -> tuple[list[str], list[str]]:
    """Split uncommitted op lines into those a commit by ``session`` takes and those it leaves
    (CE-125): it takes its own lines; another session's line naming a path the commit carries
    (one of its own lines' paths, a ``given`` path or a file under a given directory), since
    that file holds the write; and a line that does not parse, unless its text names another
    session (``session_of``), whose line it is then (CE-128). With ``sweep``, every line.

    ``derived`` maps a file generated from others (the decision index) to the directories of its
    sources: when the commit carries it, it holds every source's state on disk, so every line
    naming a file under those directories goes in too, or the file at HEAD would not be what its
    sources there generate (G-D6). Then a line taken for its path adds no new path, so the
    passes end."""
    if sweep:
        return list(lines), []
    derived = derived or {}
    parsed = []
    for ln in lines:
        try:
            o = json.loads(ln)
        except ValueError:
            o = None
        parsed.append(o if isinstance(o, dict) else None)

    keys = [o.get("session") if o is not None else session_of(ln) for ln, o in zip(lines, parsed)]

    def own(o: dict | None, key: object = None) -> bool:
        return o.get("session") == session if o is not None else key in (None, session)

    paths = {str(o["path"]) for o in parsed if o is not None and own(o) and o.get("path")} | set(given)
    under = tuple(g.rstrip("/") + "/" for g in given)
    at = [str(o.get("path") or "") if o is not None else "" for o in parsed]
    carried = lambda p: bool(p) and (p in paths or p.startswith(under))
    for gen, dirs in derived.items():  # a carried generated file brings its sources' lines
        if any(own(o) or carried(p) for o, p in zip(parsed, at) if p == gen) or gen in paths:
            under += tuple(d.rstrip("/") + "/" for d in dirs)
            paths.add(gen)
    taken, left = [], []
    for ln, o, p, k in zip(lines, parsed, at, keys):
        (taken if own(o, k) or carried(p) else left).append(ln)
    return taken, left


SESSION_FIELD = re.compile(r'"session"\s*:\s*"([^"\\]+)"')


def session_of(line: str) -> str | None:
    """The session an op log line names: its ``session`` field, read from the text when the line
    does not parse as JSON (a write cut short, a hand edit), or None when it names none (CE-128)."""
    try:
        o = json.loads(line)
    except ValueError:
        m = SESSION_FIELD.search(line)
        return m.group(1) if m else None
    return str(o.get("session")) if isinstance(o, dict) and o.get("session") is not None else None


def unparseable(lines: list[str]) -> list[str]:
    """The lines of ``lines`` that do not parse as an op log entry (a JSON object)."""
    out = []
    for ln in lines:
        try:
            ok = isinstance(json.loads(ln), dict)
        except ValueError:
            ok = False
        if not ok:
            out.append(ln)
    return out


def _whose(lines: list[str]) -> tuple[tuple[str, int], ...]:
    """(session, count) for each session with a line in ``lines``, by key; a line ``select``
    left names one, parsed or not."""
    c: Counter = Counter(str(session_of(ln)) for ln in lines)
    return tuple(sorted(c.items()))


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


def _parts(lines: list[dict], session: str, lead: tuple[str, ...] = ()) -> list[str]:
    """``<op> <id>`` for the session's own lines (a mechanical index line only when it is alone),
    the ones this operation wrote (``lead``) first."""
    own = [o for o in lines if o.get("session") == session] or lines
    named = [o for o in own if o.get("op") != "index"] or own
    keys = list(dict.fromkeys(f"{o.get('op')} {o.get('id')}" for o in named))
    return list(dict.fromkeys([*(k for k in lead if k in keys), *keys]))


def _fit(head: str, parts: list[str], limit: int) -> str:
    """``head`` and as many parts as fit in ``limit``, then ``(+n more)``."""
    out = head
    for n, p in enumerate(parts):
        more = f" (+{len(parts) - n} more)"
        sep = ", " if n else ""
        if len(out) + len(sep) + len(p) + (len(more) if n < len(parts) - 1 else 0) > limit:
            return out + more
        out += sep + p
    return out


def _carried_by(lines: list[dict], session: str) -> str:
    others = _others(lines, session)
    if not others:
        return ""
    n = sum(o.get("session") != session for o in lines)
    return (f"Also carries {n} op log line{'s' if n != 1 else ''} left uncommitted by "
            f"session{'s' if len(others) != 1 else ''} {', '.join(others)}, with the files they name.")


def message(lines: list[dict], session: str, title: str | None, *, lead: tuple[str, ...] = (), body: str = "", trailers: tuple[str, ...] = ()) -> str:
    """An engine commit's message. The title is ``engine: <op> <id>, ...``, naming the session's
    own ops, this operation's first; an operation that names its own title (a pause, a task
    close) gets an ``Ops:`` line naming them instead, when there is more than one. Then the
    operation's ``body``, a paragraph naming any other session whose uncommitted lines go in, then
    ``trailers`` and the ``Session:`` trailer, in one block."""
    parts = _parts(lines, session, lead)
    paras = []
    if not title:
        title = _fit("engine: ", parts, TITLE_MAX)
    elif len(parts) > 1:
        paras.append(_fit("Ops: ", parts, OPS_MAX))
    if body.strip():
        paras.append(body.strip())
    if _carried_by(lines, session):
        paras.append(_carried_by(lines, session))
    paras.append("\n".join([*trailers, f"Session: {session}"]))
    return "\n\n".join([title, *paras]) + "\n"


def _paragraphs(text: str) -> list[str]:
    paras, cur = [], []
    for ln in text.replace("\r\n", "\n").split("\n"):
        if ln.strip():
            cur.append(ln.rstrip())
        elif cur:
            paras.append("\n".join(cur))
            cur = []
    if cur:
        paras.append("\n".join(cur))
    return paras


def _is_trailers(para: str) -> bool:
    """A paragraph git reads as trailers: ``Token: value`` lines, a line led by whitespace
    continuing the one before."""
    lines = para.split("\n")
    return bool(TRAILER_RE.match(lines[0])) and all(TRAILER_RE.match(ln) or ln[:1].isspace() for ln in lines[1:])


def session_trailers(text: str) -> list[str]:
    """The key of every ``Session:`` trailer in a commit message: in its last paragraph, the only
    one git reads as trailers, and never its title."""
    paras = _paragraphs(text)
    if len(paras) < 2 or not _is_trailers(paras[-1]):
        return []
    return [ln.split(":", 1)[1].strip() for ln in paras[-1].split("\n") if ln.startswith("Session:")]


def session_message(text: str, lines: list[dict], session: str) -> str:
    """A session's own commit message as it wrote it, plus what the engine carries: an ``Ops:``
    line naming the uncommitted op log lines it takes in, and the paragraph naming other sessions, both
    before the closing trailer paragraphs; and a ``Session:`` trailer in the last paragraph,
    where ``git interpret-trailers`` reads it, unless the message has one already."""
    paras = _paragraphs(text)
    tail = len(paras)
    while tail > 1 and _is_trailers(paras[tail - 1]):
        tail -= 1
    ours = []
    if lines:
        ours.append(_fit("Ops: ", _parts(lines, session), OPS_MAX))
    if _carried_by(lines, session):
        ours.append(_carried_by(lines, session))
    paras[tail:tail] = ours
    if not session_trailers(text):
        if tail + len(ours) < len(paras):
            paras[-1] += f"\nSession: {session}"
        else:
            paras.append(f"Session: {session}")
    return "\n\n".join(paras) + "\n"


def _others(lines: list[dict], session: str) -> tuple[str, ...]:
    return tuple(sorted({str(o.get("session")) for o in lines if o.get("session") != session}))


def commit(root: Path, oplog: str, session: str, *, title: str | None = None, lead: tuple[str, ...] = (), body: str = "",
           trailers: tuple[str, ...] = (), text: str | None = None, paths: tuple[str, ...] = (), sweep: bool = False,
           derived: dict[str, tuple[str, ...]] | None = None) -> Outcome:
    """Commit ``session``'s uncommitted op lines (``select``; with ``sweep``, every line) with
    the files they name. Call it holding the lock.

    An engine commit's message is built from ``title``, ``lead``, ``body`` and ``trailers``
    (``message``). The session's own commit passes its message as ``text`` and its own
    ``paths``, relative to ``root`` (``session_message``); then every case that commits nothing
    says why, since a commit was asked for."""
    asked = text is not None
    remedy = (f"commit by hand: `git commit -o {oplog} <the paths its uncommitted lines name>` with a "
              f"`Session: {session}` trailer (manual-mode § What every write does)")
    set_env = [v for v in GIT_ENV if os.environ.get(v)]
    if set_env:
        return Outcome(note=f"{', '.join(set_env)} is set (inside a git hook?), so a commit would go to that repo or index; outside it, {remedy}")
    if not _in_git_tree(root):
        return Outcome(note=f"{root} is not inside a git work tree") if asked else Outcome()
    git = _Git(root)
    try:
        p = git.run("rev-parse", "--absolute-git-dir", "--show-prefix")
    except FileNotFoundError:
        return Outcome(note=f"git is not installed; {remedy}")
    except subprocess.TimeoutExpired:
        return Outcome(note=f"git did not answer in {GIT_TIMEOUT}s; {remedy}")
    if p.returncode != 0:
        if "not a git repository" in p.stderr:
            # a `.git` above that is not a repo of this tree: nothing to commit to
            return Outcome(note=f"{root} is not inside a git work tree") if asked else Outcome()
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
            how = dict(title=title, lead=tuple(lead), body=body, trailers=tuple(trailers))
            return _commit(git, root, oplog, session, prefix.strip(), Path(tmp), remedy, how, text, tuple(paths), sweep, derived)
        except subprocess.TimeoutExpired:
            lock = gitdir / "index.lock"
            left = f"; it left {lock} behind: remove it once no git command is running" if lock.exists() and lock.stat().st_mtime >= started - 1 else ""
            return Outcome(note=f"git took over {GIT_TIMEOUT}s (a hook?){left}; {remedy}")


def _pathspec(tmp: Path, name: str, paths: list[str]) -> str:
    f = tmp / name
    f.write_bytes(b"\0".join(p.encode("utf-8") for p in paths))
    return str(f)


def pending(root: Path, oplog: str, session: str | None = None, derived: dict[str, tuple[str, ...]] | None = None) -> set[str]:
    """The paths, from the top of the work tree as `git status` gives them, that the next
    commit carries: the op log and every path its lines HEAD lacks name (with ``session``, only
    the lines that session's commit takes, ``select``). Empty when
    there is no git, or nothing is uncommitted. A pause reads it to leave those paths out of its
    own list of uncommitted paths, since its commit carries them (INV-45)."""
    log = root / oplog
    if not log.exists() or not _in_git_tree(root):
        return set()
    git = _Git(root)
    try:
        top = git.run("rev-parse", "--show-prefix")
        head = git.run("show", f"HEAD:./{oplog}")
    except (OSError, subprocess.TimeoutExpired):
        return set()
    if top.returncode != 0:
        return set()
    prefix = top.stdout.strip()
    fresh = new_lines(log.read_bytes().decode("utf-8", errors="replace"), head.stdout if head.returncode == 0 else "")
    if session is not None and head.returncode == 0:
        fresh = select(fresh, session, derived=derived)[0]
    if not fresh:
        return set()
    out = {prefix + oplog}
    for ln in fresh:
        try:
            o = json.loads(ln)
        except ValueError:
            continue
        if isinstance(o, dict) and o.get("path"):
            out.add(prefix + str(o["path"]))
    return out


def carried_paths(root: Path, oplog: str, session: str, given: tuple[str, ...] = (), sweep: bool = False,
                  derived: dict[str, tuple[str, ...]] | None = None) -> set[str]:
    """The paths, relative to ``root``, a commit by ``session`` of ``given`` would carry: those,
    and when it takes any op line, the op log and the paths its taken lines name (``select``).
    Read without git's help when there is no git or no HEAD (then every line counts)."""
    out = set(given)
    fresh = taken_lines(root, oplog, session, given, sweep, derived)
    if fresh:
        out.add(oplog)
    for ln in fresh:
        try:
            o = json.loads(ln)
        except ValueError:
            continue
        if isinstance(o, dict) and o.get("path"):
            out.add(str(o["path"]))
    return out


def taken_lines(root: Path, oplog: str, session: str, given: tuple[str, ...] = (), sweep: bool = False,
                derived: dict[str, tuple[str, ...]] | None = None) -> list[str]:
    """The uncommitted op log lines a commit by ``session`` of ``given`` would take (``select``).
    Read without git's help when there is no git or no HEAD (then every line counts).

    ``unparseable(taken_lines(...))`` empty means the op log this commit puts at HEAD parses,
    though the working file may not: a line that does not parse and names another session is
    left in the tree with that session's lines (CE-128), so the lint before a commit
    (``working.Engine._lint_carried``) need not refuse for it."""
    log = root / oplog
    if not log.exists():
        return []
    head = ""
    if _in_git_tree(root):
        try:
            p = _Git(root).run("show", f"HEAD:./{oplog}")
            head = p.stdout if p.returncode == 0 else ""
        except (OSError, subprocess.TimeoutExpired):
            pass
    fresh = new_lines(log.read_bytes().decode("utf-8", errors="replace"), head)
    return select(fresh, session, given, sweep, derived)[0] if head else fresh


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


def _commit(git: _Git, root: Path, oplog: str, session: str, prefix: str, tmp: Path, remedy: str, how: dict,
            text: str | None, given: tuple[str, ...], sweep: bool = False, derived: dict[str, tuple[str, ...]] | None = None) -> Outcome:
    log = root / oplog
    fresh: list[str] = []
    left: list[str] = []
    head_text = ""
    if log.exists():
        head = git.run("show", f"HEAD:./{oplog}")
        head_text = head.stdout if head.returncode == 0 else ""
        working = log.read_bytes().decode("utf-8", errors="replace")
        lost = new_lines(head_text, working)
        if lost:
            return Outcome(note=(f"{oplog} lacks {len(lost)} line{'s' if len(lost) != 1 else ''} HEAD has, so a commit would "
                                 f"break G-W7 at HEAD; restore them (`git show HEAD:./{oplog}`), then {remedy}"))
        fresh = new_lines(working, head_text)
        if head.returncode == 0:  # before the first commit every line goes in: no HEAD op log to build a partial one on
            fresh, left = select(fresh, session, given, sweep, derived)
    whose = _whose(left)
    if not fresh and not given:
        if text is None:
            return Outcome(left=whose)
        if left:
            return Outcome(note=f"nothing to commit: every uncommitted line in {oplog} is another session's, and no path was given ({left_behind(whose)})", left=whose)
        return Outcome(note=f"nothing to commit: {oplog} has no line HEAD lacks, and no path was given")
    ops: list[dict] = []
    for ln in fresh:
        try:
            o = json.loads(ln)
        except ValueError:
            continue  # G-W7 reports it; the line still goes in with the op log
        if isinstance(o, dict):
            ops.append(o)
    wanted = list(dict.fromkeys([oplog, *(str(o["path"]) for o in ops if o.get("path"))])) if fresh else []
    codes: dict[str, str] = {}
    asked = [CONFIG, *wanted, *(g for g in given if g not in wanted)]
    for i in range(0, len(asked), STATUS_CHUNK):
        st = git.run("status", "--porcelain=v1", "-z", "--ignored", "--untracked-files=all", "--", *asked[i:i + STATUS_CHUNK])
        if st.returncode != 0:
            return Outcome(note=f"`git status` failed ({_first_error(st)}); {remedy}")
        for entry in st.stdout.split("\0"):
            if len(entry) > 3 and entry[2] == " ":
                codes[entry[3:]] = entry[:2]  # porcelain paths are from the top of the work tree
    if fresh and CONFIG not in given and (codes.get(prefix + CONFIG) in ("??", "!!") or not (root / CONFIG).exists()):
        where = f" (this target is {prefix.rstrip('/')} inside a larger repo)" if prefix else ""
        return Outcome(note=(f"{CONFIG} is not committed in this repo{where}, so a clean checkout would lack it; "
                             f"commit the kit's files by path first (procedures § Bootstrap), then {remedy}"))
    if fresh and codes.get(prefix + oplog) == "!!":
        return Outcome(note=(f"{oplog} is gitignored, so no commit can carry it and G-W7 fails on every clone; "
                             f"un-ignore it, or set `[engine] commit = \"off\"` and commit by hand"))
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
    for rel in paths:  # a record the commit carries must parse, or a clean checkout of the commit would not lint
        if rel.endswith(".md") and (root / rel).is_file():
            try:
                okf.read_head(root / rel)
            except Exception as exc:  # a Refusal from the YAML, or bytes that are not UTF-8
                why = exc.message if hasattr(exc, "message") else type(exc).__name__
                return Outcome(note=(f"{rel} does not parse ({why}): a hand edit in progress? A commit would carry it as it "
                                     f"stands; finish or undo that edit, and the next commit carries it, or {remedy}"))
    for rel in given:  # the session's own paths go to git as given; a new file is added first
        if rel in wanted:
            continue
        code = codes.get(prefix + rel)
        if code == "!!":
            return Outcome(note=f"{rel} is gitignored; drop it, or `git add -f -- {rel}` first if it belongs in git")
        paths.append(rel)
        if code == "??" and (root / rel).is_file():
            untracked.append(rel)
        elif (root / rel).is_dir():  # git status lists a directory's new files, never the directory
            under = prefix + rel + "/"
            untracked += [k[len(prefix):] for k, v in codes.items() if v == "??" and k.startswith(under)]
    untracked = list(dict.fromkeys(untracked))
    msg = tmp / "message"
    msg.write_bytes((session_message(text, ops, session) if text is not None else message(ops, session, **how)).encode("utf-8"))
    if left:  # another session's lines stay out: commit a partial op log from a temporary index
        c = _commit_partial(git, tmp, prefix, oplog, head_text, fresh, paths, msg)
        if isinstance(c, Outcome):
            return dataclasses.replace(c, note=f"{c.note}; {remedy}", left=whose)
    else:
        if untracked:
            a = git.write("add", f"--pathspec-from-file={_pathspec(tmp, 'add', untracked)}", "--pathspec-file-nul")
            if a.returncode != 0:
                return Outcome(note=f"`git add` failed ({_first_error(a)}); {remedy}")
        try:
            c = git.write("commit", "--only", "-F", str(msg), f"--pathspec-from-file={_pathspec(tmp, 'commit', paths)}", "--pathspec-file-nul")
        except subprocess.TimeoutExpired:
            _unstage(git, tmp, untracked)
            raise
    if c.returncode != 0:
        if not left:
            _unstage(git, tmp, untracked)
        if any(n in c.stdout for n in NOTHING):
            return Outcome(note="nothing to commit: no path given has a change", paths=tuple(paths), left=whose)
        return Outcome(note=f"`git commit` failed ({_first_error(c)}); {remedy}", paths=tuple(paths), left=whose)
    m = SHA_RE.search(c.stdout)
    sha = m.group(1) if m else git.run("rev-parse", "--short", "HEAD").stdout.strip()
    warn = c.stderr if c.args == "reset-failed" else ""
    if text is not None:  # the session's own commit reports what git committed, not what it was given
        shown = git.run("show", "--name-only", "-z", "--format=", "HEAD").stdout
        paths = [x.strip("\n") for x in shown.split("\0") if x.strip("\n")]
    return Outcome(sha=sha, paths=tuple(paths), left_out=tuple(left_out), carried=_others(ops, session), left=whose, warn=warn)


def _commit_partial(git: _Git, tmp: Path, prefix: str, oplog: str, head_text: str, taken: list[str], paths: list[str], msg: Path):
    """The commit when another session's lines stay out (CE-125). In a temporary index made from
    HEAD: ``paths`` as they are in the tree, and the op log as HEAD's lines plus ``taken``. Then
    ``git commit`` of that index, so hooks run, and the real index's entries for those paths are
    set to what was committed, as ``git commit --only`` leaves them. The working op log is never
    touched, and the real index not until the commit has landed, so a failure leaves nothing to
    undo. Returns git's commit process, or an Outcome naming the step that failed."""
    alt = _Git(git.root)
    alt.env = {**git.env, "GIT_INDEX_FILE": str(tmp / "index")}
    r = alt.run("read-tree", "HEAD")
    if r.returncode != 0:
        return Outcome(note=f"`git read-tree HEAD` failed ({_first_error(r)})")
    rest = [p for p in paths if p != oplog]
    if rest:
        a = alt.write("add", f"--pathspec-from-file={_pathspec(tmp, 'add', rest)}", "--pathspec-file-nul")
        if a.returncode != 0:
            return Outcome(note=f"`git add` failed ({_first_error(a)})")
    blob = tmp / "oplog"
    base = head_text if not head_text or head_text.endswith("\n") else head_text + "\n"
    blob.write_bytes((base + "".join(ln + "\n" for ln in taken)).encode("utf-8"))
    h = alt.run("hash-object", "-w", "--no-filters", str(blob))
    if h.returncode != 0:
        return Outcome(note=f"`git hash-object` failed ({_first_error(h)})")
    u = alt.run("update-index", "--add", "--cacheinfo", f"100644,{h.stdout.strip()},{prefix}{oplog}")  # from the top of the work tree
    if u.returncode != 0:
        return Outcome(note=f"`git update-index` failed ({_first_error(u)})")
    c = alt.write("commit", "-F", str(msg))
    if c.returncode == 0:
        r = git.write("reset", "-q", "HEAD", f"--pathspec-from-file={_pathspec(tmp, 'reset', [oplog, *rest])}", "--pathspec-file-nul")
        if r.returncode != 0:  # committed, but the real index still holds the old entries: a plain commit would undo it
            c.stderr = (f"the index was not updated ({_first_error(r)}): before any other commit, run "
                        f"`git reset -q HEAD -- {' '.join([prefix + oplog, *(prefix + p for p in rest)])}`")
            c.args = "reset-failed"
    return c


def _unstage(git: _Git, tmp: Path, untracked: list[str]) -> None:
    """Take back the ``git add`` of paths git had never seen, so a later plain ``git commit`` by
    anyone cannot carry a record without its op line."""
    if untracked:
        try:
            git.run("rm", "-q", "--cached", "--ignore-unmatch", f"--pathspec-from-file={_pathspec(tmp, 'unstage', untracked)}", "--pathspec-file-nul")
        except subprocess.TimeoutExpired:
            pass
