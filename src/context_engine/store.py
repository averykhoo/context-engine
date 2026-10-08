"""The record store: find records, allocate ids, write under a lock, log every operation.

Every write is one operation: it takes the repo lock, re-reads the record inside it (so two
writers never lose each other's change, AC-9), checks the result against the kind's schema
before any byte is written (AC-5), writes atomically, and appends one line to the operation log
carrying the session key and the actor (AC-6).

Deliberately not checked here: whether an actor is allowed to make a change (that is policy,
in the operations built on this core), and whether an append-only body changed *before* it was
stamped (nothing can know that).
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterator

from . import config as config_mod
from . import okf
from .config import Config, Kind
from .errors import Refusal
from .lock import FileLock

SESSION_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[a-z]+$")
ACTOR_RE = re.compile(r"^(human:\S+|process:\S+|[A-Za-z0-9._-]+/[A-Za-z0-9._:+-]+)$")  # OKF §7
OKF_STATUS = ("draft", "stable", "deprecated")  # OKF §5.4
TOOL_OWNED = ("type", "id", "body_sha")
RESERVED_MD = ("index.md", "log.md")  # OKF §3.1


@dataclass
class Record:
    id: str
    kind: Kind
    path: Path
    doc: okf.Document


@dataclass(frozen=True)
class Failure:
    guard: str
    path: str
    message: str
    remedy: str

    def __str__(self) -> str:
        return f"{self.guard} {self.path}: {self.message}. Remedy: {self.remedy}"


def slugify(title: str, limit: int = 48) -> str:
    """Generated once at `new` and never updated, so a retitle never moves a file."""
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    if len(slug) > limit:
        slug = slug[:limit].rsplit("-", 1)[0]
    return slug


def key_order(key: str) -> tuple[str, int, str]:
    """Session keys sort by date, then by letter sequence read as a number (z < aa)."""
    return (key[:10], len(key) - 10, key[10:])


def coerce(kind: Kind, key: str, text: str) -> Any:
    """Turn a CLI string into the value the kind's schema declares (CE-2 trap: no quoted dates)."""
    want = kind.types.get(key, "str")
    if text.strip().lower() in ("", "null", "~"):
        return None
    try:
        if want == "date":
            return dt.date.fromisoformat(text.strip())
        if want == "int":
            return int(text)
    except ValueError:
        raise Refusal(f"{key}={text!r} is not a {want}", f"give {key} as a {want}" + (" (YYYY-MM-DD)" if want == "date" else "")) from None
    if want == "list":
        inner = text.strip()
        if inner.startswith("[") and inner.endswith("]"):
            inner = inner[1:-1]
        return [x.strip() for x in inner.split(",") if x.strip()]
    if want == "key":
        if not SESSION_RE.match(text.strip()):
            raise Refusal(f"{key}={text!r} is not a session key", "give a key like 2026-10-08c")
        return text.strip()
    return text


def _wrong_type(want: str, value: Any) -> bool:
    if value is None:
        return False
    if want == "date":
        return not isinstance(value, dt.date) or isinstance(value, dt.datetime)
    if want == "int":
        return not isinstance(value, int) or isinstance(value, bool)
    if want == "list":
        return not isinstance(value, list)
    if want == "key":
        return not isinstance(value, str) or not SESSION_RE.match(value)
    return False


def _now() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


class Store:
    def __init__(self, root: Path | str, config: Config | None = None):
        self.root = Path(root).resolve()
        self.config = config if config is not None else config_mod.load(self.root)

    # -- reading -----------------------------------------------------------------------

    def _rel(self, path: Path) -> str:
        return path.relative_to(self.root).as_posix()

    def _dirs(self, kind: Kind) -> list[Path]:
        return [self.root / d for d in (kind.dir, *kind.extra_dirs)]

    def _files(self, kind: Kind) -> Iterator[Path]:
        for d in self._dirs(kind):
            if d.is_dir():
                yield from sorted(p for p in d.glob("*.md") if p.name not in RESERVED_MD)

    def _id_of(self, kind: Kind, path: Path) -> str | None:
        m = re.match(rf"^({re.escape(kind.prefix)}-\d+)(?:-|\.md$)", path.name)
        return m.group(1) if m else None

    def read(self, path: Path) -> okf.Document:
        return okf.parse(path.read_bytes().decode("utf-8"))

    def heads(self, kind_name: str) -> Iterator[Record]:
        """Every record of a kind with its frontmatter only (``doc.body`` is empty, AC-13)."""
        kind = self.config.kind(kind_name)
        for path in self._files(kind):
            rid = self._id_of(kind, path)
            if rid:
                yield Record(rid, kind, path, okf.read_head(path))

    def records(self, kind_name: str) -> Iterator[Record]:
        kind = self.config.kind(kind_name)
        for path in self._files(kind):
            rid = self._id_of(kind, path)
            if rid:
                yield Record(rid, kind, path, self.read(path))

    def find(self, record_id: str) -> Path:
        kind = self.config.kind_for_id(record_id)
        hits = [p for p in self._files(kind) if self._id_of(kind, p) == record_id]
        if not hits:
            raise Refusal(f"no record {record_id}", f"list the {kind.name} records to find the right id")
        if len(hits) > 1:
            names = ", ".join(self._rel(p) for p in hits)
            raise Refusal(f"id {record_id} is used by {len(hits)} files ({names})", "renumber the newer one by hand, then run lint")
        return hits[0]

    def get(self, record_id: str) -> Record:
        path = self.find(record_id)
        return Record(record_id, self.config.kind_for_id(record_id), path, self.read(path))

    def ids_in_use(self, kind: Kind) -> set[int]:
        """Every number in the series, open and closed, from file names and from `id:` keys (G-D2)."""
        used = set()
        for path in self._files(kind):
            rid = self._id_of(kind, path)
            if rid:
                used.add(int(rid.split("-")[-1]))
            try:
                fid = self.read(path).get("id")
            except Refusal:
                continue  # a broken neighbour must not block allocation; lint reports it
            m = kind.id_re.match(str(fid)) if fid else None
            if m:
                used.add(int(m.group(1)))
        return used

    # -- checks ------------------------------------------------------------------------

    def problems(self, kind: Kind, doc: okf.Document, path: Path) -> list[tuple[str, str]]:
        """Schema problems of one record, as (message, remedy) pairs. Empty means valid."""
        out = []
        if not okf.has_frontmatter(doc):
            return [("has no frontmatter", f"add frontmatter with `type: {kind.type}` and the kind's keys")]
        rtype = doc.get("type")
        if not rtype:
            out.append(("has no `type`", f"add `type: {kind.type}`"))
        elif rtype != kind.type:
            out.append((f"has type {rtype!r} in the {kind.name} series", f"set `type: {kind.type}`, or move the file"))
        rid = doc.get("id")
        if not rid or not kind.id_re.match(str(rid)):
            out.append((f"has id {rid!r}", f"set `id:` to a {kind.prefix}-n id"))
        elif self._id_of(kind, path) not in (None, rid):
            out.append((f"file name does not start with its id {rid}", f"rename the file to start with `{rid}-`"))
        for key in kind.required:
            if doc.get(key) in (None, "", []):
                out.append((f"has no `{key}`", f"set `{key}`; it is required for {kind.name} records"))
        for key, allowed in kind.enums.items():
            value = doc.get(key)
            if value is not None and str(value) not in allowed:
                out.append((f"has {key} {value!r}", f"use one of {', '.join(allowed)}"))
        for key, want in kind.types.items():
            if _wrong_type(want, doc.get(key)):
                hint = " (unquoted YYYY-MM-DD)" if want == "date" else ""
                out.append((f"has {key} {doc.get(key)!r}, not a {want}", f"set `{key}` to a {want}{hint}"))
        status = doc.get("status")
        if status is not None and status not in OKF_STATUS:
            out.append((f"has OKF status {status!r}", f"use one of {', '.join(OKF_STATUS)}; record states go in their own key"))
        return out

    def body_problem(self, kind: Kind, doc: okf.Document) -> tuple[str, str] | None:
        """G-D10: an append-only record's original body still matches its stamped hash."""
        if kind.mode != "append-only" or not okf.has_frontmatter(doc):
            return None
        stamped = doc.get("body_sha")
        if not stamped:
            return ("append-only record has no body_sha", "stamp it once its body is final (`stamp`)")
        if stamped != okf.body_sha(doc.body):
            return (
                "body above `## Amendments` changed since it was stamped",
                "restore the original text from git (`git log -p` on the file) and record the change with `amend`",
            )
        return None

    def lint(self) -> list[Failure]:
        out: list[Failure] = []
        for kind in self.config.kinds.values():
            for path in self._files(kind):
                if not self._id_of(kind, path):
                    continue
                rel = self._rel(path)
                try:
                    doc = self.read(path)
                except Refusal as r:
                    out.append(Failure("schema", rel, r.message, r.remedy))
                    continue
                out += [Failure("schema", rel, m, rem) for m, rem in self.problems(kind, doc, path)]
                bp = self.body_problem(kind, doc)
                if bp:
                    out.append(Failure("G-D10", rel, *bp))
        out += self.lint_bundles()
        return out

    def lint_bundles(self) -> list[Failure]:
        """G-D11: every non-reserved .md in a bundle directory has frontmatter with a `type`."""
        out = []
        dirs = {*self.config.bundles, *(k.dir for k in self.config.kinds.values())}
        for d in sorted(dirs):
            base = self.root / d
            if not base.is_dir():
                continue
            for path in sorted(base.rglob("*.md")):
                rel = self._rel(path)
                try:
                    doc = self.read(path)
                except Refusal as r:
                    out.append(Failure("G-D11", rel, r.message, r.remedy))
                    continue
                if path.name == "index.md":
                    extra = set(doc.data) - {"okf_version"} if okf.has_frontmatter(doc) else set()
                    if extra:
                        out.append(Failure("G-D11", rel, "index.md has frontmatter", "remove it; index.md is a plain generated listing"))
                    continue
                if path.name in RESERVED_MD:
                    continue
                if not okf.has_frontmatter(doc) or not doc.get("type"):
                    out.append(Failure("G-D11", rel, "has no `type` in an OKF bundle directory", "add frontmatter with a `type:` (e.g. `type: Readme`)"))
        return out

    # -- writing -----------------------------------------------------------------------

    def _check_caller(self, session: str, actor: str) -> None:
        if not session or not SESSION_RE.match(session):
            raise Refusal(f"session key {session!r} is not like 2026-10-08a", "pass the key `session.start` gave this session")
        if not actor or not ACTOR_RE.match(actor):
            raise Refusal(
                f"actor {actor!r} is not an OKF actor",
                "use `human:<id>`, `process:<id>` or `<producer>/<version>` (e.g. `claude-code/<model-id>`)",
            )

    def lock(self) -> FileLock:
        """The repo lock, for operations that write a non-record file (the ledger, the note)."""
        return self._lock()

    def write_text(self, path: Path, text: str) -> None:
        """Atomically replace a non-record file. Call it holding ``lock()``."""
        self._write(path, okf.Document(fm_lines=None, body="", newline="\n", raw=text))

    def log(self, op: str, rec_id: str, path: Path, session: str, actor: str, fields: list[str], mechanical: bool = False) -> None:
        self._log(op, rec_id, path, session, actor, fields, mechanical)

    def _lock(self) -> FileLock:
        path = self.root / self.config.lockfile
        ignore = path.parent / ".gitignore"
        if path.parent != self.root and not ignore.exists():
            path.parent.mkdir(parents=True, exist_ok=True)  # other processes may race us here
            ignore.write_text("*\n", encoding="utf-8")  # the lock directory is never tracked
        return FileLock(path, timeout=self.config.lock_timeout)

    def _validate(self, kind: Kind, doc: okf.Document, path: Path) -> None:
        probs = self.problems(kind, doc, path)
        if probs:
            msg, remedy = probs[0]
            more = f" (and {len(probs) - 1} more)" if len(probs) > 1 else ""
            raise Refusal(f"{self._rel(path)} {msg}{more}", remedy)

    def _write(self, path: Path, doc: okf.Document) -> None:
        data = doc.render().encode("utf-8")
        tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
        tmp.write_bytes(data)
        for attempt in range(50):  # Windows refuses a replace while a reader has the file open
            try:
                os.replace(tmp, path)
                return
            except PermissionError:
                time.sleep(0.02 * (attempt + 1))
        tmp.unlink(missing_ok=True)
        raise Refusal(f"could not replace {self._rel(path)}", "close whatever has the file open, then retry")

    def _log(self, op: str, rec_id: str, path: Path, session: str, actor: str, fields: list[str], mechanical: bool) -> None:
        entry = {
            "at": _now(),
            "session": session,
            "actor": actor,
            "op": op,
            "id": rec_id,
            "path": self._rel(path),
            "fields": fields,
            "mechanical": mechanical,
        }
        log = self.root / self.config.oplog
        log.parent.mkdir(parents=True, exist_ok=True)
        with open(log, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def new(self, kind_name: str, fields: dict[str, Any], body: str = "", *, session: str, actor: str, mechanical: bool = False) -> Record:
        """Create a record with the next free id in its series."""
        self._check_caller(session, actor)
        kind = self.config.kind(kind_name)
        clash = [k for k in TOOL_OWNED if k in fields]
        if clash:
            raise Refusal(f"`{clash[0]}` is set by the engine", f"drop `{clash[0]}` from the fields")
        with self._lock():
            used = self.ids_in_use(kind)
            rid = f"{kind.prefix}-{max(used, default=0) + 1}"
            slug = slugify(str(fields.get("title", "")))
            path = self.root / kind.dir / (f"{rid}-{slug}.md" if slug else f"{rid}.md")
            doc = okf.new_document({"type": kind.type, "id": rid, **fields}, body)
            if kind.mode == "append-only":
                doc.set("body_sha", okf.body_sha(doc.body))
            self._validate(kind, doc, path)
            path.parent.mkdir(parents=True, exist_ok=True)
            self._write(path, doc)
            self._log("new", rid, path, session, actor, list(doc.data.keys()), mechanical)
        return Record(rid, kind, path, doc)

    def set(
        self,
        record_id: str,
        changes: dict[str, Any],
        *,
        session: str,
        actor: str,
        unset: tuple[str, ...] = (),
        mechanical: bool = False,
        body: Callable[[str], str] | None = None,
        check: Callable[[Record], dict[str, Any] | None] | None = None,
        op: str = "set",
    ) -> Record:
        """Change top-level frontmatter keys, and through ``body`` the body of a non-append-only
        record. Every other byte of the file is kept. The record is re-read under the lock, so
        ``check`` (which may refuse, or return more changes) and ``body`` see the current text."""
        self._check_caller(session, actor)
        owned = [k for k in (*changes, *unset) if k in TOOL_OWNED]
        if owned:
            raise Refusal(f"`{owned[0]}` is owned by the engine", "use the operation that owns it (`stamp` for body_sha); ids and types never change")
        if not changes and not unset and body is None:
            raise Refusal("nothing to change", "pass at least one field")
        with self._lock():
            rec = self.get(record_id)
            if check is not None:
                changes = {**changes, **(check(rec) or {})}
            if body is not None:
                if rec.kind.mode == "append-only":
                    raise Refusal(f"{record_id} is append-only", "record the change with `amend`")
                rec.doc.set_body(body(rec.doc.body.replace("\r\n", "\n")))
            for key, value in changes.items():
                rec.doc.set(key, value)
            for key in unset:
                rec.doc.delete(key)
            self._validate(rec.kind, rec.doc, rec.path)
            self._write(rec.path, rec.doc)
            self._log(op, record_id, rec.path, session, actor, [*changes, *unset] + (["body"] if body else []), mechanical)
        return rec

    def stamp(self, record_id: str, *, session: str, actor: str) -> Record:
        """Record an append-only record's body hash, once."""
        self._check_caller(session, actor)
        with self._lock():
            rec = self.get(record_id)
            if rec.kind.mode != "append-only":
                raise Refusal(f"{record_id} is a {rec.kind.mode} record", "only append-only records carry body_sha")
            if rec.doc.get("body_sha"):
                raise Refusal(f"{record_id} is already stamped", "a stamp is never replaced; record changes with `amend`")
            rec.doc.set("body_sha", okf.body_sha(rec.doc.body))
            self._validate(rec.kind, rec.doc, rec.path)
            self._write(rec.path, rec.doc)
            self._log("stamp", record_id, rec.path, session, actor, ["body_sha"], False)
        return rec

    def amend(self, record_id: str, text: str, *, session: str, actor: str) -> Record:
        """Append a dated entry under ``## Amendments``: the only body change an append-only record takes."""
        self._check_caller(session, actor)
        if not text.strip():
            raise Refusal("empty amendment", "say what changed and why")
        with self._lock():
            rec = self.get(record_id)
            if rec.kind.mode != "append-only":
                raise Refusal(f"{record_id} is a {rec.kind.mode} record", "edit its body directly; `amend` is for append-only records")
            bp = self.body_problem(rec.kind, rec.doc)
            if bp and rec.doc.get("body_sha"):
                raise Refusal(f"{record_id} {bp[0]}", bp[1])
            body = rec.doc.body.rstrip("\n") + "\n"
            if not okf.AMENDMENTS_HEADING.search(body):
                body += "\n## Amendments\n"
            lines = text.strip("\n").splitlines()
            entry = f"- **{session} ({actor}):** {lines[0]}\n" + "".join(f"  {ln}\n" if ln else "\n" for ln in lines[1:])
            rec.doc.set_body(body + "\n" + entry)
            self._write(rec.path, rec.doc)
            self._log("amend", record_id, rec.path, session, actor, [], False)
        return rec
