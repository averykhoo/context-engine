"""The guard on a gate scope's exclusions, for a pytest suite (FRAMEWORK §8.5 G-V1, CE-78).

A scope's exclusion fails open: a file the scope excludes can no longer make a green run stale,
so a test that reads one could go red on a change the gate calls covered. The prior art paid for
this (graph-reachability-zanzibar-index, 2026-09-03c: a test began linting the live board twelve
days after "no test reads markdown" was surveyed). A survey goes stale when a test is added; this
guard does not. While each test runs (its fixtures included), an audit hook watches every file
the test process opens or lists, and every process it starts, under the repo root; a test that
touches a path the scope excludes fails, unless the scope names it in ``readers``:

- **open** of a file the scope excludes (one git lists: tracked, or untracked and not ignored);
- **listing** a directory that directly holds such a file (the test sees which exist);
- **a process started in the repo**: what it reads is out of the hook's sight, so it counts as
  reading everything when its working directory is under the root, given or inherited, unless
  its command names a path outside the root (a test pointing it at a temporary repo); and a
  process whose command names the root itself, or a path under it that the scope excludes or
  that holds such a path, counts too.

A reader is re-run on every file (``gate run --readers``), so its read cannot go stale; name it
by pytest node id (parameters left off) or by its file (``tests/test_x.py``). Wire the guard
from ``conftest.py``::

    from context_engine.scope_guard import pytest_runtest_makereport, pytest_runtest_protocol  # noqa: F401

The scope is ``[gate] require`` in the repo's ``context.toml``, the root is the directory
holding it, found upward from the working directory; ``CE_SCOPE_GUARD=off`` turns it off for a
run (the sabotage that proves it). Deliberately not seen: reads by a process the test starts
outside the repo, and C extensions that open files without Python's audit events.
"""

from __future__ import annotations

import os
import sys
import textwrap
from pathlib import Path

import pytest

from . import gate as G
from .config import CONFIG_NAME, load


class Guard:
    def __init__(self, root: Path, scope: G.Scope):
        self.root = root.resolve()
        self.scope = scope
        listed = G.files(self.root)
        self.excluded = {f for f in listed if not scope.matches(f)}
        self.dirs: dict[str, set[str]] = {}  # directory -> its direct children that are excluded files
        for f in self.excluded:
            parent = f.rpartition("/")[0]
            self.dirs.setdefault(parent, set()).add(f)
        self.prefix = os.path.normcase(str(self.root)) + os.sep
        self.test: str | None = None
        self.seen: dict[str, list[str]] = {}

    def reader(self, nodeid: str) -> bool:
        base = nodeid.split("[", 1)[0]
        return any(r in (base, base.split("::", 1)[0]) for r in self.scope.readers)

    def _holds(self, rel: str) -> bool:
        """``rel`` is an excluded file, the root, or a directory holding an excluded file."""
        return rel == "" or rel in self.excluded or any(f.startswith(rel.rstrip("/") + "/") for f in self.excluded)

    def _rel(self, path) -> str | None:
        try:
            p = os.fspath(path)
        except TypeError:
            return None
        if isinstance(p, bytes):
            p = os.fsdecode(p)
        full = os.path.normcase(os.path.abspath(p))
        if full == self.prefix[:-1]:
            return ""
        if not full.startswith(self.prefix):
            return None
        rel = os.path.abspath(p)[len(self.prefix):].replace(os.sep, "/")
        return rel

    def hook(self, event: str, args: tuple) -> None:
        if self.test is None or self.reader(self.test):
            return
        if event == "open":
            if args and not isinstance(args[0], int):
                rel = self._rel(args[0])
                if rel in self.excluded:
                    self._note(f"opened {rel}")
        elif event in ("os.listdir", "os.scandir"):
            if args and not isinstance(args[0], int):
                rel = self._rel(args[0] if args[0] is not None else ".")
                if rel is not None and self.dirs.get(rel):
                    self._note(f"listed {rel or '.'}/, which holds {sorted(self.dirs[rel])[0]}")
        elif event == "subprocess.Popen":
            _, argv, cwd, _ = args
            words = [os.fsdecode(a) if isinstance(a, bytes) else str(a) for a in argv] if isinstance(argv, (list, tuple)) else _split(str(argv))
            shown = " ".join(words)[:80]
            paths = [w for w in (_path_in(x) for x in words[1:]) if w]
            inside = [r for r in (self._rel(x) for x in paths) if r is not None]
            outside = len(paths) > len(inside)
            rel = self._rel(cwd if cwd is not None else os.getcwd())
            if rel is not None and not outside:
                self._note(f"started a process in {rel or '.'}/ ({shown}), which may read any file")
            elif any(self._holds(r) for r in inside):
                self._note(f"started a process naming {next(r for r in inside if self._holds(r)) or '.'} ({shown})")

    def _note(self, what: str) -> None:
        notes = self.seen.setdefault(self.test, [])
        if what not in notes and len(notes) < 5:
            notes.append(what)

    def verdict(self, nodeid: str) -> str:
        notes = self.seen.pop(nodeid, [])
        if not notes:
            return ""
        return (f"scope guard (FRAMEWORK §8.5 G-V1): this test reads what gate scope {self.scope.name!r} excludes, so a "
                f"green run on the scope would not notice a change to it: {'; '.join(notes)}. Keep the path in the scope "
                f"(drop its glob from [gate.scopes.{self.scope.name}] exclude), stop the test reading it, or name the "
                f"test in the scope's `readers`, which `context-engine gate run --readers` re-runs on every file.")


def _split(command: str) -> list[str]:
    """A Windows command line (the audit event gets one string there) cut into its words."""
    import shlex

    try:
        return shlex.split(command, posix=False)
    except ValueError:
        return command.split()


def _path_in(word: str) -> str | None:
    """The absolute path a command word names (`--root=C:/x` too), else None."""
    w = word.strip('"').split("=", 1)[-1].strip('"')
    return w if w and os.path.isabs(w) else None


GUARD: Guard | None = None


def _install() -> Guard | None:
    global GUARD
    if GUARD is not None or os.environ.get("CE_SCOPE_GUARD") == "off":
        return GUARD
    here = Path.cwd().resolve()
    root = next((p for p in (here, *here.parents) if (p / CONFIG_NAME).is_file()), None)
    if root is None:
        return None
    gate = load(root).gate
    if not gate.require:
        return None
    GUARD = Guard(root, gate.scopes[gate.require])
    sys.addaudithook(lambda event, args: GUARD.hook(event, args) if GUARD is not None else None)
    return GUARD


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    guard = _install()
    if guard is not None:
        guard.test = item.nodeid
    try:
        yield
    finally:
        if guard is not None:
            guard.test = None


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """The test fails with the reads of its setup and its call; a read in its teardown fails the
    teardown."""
    outcome = yield
    if GUARD is None or call.when == "setup":
        return
    why = GUARD.verdict(item.nodeid)
    if why:
        rep = outcome.get_result()
        rep.outcome = "failed"
        rep.longrepr = "\n".join("E   " + line for line in textwrap.wrap(why, 110))  # pytest's own failure-line form
