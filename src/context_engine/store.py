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
# A caller's check of an append-only body a write is about to leave, (id, body now, body as it
# would be written), which may refuse before anything is written (CE-183: G-D3's write-time twin)
BodyCheck = Callable[[str, str, str], None]
# A record's earlier ids, kept when an import renames it to the framework's form (FRAMEWORK §8.0.1,
# §11.4): `D-27` on DEC-27, `1h` on a board item. Lookups resolve them (`Store.resolve`); every
# write and G-D2 refuse one that is not one word, is the record's own id, has the form of a
# configured series (so it is, or may become, a live id) or is another record's alias.
ALIASES = "aliases"
ALIAS_RE = re.compile(r"(?!.*::)[A-Za-z0-9!#$%&()*+\-.:;<=>?@\\^_|~]+")  # fullmatch: printable ASCII, no quote, comma, bracket, brace, `/`, `::` or space
RESERVED_MD = ("index.md", "log.md")  # OKF §3.1
RESERVE_OP = "id.reserve"  # the op log line that holds a reserved id (CE-105, CE-119; why an op: DEC-92)
# The most ids one `id reserve` hands out: a batch of linked records, not a block of the series; a
# typo of a count would otherwise burn ids for good (they are never reused). provenance: JUDGEMENT,
# CE-105, DEC-92; wrong if a real batch of linked records needs more.
RESERVE_MAX = 20


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


_ID_LINE = re.compile(r"""^id:[ \t]*(?:"([^"]*)"|'([^']*)'|([^\s#'"][^\s#]*))[ \t]*(?:#.*)?$""")


def head_id(path: Path) -> str | None:
    """The value of a record's top-level `id:` key, read line by line from its frontmatter and
    never past its closing fence, with no YAML parse (CE-88); None when it has no frontmatter,
    no such line, a value this simple reading does not take, or cannot be read."""
    try:
        with open(path, "rb") as f:
            if f.readline().rstrip(b"\r\n") != b"---":
                return None
            for raw in f:
                line = raw.decode("utf-8", errors="replace").rstrip("\r\n")
                if line == "---":
                    return None
                m = _ID_LINE.match(line)
                if m:
                    return next(g for g in m.groups() if g is not None)
    except OSError:
        return None
    return None


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
        self._wrote_actor: str | None = None  # its actor: the commit's Co-Authored-By line comes from it (CE-197)
        self.commit_title: str | None = None  # the next commit's title, when an operation names it
        self.commit_always = False  # the next commit is made whatever the policy, `off` included (a pause)
        self.commit_milestone = False  # the next commit is a milestone's (`milestone()`)
        self.commit_body = ""  # the next commit's message body, when an operation gives one (a task close's)
        self.commit_trailers: list[str] = []  # the next commit's trailers before `Session:` (a task close's `Closes:`)
        self._lead: list[str] = []  # `<op> <id>` of the lines logged since the last commit point: this operation's
        self.last_commit = commit_mod.Outcome()  # what the newest commit attempt did
        self._skip_unreadable = 0  # open skipping_unreadable() scopes (lint's, CE-161)
        self._parses: dict[Path, bool] = {}  # within them: whether a record's whole file parses (``_whole_parses``)

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
        """Parse a file. A Refusal says what does not parse but not which file: the caller names it."""
        try:
            text = path.read_bytes().decode("utf-8")
        except UnicodeDecodeError as e:
            raise Refusal(f"is not UTF-8 ({e.reason} at byte {e.start})", "save the file as UTF-8") from None
        return okf.parse(text)

    @contextmanager
    def skipping_unreadable(self) -> Iterator[None]:
        """Within it, ``heads`` and ``records`` pass over a record that does not parse, where they
        would refuse: lint runs in it, and its schema check reports that record by name (CE-161).
        "Does not parse" is the whole file's, as ``read`` parses it, not just the frontmatter
        ``heads`` reads: a guard that reads a head's body (G-W4 on an open question, G-W12 and
        G-W13 on a reviewed item) would otherwise meet a body that is not UTF-8 and raise."""
        if not self._skip_unreadable:
            self._parses = {}
        self._skip_unreadable += 1
        try:
            yield
        finally:
            self._skip_unreadable -= 1
            if not self._skip_unreadable:
                self._parses = {}

    def _whole_parses(self, path: Path) -> bool:
        """Whether ``read`` parses the file, asked once per file within ``skipping_unreadable``
        (``lint`` fills it as it reads every record)."""
        ok = self._parses.get(path)
        if ok is None:
            try:
                self.read(path)
                ok = True
            except Refusal:
                ok = False
            self._parses[path] = ok
        return ok

    def _each(self, kind_name: str, parse: Callable[[Path], okf.Document]) -> Iterator[Record]:
        """Every record of a kind, parsed by ``parse``. One that does not parse (a hand edit in
        progress, legal under G-5) is refused naming its file, or passed over within
        ``skipping_unreadable`` (CE-161)."""
        kind = self.config.kind(kind_name)
        for path in self._files(kind):
            rid = self._id_of(kind, path)
            if not rid:
                continue
            if self._skip_unreadable and not self._whole_parses(path):
                continue
            try:
                doc = parse(path)
            except Refusal as r:
                if self._skip_unreadable:
                    continue
                raise Refusal(f"{self._rel(path)} does not parse: {r.message}", f"{r.remedy}; `context-engine lint` names every such record") from None
            yield Record(rid, kind, path, doc)

    def heads(self, kind_name: str) -> Iterator[Record]:
        """Every record of a kind with its frontmatter only (``doc.body`` is empty, AC-13)."""
        return self._each(kind_name, okf.read_head)

    def records(self, kind_name: str) -> Iterator[Record]:
        return self._each(kind_name, self.read)

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
        try:
            doc = self.read(path)
        except Refusal as r:  # named, as `_each` names it (CE-161)
            raise Refusal(f"{self._rel(path)} does not parse: {r.message}", f"{r.remedy}; `context-engine lint` names every such record") from None
        return Record(record_id, self.config.kind_for_id(record_id), path, doc)

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

    def reserved_ids(self, kind: Kind | None = None) -> dict[str, str]:
        """Every id an `id.reserve` op line holds (of ``kind``'s series, or of any), with the
        session that reserved it, the first line's if two name one id (CE-105). A reserved id is
        held for good: no other write hands it out (``new`` skips it, ``create_many`` refuses it to
        every other session), and one never written stays a gap, since ids are never reused."""
        path = self.root / self.config.oplog
        if not path.is_file():
            return {}
        out: dict[str, str] = {}
        tag = f'"{RESERVE_OP}"'
        for line in path.read_bytes().decode("utf-8", errors="replace").splitlines():
            if tag not in line:  # cheap: allocation reads this under the lock (CE-88)
                continue
            try:
                op = json.loads(line)
            except ValueError:
                continue
            if isinstance(op, dict) and op.get("op") == RESERVE_OP and op.get("id"):
                rid = str(op["id"])
                if kind is None or kind.id_re.match(rid):
                    out.setdefault(rid, str(op.get("session")))
        return out

    def _numbers(self, kind: Kind, ids) -> set[int]:
        return {int(m.group(1)) for rid in ids if (m := kind.id_re.match(rid))}

    def reserve(self, kind_name: str, count: int, *, session: str, actor: str) -> list[str]:
        """Hold the next ``count`` ids of a kind's series for ``session`` (CE-105, CE-119): above
        every id a file or `id:` key holds, every id the op log shows created (`new`, `import`),
        and every id already reserved, so it is one no write has handed out or will. Under the
        lock, one `id.reserve` op line per id, naming no path (it writes no file)."""
        self._check_caller(session, actor)
        kind = self.config.kind(kind_name)
        if isinstance(count, bool) or not isinstance(count, int) or not 1 <= count <= RESERVE_MAX:
            raise Refusal(f"a count of {count!r}", f"reserve from 1 to {RESERVE_MAX} ids at a time: the ids of one batch of records that cite each other")
        with self._lock():
            taken = self.ids_in_use(kind) | self._numbers(kind, self.created_ids()) | self._numbers(kind, self.reserved_ids(kind))
            top = max(taken, default=0)
            ids = [f"{kind.prefix}-{top + i}" for i in range(1, count + 1)]
            for rid in ids:
                self._log(RESERVE_OP, rid, None, session, actor, [], False)
        return ids

    def ids_in_use(self, kind: Kind) -> set[int]:
        """Every number in the series, open and closed, from file names and from `id:` keys (G-D2).

        It runs under the engine lock on every allocation, so it reads each file only up to its
        frontmatter's top-level `id:` line and parses no YAML (CE-88: the YAML parse was 89% of
        `new`). Lint parses every record and reports a broken or odd `id:`."""
        used = set()
        for path in self._files(kind):
            rid = self._id_of(kind, path)
            if rid:
                used.add(int(rid.split("-")[-1]))
            m = kind.id_re.match(head_id(path) or "")
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

    # -- the decision listing (FRAMEWORK §6.5): printed or published, never stored (CE-185) ------

    def decision_rows(self, base: Path) -> list[decisions.Row]:
        """Every decision as the listing sees it (frontmatter only), each link relative to
        ``base``; none when `[working] decision` names no kind."""
        name = self.config.working.decision
        if not name:
            return []
        return [decisions.Row(r.id, Path(os.path.relpath(r.path, base)).as_posix(), dict(r.doc.data)) for r in self.heads(name)]

    def lint(self, unreadable_only: bool = False) -> list[Failure]:
        """The schema check of every record (and G-D10, G-D11). A record that does not parse is a
        `schema` failure naming it, the hand edit's or the tool's (CE-161); ``unreadable_only``
        reports only those, for the guards that pass over such a record (`lint --working`)."""
        out: list[Failure] = []
        for kind in self.config.kinds.values():
            for path in self._files(kind):
                if not self._id_of(kind, path):
                    continue
                rel = self._rel(path)
                try:
                    doc = self.read(path)
                except Refusal as r:
                    out.append(Failure("schema", rel, f"does not parse: {r.message}", r.remedy))
                    if self._skip_unreadable:
                        self._parses[path] = False
                    continue
                if self._skip_unreadable:
                    self._parses[path] = True
                if unreadable_only:
                    continue
                out += [Failure("schema", rel, m, rem) for m, rem in self.problems(kind, doc, path)]
                bp = self.body_problem(kind, doc)
                if bp:
                    out.append(Failure("G-D10", rel, *bp))
        return out if unreadable_only else out + self.lint_bundles()

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

    def write_bytes(self, path: Path, data: bytes) -> None:
        """Atomically replace a non-record file with ``data``, byte for byte: material that is not
        markdown, which an archive moves unchanged (`doc archive`, CE-96). Call it holding
        ``lock()``."""
        self._put(path, data)

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
        actor, self._wrote_actor = self._wrote_actor, None
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
            co = commit_mod.co_author(actor, strict=False)  # a bad CE_CO_AUTHOR cannot refuse a write already made
            self.last_commit = commit_mod.commit(self.root, self.config.oplog, session, title=title, lead=tuple(lead), body=body,
                                                 trailers=tuple(trailers), co_author=co)
        except Exception as exc:  # a commit never undoes, or hides, the write it follows
            self.last_commit = commit_mod.Outcome(note=f"the commit raised {type(exc).__name__}: {exc}; commit the op log and the paths its uncommitted lines name by hand")
        if always and not self.last_commit.sha:
            self._missed = self.last_commit

    def commit_paths(self, text: str, paths: list[str], session: str, sweep: bool = False, co_author: str | None = None) -> commit_mod.Outcome:
        """The session's own commit (`context-engine commit`): ``paths`` by path, with the op
        log lines HEAD lacks that this session's commit takes (``commit.select``; every line with
        ``sweep``) and the files they name, under the lock, whatever the policy; ``co_author`` is
        its resolved ``Co-Authored-By:`` value (``commit.co_author``), None for none. It runs no
        gate: the session runs it first."""
        with self._lock():
            try:
                return commit_mod.commit(self.root, self.config.oplog, session, text=text, paths=tuple(paths), sweep=sweep, co_author=co_author)
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
        self._put(path, doc.render().encode("utf-8"))

    def _put(self, path: Path, data: bytes) -> None:
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

    def _replace(self, path: Path, data: bytes | None) -> None:
        """Put back what a file held before a write: its bytes, or no file at all (``None``)."""
        if data is None:
            path.unlink(missing_ok=True)
            return
        tmp = path.with_name(f".{path.name}.{os.getpid()}.undo.tmp")
        tmp.write_bytes(data)
        for attempt in range(50):
            try:
                os.replace(tmp, path)
                return
            except PermissionError:
                time.sleep(0.02 * (attempt + 1))
        tmp.unlink(missing_ok=True)
        raise OSError(f"could not restore {self._rel(path)}")

    def _write_all(self, recs: list[Record], log: Callable[[Record], None]) -> None:
        """Write several records as one: if a write fails, every record this call already wrote
        is put back as it was (CE-59), so nothing is half done and a retry of the operation
        does all of it. ``log`` logs one record, once every write landed. If a write fails and a
        record cannot be put back, it stays written and is logged, so the op log never lags a file,
        and the failure is raised: the operation's own write order (the idempotent half first,
        as `record retire` writes it) then lets a retry complete it."""
        before = {r.path: (r.path.read_bytes() if r.path.exists() else None) for r in recs}
        done: list[Record] = []
        try:
            for r in recs:
                self._write(r.path, r.doc)
                done.append(r)
        except BaseException:
            stuck = []
            for r in reversed(done):
                try:
                    self._replace(r.path, before[r.path])
                except OSError:
                    stuck.append(r)
            for r in reversed(stuck):  # what could not be put back is on disk: the op log says so
                log(r)
            raise
        for r in done:
            log(r)

    def _log(self, op: str, rec_id: str, path: Path | None, session: str, actor: str, fields: list[str], mechanical: bool, as_: dict[str, str] | None = None,
             many: list[Record] | None = None) -> None:
        """One op log line. ``many``: the line stands for every record listed (CE-187: `decision
        accept` writes one line for all it accepts); it carries them in ``ids`` and ``paths``,
        the first of them in ``id``'s place is ``rec_id`` (a label) and in ``path`` the first
        record's, so a reader of ``path`` alone still finds a file (``commit.op_paths`` reads
        every one)."""
        entry: dict[str, Any] = {
            "at": _now(),
            "session": session,
            "actor": actor,
            "op": op,
            "id": rec_id,
            "path": "" if path is None else self._rel(path),  # None: the op wrote no file (`id.reserve`)
            "fields": fields,
            "mechanical": mechanical,
        }
        if as_:
            entry["as"] = dict(as_)
        if many:
            entry["ids"] = [r.id for r in many]
            entry["paths"] = [self._rel(r.path) for r in many]
        log = self.root / self.config.oplog
        log.parent.mkdir(parents=True, exist_ok=True)
        with open(log, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        self._wrote = session
        self._wrote_actor = actor
        self._lead.append(f"{op} {rec_id}")

    def _board_status(self, kind: Kind, fields: dict[str, Any], rid: str) -> dict[str, Any]:
        """The fields a board item (`[working] board`) is created with (CE-179): a closed one gets
        `status: deprecated` derived from `state: closed` (FRAMEWORK §9.3). One whose `status`
        contradicts its `state` is refused, as G-W4's write-time twin, unless `[guards] off` names
        G-W4; the derivation runs whatever `off` says. Returns a new dict, never the caller's."""
        if kind.name not in self.config.working.board:
            return fields
        closed = fields.get("state") == "closed"
        status = fields.get("status")
        if status in (None, ""):
            return {**fields, "status": "deprecated"} if closed else fields
        if closed != (status == "deprecated") and "G-W4" not in self.config.guards.off:
            raise Refusal(
                f"{rid} would be written `state: {fields.get('state')}` with `status: {status}`, which G-W4 fails",
                "a closed board item is `status: deprecated` and an open one is not: drop `status` and the engine derives it from `state`",
            )
        return fields

    def new(self, kind_name: str, fields: dict[str, Any], body: str = "", *, session: str, actor: str, mechanical: bool = False) -> Record:
        """Create a record with the next free id in its series. A board item created closed gets
        `status: deprecated`, and one whose `status` contradicts its `state` is refused (CE-179)."""
        self._check_caller(session, actor)
        kind = self.config.kind(kind_name)
        clash = [k for k in TOOL_OWNED if k in fields]
        if clash:
            raise Refusal(f"`{clash[0]}` is set by the engine", f"drop `{clash[0]}` from the fields")
        with self._lock():
            used = self.ids_in_use(kind) | self._numbers(kind, self.reserved_ids(kind))  # a reserved id is never handed out again
            rid = f"{kind.prefix}-{max(used, default=0) + 1}"
            fields = self._board_status(kind, fields, rid)
            slug = slugify(str(fields.get("title", "")))
            path = self.root / kind.dir / (f"{rid}-{slug}.md" if slug else f"{rid}.md")
            doc = okf.new_document({"type": kind.type, "id": rid, **fields}, body)
            if kind.mode == "append-only":
                doc.set("body_sha", okf.body_sha(doc.body))
            self._validate(kind, doc, path, aliases=True)
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
        as_: dict[str, str] | None = None,
    ) -> Record:
        """Change top-level frontmatter keys, and through ``body`` the body of a non-append-only
        record. Every other byte of the file is kept. The record is re-read under the lock, so
        ``check`` (which may refuse, or return more changes) and ``body`` see the current text.
        ``as_`` maps a session-keyed field to the session key it was set to when that is not the
        writer's (housekeeping stamping `last_asked` from a ledger receipt, CE-6): the op line
        carries it as ``as``, and G-W7 checks the field against it."""
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
            self._log(op, record_id, rec.path, session, actor, [*changes, *unset] + (["body"] if body else []), mechanical, as_)
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
        return rec

    def amend(self, record_id: str, text: str, *, session: str, actor: str, check: BodyCheck | None = None) -> Record:
        """Append a dated entry under ``## Amendments``: the only body change an append-only record
        takes. ``check(id, body now, body as written)`` may refuse it before anything is written."""
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
            before = rec.doc.body
            rec.doc.set_body(amended(before, text, session, actor))
            if check:
                check(record_id, before, rec.doc.body)
            self._write(rec.path, rec.doc)
            self._log("amend", record_id, rec.path, session, actor, [], False)
        return rec

    def correct(self, record_id: str, after: str, text: str, *, session: str, actor: str, check: BodyCheck | None = None) -> tuple[Record, str]:
        """Insert ``[text]`` after the one place ``after`` occurs in the original body and log a
        ``corrected:`` amendment (DEC-13). Insert-only: undoing the logged insertions gives back
        the words as typed (``okf.strip_corrections``), which ``body_sha`` still pins, so the
        stamp is never replaced (G-D10). ``check`` as for ``amend``."""
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
            before = rec.doc.body
            rec.doc.set_body(amended(body, okf.correction_entry(pos, inserted, after), session, actor))
            if check:
                check(record_id, before, rec.doc.body)
            self._validate(rec.kind, rec.doc, rec.path)
            self._write(rec.path, rec.doc)
            self._log("correct", record_id, rec.path, session, actor, ["body"], False)
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
        one_line: str = "",
        check: BodyCheck | None = None,
    ) -> dict[str, Record]:
        """Change the frontmatter of several records as one write: under one lock, every record
        is re-read, changed by ``mutate`` (which may refuse, and returns id -> changed keys), and
        validated before any of them is written. ``mutate`` never changes a body; ``amend`` (id ->
        text) appends a dated entry under ``## Amendments`` of an append-only record in the same
        write, checked as ``amend`` checks it, so the change and its reason land together.
        ``one_line``: log the whole write as one op line with that label as its ``id`` and every
        record changed in ``ids`` and ``paths`` (``_log``'s ``many``; the changed keys must be the
        same for each), instead of one line per record. ``check`` is called on each amended body as
        ``amend`` calls it, before anything is written."""
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
                if check:
                    check(i, bodies[i], r.doc.body)
            for i, r in recs.items():
                owned = [k for k in changed.get(i, ()) if k in TOOL_OWNED]
                if owned:
                    raise Refusal(f"`{owned[0]}` is owned by the engine", "ids, types and body_sha never change this way")
                self._validate(r.kind, r.doc, r.path)
            todo = [(i, r) for i, r in recs.items() if changed.get(i) or i in amend]
            fields = {i: list(changed.get(i) or ()) + (["body"] if i in amend else []) for i, _ in todo}
            if one_line and todo:
                written = [r for _, r in todo]
                keys = list(dict.fromkeys(k for i, _ in todo for k in fields[i]))
                logged: list[bool] = []

                def once(r: Record) -> None:  # `_write_all` logs per record; this line stands for all of them
                    if not logged:
                        logged.append(True)
                        self._log(op, one_line, written[0].path, session, actor, keys, False, many=written)

                self._write_all(written, once)
            else:
                self._write_all([r for _, r in todo], lambda r: self._log(op, r.id, r.path, session, actor, fields[r.id], False))
        return recs

    def create_many(self, kind_name: str, items: list[tuple[str, dict[str, Any], str]], *, session: str, actor: str, op: str) -> list[Record]:
        """Write several new records with ids the caller chose (an import keeps every id), all or
        nothing: each id must be free and each record valid before any file is written. An id
        another session reserved (`id reserve`) is not free; one this session reserved is. Each
        item is (id, fields, body); append-only records are stamped when they are created. A board
        item (`[working] board`) closed at creation gets `status: deprecated` (FRAMEWORK §9.3, G-W4),
        and one whose `status` contradicts its `state` is refused (CE-179)."""
        self._check_caller(session, actor)
        kind = self.config.kind(kind_name)
        out: list[Record] = []
        with self._lock():
            used = self.ids_in_use(kind)
            amap = self.alias_map() if any(f.get(ALIASES) for _, f, _ in items) else {}
            created = self.created_ids()
            reserved = self.reserved_ids(kind)
            for rid, fields, body in items:
                m = kind.id_re.fullmatch(rid)
                if not m or int(m.group(1)) < 1 or rid != f"{kind.prefix}-{int(m.group(1))}":
                    want = f"{kind.prefix}-{int(m.group(1))}" if m and int(m.group(1)) >= 1 else f"{kind.prefix}-n, n from 1"
                    raise Refusal(f"{rid} is not an id of the {kind.name} series as the engine writes it", f"give {want}: no leading zeros")
                if int(m.group(1)) in used or rid in created:
                    raise Refusal(f"{rid} is already in use" + (" (the op log shows it was created before)" if int(m.group(1)) not in used else ""), "an id is never reused (G-D2)")
                if reserved.get(rid, session) != session:
                    raise Refusal(f"{rid} is reserved by session {reserved[rid]}", "use an id this session reserved (`id reserve`), or none for the next free one: a reserved id is its session's alone")
                clash = [k for k in TOOL_OWNED if k in fields]
                if clash:
                    raise Refusal(f"`{clash[0]}` is set by the engine", f"drop `{clash[0]}` from the fields")
                fields = self._board_status(kind, fields, rid)
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
            self._write_all(out, lambda r: self._log(op, r.id, r.path, session, actor, list(r.doc.data.keys()), False))
        return out


def amended(body: str, text: str, session: str, actor: str) -> str:
    """``body`` with one dated entry appended under ``## Amendments`` (added if absent)."""
    body = body.replace("\r\n", "\n").rstrip("\n") + "\n"
    if not okf.AMENDMENTS_HEADING.search(body):
        body += "\n## Amendments\n"
    lines = text.strip("\n").splitlines()
    entry = f"- **{session} ({actor}):** {lines[0]}\n" + "".join(f"  {ln}\n" if ln else "\n" for ln in lines[1:])
    return body + "\n" + entry
