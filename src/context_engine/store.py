"""The record store: find records, allocate ids, write under a lock, log every operation.

Every write is one operation: it takes the repo lock, re-reads the record inside it (so two
writers never lose each other's change, AC-9), checks the result against the kind's schema
before any byte is written (AC-5), writes atomically, and appends one line to the operation log
carrying the session key and the actor (AC-6). Before the lock is let go, the write may be
committed by path with its op log lines (``commit.commit``, FRAMEWORK §5.5 rule 4). ``[engine]
commit`` says when: at a milestone (an operation marks itself one with ``milestone()``), after
every write, or never but a pause, which is committed regardless (``commit_always``). A write
not committed stays uncommitted and goes into the next commit, which carries every op log line
HEAD lacks.
Inside ``batch()`` the commit waits for the batch's end, so one operation that writes several
times commits once, and the lock is held across all of it.

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
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterator

from . import commit as commit_mod
from . import config as config_mod
from . import decisions
from . import okf
from .config import Config, Kind
from .errors import Refusal
from .lock import FileLock

SESSION_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[a-z]+$")
ACTOR_RE = re.compile(r"^(human:\S+|process:\S+|[A-Za-z0-9._-]+/[A-Za-z0-9._:+-]+)$")  # OKF §7
OKF_STATUS = ("draft", "stable", "deprecated")  # OKF §5.4
TOOL_OWNED = ("type", "id", "body_sha")
# A record's earlier ids, kept when an import renames it to the framework's form (FRAMEWORK §8.0.1,
# §11.4): `D-27` on DEC-27, `1h` on a board item. Lookups resolve them (`Store.resolve`); every
# write and G-D2 refuse one that is not one word, is the record's own id, has the form of a
# configured series (so it is, or may become, a live id) or is another record's alias.
ALIASES = "aliases"
ALIAS_RE = re.compile(r"(?!.*::)[A-Za-z0-9!#$%&()*+\-.:;<=>?@\\^_|~]+")  # fullmatch: printable ASCII, no quote, comma, bracket, brace, `/`, `::` or space
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
    want = kind.types.get(key, "list" if key == ALIASES else "str")
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
        self._batch = 0  # open batch() scopes; the commit waits for the outermost
        self._held = False  # this Store holds the file lock (batch() holds it across an operation)
        self._missed: commit_mod.Outcome | None = None  # a pause commit that did not happen
        self._wrote: str | None = None  # the session of a write not yet committed
        self.commit_title: str | None = None  # the next commit's title, when an operation names it
        self.commit_always = False  # the next commit is made whatever the policy, `off` included (a pause)
        self.commit_milestone = False  # the next commit is a milestone's (`milestone()`)
        self.commit_body = ""  # the next commit's message body, when an operation gives one (a task close's)
        self.commit_trailers: list[str] = []  # the next commit's trailers before `Session:` (a task close's `Closes:`)
        self._lead: list[str] = []  # `<op> <id>` of the lines logged since the last commit point: this operation's
        self.last_commit = commit_mod.Outcome()  # what the newest commit attempt did

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

    # -- aliases: a record's earlier ids (FRAMEWORK §8.0.1) ------------------------------

    def alias_map(self) -> dict[str, list[str]]:
        """Every alias, with the ids of the records carrying it, over every kind (frontmatter only)."""
        out: dict[str, list[str]] = {}
        for kind in self.config.kinds.values():
            for path in self._files(kind):
                rid = self._id_of(kind, path)
                if not rid:
                    continue
                try:
                    value = okf.read_head(path).get(ALIASES)
                except Exception:
                    continue  # the schema check reports an unreadable record
                for a in decisions.as_list(value):
                    out.setdefault(a, []).append(rid)
        return out

    def series_of(self, ref: str) -> Kind | None:
        return next((k for k in self.config.kinds.values() if k.id_re.fullmatch(ref)), None)

    def _like_a_series(self, ref: str) -> str | None:
        """What ``ref`` would be mistaken for: a configured series' id in any case or padding
        (`dec-3`, `CE-007`), or an id of the criteria file's series (`AC-7`, also before the row
        exists). None when it is none of these."""
        m = re.fullmatch(r"([A-Za-z]+)-0*(\d+)", ref)
        if not m:
            return None
        head = m.group(1).upper()
        kind = next((k for k in self.config.kinds.values() if k.prefix.upper() == head), None)
        if kind is not None:
            return f"an id of the {kind.name} series ({kind.prefix}-n)"
        if head in self._criterion_prefixes():
            return f"a criterion id ({head}-n, `[working] criteria`)"
        return None

    def _criterion_prefixes(self) -> set[str]:
        rel = self.config.working.criteria
        path = self.root / rel if rel else None
        if path is None or not path.is_file():
            return set()
        text = path.read_bytes().decode("utf-8", errors="replace")
        return {p.upper() for p in re.findall(r"^\|\s*([A-Za-z]+)-\d+\s*\|", text, re.MULTILINE)}

    def resolve(self, ref: str, strict: bool = True) -> tuple[str, str | None]:
        """``ref`` as given when it has a configured series' form, else the id of the one record
        that carries it as an alias: (id, the alias it was given as, or None). Not strict: a
        ref that is neither comes back as given (a criterion id, a `file::symbol`)."""
        ref = ref.strip()
        if self.series_of(ref) is not None:
            return ref, None
        owners = self.alias_map().get(ref, [])
        if len(owners) == 1:
            return owners[0], ref
        if len(owners) > 1:
            raise Refusal(f"{ref} is an alias of {len(owners)} records ({', '.join(owners)})", "an alias names one record: drop it from all but one (lint G-D2 lists them)")
        if strict:
            series = ", ".join(k.prefix + "-n" for k in self.config.kinds.values())
            raise Refusal(f"no record {ref}: it is not an id of a configured series ({series}) and no record carries it in `{ALIASES}`", "use the record's id, or record the old id in that record's `aliases`")
        return ref, None

    def alias_problems(self, rid: str, value: Any, amap: dict[str, list[str]]) -> list[tuple[str, str]]:
        """What is wrong with record ``rid`` carrying ``value`` as its aliases, as (message,
        remedy) pairs; ``amap`` is ``alias_map()``. A value that is not a list is the schema
        check's (``problems``)."""
        if not isinstance(value, list):
            return []
        out = []
        drop = f"drop it from `{ALIASES}`"
        folded: dict[str, set[str]] = {}
        for alias, owners in amap.items():
            folded.setdefault(alias.casefold(), set()).update(owners)
        seen: set[str] = set()
        for a in value:
            like = self._like_a_series(a) if isinstance(a, str) else None
            if not isinstance(a, str) or not ALIAS_RE.fullmatch(a):
                out.append((f"has alias {a!r}, which is not one word of printable ASCII (no quotes, commas, brackets, `/` or `::`)", f"an alias is an earlier id, e.g. D-27 or 1h; {drop}"))
            elif a.casefold() == rid.casefold():
                out.append((f"lists its own id {a} as an alias", drop))
            elif like:
                out.append((f"has alias {a}, which reads as {like}, so it is or may become a live id", f"{drop}; an id of a configured series or of the criteria is never an alias"))
            elif a.casefold() in seen:
                out.append((f"lists alias {a} twice (case aside)", "list it once"))
            elif folded.get(a.casefold(), set()) - {rid}:
                others = sorted(folded[a.casefold()] - {rid})
                out.append((f"has alias {a}, which {', '.join(others)} also carries (case aside)", "an alias names one record: drop it from all but one"))
            if isinstance(a, str):
                seen.add(a.casefold())
        return out

    def created_ids(self) -> set[str]:
        """Every id the op log shows created (`new` or `import`), the set G-D2's reuse check reads:
        a chosen id (an import's, `task new --id`) must not be one, even if its file is gone."""
        path = self.root / self.config.oplog
        if not path.is_file():
            return set()
        out = set()
        for line in path.read_bytes().decode("utf-8", errors="replace").splitlines():
            try:
                op = json.loads(line)
            except ValueError:
                continue
            if isinstance(op, dict) and op.get("op") in ("new", "import") and op.get("id"):
                out.add(str(op["id"]))
        return out

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
        aliases = doc.get(ALIASES)
        if aliases is not None and (not isinstance(aliases, list) or not all(isinstance(a, str) for a in aliases)):
            out.append((f"has {ALIASES} {aliases!r}, not a list of ids", f"set `{ALIASES}` to a list, e.g. [D-27]"))
        status = doc.get("status")
        if status is not None and status not in OKF_STATUS:
            out.append((f"has OKF status {status!r}", f"use one of {', '.join(OKF_STATUS)}; record states go in their own key"))
        return out

    def body_problem(self, kind: Kind, doc: okf.Document) -> tuple[str, str] | None:
        """G-D10: an append-only record's words as typed still match its stamp. ``body_sha`` is
        never replaced, and it hashes the body above ``## Amendments`` with every logged
        correction undone, so dropping a `corrected:` line cannot pass a bracket off as typed.

        Not checked: the text under ``## Amendments`` other than its `corrected:` lines (an
        edited or deleted ordinary amendment passes), a
        record of a kind that is not append-only, and a file with no frontmatter (G-D11 reports
        that)."""
        if kind.mode != "append-only" or not okf.has_frontmatter(doc):
            return None
        stamped = doc.get("body_sha")
        if not stamped:
            return ("append-only record has no body_sha", "stamp it once its body is final (`context-engine record stamp`)")
        try:
            typed = okf.typed_sha(doc.body)
        except ValueError as exc:
            return (
                f"a `corrected:` line under ## Amendments does not match the body: {exc}",
                "restore the file from git (`git log -p` on it); a correction is made only with `context-engine record correct`",
            )
        if stamped != typed:
            return (
                "body above `## Amendments` changed since it was stamped (with logged corrections undone, it no longer matches the words as typed)",
                "restore the original text from git (`git log -p` on the file); record a change with `context-engine record amend`, a fix with `context-engine record correct`",
            )
        return None

    # -- the generated decision index (G-D6) --------------------------------------------

    def derived(self) -> dict[str, tuple[str, ...]]:
        """Each file the engine generates from records, with the directories of its sources (the
        decision index, from the decisions): a commit that carries one carries their lines too
        (``commit.select``, CE-125)."""
        ik = self._index_kind()
        return {self.config.working.decision_index: (ik.dir,)} if ik is not None else {}

    def _index_kind(self) -> Kind | None:
        w = self.config.working
        return self.config.kind(w.decision) if w.decision_index and w.decision else None

    def render_index(self) -> str | None:
        """The decision index as a regeneration would write it; None when none is configured."""
        kind = self._index_kind()
        if kind is None:
            return None
        base = (self.root / self.config.working.decision_index).parent
        rows = [decisions.Row(r.id, Path(os.path.relpath(r.path, base)).as_posix(), dict(r.doc.data)) for r in self.heads(kind.name)]
        return decisions.render_index(rows, kind.enums.get(decisions.STATUS_KEY, ()))

    def _reindex(self, kind: Kind, session: str, actor: str) -> None:
        """Holding the lock, after a write to ``kind``: rewrite the index if it changed."""
        ik = self._index_kind()
        if ik is None or kind.name != ik.name:
            return
        try:
            text = self.render_index()
        except Refusal:
            return  # a broken neighbour must not block the write; lint reports both
        path = self.root / self.config.working.decision_index
        if path.exists() and path.read_bytes().decode("utf-8").replace("\r\n", "\n") == text:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        self.write_text(path, text)
        self._log("index", "index", path, session, actor, ["index"], True)

    def reindex(self, *, session: str, actor: str) -> bool:
        """Regenerate the decision index (`hk.regen_index`); True if it changed."""
        self._check_caller(session, actor)
        kind = self._index_kind()
        if kind is None:
            raise Refusal("[working] has no `decision_index`", "set `decision_index = \"docs/decisions/index.md\"` in [working] of context.toml")
        path = self.root / self.config.working.decision_index
        with self._lock():
            before = path.read_bytes() if path.exists() else None
            self._reindex(kind, session, actor)
            return before != path.read_bytes()

    def lint_index(self) -> list[Failure]:
        """G-D6: the generated index equals a regeneration from the records' frontmatter."""
        try:
            text = self.render_index()
        except Refusal:
            return []  # the schema check reports the broken record
        if text is None:
            return []
        rel = self.config.working.decision_index
        path = self.root / rel
        remedy = "regenerate it with `context-engine decision index`; never edit it by hand"
        if not path.exists():
            kind = self._index_kind()
            return [Failure("G-D6", rel, "the decision index is missing", remedy)] if any(True for _ in self.heads(kind.name)) else []
        if path.read_bytes().decode("utf-8").replace("\r\n", "\n") != text:
            return [Failure("G-D6", rel, "is not what the decisions' frontmatter generates", remedy)]
        return []

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
        out += self.lint_index()
        return out

    def lint_bundles(self) -> list[Failure]:
        """G-D11: every non-reserved .md in a bundle directory has frontmatter with a `type`, and
        no `index.md` carries frontmatter other than `okf_version`.

        Not checked: an `index.md`'s list shape; whether `okf_version` sits only at the bundle
        root; the other reserved files (`log.md`); a configured directory that does not exist
        (skipped); and whether `status` agrees with the record's own state key (G-W4)."""
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

    def lock(self):
        """The repo lock, for operations that write a non-record file (the ledger, the orientation note)."""
        return self._lock()

    def write_text(self, path: Path, text: str) -> None:
        """Atomically replace a non-record file. Call it holding ``lock()``."""
        self._write(path, okf.Document(fm_lines=None, body="", newline="\n", raw=text))

    def log(self, op: str, rec_id: str, path: Path, session: str, actor: str, fields: list[str], mechanical: bool = False) -> None:
        self._log(op, rec_id, path, session, actor, fields, mechanical)

    def _file_lock(self) -> FileLock:
        path = self.root / self.config.lockfile
        ignore = path.parent / ".gitignore"
        if path.parent != self.root and not ignore.exists():
            path.parent.mkdir(parents=True, exist_ok=True)  # other processes may race us here
            ignore.write_text("*\n", encoding="utf-8")  # the lock directory is never tracked
        return FileLock(path, timeout=self.config.lock_timeout)

    @contextmanager
    def _lock(self) -> Iterator[None]:
        """The repo lock. A write made under it is committed before the lock is let go, unless a
        batch is open. It commits after a refusal too: what reached disk is in the op log, and
        the op log at HEAD must not lag the files it names. Re-entrant within this Store, so a
        batch can hold it across all of an operation's writes."""
        if self._held:
            yield
            return
        with self._file_lock():
            self._held = True
            try:
                yield
            finally:
                try:
                    if self._batch == 0:
                        self._commit()
                finally:
                    self._held = False

    @contextmanager
    def batch(self) -> Iterator[None]:
        """One commit for every write inside, made when the outermost batch ends. The lock is
        held from the batch's start to that commit, so no other session's write lands between
        this operation's writes. When the outermost batch ends without an exception and a
        pause's commit (``commit_always``) did not happen, it refuses: the record stays, and the
        refusal says how to commit it by hand. Before the engine committed every write, a pause
        refused the same way."""
        if self._batch:
            self._batch += 1
            try:
                yield
            finally:
                self._batch -= 1
            return
        with self._lock():
            self._batch = 1
            try:
                yield
            finally:
                self._batch = 0
        missed, self._missed = self._missed, None
        if missed is not None:
            r = Refusal(
                f"the pause record was written but not committed ({missed.note or 'git made no commit'})",
                "commit it at once, when git allows: `context-engine commit -m \"pause <id>: ...\"` carries it with the op log and every path its lines name (by hand: manual-mode.md § context-engine pause open, step 3); a pause left uncommitted in a shared tree can be lost",
            )
            r.reports_commit = True  # `Op.call` adds nothing: the refusal is about the commit
            raise r

    @contextmanager
    def milestone(self) -> Iterator[None]:
        """An operation that is a milestone (FRAMEWORK §5.5 rule 4): its writes run in one batch,
        and under the `milestones` policy the batch's end commits them, with every op log line
        HEAD lacks. Marked at the start, so a milestone refused after a write still commits what
        it wrote, as every write did under CE-45; what the commit message adds only on success
        (a close's `Closes:`) the operation sets after its last write."""
        with self.batch():
            self.commit_milestone = True
            yield

    def _commit(self) -> None:
        """Holding the lock: commit what the writes since the last commit put in the op log, if
        the policy says now. Every one-shot setting is spent here, committed or not."""
        session, self._wrote = self._wrote, None
        title, self.commit_title = self.commit_title, None
        always, self.commit_always = self.commit_always, False
        milestone, self.commit_milestone = self.commit_milestone, False
        body, self.commit_body = self.commit_body, ""
        trailers, self.commit_trailers = self.commit_trailers, []
        lead, self._lead = self._lead, []
        if not session:
            return
        policy = self.config.commit
        if not (always or policy == "every-write" or (milestone and policy == "milestones")):
            self.last_commit = commit_mod.Outcome()
            return
        try:
            self.last_commit = commit_mod.commit(self.root, self.config.oplog, session, title=title, lead=tuple(lead), body=body, trailers=tuple(trailers), derived=self.derived())
        except Exception as exc:  # a commit never undoes, or hides, the write it follows
            self.last_commit = commit_mod.Outcome(note=f"the commit raised {type(exc).__name__}: {exc}; commit the op log and the paths its uncommitted lines name by hand")
        if always and not self.last_commit.sha:
            self._missed = self.last_commit

    def commit_paths(self, text: str, paths: list[str], session: str, sweep: bool = False) -> commit_mod.Outcome:
        """The session's own commit (`context-engine commit`): ``paths`` by path, with the op
        log lines HEAD lacks that this session's commit takes (``commit.select``; every line with
        ``sweep``) and the files they name, under the lock, whatever the policy. It runs no gate:
        the session runs it first."""
        with self._lock():
            try:
                return commit_mod.commit(self.root, self.config.oplog, session, text=text, paths=tuple(paths), sweep=sweep, derived=self.derived())
            except Exception as exc:
                return commit_mod.Outcome(note=f"the commit raised {type(exc).__name__}: {exc}")

    def _validate(self, kind: Kind, doc: okf.Document, path: Path, amap: dict[str, list[str]] | None = None, aliases: bool = False) -> None:
        """Refuse a record that breaks its kind's schema; with ``aliases`` (a write that sets
        them), also one whose aliases break G-D2's rule. A write that leaves the aliases alone is
        not refused for a clash someone else made: lint G-D2 reports that one."""
        probs = self.problems(kind, doc, path)
        if not probs and aliases and doc.get(ALIASES):
            probs = self.alias_problems(str(doc.get("id")), doc.get(ALIASES), self.alias_map() if amap is None else amap)
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
        self._wrote = session
        self._lead.append(f"{op} {rec_id}")

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
            self._validate(kind, doc, path, aliases=True)
            path.parent.mkdir(parents=True, exist_ok=True)
            self._write(path, doc)
            self._log("new", rid, path, session, actor, list(doc.data.keys()), mechanical)
            self._reindex(kind, session, actor)
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
            raise Refusal(f"`{owned[0]}` is owned by the engine", "use the operation that owns it (`context-engine record stamp` for body_sha); ids and types never change")
        if not changes and not unset and body is None:
            raise Refusal("nothing to change", "pass at least one field")
        with self._lock():
            rec = self.get(record_id)
            if check is not None:
                changes = {**changes, **(check(rec) or {})}
            if body is not None:
                if rec.kind.mode == "append-only":
                    raise Refusal(f"{record_id} is append-only", "record the change with `context-engine record amend`")
                rec.doc.set_body(body(rec.doc.body.replace("\r\n", "\n")))
            for key, value in changes.items():
                rec.doc.set(key, value)
            for key in unset:
                rec.doc.delete(key)
            self._validate(rec.kind, rec.doc, rec.path, aliases=ALIASES in changes)
            self._write(rec.path, rec.doc)
            self._log(op, record_id, rec.path, session, actor, [*changes, *unset] + (["body"] if body else []), mechanical)
            self._reindex(rec.kind, session, actor)
        return rec

    def stamp(self, record_id: str, *, session: str, actor: str) -> Record:
        """Record an append-only record's body hash, once."""
        self._check_caller(session, actor)
        with self._lock():
            rec = self.get(record_id)
            if rec.kind.mode != "append-only":
                raise Refusal(f"{record_id} is a {rec.kind.mode} record", "only append-only records carry body_sha")
            if rec.doc.get("body_sha"):
                raise Refusal(f"{record_id} is already stamped", "a stamp is never replaced; record changes with `context-engine record amend`")
            rec.doc.set("body_sha", okf.body_sha(rec.doc.body))
            self._validate(rec.kind, rec.doc, rec.path)
            self._write(rec.path, rec.doc)
            self._log("stamp", record_id, rec.path, session, actor, ["body_sha"], False)
            self._reindex(rec.kind, session, actor)
        return rec

    def amend(self, record_id: str, text: str, *, session: str, actor: str) -> Record:
        """Append a dated entry under ``## Amendments``: the only body change an append-only record takes."""
        self._check_caller(session, actor)
        if not text.strip():
            raise Refusal("empty amendment", "say what changed and why")
        with self._lock():
            rec = self.get(record_id)
            if rec.kind.mode != "append-only":
                raise Refusal(f"{record_id} is a {rec.kind.mode} record", "edit its body directly; `context-engine record amend` is for append-only records")
            bp = self.body_problem(rec.kind, rec.doc)
            if bp and rec.doc.get("body_sha"):
                raise Refusal(f"{record_id} {bp[0]}", bp[1])
            rec.doc.set_body(amended(rec.doc.body, text, session, actor))
            self._write(rec.path, rec.doc)
            self._log("amend", record_id, rec.path, session, actor, [], False)
            self._reindex(rec.kind, session, actor)
        return rec

    def correct(self, record_id: str, after: str, text: str, *, session: str, actor: str) -> tuple[Record, str]:
        """Insert ``[text]`` after the one place ``after`` occurs in the original body and log a
        ``corrected:`` amendment (DEC-13). Insert-only: undoing the logged insertions gives back
        the words as typed (``okf.strip_corrections``), which ``body_sha`` still pins, so the
        stamp is never replaced (G-D10)."""
        self._check_caller(session, actor)
        if not after:
            raise Refusal("no anchor", "give the words the insertion goes right after")
        if not text.strip():
            raise Refusal("an empty correction", "give the text to insert; it is written as `[text]`")
        if any(c in after + text for c in "\r\n"):
            raise Refusal("a correction and its anchor are each one line", "correct one place at a time; a change of meaning is `record amend`")
        with self._lock():
            rec = self.get(record_id)
            if rec.kind.mode != "append-only":
                raise Refusal(f"{record_id} is a {rec.kind.mode} record", "edit its body directly; `record correct` is for append-only records")
            if not rec.doc.get("body_sha"):
                raise Refusal(f"{record_id} is not stamped yet", "its text is not final, so edit it directly, then `context-engine record stamp`")
            bp = self.body_problem(rec.kind, rec.doc)
            if bp:
                raise Refusal(f"{record_id} {bp[0]}", bp[1])
            body, pos, inserted = okf.insert_correction(rec.doc.body, after, text)
            rec.doc.set_body(amended(body, okf.correction_entry(pos, inserted, after), session, actor))
            self._validate(rec.kind, rec.doc, rec.path)
            self._write(rec.path, rec.doc)
            self._log("correct", record_id, rec.path, session, actor, ["body"], False)
            self._reindex(rec.kind, session, actor)
        return rec, inserted

    def update(
        self,
        ids: list[str],
        mutate: Callable[[dict[str, Record]], dict[str, list[str]]],
        *,
        session: str,
        actor: str,
        op: str,
        amend: dict[str, str] | None = None,
    ) -> dict[str, Record]:
        """Change the frontmatter of several records as one write: under one lock, every record
        is re-read, changed by ``mutate`` (which may refuse, and returns id -> changed keys), and
        validated before any of them is written. ``mutate`` never changes a body; ``amend`` (id ->
        text) appends a dated entry under ``## Amendments`` of an append-only record in the same
        write, checked as ``amend`` checks it, so the change and its reason land together."""
        self._check_caller(session, actor)
        amend = amend or {}
        with self._lock():
            recs = {i: self.get(i) for i in dict.fromkeys([*ids, *amend])}
            bodies = {i: r.doc.body for i, r in recs.items()}
            changed = mutate(recs)
            for i, r in recs.items():
                if r.doc.body != bodies[i]:
                    raise Refusal(f"an update tried to change the body of {i}", "bodies change only through their own operations")
            for i, text in amend.items():
                r = recs[i]
                if r.kind.mode != "append-only":
                    raise Refusal(f"{i} is a {r.kind.mode} record", "only append-only records take amendments")
                if not text.strip():
                    raise Refusal("empty amendment", "say what changed and why")
                bp = self.body_problem(r.kind, r.doc)
                if bp and r.doc.get("body_sha"):
                    raise Refusal(f"{i} {bp[0]}", bp[1])
                r.doc.set_body(amended(r.doc.body, text, session, actor))
            for i, r in recs.items():
                owned = [k for k in changed.get(i, ()) if k in TOOL_OWNED]
                if owned:
                    raise Refusal(f"`{owned[0]}` is owned by the engine", "ids, types and body_sha never change this way")
                self._validate(r.kind, r.doc, r.path)
            for i, r in recs.items():
                if changed.get(i) or i in amend:
                    self._write(r.path, r.doc)
                    self._log(op, i, r.path, session, actor, list(changed.get(i) or ()) + (["body"] if i in amend else []), False)
            for kind in {r.kind.name: r.kind for r in recs.values()}.values():
                self._reindex(kind, session, actor)
        return recs

    def create_many(self, kind_name: str, items: list[tuple[str, dict[str, Any], str]], *, session: str, actor: str, op: str) -> list[Record]:
        """Write several new records with ids the caller chose (an import keeps every id), all or
        nothing: each id must be free and each record valid before any file is written. Each
        item is (id, fields, body); append-only records are stamped when they are created."""
        self._check_caller(session, actor)
        kind = self.config.kind(kind_name)
        out: list[Record] = []
        with self._lock():
            used = self.ids_in_use(kind)
            amap = self.alias_map() if any(f.get(ALIASES) for _, f, _ in items) else {}
            created = self.created_ids()
            for rid, fields, body in items:
                m = kind.id_re.fullmatch(rid)
                if not m or int(m.group(1)) < 1 or rid != f"{kind.prefix}-{int(m.group(1))}":
                    want = f"{kind.prefix}-{int(m.group(1))}" if m and int(m.group(1)) >= 1 else f"{kind.prefix}-n, n from 1"
                    raise Refusal(f"{rid} is not an id of the {kind.name} series as the engine writes it", f"give {want}: no leading zeros")
                if int(m.group(1)) in used or rid in created:
                    raise Refusal(f"{rid} is already in use" + (" (the op log shows it was created before)" if int(m.group(1)) not in used else ""), "an id is never reused (G-D2)")
                clash = [k for k in TOOL_OWNED if k in fields]
                if clash:
                    raise Refusal(f"`{clash[0]}` is set by the engine", f"drop `{clash[0]}` from the fields")
                slug = slugify(str(fields.get("title", "")))
                path = self.root / kind.dir / (f"{rid}-{slug}.md" if slug else f"{rid}.md")
                doc = okf.new_document({"type": kind.type, "id": rid, **fields}, body)
                if kind.mode == "append-only":
                    doc.set("body_sha", okf.body_sha(doc.body))
                self._validate(kind, doc, path, amap, aliases=True)
                if path.exists():
                    raise Refusal(f"{self._rel(path)} already exists", "move it aside, then retry")
                for a in decisions.as_list(doc.get(ALIASES)):
                    amap.setdefault(a, []).append(rid)  # so two records of one import cannot share an alias
                out.append(Record(rid, kind, path, doc))
            if len({r.path for r in out}) != len(out) or len({r.id for r in out}) != len(out):
                raise Refusal("two of the records share an id or a file name", "give each its own id and title")
            for r in out:
                r.path.parent.mkdir(parents=True, exist_ok=True)
                self._write(r.path, r.doc)
                self._log(op, r.id, r.path, session, actor, list(r.doc.data.keys()), False)
            self._reindex(kind, session, actor)
        return out


def amended(body: str, text: str, session: str, actor: str) -> str:
    """``body`` with one dated entry appended under ``## Amendments`` (added if absent)."""
    body = body.replace("\r\n", "\n").rstrip("\n") + "\n"
    if not okf.AMENDMENTS_HEADING.search(body):
        body += "\n## Amendments\n"
    lines = text.strip("\n").splitlines()
    entry = f"- **{session} ({actor}):** {lines[0]}\n" + "".join(f"  {ln}\n" if ln else "\n" for ln in lines[1:])
    return body + "\n" + entry
