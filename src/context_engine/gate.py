"""The scoped gate: each gate run's result recorded against a content id of its inputs (FRAMEWORK
§8.5 G-V1, CE-78).

``[gate]`` in ``context.toml`` names the repo's gate command and its scopes. A scope is a set of
globs over the repo's files; its **scope id** is a content address over the tracked and
untracked-non-ignored files it matches (``git ls-files --cached --others --exclude-standard``),
``g1/<scope>:<16 hex>``. ``gate run`` runs the command and appends one row to a gitignored run
ledger: its result and the id of every scope, taken before and after the run. ``gate status``
says whether a scope is covered: the newest row on its current id passed, with the command
configured now. ``context-engine commit`` refuses a commit that names a path in the ``require``
scope while that scope is not covered (P7: a refusal, not a doc rule).

**What the id is.** A digest of each file's path, size and sha256, in path order, after a header
holding the algorithm, the scope's name and its whole definition (so a changed glob can never
match a row recorded under the old one). No commit id goes in: the id does not move on ``git
add`` or ``git commit``, so a green row earned before a commit is still green after it. A path
in the index but gone from the work tree (a deletion, or the old half of a rename, not yet
committed) is skipped, exactly as it is once the deletion is committed and the path leaves the
index; so the id survives that commit too, and still moves when the file goes, since its content
leaves the hash.

**It fails loudly, never plausibly.** A git failure, an unreadable file or a scope that matches
nothing refuses (``Refusal``); no id is ever invented, and a run whose ids could not be taken
records none, so it matches nothing.

**What it does not see:** gitignored files and the environment (the interpreter, installed
packages). A green row means "the command passed against these sources", not full provenance;
so the push still runs the full gate (FRAMEWORK §6.8). It hashes bytes, so a checkout that
rewrites line endings (``core.autocrlf=true``) moves the id with no content change: a false red,
never a false green (kit README § 2a; init warns, ``bootstrap.eol_warnings``; DEC-273).

**The run ledger must be gitignored**, or each row would sit inside the id it records and every
row would be born stale. ``gate run`` writes a ``.gitignore`` of ``*`` into a ledger directory
it creates, and refuses to record into a ledger git does not ignore.

**A scope's exclusions fail open:** an excluded file can no longer invalidate a green row. So an
exclusion must be verified, not assumed: ``scope_guard`` is the check for a pytest suite (a test
that opens an excluded path fails unless the scope names it in ``readers``). The readers are a
part of their own: they read files outside the scope, so they are keyed on every file
(``<scope>+readers``). After a hand edit outside the scope, ``gate status --require
<scope>+readers`` says whether they are covered and ``gate run --readers`` re-runs just them
(their names are appended to the command, as pytest takes node ids). The commit refusal checks
the scope alone (``check_commit`` says why).

**A run whose files move while it runs** records only the ids that did not move, and names the
rest in ``moved``; it is ``INCONSISTENT``, and counts for nothing, only when every id moved.

**A gate too long for one command is split into parts** (``[gate.parts.<name>]``, CE-181): each
its own command, keyed on the scope it reads, run in declared order, with no top-level
``command`` and no ``readers`` beside them. Each part's run appends its own row, ``part`` its
name, with every scope's id, so a part keyed on every file still counts toward the code scope. A
scope is **covered** when every part's newest row on its id passed with that part's command now
(``covered``: what ``check_commit`` and ``--require <scope>`` test); a part is **fresh** when it
covers its own scope, and **stale** when it is not fresh or does not cover ``require``
(``stale_parts``). ``gate run --stale`` re-runs only the stale parts, so a close's record writes
re-run only the parts that read records; ``--require <scope>+parts`` is the scope covered and
every part fresh (the close's last check, and the push's).
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

from .errors import Refusal

ALGO = "g1"
PASSED, FAILED, INCONSISTENT = "PASSED", "FAILED", "INCONSISTENT"
LEDGER = ".context/gate/runs.jsonl"
PYTHON = "{python}"  # in `command`: the interpreter the engine runs on
NAME_RE = re.compile(r"^[a-z][a-z0-9-]*$")
GIT_TIMEOUT = 120


@dataclass(frozen=True)
class Scope:
    """``[gate.scopes.<name>]``: which files a gate result depends on."""

    name: str
    include: tuple[str, ...] = ("**",)  # repo-relative globs; `**` spans directories, `*` does not
    exclude: tuple[str, ...] = ()  # a fail-open surface: verify every one (scope_guard)
    readers: tuple[str, ...] = ()  # the tests that read excluded paths, as the command takes them (pytest node ids): re-run on every file

    def matches(self, rel: str) -> bool:
        return any(_glob(g).fullmatch(rel) for g in self.include) and not any(_glob(g).fullmatch(rel) for g in self.exclude)

    def header(self) -> bytes:
        spec = json.dumps({"include": sorted(self.include), "exclude": sorted(self.exclude), "readers": sorted(self.readers)}, sort_keys=True)
        return f"context-engine-gate/{ALGO}/{self.name}/{spec}".encode() + b"\0"


def _argv(command: tuple[str, ...]) -> list[str]:
    return [sys.executable if a == PYTHON else a for a in command]


@dataclass(frozen=True)
class Part:
    """``[gate.parts.<name>]``: one command of a gate split into parts, keyed on ``scope``, the
    scope whose files it reads (CE-181)."""

    name: str
    command: tuple[str, ...]
    scope: str

    def argv(self) -> list[str]:
        return _argv(self.command)


@dataclass(frozen=True)
class Gate:
    """``[gate]``: the repo's gate command (or its parts), its run ledger, its scopes, and the
    scope a session's own commit of a path in it needs green (``require``; empty: no check)."""

    command: tuple[str, ...] = ()
    ledger: str = LEDGER
    require: str = ""
    scopes: dict[str, Scope] = field(default_factory=dict)
    skip: tuple[str, ...] = ()  # the engine's own working files (its lock file), never in a scope: set from [engine]
    parts: tuple[Part, ...] = ()  # [gate.parts], in declared order; exclusive with `command` and with scope readers

    def argv(self) -> list[str]:
        return _argv(self.command)


GATE_KEYS = ("command", "ledger", "parts", "require", "scopes")
SCOPE_KEYS = ("include", "exclude", "readers")
PART_KEYS = ("command", "scope")
RESERVED_PARTS = ("all", "readers")  # the `part` a single-command run writes in its row: never a part's name


def from_dict(raw: dict) -> Gate:
    """Parse ``[gate]``, refusing an unknown key, a wrong type, a bad glob or an unknown scope."""
    if not isinstance(raw, dict):
        raise Refusal(f"`gate` is {type(raw).__name__}, not a table", "write it as a [gate] table (the kit's context.toml.template shows it)")
    extra = sorted(set(raw) - set(GATE_KEYS))
    if extra:
        raise Refusal(f"[gate] has unknown key {extra[0]!r}", f"use only {', '.join(GATE_KEYS)} (the kit's context.toml.template is the schema)")
    cmd = raw.get("command", [])
    if not isinstance(cmd, list) or not all(isinstance(x, str) and x for x in cmd):
        raise Refusal(f"[gate] `command` is {cmd!r}", 'give the gate command as a list of words, e.g. ["{python}", "-m", "pytest", "-q"]')
    for key in ("ledger", "require"):
        if not isinstance(raw.get(key, ""), str):
            raise Refusal(f"[gate] `{key}` is {type(raw[key]).__name__}, not str", "fix its type (the kit's context.toml.template shows each)")
    ledger = raw.get("ledger", LEDGER)
    _check_rel("[gate] `ledger`", ledger)
    scopes = {}
    table = raw.get("scopes", {})
    if not isinstance(table, dict):
        raise Refusal("[gate] `scopes` is not a table", "declare each scope as [gate.scopes.<name>]")
    for name, s in table.items():
        if not NAME_RE.match(name):
            raise Refusal(f"[gate.scopes] names a scope {name!r}", "name scopes in lower case: letters, digits and `-`, starting with a letter")
        if not isinstance(s, dict):
            raise Refusal(f"[gate.scopes.{name}] is not a table", "give it include, exclude and readers lists")
        extra = sorted(set(s) - set(SCOPE_KEYS))
        if extra:
            raise Refusal(f"[gate.scopes.{name}] has unknown key {extra[0]!r}", f"use only {', '.join(SCOPE_KEYS)}")
        for key in SCOPE_KEYS:
            v = s.get(key, [])
            if not isinstance(v, list) or not all(isinstance(x, str) and x for x in v):
                raise Refusal(f"[gate.scopes.{name}] `{key}` is {v!r}", "give a list of non-empty strings")
        for g in [*s.get("include", []), *s.get("exclude", [])]:
            _check_rel(f"[gate.scopes.{name}] glob", g)
        scopes[name] = Scope(name, tuple(s.get("include", ["**"])), tuple(s.get("exclude", [])), tuple(s.get("readers", [])))
    require = raw.get("require", "")
    if require and require not in scopes:
        raise Refusal(f"[gate] `require` names scope {require!r}, which is not declared", f"declare [gate.scopes.{require}], or name one of: {', '.join(sorted(scopes)) or 'none declared'}")
    parts = _parts(raw.get("parts", {}), scopes)
    if parts and cmd:
        raise Refusal("[gate] sets both `command` and `parts`", "give either `command` or `parts`, not both: one command for the whole gate, or one per part")
    if require and not cmd and not parts:
        raise Refusal("[gate] sets `require` but no `command`", "set the gate command, or unset `require`")
    return Gate(tuple(cmd), ledger, require, scopes, parts=parts)


def _parts(table: object, scopes: dict[str, Scope]) -> tuple[Part, ...]:
    """Parse ``[gate.parts]``: each part a command and the declared scope it is keyed on."""
    if not isinstance(table, dict):
        raise Refusal("[gate] `parts` is not a table", "declare each part as [gate.parts.<name>], with `command` and `scope`")
    out = []
    for name, p in table.items():
        if not NAME_RE.match(name):
            raise Refusal(f"[gate.parts] names a part {name!r}", "name parts in lower case: letters, digits and `-`, starting with a letter")
        if name in RESERVED_PARTS:
            raise Refusal(f"[gate.parts] names a part {name!r}, which is reserved", f"rename it: {' and '.join(RESERVED_PARTS)} label a single-command run's row")
        if not isinstance(p, dict):
            raise Refusal(f"[gate.parts.{name}] is not a table", "give it `command` and `scope`")
        extra = sorted(set(p) - set(PART_KEYS))
        if extra:
            raise Refusal(f"[gate.parts.{name}] has unknown key {extra[0]!r}", f"use only {', '.join(PART_KEYS)}")
        cmd = p.get("command")
        if not isinstance(cmd, list) or not cmd or not all(isinstance(x, str) and x for x in cmd):
            raise Refusal(f"[gate.parts.{name}] `command` is {cmd!r}", 'give the part\'s command as a non-empty list of words, e.g. ["{python}", "-m", "pytest", "-q", "tests/unit"]')
        scope = p.get("scope", "")
        if not isinstance(scope, str) or not scope:
            raise Refusal(f"[gate.parts.{name}] names no `scope`", "name the scope whose files the part reads, e.g. scope = \"code\" (a part keyed on too narrow a scope fails open)")
        if scope not in scopes:
            raise Refusal(f"[gate.parts.{name}] names scope {scope!r}, which is not declared", f"declare [gate.scopes.{scope}], or name one of: {', '.join(sorted(scopes)) or 'none declared'}")
        out.append(Part(name, tuple(cmd), scope))
    if out and any(s.readers for s in scopes.values()):
        raise Refusal("[gate] declares `parts` and a scope with `readers`", "parts and readers are exclusive: drop the readers, and key a part on a scope that holds what they read")
    return tuple(out)


def _check_rel(what: str, path: str) -> None:
    if not path or "\\" in path or path.startswith("/") or re.match(r"^[A-Za-z]:", path) or ".." in path.split("/"):
        raise Refusal(f"{what} {path!r} is not a path relative to the repo root", "write it from the repo root with `/`, no `..`, no leading `/` or drive")


_GLOBS: dict[str, re.Pattern[str]] = {}


def _glob(pattern: str) -> re.Pattern[str]:
    """A repo-relative glob as a regex over a whole `/`-separated path: `**` spans directories
    (`docs/**` is everything under docs/, `**/*.md` every .md file), `*` and `?` stay inside one
    path part. Unlike gitignore, a pattern without `/` is not matched at every depth."""
    if pattern not in _GLOBS:
        out, i = [], 0
        while i < len(pattern):
            if pattern.startswith("**/", i):
                out.append("(?:.*/)?")
                i += 3
            elif pattern.startswith("/**", i) and i + 3 == len(pattern):
                out.append("(?:/.*)?")
                i += 3
            elif pattern.startswith("**", i):
                out.append(".*")
                i += 2
            elif pattern[i] == "*":
                out.append("[^/]*")
                i += 1
            elif pattern[i] == "?":
                out.append("[^/]")
                i += 1
            else:
                out.append(re.escape(pattern[i]))
                i += 1
        _GLOBS[pattern] = re.compile("".join(out), re.DOTALL)
    return _GLOBS[pattern]


# -- the scope id ------------------------------------------------------------------------------


def _git(root: Path, *args: str) -> bytes:
    """Git's stdout as bytes, or a refusal: never a guess. Output goes through a temporary file,
    as the engine's commits do (a hook's child can hold a pipe open on Windows)."""
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        try:
            p = subprocess.run(["git", "-C", str(root), *args], stdin=subprocess.DEVNULL, stdout=out, stderr=err, timeout=GIT_TIMEOUT)
        except (OSError, subprocess.SubprocessError) as exc:
            raise Refusal(f"`git {' '.join(args)}` could not run ({exc})", "a scope id needs git: install it, or run the full gate") from exc
        out.seek(0)
        err.seek(0)
        if p.returncode != 0:
            tail = err.read().decode("utf-8", "replace").strip().splitlines()
            raise Refusal(f"`git {' '.join(args)}` exited {p.returncode}" + (f" ({tail[-1]})" if tail else ""), "a scope id needs a git work tree; outside one, run the full gate")
        return out.read()


def files(root: Path) -> list[str]:
    """Every path a scope can cover, relative to ``root`` with `/`: tracked and untracked, less
    what git ignores; sorted, each once (an unmerged path is listed once per stage)."""
    raw = _git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    return sorted({p.decode("utf-8", "surrogateescape") for p in raw.split(b"\0") if p})


def _fingerprint(root: Path, rel: str) -> bytes | None:
    path = root / rel
    try:
        data = path.read_bytes()
    except FileNotFoundError:
        return None  # in the index, gone from the work tree: skipped, as after its deletion is committed
    except IsADirectoryError:
        return b"dir"  # a submodule's gitlink: its content is not this repo's
    except PermissionError:
        if path.is_dir():
            return b"dir"  # Windows says PermissionError for a directory
        raise Refusal(f"cannot read {rel}", "a scope id must read every file it covers; fix its permissions, or run the full gate") from None
    except OSError as exc:
        raise Refusal(f"cannot read {rel} ({exc})", "a scope id must read every file it covers; fix it, or run the full gate") from exc
    return b"%d:%s" % (len(data), hashlib.sha256(data).hexdigest().encode())


def listing(root: Path, gate: Gate) -> list[str]:
    """``files``, less the engine's own working files: its lock file and the run ledger's
    directory, which change as the engine runs and say nothing about what the gate tested."""
    runs = Path(gate.ledger).parent.as_posix() + "/"
    return [f for f in files(root) if f not in gate.skip and not f.startswith(runs)]


def scope_id(root: Path, scope: Scope, listed: list[str] | None = None) -> str:
    """The content id of ``scope`` in the work tree at ``root``. ``listed`` is ``files(root)``,
    when the caller already has it."""
    h = hashlib.sha256(scope.header())
    covered = 0
    for rel in files(root) if listed is None else listed:
        if not scope.matches(rel):
            continue
        fp = _fingerprint(root, rel)
        if fp is None:
            continue
        covered += 1
        h.update(rel.encode("utf-8", "surrogateescape") + b"\0" + fp + b"\0")
    if not covered:
        raise Refusal(f"scope {scope.name!r} covers no file", "an id over nothing would certify anything: fix the scope's globs")
    return f"{ALGO}/{scope.name}:{h.hexdigest()[:16]}"


def readers_scope(scope: Scope) -> Scope:
    """What a scope's readers depend on: every file (they read what the scope leaves out, and the
    code too). Its id names the readers, so a run of another reader list never matches."""
    return Scope(f"{scope.name}+readers", ("**",), (), scope.readers)


def scope_ids(root: Path, gate: Gate) -> dict[str, str]:
    """The id of every scope, and of every scope's readers (``<scope>+readers``), here."""
    listed = listing(root, gate)
    out = {}
    for name, s in sorted(gate.scopes.items()):
        out[name] = scope_id(root, s, listed)
        if s.readers:
            out[f"{name}+readers"] = scope_id(root, readers_scope(s), listed)
    return out


# -- the run ledger ----------------------------------------------------------------------------


def read_rows(path: Path) -> list[dict]:
    """The ledger's rows, in the order they were appended; a torn or foreign line is skipped."""
    if not path.is_file():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict) and isinstance(row.get("scopes"), dict):
            rows.append(row)
    return rows


def covering(rows: list[dict], gate: Gate, key: str, here: str) -> dict | None:
    """The newest row recorded on ``key`` (a scope, or ``<scope>+readers``) at id ``here``, if it
    passed with the command configured now; else None. The newest row on that id decides: a pass
    then a fail on the same files is not green."""
    last = None
    for row in rows:
        if row.get("scopes", {}).get(key) == here and row.get("status") in (PASSED, FAILED):
            last = row
    if last and last["status"] == PASSED and list(last.get("command", [])) == list(gate.command):
        return last
    return None


def _part_rows(rows: list[dict], part: Part, key: str, here: str) -> list[dict]:
    return [r for r in rows if r.get("part") == part.name and r.get("scopes", {}).get(key) == here and r.get("status") in (PASSED, FAILED)]


def part_covering(rows: list[dict], part: Part, key: str, here: str) -> dict | None:
    """``covering`` for one part: the newest row of this part on ``key`` at id ``here``, if it
    passed with the part's command now; else None. Another part's row never counts, whatever its
    command."""
    seen = _part_rows(rows, part, key, here)
    if seen and seen[-1]["status"] == PASSED and list(seen[-1].get("command", [])) == list(part.command):
        return seen[-1]
    return None


def covered(rows: list[dict], gate: Gate, key: str, here: str) -> tuple[bool, list[str]]:
    """Whether the whole gate passed on scope ``key`` at id ``here``, and the names of the parts
    that did not: with parts, every part must cover it; without, ``covering`` decides."""
    if not gate.parts:
        return covering(rows, gate, key, here) is not None, []
    missing = [p.name for p in gate.parts if part_covering(rows, p, key, here) is None]
    return not missing, missing


def stale_parts(rows: list[dict], gate: Gate, ids: dict[str, str]) -> list[Part]:
    """The parts ``gate run --stale`` runs, in declared order: each not fresh (no green run of it
    on its own scope's id here) or not covering the ``require`` scope's id here."""
    out = []
    for p in gate.parts:
        fresh = part_covering(rows, p, p.scope, ids[p.scope]) is not None
        if not fresh or (gate.require and part_covering(rows, p, gate.require, ids[gate.require]) is None):
            out.append(p)
    return out


def _part_why(rows: list[dict], part: Part, key: str, here: str) -> str:
    seen = _part_rows(rows, part, key, here)
    if not seen:
        return "no run on it"
    return f"its newest run on it {seen[-1]['status']}" if seen[-1]["status"] != PASSED else "its newest run on it ran another command"


def _ignored(root: Path, rel: str) -> bool:
    try:
        _git(root, "check-ignore", "-q", "--no-index", rel)
        return True
    except Refusal:
        return False


def _ledger_path(root: Path, gate: Gate) -> Path:
    """The ledger, in a directory that git ignores: a directory gate run creates gets a
    `.gitignore` of `*`, as `.context/` does. A ledger git tracks or does not ignore is refused."""
    path = root / gate.ledger
    if not path.parent.exists():
        path.parent.mkdir(parents=True)
        (path.parent / ".gitignore").write_text("*\n", encoding="utf-8")
    if not _ignored(root, gate.ledger) or gate.ledger in files(root):
        raise Refusal(f"the run ledger {gate.ledger} is tracked or not gitignored, so each row would sit inside the scope id it records",
                      f"untrack and ignore it (a `.gitignore` of `*` in {Path(gate.ledger).parent.as_posix()}/), or point [gate] `ledger` into .context/")
    return path


def _stamp(t: float) -> str:
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def _head(root: Path) -> str:
    """A label for the row, never part of a match: HEAD's short hash."""
    try:
        return _git(root, "rev-parse", "--short", "HEAD").decode().strip()
    except Refusal:
        return ""


def run(root: Path, gate: Gate, *, readers: bool = False, parts: list[str] | None = None, stale: bool = False,
        session: str | None = None, actor: str | None = None) -> tuple[int, str]:
    """Run the gate command at ``root`` and append its row; the reply is one line. ``readers``
    runs only the scopes' readers (their names appended to the command) and records only their
    ids: what a change outside a covered scope needs. An id that moved while the command ran is
    left out of the row (named in ``moved``): the run tested no set of those files anyone can
    name; the ids that did not move are recorded.

    With ``[gate.parts]``, it runs every part in declared order, or the named ``parts``, or with
    ``stale`` only the stale ones (``stale_parts``), and goes on past a failing part; each part
    appends its own row as it ends. The reply is a line per part, then a summary."""
    if readers and (parts or stale):
        raise Refusal("`--readers` with `--part` or `--stale`", "give one: readers belong to a single-command gate, parts to a gate split into parts")
    if parts and stale:
        raise Refusal("`--part` with `--stale`", "give one: `--part NAME` runs the parts named, `--stale` the parts whose files moved")
    if not gate.command and not gate.parts:
        raise Refusal("[gate] has no `command`", 'set it in context.toml, e.g. command = ["{python}", "-m", "pytest", "-q"]; or run the gate by hand')
    if gate.parts:
        if readers:
            raise Refusal("[gate] declares parts, which take no `--readers`", "run `context-engine gate run --stale`: it re-runs the parts whose files moved")
        return _run_parts(root, gate, parts, stale, session, actor)
    if parts or stale:
        raise Refusal(f"`--{'part' if parts else 'stale'}` but [gate] declares no parts", "run the whole gate: `context-engine gate run` (or `context-engine gate run --readers` for the readers)")
    names = list(dict.fromkeys(r for s in gate.scopes.values() for r in s.readers))
    if readers and not names:
        raise Refusal("no gate scope names `readers`", "run the whole gate: `context-engine gate run`")
    ledger = _ledger_path(root, gate)
    keep = (lambda k: k.endswith("+readers")) if readers else (lambda k: True)
    row, moved, kept, log = _run_one(root, gate, ledger, gate.argv() + (names if readers else []), gate.command,
                                     "readers" if readers else "all", keep, names if readers else [], session, actor, "")
    status, seconds = row["status"], row["seconds"]
    what = "gate readers" if readers else "gate"
    if status == INCONSISTENT:
        return 1, f"{what} {status}: the files of {', '.join(moved)} changed while it ran ({seconds}s), so the run counts for nothing; run it again; log {row['log']}"
    unrecorded = f"; not recorded on {', '.join(moved)}: their files changed while it ran" if moved else ""
    return (0 if status == PASSED else 1), f"{what} {status} in {seconds}s ({_last_line(log)}) on {', '.join(kept.values())}{unrecorded}; log {row['log']}"


def _run_parts(root: Path, gate: Gate, parts: list[str] | None, stale: bool, session: str | None, actor: str | None) -> tuple[int, str]:
    names = [p.name for p in gate.parts]
    unknown = [n for n in parts or [] if n not in names]
    if unknown:
        raise Refusal(f"no gate part named {unknown[0]!r}", f"name one of: {', '.join(names)}")
    ledger = _ledger_path(root, gate)
    if parts:
        chosen = [p for p in gate.parts if p.name in parts]
    elif stale:
        chosen = stale_parts(read_rows(ledger), gate, scope_ids(root, gate))
        if not chosen:
            return 0, "gate: every part is fresh" + (f" and covers {gate.require}" if gate.require else "") + ": nothing to run"
    else:
        chosen = list(gate.parts)
    lines, results = [], {PASSED: [], FAILED: [], INCONSISTENT: []}
    for p in chosen:
        row, moved, kept, log = _run_one(root, gate, ledger, p.argv(), p.command, p.name, lambda k: True, [], session, actor, p.name)
        status, seconds = row["status"], row["seconds"]
        results[status].append(p.name)
        if status == INCONSISTENT:
            lines.append(f"gate part {p.name} {status}: the files of {', '.join(moved)} changed while it ran ({seconds}s), so the run counts for nothing; log {row['log']}")
            continue
        unrecorded = f"; not recorded on {', '.join(moved)}: their files changed while it ran" if moved else ""
        lines.append(f"gate part {p.name} {status} in {seconds}s ({_last_line(log)}) on {', '.join(kept.values())}{unrecorded}; log {row['log']}")
    summary = f"gate: {len(chosen)} part{'s' if len(chosen) != 1 else ''} run: {len(results[PASSED])} {PASSED}"
    summary += "".join(f"; {s}: {', '.join(results[s])}" for s in (FAILED, INCONSISTENT) if results[s])
    return (0 if len(results[PASSED]) == len(chosen) else 1), "\n".join([*lines, summary])


def _run_one(root: Path, gate: Gate, ledger: Path, argv: list[str], command: tuple[str, ...], part: str, keep, args: list[str],
             session: str | None, actor: str | None, tag: str) -> tuple[dict, list[str], dict[str, str], Path]:
    """Run one command, append its row and return it, with the ids that moved, those kept, and
    its log. ``tag`` goes in the log's name, so parts run in the same second keep their logs."""
    before = {k: v for k, v in scope_ids(root, gate).items() if keep(k)}
    started = time.time()
    log = ledger.parent / f"{dt.datetime.fromtimestamp(started).strftime('%Y%m%dT%H%M%S')}-{os.getpid()}{'-' + tag if tag else ''}.log"
    with open(log, "wb") as out:
        try:
            code = subprocess.run(argv, cwd=root, stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT).returncode
        except OSError as exc:
            out.write(f"could not start {argv!r}: {exc}\n".encode())
            code = 127
    seconds = round(time.time() - started, 1)
    try:
        after = {k: v for k, v in scope_ids(root, gate).items() if keep(k)}
    except Refusal:
        after = {}
    # Each id is judged on its own: a scope whose files did not move is recorded, so a change
    # elsewhere during a long run (another session's op-log line, a HANDOFF edit) costs only the
    # ids it moved, never the code scope's. INCONSISTENT only when every id moved.
    moved = sorted(k for k in before if before[k] != after.get(k))
    kept = {k: v for k, v in before.items() if k not in moved}
    status = INCONSISTENT if not kept else PASSED if code == 0 else FAILED
    row = {
        "started": _stamp(started), "seconds": seconds, "status": status, "exit": code, "part": part,
        "command": list(command), "args": list(args), "scopes": kept,
        "log": log.relative_to(root).as_posix(), "head": _head(root), "session": session or "", "actor": actor or "",
    }
    if moved:
        row["moved"] = moved
    with open(ledger, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(row) + "\n")
    return row, moved, kept, log


def _last_line(log: Path) -> str:
    lines = [ln.strip() for ln in log.read_text(encoding="utf-8", errors="replace").splitlines() if ln.strip()]
    return (lines[-1].strip("= ") if lines else "no output")[:160]


def _verdict(rows: list[dict], gate: Gate, key: str, here: str) -> tuple[bool, str]:
    row = covering(rows, gate, key, here)
    if row:
        return True, f"{key}: covered on {here} by the {row.get('part', 'all')} run of {row['started']} ({row['seconds']}s, {row.get('log', '')})"
    seen = [r for r in rows if r.get("scopes", {}).get(key) == here]
    why = f"its newest run on it {seen[-1]['status']}" if seen else "no run on it"
    return False, f"{key}: NOT covered on {here} ({why})"


def status(root: Path, gate: Gate, require: str = "") -> tuple[int, str]:
    """One line per scope, and per scope's readers: its id here and whether a green run covers
    it. ``require`` names what must be covered, or the exit code is 1 and the last line says what
    to run: a scope (``code``: what ``context-engine commit`` checks for a path in it), or a
    scope with its readers (``code+readers``: what a hand-edited file the scope leaves out
    needs)."""
    if not gate.scopes:
        raise Refusal("[gate] declares no scopes", "declare one, e.g. [gate.scopes.all] (include defaults to every file)")
    if gate.parts:
        return _status_parts(root, gate, require)
    name, plus, _ = require.partition("+")
    keys = sorted(gate.scopes) + sorted(f"{n}+readers" for n, s in gate.scopes.items() if s.readers)
    if require and require not in keys:
        raise Refusal(f"no gate scope named {require!r}", f"name one of: {', '.join(keys)}")
    rows = read_rows(root / gate.ledger)
    out, ok = [], {}
    for key, here in scope_ids(root, gate).items():
        ok[key], line = _verdict(rows, gate, key, here)
        out.append(line)
    if not require:
        return 0, "\n".join(out)
    code, part = ok[name], ok[require] if plus else True
    if code and part:
        out.append(f"require {require}: green")
    elif code:
        out.append(f"require {require}: red: the scope is covered, its readers are not (a file it leaves out changed): run `context-engine gate run --readers`")
    else:
        out.append(f"require {require}: red: run `context-engine gate run` ({' '.join(gate.command)})")
    return (0 if code and part else 1), "\n".join(out)


def _status_parts(root: Path, gate: Gate, require: str) -> tuple[int, str]:
    """``status`` for a gate split into parts: a line per scope (covered when every part passed on
    its id), a line per part (fresh, or STALE: what ``gate run --stale`` runs), and with
    ``require`` (a scope, or ``<scope>+parts``: the scope covered and every part fresh) a last
    line naming what to run."""
    keys = sorted(gate.scopes) + sorted(f"{n}+parts" for n in gate.scopes)
    if require and require not in keys:
        raise Refusal(f"no gate scope named {require!r}", f"name one of: {', '.join(keys)}")
    rows = read_rows(root / gate.ledger)
    ids = scope_ids(root, gate)
    out, missing = [], {}
    for key, here in ids.items():
        ok, missing[key] = covered(rows, gate, key, here)
        if ok:
            out.append(f"{key}: covered on {here} (every part passed on it)")
        else:
            whys = "; ".join(f"part {p.name}: {_part_why(rows, p, key, here)}" for p in gate.parts if p.name in missing[key])
            out.append(f"{key}: NOT covered on {here} ({whys})")
    stale = [p.name for p in stale_parts(rows, gate, ids)]
    unfresh = []
    for p in gate.parts:
        here = ids[p.scope]
        row = part_covering(rows, p, p.scope, here)
        if row is None:
            unfresh.append(p.name)
            out.append(f"part {p.name} (scope {p.scope}): STALE on {here} ({_part_why(rows, p, p.scope, here)})")
        elif p.name in stale:
            out.append(f"part {p.name} (scope {p.scope}): STALE: it passed on {here}, not on {gate.require}'s files ({ids[gate.require]})")
        else:
            out.append(f"part {p.name} (scope {p.scope}): fresh on {here} by the run of {row['started']} ({row['seconds']}s, {row.get('log', '')})")
    if not require:
        return 0, "\n".join(out)
    name, plus, _ = require.partition("+")
    need = list(dict.fromkeys(n for n in [p.name for p in gate.parts] if n in missing[name] or (plus and n in unfresh)))
    if not need:
        out.append(f"require {require}: green")
        return 0, "\n".join(out)
    what = "--stale" if set(need) <= set(stale) else " ".join(f"--part {n}" for n in need)
    out.append(f"require {require}: red: run `context-engine gate run {what}` (parts {', '.join(need)})")
    return 1, "\n".join(out)


def _under(root: Path, path: str, listed: list[str]) -> list[str]:
    """The files a commit path stands for: a directory's listed files, else the path itself
    (a file, or one deleted from the tree and the index, which is a change all the same)."""
    rel = path.rstrip("/")
    if (root / rel).is_dir():
        return [f for f in listed if f.startswith(rel + "/")]
    return [rel, *(f for f in listed if f.startswith(rel + "/"))]


def check_commit(root: Path, gate: Gate, paths: list[str]) -> None:
    """Refuse a session's own commit that names a path in the ``require`` scope unless a green run
    covers that scope's current id (FRAMEWORK §8.5 G-V1). Paths the op log's lines name are not
    counted: the engine's own commits of its writes are the gate's one exception (FRAMEWORK §5.5
    rule 4).

    The scope's readers are not checked here. A green row on the scope is a whole-gate run,
    readers included, on exactly these files; what the readers would re-check is the files the
    scope leaves out, which a commit of a path in it does not commit. Their id is keyed on every
    file, the op log included (lint reads it), so every engine write moves it, this session's or
    a concurrent one's: requiring it here refused code commits on activity unrelated to them
    (review of 2026-10-14g). A hand-edited file outside the scope needs ``gate status --require
    <scope>+readers``, as a records-only commit, which is not refused, always has."""
    if not gate.require or not paths:
        return
    scope = gate.scopes[gate.require]
    listed = listing(root, gate)
    hit = next((p for p in paths if any(scope.matches(f) for f in _under(root, p, listed))), None)
    if hit is None:
        return
    rows = read_rows(root / gate.ledger)
    here = scope_id(root, scope, listed)
    ok, missing = covered(rows, gate, scope.name, here)
    if ok:
        return
    if gate.parts:  # every part must have passed on these files; freshness is not checked, as the readers are not
        raise Refusal(f"{hit} is in gate scope {scope.name!r}, which no green gate run covers ({here}); parts not passed on it: {', '.join(missing)}",
                      "run `context-engine gate run --stale` (the stale parts, recorded), then commit; `context-engine gate status` says what is covered")
    raise Refusal(f"{hit} is in gate scope {scope.name!r}, which no green gate run covers ({here})",
                  "run `context-engine gate run` (the whole gate, recorded), then commit; `context-engine gate status` says what is covered")
