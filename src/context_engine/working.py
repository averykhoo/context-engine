"""Working-state operations: sessions, the board, owner questions, batons, pauses, the banner,
``orient()`` and the working-state guards (FRAMEWORK §5, §6.1, §6.3, §6.4, §8.4).

Every operation here is one function that the CLI and the MCP server call. Each
write goes through the store, so it is checked against its kind's schema, made under the repo
lock and logged with the session key and the actor. Every write returns one line.

Which kinds play which part is configured in ``[working]`` of ``context.toml``; an operation
whose part is not configured refuses and says so.

Deliberately not handled here: the G-W11 guard itself (a stale stub is abandoned by
``session_abandon``, CE-124, which housekeeping runs), rotating the ledger, and the `hk_` operations other than baton
expiry and regenerating the decision index (CE-6).
"""

from __future__ import annotations

import datetime as dt
import collections
import functools
import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any, Callable, NamedTuple

from . import __version__
from . import archive as A
from . import decisions as D
from . import guards as G
from . import ledger as L
from . import okf
from . import review as R
from . import bootstrap as K  # the kit: its block markers, kit block and contract (G-D0)
from . import commit as C
from . import gate as GATE
from .bootstrap import ANY_BEGIN  # the kit block's begin marker, any version
from .config import CONFIG_NAME, Config
from .errors import Refusal
from .store import ACTOR_RE, ALIASES, Failure, Record, Store, _now, amended, coerce, key_order

ID_RE = re.compile(r"\b[A-Z]+-\d+\b")
CRITERION_ROW_RE = re.compile(r"^\|\s*([A-Z]+-\d+)\s*\|", re.MULTILINE)  # the rows guards.py::ROW_ID_RE reads
# G-D0 (DEC-23): the engine is major.minor.patch, the framework major.minor; `0.5.*` == `0.5`
VERSION_RE = re.compile(r"(?P<major>\d+)\.(?P<minor>\d+)\b")
FRAMEWORK_LINE_RE = re.compile(r"^framework:[ \t]*(\S*)", re.MULTILINE)  # the value; words after it are a comment
PIN_RE = re.compile(r"(?P<major>\d+)\.(?P<minor>\d+)(?:\.\*)?")
AMENDMENT_ENTRY_RE = re.compile(r"^- \*\*[^\n]*?\):\*\* (.*?)(?=^- \*\*|\Z)", re.MULTILINE | re.DOTALL)  # store.py::amended's entries
CONFIRMED_RE = re.compile(r"confirmed \(by [^)]*\): (.*)")  # Engine.confirm's amendment text


def confirmation_words(body: str) -> list[str]:
    """The words of each `confirmed (by <who>): <words>` amendment of a story's body, each with
    its whitespace collapsed (the entry's own indentation included), so a quote re-wrapped or
    re-indented is still the same words."""
    out = []
    for m in AMENDMENT_ENTRY_RE.finditer(okf.get_section(body, "Amendments") or ""):
        if c := CONFIRMED_RE.fullmatch(" ".join(m.group(1).split())):
            out.append(c.group(1))
    return out


BRIEF_MAX = 120  # FRAMEWORK §5.2: a constraint, not a summary
BOARD_OWNED = {
    "state": "close or reopen",
    "status": "close or reopen (status is derived from state)",
    "closed": "close or reopen",
    "moved": "touch or promote (moved is never hand-edited, FRAMEWORK §5.2)",
    "updated": "any operation (it is bumped on every write)",
    "pri": "promote",
    "deps": "dep",
    "last_asked": "ask raised or ask later",
    "answered": "ask answer; an answer changes only through its decision (`record amend`, `decision supersede`)",
}
# A decision's keys that `decision set` refuses (CE-32), each with the remedy. The engine-owned
# `type`, `id` and `body_sha` are refused by Store.set itself.
_FIXED = "it is fixed when the record is created (provenance of the decision); note a correction with `record amend <id> \"<text>\"`"
DECISION_OWNED = {
    "status": "use `decision supersede <id> <new>`: OKF status is derived from SUPERSEDED",
    "answers": "it is written by `ask answer` and never changes",
    **{k: _FIXED for k in ("actor", "decided", "session", "attribution", "imported_from", "generated", "ruled_by")},
    "verified": "an owner's endorsement must be the owner's own words, which no operation can supply: record them with `record amend <id> \"<the owner's words>\"`",
    **{k: "use `decision supersede <old> <new>`: it writes both directions" for k in ("supersedes", "superseded_by")},
    "narrowed_by": "it is the backlink `relaxes` writes: run `decision link <other> <id> --rel relaxes` on the decision that narrows this one",
    **{k: "use `decision link <id> <target> --rel <field>`; no operation removes an id link (ids are never reused, so it never goes stale)" for k in D.LINK_FIELDS if k not in ("supersedes", "superseded_by", "narrowed_by", "code")},
    "code": "add one with `decision link <id> <file::symbol>`; move one when the code moves with `decision relink <id> <old> <new>`",
    ALIASES: "a decision's earlier ids are provenance, fixed when it is created (`decision import`, or `record new decision ... --set aliases=[<old id>]`)",
}


def actor_model(actor: str) -> tuple[str, str] | None:
    """An agent actor's (harness, model) in one spelling (CE-122): lowercase, `.` and `_` read as
    `-`, a leading `claude-` dropped from the model, so `claude-code/claude-opus-5-5`,
    `claude-code/Opus-5.5` and `claude-code/opus-5_5` are one agent. None for a `human:` or
    `process:` actor, which is the owner's or a tool's own spelling."""
    if actor.startswith(("human:", "process:")) or "/" not in actor:
        return None
    harness, model = actor.split("/", 1)
    model = re.sub(r"[._]", "-", model.lower())
    return harness.lower(), model.removeprefix("claude-")


def same_agent(a: str, b: str) -> bool:
    """Two actor spellings that name one agent (CE-122): the same harness and model in
    ``actor_model``'s spelling, or one model a dash-prefix of the other (`opus` and `opus-5-5`,
    a bare tier and a versioned id)."""
    x, y = actor_model(a), actor_model(b)
    if not x or not y or x[0] != y[0]:
        return False
    return x[1] == y[1] or x[1].startswith(y[1] + "-") or y[1].startswith(x[1] + "-")


def _resolved(alias: str | None, rid: str) -> str:
    """The line that says an alias was looked up, so a reader knows which record answered."""
    return f"{alias} is an alias of {rid}\n" if alias else ""
TASK_BODY = "{summary}\n\n## Traps\n\n- none yet\n\n## Read first\n\n- none yet\n\n## Log\n"
SHOW_LOG_HEAD = 5
LINK_RELS = ("tasks", "creates", "amends", "retires", "relaxes", "code", "refs")  # what `decision link` writes
HOUSEKEEPER = "process:housekeep"
BANNER_REST = "`context-engine banner show`"  # where orient says the rest of a cut banner is
RERANK_HOW = "The full rerank is procedures.md § Rerank: run it now that NEXT is empty, or whenever the owner asks."
RERANK_REST = "procedures.md § Rerank"


def answered_remedy(rid: str, dec: str, was: str | None = None) -> str:
    """What to do instead of reopening or re-answering an answered question (CE-31): the answer
    is a decision. ``dec`` is the decision that stands now; ``was`` the owner's answer it replaced."""
    now = f"the owner's answer was {was}, superseded by {dec}" if was and was != dec else f"the owner's answer is {dec}"
    return (f"{now}: change it with `record amend {dec} \"<words>\"` or replace it "
            f"with `decision supersede {dec} <new DEC>`; for a follow-up, `ask new \"<question>\" --body-file <ask.md>` citing {rid} and {dec}")


def _answered_by(answered: Any) -> str:
    """The decision id in a question's `answered:` mapping, or a placeholder."""
    return str(answered.get("decision") or "<DEC>") if isinstance(answered, dict) else "<DEC>"


def _milestone(fn):
    """The operation is a milestone (FRAMEWORK §5.5 rule 4, DEC-36): under the `milestones`
    policy its end commits its writes, with every op log line HEAD lacks and the files they
    name. Milestones are what must reach HEAD at once: a task's close, owner words (a story or
    decision recorded, amended, retired or superseded; a story confirmed; a question answered), a hand-off to the
    next session (a baton, a pause), the session's own close or pause, another session's stub
    abandoned, and the banner, which a
    clean close writes after the session's close. Every other write stays uncommitted and goes
    into the next commit."""

    @functools.wraps(fn)
    def run(self, *args, **kw):
        with self.store.milestone():
            return fn(self, *args, **kw)

    return run


def _short(text: str, limit: int) -> str:
    """The first line of ``text``, cut at a word to fit ``limit`` characters."""
    line = text.strip().splitlines()[0].strip() if text.strip() else ""
    if len(line) <= limit:
        return line
    cut = line[: limit - 3].rsplit(" ", 1)[0].rstrip(" ,;:")
    return (cut or line[: limit - 3]) + "..."


def _one(items) -> str:
    return ", ".join(items) if items else "none"


def status_paths(z: str) -> list[str]:
    """Every path `git status --porcelain=v1 -z` names, from the top of the work tree, as it is
    on disk: -z neither quotes a path (non-ASCII, a quote, a backslash) nor writes `old -> new`.
    A rename or copy entry (`R`/`C` in either column) is followed by its source path, a field of
    its own, which is read and dropped: a rename is listed by its new path, as the by-hand step
    does (manual-mode § context-engine pause open, CE-66)."""
    out: list[str] = []
    fields = iter(z.split("\0"))
    for entry in fields:
        if len(entry) < 4:
            continue  # the empty field after the last NUL
        out.append(entry[3:])
        if "R" in entry[:2] or "C" in entry[:2]:
            next(fields, None)  # the source path, never read as an entry of its own
    return list(dict.fromkeys(out))


def _same_words(a: okf.Document, b: okf.Document) -> bool:
    """Two append-only records carry the same words as typed (above `## Amendments`, logged
    corrections undone): the test of a replacement story, a new record with the same words (`record retire --by
    agent`)."""
    try:
        return okf.typed_sha(a.body) == okf.typed_sha(b.body)
    except ValueError:
        return False  # a broken `corrected:` line: G-D10 reports it


class Engine:
    def __init__(self, root: Path | str, config: Config | None = None, today: Callable[[], dt.date] | None = None):
        self.store = Store(root, config)
        self.root = self.store.root
        self.w = self.store.config.working
        self.today = today or dt.date.today

    # -- configuration -----------------------------------------------------------------

    def _role(self, role: str) -> str:
        name = getattr(self.w, role)
        if not name:
            raise Refusal(f"no kind is configured as the {role}", f"set `{role} = \"<kind>\"` in [working] of context.toml")
        return name

    def _path(self, setting: str) -> Path:
        rel = getattr(self.w, setting)
        if not rel:
            raise Refusal(f"[working] has no `{setting}` path", f"set `{setting} = \"<repo-relative path>\"` in [working] of context.toml")
        return self.root / rel

    def _board(self) -> tuple[str, ...]:
        if not self.w.board:
            raise Refusal("[working] names no board kinds", 'set `board = ["task", "question"]` in [working] of context.toml')
        return self.w.board

    def _check(self, session: str, actor: str) -> None:
        self.store._check_caller(session, actor)

    # -- reading working state ---------------------------------------------------------

    def read_ledger(self) -> L.Ledger:
        path = self._path("ledger")
        return L.parse_ledger(path.read_bytes().decode("utf-8")) if path.exists() else L.parse_ledger(L.EMPTY_LEDGER)

    def banner(self) -> L.Banner | None:
        path = self._path("handoff")
        return L.find_banner(path.read_bytes().decode("utf-8")) if path.exists() else None

    def board_heads(self, kinds: tuple[str, ...] | None = None) -> list[Record]:
        return [r for k in (kinds or self._board()) for r in self.store.heads(k)]

    def _open_board(self) -> list[Record]:
        return [r for r in self.board_heads() if r.doc.get("state") == "open"]

    def _age(self, led: L.Ledger, key: str | None) -> int:
        """Sessions closed or paused after the session ``key``."""
        return len(led.after(key)) if key else 10**6

    def overdue(self, q: Record, led: L.Ledger) -> bool:
        """FRAMEWORK §5.3: not raised in the last N sessions or D days, whichever comes first."""
        last = q.doc.get("last_asked")
        if not last:
            return True
        if self._age(led, str(last)) >= self.w.ask_overdue_sessions:
            return True
        return (self.today() - dt.date.fromisoformat(str(last)[:10])).days >= self.w.ask_overdue_days

    def _questions(self) -> list[Record]:
        if not self.w.question:
            return []
        return [r for r in self.store.heads(self.w.question) if r.doc.get("state") == "open"]

    def _pending_asks(self, led: L.Ledger) -> tuple[list[str], list[str]]:
        """(questions at NOW or NEXT, overdue questions): the ones a session must raise."""
        qs = self._questions()
        return [q.id for q in qs if q.doc.get("pri") in ("NOW", "NEXT")], [q.id for q in qs if self.overdue(q, led)]

    # -- sessions (FRAMEWORK §5.5, §6.3, §6.4) ------------------------------------------

    def session_start(self, *, actor: str) -> str:
        """Mint ``max(newest ledger key, banner key) + 1 letter`` under the lock and reserve it
        with a ``kind: open`` stub (AC-10), recording HEAD as its ``start head``: the session
        reconciles foreign commits up to it (CE-65)."""
        if not actor or not ACTOR_RE.match(actor):
            self._check("2000-01-01a", actor)  # raises the actor refusal
        path = self._path("ledger")
        with self.store.lock():
            led = self.read_ledger()
            b = self.banner()
            key = L.next_key(L.newest([*led.keys(), b.key if b else None]), self.today())
            led.entries.insert(0, L.Entry(key, "open", L.render_open(key, _now(), actor, L.head_sha(self.root))))
            path.parent.mkdir(parents=True, exist_ok=True)
            self.store.write_text(path, led.render())
            self.store.log("session.start", key, path, key, actor, ["kind"])
        return key

    def actor_spellings(self, actor: str) -> list[tuple[str, int]]:
        """The other spellings of ``actor`` the op log already signs with (``same_agent``), each
        with its line count, most used first (CE-122; adhoc AAR entry 35: one agent signed under
        three spellings, so a query for one missed the rest). `session start` warns with them.

        Not checked: two spellings of one agent that share no model prefix (`opus` and
        `claude-4-opus`); an agent that differs only in a suffix the other lacks is read as one."""
        log = self.root / self.store.config.oplog
        if actor_model(actor) is None or not log.is_file():
            return []
        counts: dict[str, int] = {}
        for ln in log.read_bytes().decode("utf-8", errors="replace").splitlines():
            try:
                o = json.loads(ln)
            except ValueError:
                continue
            a = o.get("actor") if isinstance(o, dict) else None
            if isinstance(a, str) and a != actor:
                counts[a] = counts.get(a, 0) + 1
        return sorted(((a, n) for a, n in counts.items() if same_agent(a, actor)), key=lambda x: (-x[1], x[0]))

    def _finalise(self, key: str, actor: str, render: Callable[[L.Entry], str], op: str, check: Callable[[L.Ledger, L.Entry], None] | None = None) -> None:
        path = self._path("ledger")
        with self.store.lock():
            led = self.read_ledger()
            entry = led.get(key)
            if entry is None:
                raise Refusal(f"the ledger has no entry for {key}", "run `session start` at the start of a session and use the key it gives")
            if entry.kind != "open":
                raise Refusal(f"session {key} is already `kind: {entry.kind}`", "a session closes or pauses once; start a new session for new work")
            if check:
                check(led, entry)
            entry.text = render(entry)
            entry.kind = op.split(".")[1]
            self._refuse_prose(path, led.render(), f"this {op.replace('.', ' ')}")  # CE-63: a digest line lint would fail
            self.store.write_text(path, led.render())
            self.store.log(op, key, path, key, actor, ["kind"])

    @_milestone
    def session_close(self, key: str, *, actor: str, rows: str, summary: list[str], receipts: dict[str, str], owed: list[str] | None = None) -> str:
        """Write the session's ledger entry over its stub, refusing a malformed receipt (AC-11, G-W6, G-W8)."""
        self._check(key, actor)
        summary = [s.strip() for s in summary if s.strip()]
        if not rows.strip():
            raise Refusal("the close has no rows", "name the items this session touched, e.g. `CE-2 (closed); AC-10 (tested)`")
        if not 1 <= len(summary) <= 7:
            raise Refusal(f"the summary has {len(summary)} lines", "give the owner digest in 1 to 7 lines (FRAMEWORK §5.6)")
        for name in ("guards", "read"):
            if not (receipts.get(name) or "").strip():
                raise Refusal(f"the close has no `{name}` receipt", "guards: the gate and lint results, verbatim; read: what was read to start work")
        receipts = dict(receipts)

        def check(led: L.Ledger, stub: L.Entry) -> None:
            stated = receipts.get("asked") or ""
            if not stated and stub.field("asked"):
                receipts["asked"] = stated = stub.field("asked")
            named = set(ID_RE.findall(stated)) | set(ID_RE.findall(stub.field("asked") or ""))
            pending, overdue = self._pending_asks(led)
            missing = [q for q in pending if q not in named]
            if missing:
                raise Refusal(
                    f"the `asked` receipt does not name {_one(missing)}, which sit at NOW or NEXT",
                    "raise each in chat, one line each, then run `ask raised`; or demote the question to LATER",
                )
            unraised = [q for q in overdue if q not in named]
            if unraised:
                raise Refusal(f"overdue owner questions {_one(unraised)} were not raised this session (G-W8)", "raise each in chat, then run `ask raised`, or `ask later` if the owner defers")

        self._finalise(key, actor, lambda e: L.render_close(key, rows, receipts, summary, owed or [], e.field(L.START_HEAD)), "session.close", check)
        return f"session {key} closed: ledger entry written ({len(summary)}-line summary)"

    def staleness(self, keys: list[str]) -> dict[str, tuple[int, str]]:
        """For each key, how many other sessions closed or paused after its last activity, and when
        that was (``last_active``): DEC-29's window (CE-124). The op log is read in order, so a
        close counts only when its line comes after the key's newest line, and, when the key's
        newest activity is a commit, only when its line is not in the op log that commit carries
        (CE-129: op log position, not a date, so a skewed clock or a rebase that rewrote the
        committer date does not move the window). A live session resets the count by doing
        anything. A commit whose op log cannot be read (it is gone, or it carries none) falls back
        to its date; a stub with neither an op line nor a commit (written by hand) counts from
        its `opened` time.

        Not checked: a close written to the working op log before that commit but not carried by
        it (another session's close it left uncommitted) counts as after it, so the window can
        close one session early; which activity is newest is still chosen by time
        (``last_active``)."""
        seen = self.last_active(keys)
        want = set(keys)
        last: dict[str, int] = {}
        closes: list[tuple[int, str, str, str]] = []
        log = self.root / self.store.config.oplog
        lines = log.read_bytes().decode("utf-8", errors="replace").splitlines() if log.is_file() else []
        for n, ln in enumerate(lines):
            try:
                o = json.loads(ln)
            except ValueError:
                continue
            if not isinstance(o, dict):
                continue
            if o.get("session") in want:
                last[str(o["session"])] = n
            if o.get("op") in ("session.close", "session.pause"):
                closes.append((n, str(o.get("session")), str(o.get("at") or ""), ln.strip()))

        def when(at: str) -> dt.datetime | None:
            try:
                t = dt.datetime.fromisoformat(at.strip())
            except ValueError:
                return None
            return t if t.tzinfo else t.astimezone()

        led = self.read_ledger()
        out: dict[str, tuple[int, str]] = {}
        for k in keys:
            at, what = seen.get(k, ("", ""))
            if not at and led.get(k) is not None:  # no op line and no commit: count from its stub's `opened`
                at, what = (led.get(k).field("opened") or "").split(" by ")[0], "opened"
            carried = self._carried_log(what.split()[1]) if what.startswith("commit ") else None
            floor = when(at) if carried is None and (what.startswith("commit") or what == "opened") else None

            def after(line: str, a: str) -> bool:
                if carried is not None:
                    return line not in carried
                return floor is None or ((w := when(a)) is not None and w >= floor)

            n = sum(1 for i, s, a, line in closes if i > last.get(k, -1) and s != k and after(line, a))
            out[k] = (n, at or "never")
        return out

    def _carried_log(self, sha: str) -> set[str] | None:
        """The op log lines commit ``sha`` carries (CE-129), or None when git cannot show it."""
        text = L._git(self.root, "show", f"{sha}:./{self.store.config.oplog}")
        if not text:
            return None
        return {ln.strip() for ln in text.splitlines() if ln.strip()}

    def stale_stubs(self, session: str | None = None) -> list[tuple[str, int, str]]:
        """(key, closes or pauses since its last activity, that time) for every other session's
        open stub past DEC-29's window (``ABANDON_AFTER``)."""
        others = [e.key for e in self.read_ledger().entries if e.kind == "open" and e.key != session]
        st = self.staleness(others)
        return [(k, *st[k]) for k in others if k in st and st[k][0] >= ABANDON_AFTER]

    @_milestone
    def session_abandon(self, key: str = "", *, session: str, actor: str, force: bool = False, stale: bool = False) -> str:
        """Mark another session's stale stub `kind: abandoned` (CE-124, DEC-69 amending DEC-29):
        its lines kept, an `abandoned:` line added, and a baton filed for what it left in flight
        (its op log lines HEAD lacks, and the open board items whose `updated` or `moved` names it,
        CE-131). ``stale`` does it for every stub past the window, which
        start-of-session housekeeping runs without the owner's word: by then the stub was shown to
        the owner at every one of those sessions. A single ``key`` short of the window is refused
        unless ``force`` (the owner's word); the session's own key is always refused."""
        self._check(session, actor)
        if bool(key) == bool(stale):
            raise Refusal("name one stub to abandon, or pass --stale for every stale one", "`session abandon <key>`, or `session abandon --stale` (housekeeping)")
        if stale and force:
            raise Refusal("--force with --stale", "--stale takes only stubs past the window; to abandon one short of it on the owner's word, name it: `session abandon <key> --force`")
        if stale:
            done = [self._abandon(k, n, last, session=session, actor=actor, forced=False) for k, n, last in self.stale_stubs(session)]
            return "\n".join(done) if done else f"no stale stubs (none has {ABANDON_AFTER} or more closes or pauses since its last activity)"
        if key == session:
            raise Refusal(f"{key} is this session's own key", "close or pause this session instead (`session close`, `session pause`)")
        entry = self.read_ledger().get(key)
        if entry is None or entry.kind != "open":
            raise Refusal(f"{key} has no open stub in {self.w.ledger}" + (f" (it is `kind: {entry.kind}`)" if entry else ""), "name another session's `kind: open` stub, as orient lists them")
        n, last = self.staleness([key]).get(key, (0, "?"))
        if n < ABANDON_AFTER and not force:
            raise Refusal(f"{key} is not stale: it last did anything at {last}, and {n} closes or pauses came after (the window is {ABANDON_AFTER}, DEC-29)",
                          "show it to the owner; abandon it now only on the owner's word, with --force")
        return self._abandon(key, n, last, session=session, actor=actor, forced=n < ABANDON_AFTER)

    def _abandon(self, key: str, n: int, last: str, *, session: str, actor: str, forced: bool) -> str:
        path = self._path("ledger")
        oplog = self.store.config.oplog
        with self.store.batch():
            with self.store.lock():
                led = self.read_ledger()
                entry = led.get(key)
                if entry is None or entry.kind != "open":
                    raise Refusal(f"{key} is no longer an open stub", "re-read the ledger; another session closed or abandoned it")
                why = f"{session}: never closed or paused; last active {last}, {n} closes or pauses since" + ("; on the owner's word (--force)" if forced else "")
                entry.text = entry.text.replace(f"## {key} · kind: open", f"## {key} · kind: abandoned", 1).rstrip("\n") + "\n" + L.bullet("abandoned", why)
                entry.kind = "abandoned"
                self.store.write_text(path, led.render())
                self.store.log("session.abandon", key, path, session, actor, ["kind"])
            head = L._git(self.root, "show", f"HEAD:./{oplog}") or ""
            log = self.root / oplog
            fresh = C.new_lines(log.read_bytes().decode("utf-8", errors="replace"), head) if log.is_file() else []
            left = []
            for ln in fresh:
                try:
                    o = json.loads(ln)
                except ValueError:
                    continue
                if isinstance(o, dict) and o.get("session") == key and o.get("path") != self.w.ledger:  # this commit carries the ledger's
                    left.append(str(o.get("path") or f"{o.get('op')} {o.get('id')}"))  # `id.reserve` names no path
            # CE-131: the open board items it was working on, as the board records it (the last
            # session to write or move each), so a task it took up is not left looking owned
            claimed = [r.id for r in self._open_board() if key in (str(r.doc.get("updated") or ""), str(r.doc.get("moved") or ""))]
            baton = ""
            if (left or claimed) and self.w.baton:
                parts = []
                if left:
                    files = list(dict.fromkeys(left))
                    parts.append(f"{len(left)} uncommitted op line{'s' if len(left) != 1 else ''} naming "
                                 f"{', '.join(files[:5])}{' (+' + str(len(files) - 5) + ' more)' if len(files) > 5 else ''}: review them, then commit them "
                                 f"with `context-engine commit --sweep`, or undo them by hand")
                if claimed:
                    parts.append(f"open item{'s' if len(claimed) != 1 else ''} it last wrote or moved, "
                                 f"{', '.join(claimed[:8])}{' (+' + str(len(claimed) - 8) + ' more)' if len(claimed) > 8 else ''}: "
                                 f"check each one's state and log, then take it up, re-rank it or comment on it")
                step = f"Settle what {key} left in flight: " + "; and ".join(parts)
                baton = "; " + self.baton_add(step, f"session {key} was abandoned by {session} (never closed or paused)", session=session, actor=actor).split(":")[0] + " filed for what it left in flight"
        return f"{key}: abandoned ({n} closes or pauses since its last activity, {last}){baton or '; it left nothing uncommitted and no open item it last wrote'}"

    @_milestone
    def session_pause(self, key: str, *, actor: str, rows: str, deferred: str) -> str:
        """A three-line ``kind: pause`` entry over the stub (FRAMEWORK §6.4, AC-11)."""
        self._check(key, actor)
        if not rows.strip() or not deferred.strip():
            raise Refusal("a pause needs both `rows` (the items touched) and `deferred` (the steps skipped)", "name the items touched and the steps deferred (the gate, the commit, ...)")
        self._finalise(key, actor, lambda e: L.render_pause(key, rows, deferred, e.field(L.START_HEAD)), "session.pause")
        return f"session {key} paused: ledger entry written"

    # -- the board (FRAMEWORK §5.2) -----------------------------------------------------

    def _now_short(self, open_: list[Record]) -> str | None:
        """G-W5's NOW rule: while anything is open, NOW holds exactly its cap. The failure's
        message when ``open_`` breaks it, else None (read by G-W5 and by `close`, CE-36)."""
        cap = self.w.caps.get("NOW")
        if cap is None or not open_:
            return None
        holders = [r.id for r in open_ if r.doc.get("pri") == "NOW"]
        return None if len(holders) == cap else f"NOW holds {len(holders)} ({_one(holders)}); the cap is exactly {cap}"

    def _cap_check(self, pri: str, exclude: str | None = None) -> None:
        cap = self.w.caps.get(pri)
        if cap is None:
            return
        holders = [r.id for r in self._open_board() if r.doc.get("pri") == pri and r.id != exclude]
        if len(holders) >= cap:
            raise Refusal(f"{pri} already holds {len(holders)} of {cap} ({_one(holders)})", f"demote one with `promote <id> LATER` first")

    def new(self, kind: str, title: str, *, session: str, actor: str, pri: str = "LATER", brief: str = "", deps: list[str] | None = None, body: str = "", extra: dict[str, Any] | None = None, rid: str = "", goals: list[str] | None = None, capped: bool = True) -> Record:
        """File a board item with the next free id, or with ``rid`` when an import keeps a number
        (`Q8` becomes ASK-8, FRAMEWORK §11.4): an id of the kind's series that was never used.
        An item of the `[guards] task_goals` kind names the charter goals it serves (``goals``,
        G-I1's write-time twin, CE-99); ``goals=None`` skips that check, for housekeeping, which
        makes no judgement call (an expired baton's task is then G-I1's to flag). ``capped=False``
        skips the tier cap, for an item closed before the operation returns (an answered question,
        CE-111): it never holds a place in its tier."""
        self._check(session, actor)
        if kind not in self._board():
            raise Refusal(f"{kind!r} is not a board kind", f"use one of {', '.join(self._board())}")
        if goals is not None:
            self._task_goal_check(kind, goals)
        if len(brief) > BRIEF_MAX:
            raise Refusal(f"the brief is {len(brief)} characters", f"cut it to {BRIEF_MAX}: a constraint, not a summary")
        for d in deps or []:
            self.store.find(d)
        if capped:
            self._cap_check(pri)
        fields: dict[str, Any] = {"title": title}
        if brief:
            fields["brief"] = brief
        fields.update(pri=pri, state="open", deps=list(deps or []))
        if goals:
            fields["goals"] = list(goals)
        fields.update(source=f"session {session}", created=self.today(), moved=session, updated=session)
        fields.update(extra or {})
        text = body if body.strip() else TASK_BODY.format(summary=title + ".")
        if rid:
            k = self.store.config.kind(kind)
            if not k.id_re.match(rid.strip()):
                raise Refusal(f"{rid} is not an id of the {k.name} series", f"give an id of the form {k.prefix}-n, or none for the next free one")
            return self.store.create_many(kind, [(rid.strip(), fields, text)], session=session, actor=actor, op="new")[0]
        return self.store.new(kind, fields, text, session=session, actor=actor)

    def reserve(self, kind: str, count: int = 1, *, session: str, actor: str) -> str:
        """Reserve the next ``count`` ids of a kind's series for this session (CE-105, CE-119), so
        a batch of records that cite each other, or a draft that cites a record not yet written,
        cites ids that will exist instead of a guess or a `DEC-<NEW>` placeholder; each is then
        written with its operation's ``id``. Only kinds an operation creates with a chosen id: the
        board's and the append-only ones."""
        self._check(session, actor)
        k = self.store.config.kind(kind)
        if kind not in self._board() and k.mode != "append-only":
            makers = [*self._board(), *(n for n, x in self.store.config.kinds.items() if x.mode == "append-only")]
            raise Refusal(f"{kind!r} is a {k.mode} kind no operation creates with a chosen id", f"reserve ids of {', '.join(makers)}")
        ids = self.store.reserve(kind, count, session=session, actor=actor)
        how = "ask new --id" if kind == self.w.question else "task new --id" if kind in self._board() else "record new --id"
        return f"reserved {', '.join(ids)} for session {session}: cite them, then write each with `{how}`"

    def _task_goal_check(self, kind: str, goals: list[str]) -> None:
        """Refuse a task of the `[guards] task_goals` kind whose `goals` are not goals of the
        charter in the standard form (G-I1 at write time). Quiet for other kinds and while G-I1
        is off or has no charter to read."""
        g = self.store.config.guards
        if kind != g.task_goals or "G-I1" in g.off:
            return
        known, bad = G.known_goals(self)
        if known is None:
            return
        if not known:
            raise Refusal(f"no task's goals can be checked against the charter: {bad[0].path}: {bad[0].message}", bad[0].remedy)
        problems = G.goal_problems(goals, known, legacy=False)
        if problems:
            raise Refusal(f"the task {problems[0]}" + (f" (and {len(problems) - 1} more)" if len(problems) > 1 else ""), f"pass `--goals G-n,...` naming the charter goals it serves ({', '.join(sorted(known, key=lambda x: int(x[2:])))}); a goal the charter lacks is an owner question (FRAMEWORK §3.1)")

    def _board_set(self, rid: str, changes: dict[str, Any], *, session: str, actor: str, unset: tuple[str, ...] = (), body: Callable[[str], str] | None = None, check: Callable[[Record], None] | None = None, mechanical: bool = False, op: str = "set") -> Record:
        kind = self.store.config.kind_for_id(rid)
        if kind.name not in self._board():
            raise Refusal(f"{rid} is a {kind.name}, not a board item", "use the operation for that kind")
        changes = {**changes, "updated": session}
        return self.store.set(rid, changes, session=session, actor=actor, unset=unset, body=body, check=check, mechanical=mechanical, op=op)

    def _log_line(self, session: str, actor: str, text: str) -> Callable[[str], str]:
        lines = text.strip().splitlines()
        line = f"- {session} ({actor}): {lines[0]}" + "".join(f"\n  {ln}" for ln in lines[1:])
        return lambda body: okf.append_to_section(body, "Log", line)

    def set(self, rid: str, raw: dict[str, str], *, session: str, actor: str, unset: tuple[str, ...] = (), mechanical: bool = False) -> str:
        """Set fields from CLI strings, coerced by the kind's declared types."""
        self._check(session, actor)
        owned = [k for k in (*raw, *unset) if k in BOARD_OWNED]
        if owned:
            raise Refusal(f"`{owned[0]}` is changed by an operation", f"use {BOARD_OWNED[owned[0]]}")
        if "brief" in raw and len(raw["brief"]) > BRIEF_MAX:
            raise Refusal(f"the brief is {len(raw['brief'])} characters", f"cut it to {BRIEF_MAX}")
        kind = self.store.config.kind_for_id(rid)
        changes = {k: coerce(kind, k, v) for k, v in raw.items()}
        if "goals" in changes or "goals" in unset:
            self._task_goal_check(kind.name, [] if "goals" in unset else list(changes.get("goals") or []))
        if changes.get("review") is not None:
            self._review_triggers(changes["review"])
        review = None if "review" in unset else changes.get("review")
        dropped: list[str] = []

        def check(rec: Record) -> None:
            if "review" in changes or "review" in unset:
                if not review:
                    self._review_kept(rec)
                else:
                    self._review_ready_at_now(rec, rec.doc.body, review)
            if ALIASES in changes or ALIASES in unset:  # `aliases=` replaces the list: say which old ids stop resolving
                keep = set(D.as_list(None if ALIASES in unset else changes.get(ALIASES)))
                dropped.extend(a for a in D.as_list(rec.doc.get(ALIASES)) if a not in keep)

        self._board_set(rid, changes, session=session, actor=actor, unset=unset, check=check, mechanical=mechanical)
        return f"{rid}: set {_one([*raw, *unset])}" + (f"; dropped alias {', '.join(dropped)}, which no longer resolves" if dropped else "")

    def promote(self, rid: str, pri: str, *, session: str, actor: str) -> str:
        self._check(session, actor)
        allowed = self.store.config.kind_for_id(rid).enums.get("pri", ())
        if allowed and pri not in allowed:
            raise Refusal(f"priority {pri!r}", f"use one of {', '.join(allowed)}")
        old: list[str] = []

        def check(rec: Record) -> None:
            if rec.doc.get("state") != "open":
                raise Refusal(f"{rid} is closed", "reopen it first")
            old.append(str(rec.doc.get("pri")))
            self._cap_check(pri, exclude=rid)
            if pri == "NOW" and rec.doc.get("review"):
                self._review_ready(rid, rec.doc.body, rec.doc.get("review"))

        self._board_set(rid, {"pri": pri, "moved": session}, session=session, actor=actor, check=check, op="promote")
        return f"{rid}: {old[0]} -> {pri}{self._now_left(old)}"

    def dep(self, rid: str, *, session: str, actor: str, add: list[str] = (), remove: list[str] = ()) -> str:
        self._check(session, actor)
        for d in add:
            if d == rid:
                raise Refusal(f"{rid} cannot depend on itself", "name another item")
            self.store.find(d)
        if not add and not remove:
            raise Refusal("no dependency named", "pass --add or --remove")

        def check(rec: Record) -> dict[str, Any]:
            deps = [str(d) for d in (rec.doc.get("deps") or [])]
            return {"deps": [d for d in deps if d not in remove] + [d for d in add if d not in deps]}

        rec = self._board_set(rid, {}, session=session, actor=actor, check=check, op="dep")
        return f"{rid}: deps [{', '.join(map(str, rec.doc.get('deps')))}]"

    def comment(self, rid: str, text: str, *, session: str, actor: str, mechanical: bool = False) -> str:
        self._check(session, actor)
        if not text.strip():
            raise Refusal("empty comment", "say what happened")
        self._board_set(rid, {}, session=session, actor=actor, body=self._log_line(session, actor, text), mechanical=mechanical, op="comment")
        return f"{rid}: comment added to ## Log"

    def touch(self, rid: str, *, session: str, actor: str, mechanical: bool = False) -> str:
        """Progress was made: bump `moved` (a mechanical touch bumps only `updated`)."""
        self._check(session, actor)
        self._board_set(rid, {} if mechanical else {"moved": session}, session=session, actor=actor, mechanical=mechanical, op="touch")
        return f"{rid}: {'updated' if mechanical else 'moved'} {session}"

    @_milestone
    def close(self, rid: str, msg: str, *, session: str, actor: str, body: str = "") -> str:
        """``state: closed`` and the derived OKF ``status: deprecated``, in place (AC-12). A
        milestone: its commit is titled ``<id>: close; <msg>`` and carries ``Closes: <id>``
        (DEC-22), and ``body`` goes in its message (the `Sabotage:` and receipt lines, DEC-11)."""
        self._check(session, actor)
        if not msg or not msg.strip():
            raise Refusal(f"closing {rid} without a message", "say why it is closed, e.g. `done in <commit>` or `superseded by CE-n`")
        if self.w.question and self.store.config.kind_for_id(rid).name == self.w.question:
            # FRAMEWORK §5.3: a question is closed only by an owner answer (audit finding A20)
            raise Refusal(
                f"{rid} is an owner question, which closes only on the owner's answer (FRAMEWORK §5.3)",
                f"record the owner's words with `ask answer {rid} \"<owner words>\" --title \"<decision title>\"`; if the owner said later, `ask later {rid}`",
            )

        filed: list[str] = []
        was: list[str] = []

        def check(rec: Record) -> None:
            if rec.doc.get("state") == "closed":
                raise Refusal(f"{rid} is already closed", "nothing to do; `reopen` it if it is not done")
            self._plans_frozen(rec.id)
            was.append(str(rec.doc.get("pri")))
            if rec.doc.get("review"):
                filed.extend(self._file_residuals(rec, session, actor))

        changes = {"state": "closed", "status": "deprecated", "closed": session, "moved": session}
        self._board_set(rid, changes, session=session, actor=actor, check=check, body=self._log_line(session, actor, f"closed: {msg.strip()}"), op="close")
        # set after the write, so a close refused partway never commits a `Closes:` (the batch of
        # `_milestone` commits when the operation ends)
        title = f"{rid}: close; " + _short(msg, C.TITLE_MAX - len(rid) - 9)
        whole = msg.strip()
        self.store.commit_title = title
        self.store.commit_body = "\n\n".join(x for x in (whole if len(whole.splitlines()) > 1 or whole.splitlines()[0].strip() not in title else "", body.strip()) if x)
        self.store.commit_trailers = [f"Closes: {rid}"]
        moved = f"; residuals filed as {', '.join(filed)}" if filed else ""
        return f"{rid}: closed ({msg.strip().splitlines()[0][:80]}){moved}{self._now_left(was)}"

    def _plans_frozen(self, rid: str) -> None:
        """CE-27 (FRAMEWORK §6.7: an ACTIVE-PLAN doc freezes when its item closes): refuse to close
        the last open item an ACTIVE-PLAN doc names, which would turn G-D4 red on that doc. Off
        with G-D4 (`[guards] off`)."""
        if "G-D4" in self.store.config.guards.off:
            return
        left = [rel for rel, named in G.active_plans(self) if rid in named and not any(o for i, o in named.items() if i != rid)]
        if left:
            docs = ", ".join(left)
            given, _ = G.given(self)  # CE-95: `doc freeze` refuses a doc whose liveness config gives
            steps = [f"set its `[guards] liveness_given` entry ({given[d][1]}) to FROZEN in {CONFIG_NAME} for {d}" if d in given else f"`doc freeze {d}`" for d in left]
            raise Refusal(
                f"{rid} is the last open item that ACTIVE-PLAN {'doc' if len(left) == 1 else 'docs'} {docs} {'names' if len(left) == 1 else 'name'}, so closing it would turn G-D4 red (FRAMEWORK §6.7: a plan freezes when its item closes)",
                f"freeze {'it' if len(left) == 1 else 'each'} first: {'; '.join(steps)}; then close {rid} again (its commit carries the freeze)",
            )

    def _now_left(self, was: list[str]) -> str:
        """CE-36: taking an item off NOW (`close`, `ask answer`, a demoting `promote`) can leave NOW
        below its cap while items stay open, which fails G-W5 at the next gate. Say so in the op's
        reply, with the remedy; never refuse, never promote: the next NOW item is the owner's call.
        Quiet when G-W5 is off, and when NOW is still at or over its cap (refilling is then not
        the remedy; G-W5 says what is)."""
        if was != ["NOW"] or "G-W5" in self.store.config.guards.off:
            return ""
        open_ = self._open_board()
        cap = self.w.caps.get("NOW")
        if cap is None or sum(r.doc.get("pri") == "NOW" for r in open_) >= cap:
            return ""
        short = self._now_short(open_)
        if not short:
            return ""
        nxt = [r.id for r in open_ if r.doc.get("pri") == "NEXT"]
        where = f"NEXT holds {_one(nxt)}" if nxt else "NEXT is empty; `task list` shows the rest"
        return f"; G-W5 is red until NOW is refilled: {short}; ask the owner which item to `task promote <id> NOW` ({where})"

    # -- design review and the residual-risk register (FRAMEWORK §5.2, §7.4) ------------

    def _review_ready(self, rid: str, body: str, review: list) -> None:
        """Refuse unless ``body`` holds a design review that passes (the gate on NOW, AC-26)."""
        _, probs = R.check(body)
        if probs:
            raise Refusal(
                f"{rid} is above the review threshold ({', '.join(map(str, review))}) and its design review is not ready: {'; '.join(probs)}",
                f"write it with `task section {rid} \"{R.SECTION}\" \"<text>\"` from the template in docs/runbooks/manual-mode.md § context-engine task promote",
            )

    def _review_ready_at_now(self, rec: Record, body: str, review: list | None) -> None:
        """The same gate for a write to an item already at NOW (`task set review=`, `task section`)."""
        if review and rec.doc.get("state") == "open" and rec.doc.get("pri") == "NOW":
            self._review_ready(rec.id, body, review)

    def _review_kept(self, rec: Record) -> None:
        """Refuse to drop `review` from an item whose design review lists residuals: its close
        would then file nothing, and G-W13 would not look at it."""
        rv, _ = R.read(rec.doc.body)
        if rec.doc.get("review") and rv is not None and rv.residuals:
            raise Refusal(
                f"{rec.id}'s design review lists {len(rv.residuals)} residual risks, so removing `review` would skip filing them on close",
                f"close it to file them, or first take the residual lines out of `## {R.SECTION}` with `task section {rec.id} \"{R.SECTION}\" \"<text>\"`",
            )

    def _review_triggers(self, values: list[str]) -> None:
        allowed = self.w.review_triggers
        bad = [str(v) for v in values if str(v) not in allowed]
        if bad:
            raise Refusal(f"review trigger {bad[0]!r} is not configured", f"use one of {_one(allowed)} (`review_triggers` in [working] of context.toml)")

    def _file_residuals(self, rec: Record, session: str, actor: str) -> list[str]:
        """Inside the close's lock: append the review's residuals to the register (idempotent)."""
        rv, probs = R.check(rec.doc.body)
        if probs:
            raise Refusal(f"{rec.id}'s design review is not ready, so its residuals cannot be filed: {'; '.join(probs)}", f"fix `## {R.SECTION}` with `task section {rec.id} \"{R.SECTION}\" \"<text>\"`, then close")
        if not rv.residuals:
            return []
        if not self.w.register:
            raise Refusal(f"{rec.id} has {len(rv.residuals)} residual risks and no register is configured", "set `register = \"<repo-relative path>\"` in [working] of context.toml (FRAMEWORK §10: docs/invariants.md)")
        path = self.root / self.w.register
        text = path.read_bytes().decode("utf-8") if path.exists() else None
        new, added = R.append(text, rv, rec.id, session, floor=self._inv_issued())
        if added:
            path.parent.mkdir(parents=True, exist_ok=True)
            self.store.write_text(path, new)
            self.store.log("register.append", rec.id, path, session, actor, added)
        return added

    def _inv_issued(self) -> int:
        """The highest INV-n any `register.append` op has handed out, so an entry deleted from
        the register does not give its id to another risk (§7.4: never reused)."""
        log = self.root / self.store.config.oplog
        if not log.exists():
            return 0
        top = 0
        for ln in log.read_bytes().decode("utf-8").splitlines():
            if '"register.append"' not in ln:
                continue
            try:
                entry = json.loads(ln)
            except ValueError:
                continue
            if entry.get("op") == "register.append":
                top = max([top, *(int(f[4:]) for f in entry.get("fields") or [] if re.fullmatch(r"INV-\d+", str(f)))])
        return top

    def register_show(self, engine: bool = False) -> str:
        """The register's entries: this repo's, or with ``engine`` the one shipped in the package."""
        if engine:
            path, where = R.packaged(), f"engine {__version__}"
        else:
            if not self.w.register:
                raise Refusal("[working] has no `register` path", "set `register = \"<repo-relative path>\"` in [working], or pass --engine for the engine's own")
            path, where = self.root / self.w.register, self.w.register
        if not path.exists():
            raise Refusal(f"no register at {path}", "reinstall the engine: its REGISTER.md is package data" if engine else "the first `task close` that files a residual creates it")
        return R.summary(path.read_bytes().decode("utf-8"), where)

    def _engine_register_line(self) -> str | None:
        """Orient's pointer at the engine's register, in a repo that is not the engine's own."""
        pkg = R.packaged()
        if not pkg.exists():
            return None
        if self.w.register and (self.root / self.w.register).resolve() == pkg.resolve():
            return None
        n = len(R.entries(pkg.read_bytes().decode("utf-8")))
        return f"Engine register ({__version__}): {n} residual risks, `context-engine register show --engine`"

    def lint_review(self) -> list[Failure]:
        """G-W12: an open NOW item above the threshold has a valid design review. G-W13: every
        closed reviewed item's residuals are in the register, and every entry is well-formed."""
        out: list[Failure] = []
        reviewed = [r for r in self.board_heads() if r.doc.get("review")]
        reg = (self.root / self.w.register) if self.w.register else None
        text = reg.read_bytes().decode("utf-8") if reg is not None and reg.exists() else ""
        es = R.entries(text)
        have = {R.key(e.source, e.risk) for e in es}
        for h in reviewed:
            rel = h.path.relative_to(self.root).as_posix()
            if h.doc.get("state") == "open" and h.doc.get("pri") == "NOW":
                _, probs = R.check(self.store.get(h.id).doc.body)
                if probs:
                    out.append(Failure("G-W12", rel, f"{h.id} is at NOW above the review threshold, and its design review is not ready: {probs[0]}", f"fix `## {R.SECTION}` (template: manual-mode.md § context-engine task promote), or demote it"))
            elif h.doc.get("state") == "closed":
                rv, _ = R.read(self.store.get(h.id).doc.body)
                missing = [r.text for r in (rv.residuals if rv else []) if R.key(h.id, r.text) not in have]
                if missing:
                    where = self.w.register or "no register configured"
                    out.append(Failure("G-W13", rel, f"{h.id} is closed but {len(missing)} of its residuals are not in the register ({where}): {missing[0][:60]!r}", "copy each into the register as the next INV-n (manual-mode.md § context-engine task close)"))
        for p in R.entry_problems(es):
            out.append(Failure("G-W13", self.w.register, p, "give every entry `affects`, `why not eliminated`, `control` and `from` lines and its own INV id"))
        return out

    def _answered_remedy(self, rid: str, answered: Any) -> str:
        """`answered_remedy` for the decision that stands now: follow `superseded_by` from the
        owner's answer, so a remedy never says to supersede a decision already superseded."""
        was = dec = _answered_by(answered)
        seen = {dec}
        while True:
            try:
                later = D.as_list(self.store.get(dec).doc.get("superseded_by"))
            except (Refusal, OSError, UnicodeDecodeError):  # missing or unreadable: name what `answered:` says
                break
            if not later or str(later[-1]) in seen:
                break
            dec = str(later[-1])
            seen.add(dec)
        return answered_remedy(rid, dec, was)

    def reopen(self, rid: str, msg: str, *, session: str, actor: str) -> str:
        self._check(session, actor)
        if not msg or not msg.strip():
            raise Refusal(f"reopening {rid} without a message", "say why it is open again")

        def check(rec: Record) -> None:
            if rec.doc.get("state") != "closed":
                raise Refusal(f"{rid} is not closed", "nothing to reopen")
            answered = rec.doc.get("answered")
            if self.w.question and rec.kind.name == self.w.question and answered:
                # CE-31: refuse, never clear `answered:` (that would orphan the decision whose
                # `answers:` names this question). A question closed without an answer (a
                # pre-CE-20 `task close`, audit A20) carries no `answered:` and may reopen.
                raise Refusal(f"{rid} was answered by the owner, and an answered question never reopens (FRAMEWORK §5.3)", self._answered_remedy(rid, answered))
            try:  # CE-103: a closed task is not read by G-I1, so it may lack goals; open, it is read
                self._task_goal_check(rec.kind.name, D.as_list(rec.doc.get("goals")))
            except Refusal as r:
                raise Refusal(f"reopening {rid} would leave an open task G-I1 fails: {r.message}",
                              f"name the charter goals it serves first, `task set {rid} --set goals=[G-n,...]` (a closed task takes it), then reopen it") from None

        self._board_set(rid, {"state": "open", "closed": None, "moved": session}, session=session, actor=actor, unset=("status",), check=check, body=self._log_line(session, actor, f"reopened: {msg.strip()}"), op="reopen")
        return f"{rid}: reopened"

    def section(self, rid: str, name: str, text: str, *, session: str, actor: str) -> str:
        """Replace one named body section (`section.set`, FRAMEWORK §8.0.2)."""
        self._check(session, actor)
        if name == "Log":
            raise Refusal("## Log is appended to, never replaced", "use `comment`")

        def check(rec: Record) -> None:
            self._review_ready_at_now(rec, okf.set_section(rec.doc.body, name, text), rec.doc.get("review"))

        self._board_set(rid, {}, session=session, actor=actor, body=lambda b: okf.set_section(b, name, text), check=check, op="section")
        return f"{rid}: ## {name} replaced"

    def list(self, *, state: str | None = "open", pri: str | None = None, label: str | None = None, kinds: tuple[str, ...] | None = None) -> list[str]:
        """One line per record, read from frontmatter only, sorted by tier then id (AC-13)."""
        tiers = list(self.store.config.kind(self._board()[0]).enums.get("pri", ())) or ["NOW", "NEXT", "LATER", "SOMEDAY"]
        rows = []
        for r in self.board_heads(kinds):
            d = r.doc
            if state and d.get("state") != state:
                continue
            if pri and d.get("pri") != pri:
                continue
            if label and label not in (d.get("labels") or []):
                continue
            rows.append(r)
        rows.sort(key=lambda r: (tiers.index(r.doc.get("pri")) if r.doc.get("pri") in tiers else len(tiers), r.kind.prefix, int(r.id.rsplit("-", 1)[1])))
        out = []
        for r in rows:
            deps = r.doc.get("deps") or []
            line = f"{str(r.doc.get('pri')):<7} {r.id:<7} {r.doc.get('title')}"
            if r.doc.get("state") != "open":
                line += f"  ({r.doc.get('state')} {r.doc.get('closed') or ''})".rstrip()
            out.append(line + (f"  [deps: {', '.join(map(str, deps))}]" if deps else ""))
        return out

    def show(self, rid: str, section: str | None = None, head: int = SHOW_LOG_HEAD) -> str:
        rid, alias = self.store.resolve(rid)
        rec = self.store.get(rid)
        d = rec.doc
        top = _resolved(alias, rid) + f"{rid} · {d.get('pri')} · {d.get('state')} · {d.get('title')}\n"
        if d.get(ALIASES):
            top += f"aliases: {', '.join(D.as_list(d.get(ALIASES)))}\n"
        if d.get("brief"):
            top += f"brief: {d.get('brief')}\n"
        if d.get("deps"):
            top += f"deps: {', '.join(map(str, d.get('deps')))}\n"
        body = d.body.replace("\r\n", "\n")
        if section:
            text = okf.get_section(body, section)
            if text is None:
                raise Refusal(f"{rid} has no `## {section}`", "show the record without a section to see its headings")
            return top + f"\n## {section}\n\n{text}\n"
        log = okf.get_section(body, "Log")
        if log is not None:
            entries = re.split(r"\n(?=- )", log.strip()) if log.strip() else []
            shown = entries[::-1][: head or None]
            note = f"showing {len(shown)} of {len(entries)} log entries, newest first (head=0 for all)\n" if len(shown) < len(entries) else ""
            body = okf.set_section(body, "Log", "PLACEHOLDER").replace("PLACEHOLDER", note + "\n".join(shown) if entries else "")
        return top + body

    # -- owner questions (FRAMEWORK §5.3) -----------------------------------------------

    def ask_new(self, title: str, *, session: str, actor: str, pri: str = "NEXT", brief: str = "", body: str = "", blocks: list[str] | None = None, rid: str = "") -> Record:
        """File an open owner question. Its body states the three parts (FRAMEWORK §5.3, CE-44):
        context, two or more options, and a recommendation with its why (``guards.ask_problems``);
        a body that lacks one is refused before anything is written, and so is no body (the
        template, which only names the parts). G-W4 re-checks an open question's stored body, so
        it fails one filed another way (`task new --kind question`) or emptied by a later edit."""
        self._check(session, actor)
        extra: dict[str, Any] = {"last_asked": None}
        if blocks:
            extra["blocks"] = list(blocks)
        text = body if body.strip() else f"**Question:** {title}\n\n**Context:**\n\n**Why owner-only:**\n\n**Options:**\n\n**Recommendation:** <the option, and why in a line; or \"none (too costly): <why>\" or \"none (needs human judgement): <why>\" (FRAMEWORK §5.3)>\n\n**Blocks:** {_one(blocks or [])}\n\n## Log\n"
        if "G-W4" not in self.store.config.guards.off and (bad := G.ask_problems(text)):
            raise Refusal(f"the question {bad[0]}" + (f" (and {len(bad) - 1} more: {'; '.join(bad[1:])})" if len(bad) > 1 else "") + " (FRAMEWORK §5.3)",
                          G.ASK_REMEDY + "; write the body to a file and pass it with `--body-file`")
        return self.new(self._role("question"), title, session=session, actor=actor, pri=pri, brief=brief, body=text, extra=extra, rid=rid)

    @_milestone
    def ask_answered(self, question: str, words: str, *, title: str, session: str, actor: str, pri: str = "NEXT", brief: str = "", body: str = "", blocks: list[str] | None = None, rid: str = "", ruling: str = "", ruled_by: str = "") -> str:
        """CE-111: file a question the owner already answered in chat (one put through a chat
        question tool, with no ask record behind it) and record the answer, in one milestone:
        the question as ``ask_new`` files it, then ``ask_answer`` on its id, so the decision is the
        one `ask answer` writes (``words`` verbatim, `actor: owner`, `answers:`; ``ruling`` and
        ``ruled_by`` for a delegated ruling). What ``ask_answer`` would refuse is refused before
        the question is written, so a refusal leaves nothing behind. The question is never open,
        so it takes no place in its tier (``capped=False``).

        Not checked: that the words answer this question (only the caller saw the chat)."""
        self._check(session, actor)
        if not words.strip():
            raise Refusal("an answered question with no owner words", "pass the owner's answer verbatim with `--answered` (or `--answered-file`); a question still waiting on the owner takes none")
        if not title.strip():
            raise Refusal("an answered question with no decision title", "name the decision the answer makes with `--decision-title`, as `ask answer --title` does")
        self._answer_decision("<the new question>", words, title, ruling, ruled_by, session, actor)  # refuse before anything is written
        extra: dict[str, Any] = {"last_asked": None}
        if blocks:
            extra["blocks"] = list(blocks)
        text = body if body.strip() else f"**Question:** {question}\n\nAsked in chat and answered there, so it was never open on the board; recorded with `ask new --answered`.\n\n**Blocks:** {_one(blocks or [])}\n\n## Log\n"
        rec = self.new(self._role("question"), question, session=session, actor=actor, pri=pri, brief=brief, body=text, extra=extra, rid=rid, capped=False)
        out = self.ask_answer(rec.id, words, title=title, ruling=ruling, ruled_by=ruled_by, session=session, actor=actor)
        return out.replace(f"{rec.id}: answered", f"{rec.id}: filed as answered in chat, recorded", 1)

    def _answer_decision(self, rid: str, words: str, title: str, ruling: str, ruled_by: str, session: str, actor: str) -> tuple[dict[str, Any], str]:
        """The decision ``ask_answer`` writes for ``rid``, as (fields, body), or the refusal of
        what it refuses in the owner's words, the ruling and G-I3. ``ask_answered`` calls it too,
        before it writes its question."""
        ruling, ruled_by = ruling.strip("\n"), ruled_by.strip()
        if not words.strip():
            raise Refusal("no owner words", "pass the owner's answer verbatim" + ("; for a delegated ruling, the words in which the owner delegated it" if ruling.strip() else ""))
        if bool(ruling.strip()) != bool(ruled_by):
            given, missing = ("a ruling", "`ruled_by`") if ruling.strip() else ("`ruled_by`", "a ruling")
            raise Refusal(f"{given} without {missing}: a ruling made on the owner's delegation is recorded with both (FRAMEWORK §5.3)",
                          f"pass the ruling (`--ruling` or `--ruling-file`) and who made it (`--ruled-by`: the agent that ruled, or your own actor `{actor}` if you did), with the owner's delegating words as the words; for the owner's own answer, pass neither")
        fields: dict[str, Any] = {"title": title, "actor": "owner", "decided": self.today(), "session": session, "decision_status": "PROVISIONAL", "answers": rid}
        body = f'Owner, answering {rid}: *"{words.strip()}"*\n'
        if ruled_by:
            fields = {**fields, "actor": G.DELEGATED_ACTOR, G.RULED_BY: ruled_by}
            body = (f'Owner, answering {rid} by delegating the ruling to {ruled_by}: *"{words.strip()}"*\n\n'
                    f"## Ruling\n\nRuled by {ruled_by} on the owner's delegation; only the quote above is the owner's words.\n\n{ruling}\n")
        if "G-I3" not in self.store.config.guards.off and (bad := G.delegation_problems(fields, body, new=True)):
            raise Refusal(f"the decision answering {rid} {bad[0]}" + (f" (and {len(bad) - 1} more)" if len(bad) > 1 else ""),
                          "a ruling made on the owner's delegation goes in `--ruling`, with `--ruled-by` naming who made it (never `owner`, in any case); the owner's words hold no `## Ruling` heading, and neither part holds a `## Amendments` line (a later note goes in with `record amend`)")
        return fields, body

    def _is_question(self, rid: str) -> None:
        if self.store.config.kind_for_id(rid).name != self._role("question"):
            raise Refusal(f"{rid} is not an owner question", f"use an id from the {self.w.question} series")

    def ask_raised(self, ids: list[str], *, session: str, actor: str) -> str:
        """Stamp `last_asked` and write the `asked:` receipt into the session's ledger stub."""
        self._check(session, actor)
        if not ids:
            raise Refusal("no questions named", "pass the ids raised in chat")
        for rid in ids:
            self._is_question(rid)
        led = self.read_ledger()
        stub = led.get(session)
        if stub is None or stub.kind != "open":
            raise Refusal(f"session {session} has no open ledger stub", "run `session start` first and pass its key")
        for rid in ids:
            self._board_set(rid, {"last_asked": session}, session=session, actor=actor, op="ask.raised")
        path = self._path("ledger")
        with self.store.lock():
            led = self.read_ledger()
            stub = led.get(session)
            if stub is None or stub.kind != "open":
                raise Refusal(f"session {session} closed while its questions were being raised", "record the receipt by hand in the ledger entry")
            already = ID_RE.findall(stub.field("asked") or "")
            named = already + [i for i in ids if i not in already]
            text = re.sub(r"^- \*\*asked:\*\*.*(?:\n  .*)*\n?", "", stub.text, flags=re.MULTILINE)
            stub.text = text.rstrip("\n") + "\n" + L.bullet("asked", ", ".join(named))
            self.store.write_text(path, led.render())
            self.store.log("ask.raised", session, path, session, actor, ["asked"])
        return f"raised {', '.join(ids)}: last_asked {session}, asked receipt in the {session} stub"

    def ask_later(self, rid: str, *, session: str, actor: str) -> str:
        """The owner said "later": re-stamp, never treat it as an answer (FRAMEWORK §5.3)."""
        self._check(session, actor)
        self._is_question(rid)
        self._board_set(rid, {"last_asked": session}, session=session, actor=actor, body=self._log_line(session, actor, "owner said later; still open"), op="ask.later")
        return f"{rid}: deferred by the owner, last_asked {session}, still open"

    @_milestone
    def ask_answer(self, rid: str, words: str, *, title: str, ruling: str = "", ruled_by: str = "", session: str, actor: str) -> str:
        """Record the owner's words verbatim as a decision (`actor: owner`), close the question,
        and report what it unblocked. When the owner delegated the ruling (CE-113), ``words`` are
        the owner's delegating words, ``ruling`` the ruling and ``ruled_by`` who made it: the
        decision is `actor: owner asked` with `ruled_by`, the owner's words quoted above a `##
        Ruling` section holding the ruling, so the ruling never reads as the owner's own."""
        self._check(session, actor)
        self._is_question(rid)
        ruled_by = ruled_by.strip()
        fields, body = self._answer_decision(rid, words, title, ruling, ruled_by, session, actor)
        q = self.store.get(rid)
        if q.doc.get("state") != "open":
            raise Refusal(f"{rid} is already closed", "record a new decision instead")
        if q.doc.get("answered"):
            # CE-31: open and answered is a by-hand reopen (G-W4); a second answer would make two
            # decisions answer one question and hide the G-W4 failure.
            raise Refusal(f"{rid} was already answered by the owner ({_answered_by(q.doc.get('answered'))}), so it takes no second answer (FRAMEWORK §5.3)",
                          f"restore `state: closed` and `status: deprecated` from git; {self._answered_remedy(rid, q.doc.get('answered'))}")
        self._plans_frozen(rid)  # CE-95: the answer closes the question, so a plan naming it freezes first
        dec = self.store.new(self._role("decision"), fields, body, session=session, actor=actor)
        answered = {"on": self.today(), "session": session, "decision": dec.id, **({G.RULED_BY: ruled_by} if ruled_by else {})}
        was: list[str] = []

        def check(rec: Record) -> None:
            was.append(str(rec.doc.get("pri")))

        how = f"answered on the owner's delegation, ruled by {ruled_by}" if ruled_by else "answered by the owner"
        self._board_set(rid, {"state": "closed", "status": "deprecated", "closed": session, "last_asked": session, "answered": answered}, session=session, actor=actor, check=check, body=self._log_line(session, actor, f"{how}: {dec.id}"), op="ask.answer")
        closed = {r.id for r in self.board_heads() if r.doc.get("state") == "closed"}
        freed = [r.id for r in self._open_board() if rid in (r.doc.get("deps") or []) and all(str(d) in closed for d in r.doc.get("deps"))]
        freed += [str(b) for b in (q.doc.get("blocks") or []) if str(b) not in freed]
        whose = f" (ruled by {ruled_by} on the owner's delegation; actor: {G.DELEGATED_ACTOR})" if ruled_by else ""
        return f"{rid}: answered as {dec.id}{whose}, closed; unblocked {_one(freed)}{self._now_left(was)}"

    # -- batons and pauses (FRAMEWORK §5.4) ---------------------------------------------

    @_milestone
    def baton_add(self, step: str, why: str, *, session: str, actor: str) -> str:
        self._check(session, actor)
        if not step.strip():
            raise Refusal("an empty baton", "name the skipped step")
        title = step.strip().splitlines()[0][:100]
        fields = {"title": title, "session": session, "state": "open", "created": self.today(), "why": why.strip()}
        rec = self.store.new(self._role("baton"), fields, f"{step.strip()}\n\n**Why skipped:** {why.strip() or 'not given'}\n", session=session, actor=actor)
        return f"{rec.id}: baton added for the next session"

    def _end(self, rid: str, role: str, state: str, fields: dict[str, Any], *, session: str, actor: str, op: str, mechanical: bool = False) -> None:
        if self.store.config.kind_for_id(rid).name != self._role(role):
            raise Refusal(f"{rid} is not a {role}", f"use an id from the {getattr(self.w, role)} series")

        def check(rec: Record) -> None:
            if rec.doc.get("state") != "open":
                raise Refusal(f"{rid} is already {rec.doc.get('state')}", "nothing to do")

        self.store.set(rid, {"state": state, **fields}, session=session, actor=actor, check=check, op=op, mechanical=mechanical)

    def baton_done(self, rid: str, evidence: str, *, session: str, actor: str) -> str:
        self._check(session, actor)
        if not evidence.strip():
            raise Refusal("a baton closed without evidence", "name the commit, file or ledger entry that shows the step done")
        self._end(rid, "baton", "done", {"done": session, "evidence": evidence.strip()}, session=session, actor=actor, op="baton.done")
        return f"{rid}: done ({evidence.strip()[:80]})"

    def commit(self, paths: list[str], message: str, *, session: str, actor: str, sweep: bool = False) -> str:
        """The session's own commit (FRAMEWORK §5.5 rule 4): ``paths`` by path, with this
        session's op log lines HEAD lacks and the files they name, so a record is never committed
        without its op line, nor a line without its record; another session's lines stay out
        unless they name a file the commit carries, and the reply names them (CE-125); ``sweep``
        takes every line, for a session known dead. Whatever the policy. It runs no gate: the
        session runs the gate first, as before any commit."""
        self._check(session, actor)
        if not message.strip():
            raise Refusal("a commit with no message", "give one (`-m` on the CLI) whose title leads with the task id (FRAMEWORK §6.10); the engine adds the `Session:` trailer")
        other = [k for k in C.session_trailers(message) if k != session]
        if other:
            raise Refusal(f"the message's `Session:` trailer names {other[0]}, not this session ({session})", "drop the trailer, and the engine adds this session's")
        rels = [self._commit_path(x) for x in paths]
        GATE.check_commit(self.root, self.store.config.gate, rels)  # a code path needs a green gate run on its scope (CE-78)
        self._lint_carried(rels, session, sweep)
        out = self.store.commit_paths(message, rels, session, sweep=sweep)
        if not out.sha:
            raise Refusal(f"not committed: {out.note or 'git made no commit'}",  # the note names any lines left behind
                          "fix what it names and run it again; by hand: manual-mode.md § context-engine commit")
        extra = []
        if out.carried:
            extra.append(f"including op lines that {', '.join(out.carried)} left uncommitted")
        if out.left_out:
            extra.append(f"left out as gitignored: {', '.join(out.left_out)}")
        if out.left:
            extra.append(C.left_behind(out.left))
        if out.warn:
            extra.append(f"WARNING: {out.warn}")
        n = len(out.paths)
        return f"committed {out.sha}: {n} path{'s' if n != 1 else ''}" + (f" ({'; '.join(extra)})" if extra else "")

    def _lint_carried(self, rels: list[str], session: str, sweep: bool) -> None:
        """Refuse a commit when lint fails on a path it would carry: a given path, a file under a
        given directory, or a path its op lines name (CE-63; adhoc AAR entry 18: a commit went in
        with lint red). A failure on any other path is not this commit's, and lint in the gate
        still reports it. Read without the lock: a write landing meanwhile is checked by the next
        commit, or the gate."""
        oplog = self.store.config.oplog
        carried = C.carried_paths(self.root, oplog, session, tuple(rels), sweep, self.store.derived())
        dirs = tuple(r.rstrip("/") + "/" for r in rels)
        bad = [f for f in self.lint() if f.path in carried or f.path.startswith(dirs)]
        if any(_unparseable_oplog(f, oplog) for f in bad):
            # G-W7's parse failure is for the working op log; the commit leaves out another
            # session's broken line, so refuse only for one it would take, and name it (CE-128)
            taken = C.unparseable(C.taken_lines(self.root, oplog, session, tuple(rels), sweep, self.store.derived()))
            named = []
            if taken:
                lines = (self.root / oplog).read_bytes().decode("utf-8", errors="replace").splitlines()
                n = next((i for i, ln in enumerate(lines, 1) if ln.strip() == taken[0].strip()), 0)
                k = len(taken)
                named = [Failure("G-W7", oplog,
                                 f"{k} op line{'s' if k != 1 else ''} this commit would take {'do' if k != 1 else 'does'} not parse as JSON "
                                 f"(line {n}: {taken[0].strip()[:120]})",
                                 "repair the line by hand, or redo the operation that wrote it and delete the line; the op log is written only by the engine")]
            bad = named + [f for f in bad if not _unparseable_oplog(f, oplog)]
        if bad:
            f = bad[0]
            more = f" (and {len(bad) - 1} more: `context-engine lint`)" if len(bad) > 1 else ""
            raise Refusal(f"lint fails on what this commit carries: {f.guard} {f.path}: {f.message}{more}", f"{f.remedy}; then commit again (nothing was committed)")

    def _commit_path(self, given: str) -> str:
        """A path for ``commit``, relative to the root with forward slashes. The whole root and
        pathspec magic are refused: a commit names its paths (never the whole tree)."""
        raw = str(given).strip()
        if not raw or raw.startswith(":"):
            raise Refusal(f"path {given!r} is empty or pathspec magic", "name each file or directory to commit")
        q = Path(raw.replace("\\", "/"))
        try:
            rel = (q if q.is_absolute() else self.root / q).resolve().relative_to(self.root).as_posix()
        except (ValueError, OSError):  # outside the root: `..`, another drive, a junction out
            raise Refusal(f"{given} is outside this repo's root ({self.root})", "name paths under the root; commit anything else with git itself") from None
        if rel in (".", ""):
            raise Refusal(f"{given!r} is the whole repo", "name the paths to commit: by path, never the whole tree (FRAMEWORK §5.5)")
        return rel

    def _git(self, *args: str) -> str:
        try:
            p = subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True, encoding="utf-8")
        except FileNotFoundError:
            raise Refusal("git is not installed", "install git, or write the pause record by hand") from None
        if p.returncode != 0:
            raise Refusal(f"`git {' '.join(args)}` failed: {p.stderr.strip()[:200]}", "run the engine inside a git checkout and fix the git error")
        return p.stdout

    def pause_open(self, in_flight: str, resume_step: str, *, session: str, actor: str, evidence: str = "", deferred: list[str] | None = None) -> str:
        """A pause record carrying the branch and uncommitted paths from git itself, committed
        by path at once (FRAMEWORK §5.4, §5.5 rule 4; AC-14)."""
        self._check(session, actor)
        if not in_flight.strip() or not resume_step.strip():
            raise Refusal("a pause needs what was in flight and the exact resume step", "pass both")
        branch = self._git("rev-parse", "--abbrev-ref", "HEAD").strip()
        dirty = []
        # the pause's own commit carries the op log's uncommitted lines and the files they name,
        # so they are not left uncommitted (INV-45); the list holds what stays so
        carried = C.pending(self.root, self.store.config.oplog, session, self.store.derived())
        # -z: a path as it is on disk, never quoted, so it matches the carried set (CE-66)
        for path in status_paths(self._git("status", "--porcelain=v1", "-z", "--untracked-files=all")):
            if path not in carried:
                dirty.append(path)
        fields = {
            "title": in_flight.strip().splitlines()[0][:100],
            "session": session,
            "state": "open",
            "created": self.today(),
            "branch": branch,
            "uncommitted": dirty,
            "resume_step": resume_step.strip(),
            "evidence": evidence.strip() or "none",
            "deferred": list(deferred or []),
        }
        body = f"**In flight:** {in_flight.strip()}\n\n**Resume step:** {resume_step.strip()}\n"
        # The store commits the record with its op line when the batch ends (CE-45), under the
        # pause's own title and whatever the policy, `"off"` included: a pause is always committed
        # at once (AC-14). Through `ops` the batch is the operation's, which reports the commit.
        with self.store.batch():
            rec = self.store.new(self._role("pause"), fields, body, session=session, actor=actor)
            self.store.commit_title = f"pause {rec.id} ({session}): {fields['title'][:60]}"
            self.store.commit_always = True
        return f"{rec.id}: pause recorded on {branch} ({len(dirty)} uncommitted paths){self.store.last_commit.line()}"

    def pause_resume(self, rid: str, *, session: str, actor: str) -> str:
        self._check(session, actor)
        self._end(rid, "pause", "done", {"resumed": session}, session=session, actor=actor, op="pause.resume")
        return f"{rid}: resumed by {session}"

    def _carried(self) -> list[Record]:
        return [r for role in ("baton", "pause") if getattr(self.w, role) for r in self.store.heads(getattr(self.w, role)) if r.doc.get("state") == "open"]

    def expire_batons(self, *, session: str, actor: str = HOUSEKEEPER) -> str:
        """Housekeeping: turn every baton or pause older than the configured age into a task (G-W3, AC-15)."""
        self._check(session, actor)
        led = self.read_ledger()
        made = []
        for r in self._carried():
            if self._age(led, r.doc.get("session")) < self.w.baton_max_age:
                continue
            body = TASK_BODY.format(summary=f"Expired {r.id} from session {r.doc.get('session')}: {r.doc.get('title')}. Converted by housekeeping (G-W3); read {r.path.relative_to(self.root).as_posix()}.")
            task = self.store.new(self._role("task"), {"title": f"Expired {r.id}: {r.doc.get('title')}"[:120], "pri": "LATER", "state": "open", "deps": [], "source": r.id, "created": self.today(), "moved": session, "updated": session}, body, session=session, actor=actor, mechanical=True)
            self._end(r.id, "baton" if r.kind.name == self.w.baton else "pause", "expired", {"expired_to": task.id}, session=session, actor=actor, op="hk.expire_batons", mechanical=True)
            made.append(f"{r.id}->{task.id}")
        return f"expired {len(made)}: {_one(made)}"

    # -- append-only records (G-D10) ----------------------------------------------------

    @_milestone
    def record_new(self, kind: str, title: str, body: str, raw: dict[str, str], *, session: str, actor: str, rid: str = "") -> Record:
        """A new decision or story, stamped when it is created, with the next free id or ``rid``
        (one this session reserved, or a never-used id of the series). A required key the caller left out
        is filled when its only possible value is the present: a date-typed key with today, a key-typed one with this session."""
        self._check(session, actor)
        k = self.store.config.kind(kind)
        if k.mode != "append-only":
            raise Refusal(f"{kind!r} is a {k.mode} kind", "use `task new` for board items; `record new` is for decisions and stories")
        if not body.strip():
            raise Refusal("an empty body", "pass the owner's words verbatim (for a story) or the decision and its reason")
        fields: dict[str, Any] = {"title": title}
        fields.update({key: coerce(k, key, v) for key, v in raw.items()})
        for key in k.required:
            if key not in fields and k.types.get(key) == "date":
                fields[key] = self.today()
            elif key not in fields and k.types.get(key) == "key":
                fields[key] = session
        if kind == self.store.config.guards.stories:
            self._story_checks(fields)  # after the defaults: a story recorded today needs no `--set date`
        if kind == self.w.decision and "G-I3" not in self.store.config.guards.off and (bad := G.delegation_problems(fields, body, new=True)):
            raise Refusal(f"the decision {bad[0]}" + (f" (and {len(bad) - 1} more)" if len(bad) > 1 else ""),
                          f"for a ruling made on the owner's delegation (FRAMEWORK §6.5): `--set ruled_by=<who ruled>` (never `owner`) and an actor that is not the owner alone (`--set \"actor={G.DELEGATED_ACTOR}\"`), the body the owner's delegating words verbatim, then a `## Ruling` section holding the ruling; the owner's own decision has neither `ruled_by` nor `## Ruling`; no decision's text holds a `## Amendments` line when it is recorded (a later note goes in with `record amend`)")
        if rid.strip():
            return self.store.create_many(kind, [(rid.strip(), fields, body.strip("\n") + "\n")], session=session, actor=actor, op="new")[0]
        return self.store.new(kind, fields, body.strip("\n") + "\n", session=session, actor=actor)

    def _story_checks(self, fields: dict[str, Any]) -> None:
        """The write-time twins of G-I2 and G-I1, by the same checks: a story's provenance from the
        vocabulary, and goals that are the charter's, in the standard id form (`G-n`)."""
        off = self.store.config.guards.off
        problems = [] if "G-I2" in off else G.story_problems(fields)
        if "G-I2" not in off:
            if str(fields.get("story_status")) == "retired":
                problems.insert(0, "would be created as `retired`, which only `record retire` sets (it records who retired a story and why)")
            preset = [f"`{k}`" for k in G.RETIRE_KEYS if k in fields] + (["`status: deprecated`"] if str(fields.get("status")) == "deprecated" else [])
            if preset:
                problems.insert(0, f"would be created with {preset[0]}, which only `record retire` writes")
            status = str(fields.get("story_status"))
            if status in G.CONFIRMED and G.AGENT_ACTOR_RE.fullmatch(str(fields.get("actor") or "")):
                problems.insert(0, f"would be created `{status}` with an agent's actor, but an agent's reconstruction is created `unconfirmed` and only `record confirm` moves it on, with the owner's words")
        known, bad = G.known_goals(self)
        if known is not None and "G-I1" not in off:
            if not known:  # the charter is missing or yields no goal: no story's goals can be checked
                raise Refusal(f"no story can be checked against the charter: {bad[0].path}: {bad[0].message}", bad[0].remedy)
            problems += G.goal_problems(fields.get("goals"), known, legacy=False)  # the charter's own failures are lint's (G-I1)
        if problems:
            raise Refusal(f"the story {problems[0]}" + (f" (and {len(problems) - 1} more)" if len(problems) > 1 else ""), "pass `--set actor=owner` (or `human:<id>`), a `date` as YYYY-MM-DD or none for today, `story_status` from live, unspecified, unconfirmed (`unconfirmed` for an agent's reconstruction, which only `record confirm` moves on; `retired`, `status: deprecated`, `supersedes` and `superseded_by` are set only by `record retire`), and `goals=[G-n, ...]` naming goals of the charter; a goal the charter lacks is an owner question (FRAMEWORK §6.2 step 2)")

    def stamp(self, ids: list[str], *, session: str, actor: str) -> str:
        """Freeze each record's body hash, once; all ids are checked before any is written."""
        self._check(session, actor)
        if not ids:
            raise Refusal("no ids to stamp", "name the decisions or stories whose text is final")
        for rid in ids:
            rec = self.store.get(rid)
            if rec.kind.mode != "append-only":
                raise Refusal(f"{rid} is a {rec.kind.mode} record", "only append-only records carry body_sha")
            if rec.doc.get("body_sha"):
                raise Refusal(f"{rid} is already stamped", "a stamp is never replaced; record changes with `context-engine record amend`")
        for rid in ids:
            self.store.stamp(rid, session=session, actor=actor)
        return f"stamped {len(ids)}: {_one(ids)}"

    @_milestone
    def amend(self, rid: str, text: str, *, session: str, actor: str) -> str:
        """Append a dated entry under ``## Amendments``; the text above it never changes."""
        self.store.amend(rid, text, session=session, actor=actor)
        return f"{rid}: amendment added under ## Amendments"

    def correct(self, rid: str, after: str, text: str, *, session: str, actor: str) -> str:
        """A bracketed insertion into an append-only record (DEC-13): insert-only and logged; the
        stamp is kept, since it pins the words as typed."""
        _, inserted = self.store.correct(rid, after, text, session=session, actor=actor)
        return f"{rid}: inserted {inserted!r} after {after[-40:]!r}; `corrected:` logged under ## Amendments; body_sha unchanged (the words as typed)"

    @_milestone
    def retire(self, rid: str, why: str, *, by: str, superseded_by: str = "", session: str, actor: str) -> str:
        """Retire a story (FRAMEWORK §3.2): `story_status: retired` with the derived OKF
        `status: deprecated`, `superseded_by` on it and `supersedes` on its successor when one
        replaces it, and the reason as an amendment, all in one write. ``by`` says whose call it
        is: `owner` or `human:<id>`, whose words ``why`` is, or `agent`, only when a replacement
        story exists (``superseded_by``, a new record with the same words as typed). A retirement is
        never undone, nor redone: a story that a logged `retire` retired is refused, whatever its
        frontmatter says now. A story retired by hand, with no logged `retire`, may be retired here
        to record who and why."""
        self._check(session, actor)
        kind = self.store.config.guards.stories
        if not kind:
            raise Refusal("no kind holds the stories ([guards] stories is unset)", "set `stories` in [guards] of context.toml to the kind holding the stories (the kit's is `story`); `record retire` retires a story")
        prefix = self.store.config.kind(kind).prefix
        not_story = f"`record retire` retires a story ({prefix}-n); a decision is replaced with `decision supersede`, a criterion is retired in the criteria file"
        if self.store.config.kind_for_id(rid).name != kind:
            raise Refusal(f"{rid} is not a story", not_story)
        by, why, new = by.strip(), why.strip("\n"), superseded_by.strip()
        if not G.RETIRE_BY_RE.fullmatch(by):
            raise Refusal(f"`by: {by}` is none of `owner`, `human:<id>` or `agent`", "say whose call it is: `owner` (or `human:<id>`), with their words verbatim in `why`; or `agent`, with `superseded_by` naming the replacement story (a new record with the same words)")
        if not why.strip():
            raise Refusal("no reason", "pass `why`: the owner's words verbatim (`by owner`), or what was wrong with the story (`by agent`)")
        if by == "agent" and not new:
            raise Refusal(f"an agent retires a story only in favour of a replacement story (a new record with the same words), and no `superseded_by` names one for {rid}",
                          f"record the replacement story with `record new story` (the owner's words as they are, the right fields), then pass `superseded_by`; withdrawing {rid} is the owner's call: `by owner` with their words")
        if new:
            if new == rid:
                raise Refusal(f"{rid} cannot supersede itself", "name the story that replaces it")
            if self.store.config.kind_for_id(new).name != kind:
                raise Refusal(f"{new} is not a story, so it cannot replace {rid}", f"name the {prefix}-n story that replaces it")

        def mutate(recs: dict[str, Record]) -> dict[str, list[str]]:
            o = recs[rid].doc
            done = G.logged_retires(self).get(rid)
            if done is not None:  # final, even when a hand edit has since undone it (G-I2 fails that)
                now = o.get("story_status")
                if now == "retired":
                    raise Refusal(f"{rid} is already retired (`record retire` in session {done.get('session')})", "a retirement is final: to bring the intent back, record it as a new story (`record new story`) with the owner's words")
                raise Refusal(f"{rid} was retired by `record retire` in session {done.get('session')}, and a hand edit has since made it `{now}`",
                              "a retirement is never undone: restore `story_status: retired` and `status: deprecated` from git (`git log -p` on the file); to bring the intent back, record a new story (`record new story`)")
            if new:
                n = recs[new].doc
                if n.get("story_status") == "retired":
                    raise Refusal(f"{new} is retired, so it cannot replace {rid}", "name a story that stands, or record the new story first (`record new story`)")
                if by == "agent" and not _same_words(o, n):
                    raise Refusal(f"{new} does not carry {rid}'s words as typed, so it is not {rid} recorded again with the same words, and an agent retires a story only for that",
                                  f"record {rid} again with its body as it is (`record new story --file`, the right fields; redo any `record correct`), or, if the owner withdrew it or replaced it with new words, `by owner` with their words")
            o.set("story_status", "retired")
            o.set("status", "deprecated")
            keys = {rid: ["story_status", "status"]}
            if new:
                o.set("superseded_by", [*dict.fromkeys([*D.as_list(o.get("superseded_by")), new])])
                n.set("supersedes", [*dict.fromkeys([*D.as_list(n.get("supersedes")), rid])])
                keys = {new: ["supersedes"], rid: [*keys[rid], "superseded_by"]}
            return keys

        head = f"retired (by {by}" + (f"; superseded by {new}" if new else "") + "): "
        # the successor first: its `supersedes` is idempotent, so if the story's write fails, a
        # retry (no story `retire` line logged yet) completes both
        self.store.update([*([new] if new else []), rid], mutate, session=session, actor=actor, op="retire", amend={rid: head + why})
        tail = f"; superseded by {new}, which now supersedes {rid}" if new else ""
        return f"{rid}: retired by {by} (status: deprecated){tail}; the reason is under ## Amendments"

    @_milestone
    def confirm(self, rid: str, words: str, *, by: str = "owner", status: str = "live", session: str, actor: str) -> str:
        """Confirm a story an agent reconstructed (FRAMEWORK §3.2, §11.4): `story_status:
        unconfirmed` becomes ``status`` (`live`, or `unspecified` while no criterion comes from it),
        with the confirmer's words as an amendment, in one write. ``by`` is `owner` or `human:<id>`,
        whose words ``words`` are, verbatim: an agent never confirms intent. The `actor` stays the
        agent's: provenance is never rewritten. A confirmation is not redone: a story that a logged
        `confirm` confirmed is refused, whatever its frontmatter says now. A reconstruction made
        `live` or `unspecified` by hand, with no logged `confirm`, may be confirmed here to record
        whose words confirmed it. A successor is confirmed in new words: words that confirmed a
        story it supersedes, directly or down the chain, are refused (DEC-66)."""
        self._check(session, actor)
        kind = self.store.config.guards.stories
        if not kind:
            raise Refusal("no kind holds the stories ([guards] stories is unset)", "set `stories` in [guards] of context.toml to the kind holding the stories (the kit's is `story`); `record confirm` confirms a story")
        prefix = self.store.config.kind(kind).prefix
        if self.store.config.kind_for_id(rid).name != kind:
            raise Refusal(f"{rid} is not a story", f"`record confirm` confirms a story ({prefix}-n) an agent reconstructed; a decision's status is `decision set`")
        by, words, status = by.strip(), words.strip("\n"), status.strip()
        if not G.CONFIRM_BY_RE.fullmatch(by):
            raise Refusal(f"`by: {by}` is neither `owner` nor `human:<id>`", "a story is confirmed in the words of the owner (or of a human the charter names): pass `by` as `owner` or `human:<id>`, with their words verbatim; an agent never confirms intent")
        if not words.strip():
            raise Refusal("no words", "pass the owner's words verbatim: what they said when they confirmed the story")
        if status not in G.CONFIRMED:
            raise Refusal(f"`status: {status}` is neither `live` nor `unspecified`", "confirm a story as `live`, or as `unspecified` while no criterion comes from it yet (G-T1)")

        def mutate(recs: dict[str, Record]) -> dict[str, list[str]]:
            d = recs[rid].doc
            now = str(d.get("story_status") or "")
            done = G.logged_confirms(self).get(rid)
            if done is not None:
                if now == "unconfirmed":
                    raise Refusal(f"{rid} was confirmed by `record confirm` in session {done.get('session')}, and a hand edit has since made it `unconfirmed`",
                                  "a confirmation stands: restore `story_status` from git (`git log -p` on the file); if the owner withdrew the story, `record retire` it with their words")
                raise Refusal(f"{rid} is already confirmed (`record confirm` in session {done.get('session')})", "nothing to do; more of the owner's words go in with `record amend`")
            if now == "retired":
                raise Refusal(f"{rid} is retired", "a retirement is final: to bring the intent back, record it as a new story (`record new story`) with the owner's words")
            who = str(d.get("actor") or "")
            if not G.AGENT_ACTOR_RE.fullmatch(who):
                raise Refusal(f"{rid}'s actor is `{who}`, not an agent's reconstruction, so there is nothing to confirm",
                              "`record confirm` confirms a story an agent reconstructed (`actor: agent (reconstructed from ...)`); an owner's story is recorded `live` at `record new`")
            if now not in ("unconfirmed", *G.CONFIRMED):
                raise Refusal(f"{rid} is `story_status: {now}`, none of unconfirmed, live, unspecified", "restore `story_status` from git (`git log -p` on the file)")
            # a successor is re-confirmed by asking the owner again, never by quoting the words that
            # confirmed a story it replaces, however far back the `supersedes` chain (DEC-66, CE-102);
            # the guard and its remedy for an owner who repeats themselves are DEC-98
            said = " ".join(words.split())
            seen, todo = {rid}, [str(s) for s in D.as_list(d.get("supersedes"))]
            while todo:
                pid = todo.pop(0)
                if pid in seen:
                    continue
                seen.add(pid)
                try:
                    old = self.store.get(pid).doc
                except Refusal:
                    continue  # a dangling link is G-I2's to report, not a reason to refuse here
                if said in confirmation_words(old.body):
                    raise Refusal(f"these are the words that confirmed {pid}, which {rid} replaces",
                                  f"a replaced reconstruction is confirmed by asking the owner again, never by quoting their earlier confirmation (FRAMEWORK §3.2): ask them to confirm {rid} and pass their new words; if they answer with the very same words, quote them with when and where they said them")
                todo += [str(s) for s in D.as_list(old.get("supersedes"))]
            d.set("story_status", status)
            return {rid: ["story_status"]}

        head = f"confirmed (by {by}" + ("; unspecified" if status == "unspecified" else "") + "): "
        self.store.update([rid], mutate, session=session, actor=actor, op="confirm", amend={rid: head + words})
        return f"{rid}: confirmed by {by} (story_status: {status}); their words are under ## Amendments"

    # -- decisions (FRAMEWORK §6.5, CE-5) -----------------------------------------------

    def _decision_kind(self) -> str:
        return self._role("decision")

    def _is_decision(self, rid: str) -> None:
        if self.store.config.kind_for_id(rid).name != self._decision_kind():
            raise Refusal(f"{rid} is not a decision", f"name a {self.store.config.kind(self._decision_kind()).prefix}-n record")

    @_milestone
    def supersede(self, old: str, new: str, *, session: str, actor: str) -> str:
        """``new`` replaces ``old``: both directions are written under one lock, and ``old``
        becomes SUPERSEDED with the derived OKF ``status: deprecated``."""
        self._check(session, actor)
        (old, was_old), (new, was_new) = self._decision(old), self._decision(new)
        if old == new:
            raise Refusal(f"{old} cannot supersede itself", "name the decision that replaces it")

        def mutate(recs: dict[str, Record]) -> dict[str, list[str]]:
            o, n = recs[old].doc, recs[new].doc
            if new in D.as_list(o.get("superseded_by")):
                raise Refusal(f"{old} is already superseded by {new}", "nothing to do")
            if str(n.get(D.STATUS_KEY)) in ("SUPERSEDED", "REJECTED"):
                raise Refusal(f"{new} is {n.get(D.STATUS_KEY)}, so it cannot replace anything", "supersede with a decision that stands, or record a new one first")
            o.set(D.STATUS_KEY, "SUPERSEDED")
            o.set("status", "deprecated")
            o.set("superseded_by", [*D.as_list(o.get("superseded_by")), new])
            n.set("supersedes", [*dict.fromkeys([*D.as_list(n.get("supersedes")), old])])
            return {old: [D.STATUS_KEY, "status", "superseded_by"], new: ["supersedes"]}

        self.store.update([old, new], mutate, session=session, actor=actor, op="supersede")
        via = "".join(f" ({a} is an alias of {i})" for a, i in ((was_old, old), (was_new, new)) if a)
        return f"{old}: SUPERSEDED by {new} (status: deprecated); {new} supersedes {old}{via}"

    def decision_set(self, rid: str, raw: dict[str, str], *, session: str, actor: str, unset: tuple[str, ...] = ()) -> str:
        """Set or unset a decision's own frontmatter (`decision.set`, CE-32): `decision_status`
        (never to or from SUPERSEDED), `reopen_if` (a REJECTED decision only), `tags`, `title`,
        `description` and keys no operation owns. Links, provenance and `answers` belong to other
        operations."""
        self._check(session, actor)
        self._is_decision(rid)
        owned = [k for k in (*raw, *unset) if k in DECISION_OWNED]
        if owned:
            raise Refusal(f"`decision set` does not change a decision's `{owned[0]}`", DECISION_OWNED[owned[0]])
        kind = self.store.config.kind_for_id(rid)
        changes = {k: coerce(kind, k, v) for k, v in raw.items()}
        if str(changes.get(D.STATUS_KEY)) == "SUPERSEDED":
            raise Refusal(f"`decision set` does not mark {rid} SUPERSEDED", f"use `decision supersede {rid} <new>`: it writes `superseded_by`, `supersedes` and `status: deprecated` with it")

        def check(rec: Record) -> None:
            was = str(rec.doc.get(D.STATUS_KEY))
            if was == "SUPERSEDED" and (D.STATUS_KEY in changes or D.STATUS_KEY in unset):
                later = ", ".join(D.as_list(rec.doc.get("superseded_by"))) or "<DEC>"
                raise Refusal(f"{rid} is SUPERSEDED by {later}, so its status is kept as history and does not change", f"a superseded decision stays superseded; to bring it back, record a new decision and `decision supersede {later} <new>`")
            if "reopen_if" in changes or D.STATUS_KEY in changes or D.STATUS_KEY in unset:
                status = None if D.STATUS_KEY in unset else changes.get(D.STATUS_KEY, rec.doc.get(D.STATUS_KEY))
                reopen = None if "reopen_if" in unset else changes.get("reopen_if", rec.doc.get("reopen_if"))
                if reopen not in (None, "") and str(status) != "REJECTED":
                    if "reopen_if" in changes:
                        raise Refusal(f"`reopen_if` is for a REJECTED decision, and {rid} would be {status}", "set it with `decision_status=REJECTED`; a live decision's caveat is an amendment (`record amend`)")
                    raise Refusal(f"{rid} carries `reopen_if`, which only a REJECTED decision has", "unset it in the same call (`--unset reopen_if`): it named what would reopen a rejection that no longer stands")

        self.store.set(rid, changes, session=session, actor=actor, unset=unset, check=check)
        return f"{rid}: set {_one([*raw, *unset])}"

    def _link_rel(self, target: str) -> str:
        if "::" in target or "/" in target:
            return "code"
        if ID_RE.fullmatch(target):
            try:
                kind = self.store.config.kind_for_id(target).name
            except Refusal:
                kind = None
            if kind in (self.w.board or ()):
                return "tasks"
            if kind == self._decision_kind():
                raise Refusal(f"{target} is a decision", "use `decision supersede`, or `--rel relaxes` for a decision this one narrows")
        raise Refusal(f"cannot tell how {target!r} is linked", f"pass --rel, one of {', '.join(LINK_RELS)}")

    def _code_exists(self, target: str) -> None:
        """A `file` or `file::symbol` link names code: a repo file inside the root, case-exact, that
        names each part of the symbol (guards.py::code_link_problem, the rule G-T3 applies)."""
        problem = G.code_link_problem(G.Files(self.root), target)
        if problem:
            raise Refusal(*problem)

    def _criteria(self) -> set[str]:
        """The criterion ids: the first cell of each table row of ``[working] criteria``."""
        path = self.root / self.w.criteria if self.w.criteria else None
        if path is None or not path.is_file():
            return set()
        return set(CRITERION_ROW_RE.findall(path.read_bytes().decode("utf-8", errors="replace")))

    def link(self, rid: str, target: str, rel: str = "", *, session: str, actor: str) -> str:
        """Link a decision to a task, story, criterion, `file::symbol` or another record
        (`decision.link`). `relaxes` also writes the backlink `narrowed_by` on the other decision."""
        self._check(session, actor)
        rid, was = self._decision(rid)
        target, was_t = self._resolve_target(target)
        rel = rel or self._link_rel(target)
        if rel not in LINK_RELS:
            raise Refusal(f"--rel {rel!r} is not a link this operation writes", f"use one of {', '.join(LINK_RELS)}; `supersedes` is `decision supersede`")
        if rel == "code":
            self._code_exists(target)
        elif not ID_RE.fullmatch(target):
            raise Refusal(f"{target!r} is not an id", f"--rel {rel} links an id like CE-3, US-2 or AC-7")
        else:
            try:
                kind = self.store.config.kind_for_id(target)
            except Refusal:
                kind = None
            if rel == "relaxes":
                self._is_decision(target)
                if target == rid:
                    raise Refusal(f"{rid} cannot relax itself", "name the decision it narrows")
            if kind is not None:
                self.store.find(target)  # refuses an id that is not a record
            elif target not in self._criteria():
                crit = f" or a criterion in {self.w.criteria}" if self.w.criteria else " (no `[working] criteria` file is set, so no criterion id can be checked)"
                series = ", ".join(k.prefix + "-n" for k in self.store.config.kinds.values())
                raise Refusal(f"{target} is not a record{crit}", f"link an id that exists: a record ({series}) or a criterion row of the criteria file")
        ids = [rid, target] if rel == "relaxes" else [rid]

        def mutate(recs: dict[str, Record]) -> dict[str, list[str]]:
            d = recs[rid].doc
            have = D.as_list(d.get(rel))
            if target in have:
                raise Refusal(f"{rid} already has {target} in `{rel}`", "nothing to do")
            d.set(rel, [*have, target])
            changed = {rid: [rel]}
            if rel == "relaxes":
                t = recs[target].doc
                t.set("narrowed_by", [*dict.fromkeys([*D.as_list(t.get("narrowed_by")), rid])])
                changed[target] = ["narrowed_by"]
            return changed

        self.store.update(ids, mutate, session=session, actor=actor, op="link")
        via = "".join(f" ({a} is an alias of {i})" for a, i in ((was, rid), (was_t, target)) if a)
        return f"{rid}: {rel} + {target}" + (f"; {target}: narrowed_by + {rid}" if rel == "relaxes" else "") + via

    def _resolve_target(self, target: str) -> tuple[str, str | None]:
        """A link or `why` target with an alias resolved to its record. A `file::symbol`, a path
        and a criterion id are taken as given; so is anything no record carries as an alias."""
        target = target.strip()
        if "::" in target or "/" in target or target in self._criteria():
            return target, None
        return self.store.resolve(target, strict=False)

    def relink(self, rid: str, old: str, new: str, *, session: str, actor: str) -> str:
        """Replace one `code:` link of a current decision with another when the code moves
        (`decision.relink`, CE-35): in place, the new link checked as `link` checks it. Only
        `code:` moves: id links never do (ids are never reused), and a superseded decision's
        links are history."""
        self._check(session, actor)
        self._is_decision(rid)
        old, new = old.strip(), new.strip()
        if old == new:
            raise Refusal(f"the old and new link are the same ({old!r})", "nothing to do")
        self._code_exists(new)

        def mutate(recs: dict[str, Record]) -> dict[str, list[str]]:
            d = recs[rid].doc
            if d.get("status") == "deprecated":
                later = D.as_list(d.get("superseded_by")) or ["<successor>"]
                cmds = " or ".join(f"`decision link {s} {new}`" for s in later)
                raise Refusal(f"{rid} is superseded, so its links are kept as history and do not change", f"link the code to the decision that replaced it: {cmds}")
            have = D.as_list(d.get("code"))
            if old not in have:
                field = next((f for f in D.LINK_FIELDS if old in D.as_list(d.get(f))), None)
                if field:
                    raise Refusal(f"{rid} links {old} in `{field}`, not `code`", "only a `code:` link moves; an id is never reused, so an id link never goes stale")
                raise Refusal(f"{rid} has no `code:` link {old!r}", f"name one of its `code:` links ({', '.join(have) or 'it has none'}), or add a link with `decision link {rid} {new}`")
            d.set("code", list(dict.fromkeys(new if v == old else v for v in have)))
            return {rid: ["code"]}

        self.store.update([rid], mutate, session=session, actor=actor, op="relink")
        return f"{rid}: code {old} -> {new}"

    def _row(self, r: Record) -> str:
        d = r.doc
        who = ", ".join(str(x) for x in (d.get("actor"), d.get("decided")) if x)
        tags = D.as_list(d.get("tags"))
        return f"{r.id:<7} {str(d.get(D.STATUS_KEY)):<11} {d.get('title')}" + (f" ({who})" if who else "") + (f"  [{', '.join(tags)}]" if tags else "")

    @staticmethod
    def _links_to(d: Any, target: str) -> list[str]:
        """The link fields of ``d`` that name ``target``. A file matches its own `file::symbol`
        links, and `file::symbol` matches a link to the whole file."""
        out = []
        for f in (*D.LINK_FIELDS, "answers"):
            for v in D.as_list(d.get(f)):
                if v == target or ("::" in target and v == target.split("::")[0]) or ("::" not in target and v.startswith(target + "::")):
                    out.append(f)
                    break
        return out

    def find(self, text: str = "", tag: str = "", status: str = "", links_to: str = "") -> list[str]:
        """Decisions matching every filter given, one line each, by id (`decision.find`)."""
        kind = self._decision_kind()
        out = []
        alias = None
        if links_to:
            links_to, alias = self._resolve_target(links_to)
        recs = self.store.records(kind) if text else self.store.heads(kind)
        for r in sorted(recs, key=lambda r: int(r.id.rsplit("-", 1)[1])):
            d = r.doc
            if status and str(d.get(D.STATUS_KEY)).upper() != status.upper():
                continue
            if tag and tag not in D.as_list(d.get("tags")):
                continue
            if links_to and not self._links_to(d, links_to):
                continue
            if text and text.lower() not in " ".join(str(x) for x in (r.id, *D.as_list(d.get(ALIASES)), d.get("title"), d.get("description") or "", d.body)).lower():
                continue
            out.append(self._row(r))
        if alias:
            return [_resolved(alias, links_to).rstrip("\n"), *(out or ["no matching decisions"])]
        return out

    def _decision(self, ref: str) -> tuple[str, str | None]:
        """A decision named by its id or an alias; a refusal names the alias it followed."""
        rid, alias = self.store.resolve(ref)
        try:
            self._is_decision(rid)
        except Refusal as r:
            if alias:
                raise Refusal(f"{alias} is an alias of {rid}, which is not a decision", f"{r.remedy}; `task show {alias}` shows it") from None
            raise
        return rid, alias

    def decision_show(self, rid: str, section: str | None = None) -> str:
        """One decision: a head line, its links, then its body or one `## section` (`decision.show`)."""
        rid, alias = self._decision(rid)
        rec = self.store.get(rid)
        d = rec.doc
        top = _resolved(alias, rid) + f"{rid} · {d.get(D.STATUS_KEY)} · {d.get('title')}\n"
        top += "".join(f"{k}: {d.get(k)}\n" for k in ("actor", "decided", "session") if d.get(k))
        top += "".join(f"{k}: {', '.join(D.as_list(d.get(k)))}\n" for k in (ALIASES, *D.LINK_FIELDS, "tags", "answers") if D.as_list(d.get(k)))
        body = d.body.replace("\r\n", "\n")
        if section:
            got = okf.get_section(body, section)
            if got is None:
                raise Refusal(f"{rid} has no `## {section}`", "show the decision without a section to see its headings")
            return top + f"\n## {section}\n\n{got}\n"
        return top + body

    def why(self, target: str) -> list[str]:
        """The decisions that link ``target`` (a task, story, criterion, decision or
        `file::symbol`), one line each with the field that links it (`why()`)."""
        target = target.strip()
        if not target:
            raise Refusal("no target given", "name a task, criterion, decision or `file::symbol`")
        target, alias = self._resolve_target(target)
        out = []
        for r in sorted(self.store.heads(self._decision_kind()), key=lambda r: int(r.id.rsplit("-", 1)[1])):
            via = self._links_to(r.doc, target)
            if via:
                out.append(f"{self._row(r)}  via {', '.join(via)}")
        if alias:
            return [_resolved(alias, target).rstrip("\n"), *(out or [f"no decision links {target}"])]
        return out

    def reindex(self, *, session: str, actor: str) -> str:
        changed = self.store.reindex(session=session, actor=actor)
        return f"{self.w.decision_index}: {'regenerated' if changed else 'already current'}"

    def import_log(self, path: str, *, session: str, actor: str, dry_run: bool = False) -> str:
        """Import a single-file decision log (FRAMEWORK §11.4): every entry keeps its number and
        its text, stamped, an id in another prefix taking the kind's with its old id as an alias;
        the rejected table's rows become REJECTED records. All or nothing; the dry run checks the
        aliases as the import does and prints the id map as a doc to save."""
        self._check(session, actor)
        kind = self.store.config.kind(self._decision_kind())
        src = Path(path) if Path(path).is_absolute() else self.root / path
        if not src.is_file():
            raise Refusal(f"no file {path}", "give the path of the single-file log (a copy, for a trial)")
        try:
            source = src.resolve().relative_to(self.root).as_posix()
        except ValueError:
            source = src.name
        amap = self.store.alias_map()
        before = {str(r.doc.get("title")): r.id for r in self.store.heads(kind.name) if r.doc.get("imported_from") and str(r.doc.get(D.STATUS_KEY)) == "REJECTED"}
        planned, notes, parsed = D.plan_import(src.read_bytes().decode("utf-8-sig"), kind.prefix, self.store.ids_in_use(kind), source, amap, before)
        for e in planned:  # the rule every write applies (G-D2), checked here so the dry run says what the import would
            for msg, _ in self.store.alias_problems(e.id, e.fields.get(ALIASES) or [], amap):
                raise Refusal(f"the log's entry {e.old} would become {e.id}, whose old id {msg.removeprefix('has alias ')}", "the old id cannot stay an alias: rename the entry in the copy (or, if the prefix is a kind's here, change that kind's prefix), then import again")
        items = []
        for e in planned:
            f = e.fields
            fields: dict[str, Any] = {"title": f["title"], "actor": f["actor"], "decided": f["decided"], "session": session, D.STATUS_KEY: f["decision_status"]}
            if f["decision_status"] == "SUPERSEDED":
                fields["status"] = "deprecated"
            fields.update({k: e.links[k] for k in D.LINK_FIELDS if e.links.get(k)})
            fields.update({k: f[k] for k in ("attribution", "imported_from", ALIASES) if f.get(k)})
            body = amended(e.body, f"imported heading note: {e.note}", session, actor) if e.note else e.body
            items.append((e.id, fields, body))
        review = [n for n in notes if "BUILT by default" in n]
        summary = "; ".join(n for n in notes if n not in review)
        after = "".join(f". {n}" for n in review)
        if dry_run:
            doc = (
                f"# Decision id map: {source} into {kind.dir}\n\nFROZEN. Printed by `context-engine decision import --dry-run` on "
                f"{self.today().isoformat()}, session {session}; the import gives each record below its id, and the old id, where "
                f"there was one, stays in its `{ALIASES}` (FRAMEWORK §11.4). Line numbers are the log's.\n\n{D.id_map(planned)}\n{D.layout(parsed)}"
            )
            return f"dry run, nothing written: would import {summary} into {kind.dir}{after}\n\nSave everything below this line as the id map's evidence doc, then import:\n\n{doc}"
        self.store.create_many(kind.name, items, session=session, actor=actor, op="import")
        return f"imported {summary} into {kind.dir}, each stamped" + (f"; index {self.w.decision_index} regenerated" if self.w.decision_index else "") + after

    # -- docs: freeze and archive (FRAMEWORK §6.7, §7.2, §7.3, CE-27) --------------------

    def _doc(self, path: str) -> tuple[str, Path]:
        """A hand-written `.md` doc inside the root, as (repo-relative path, path): not a record,
        whose liveness is its state (§6.7: a closed item stays in place)."""
        raw = str(path).strip().replace("\\", "/")
        q = Path(raw)
        try:
            rel = (q if q.is_absolute() else self.root / q).resolve().relative_to(self.root.resolve()).as_posix()
        except (ValueError, OSError):
            raise Refusal(f"{path} is outside this repo's root ({self.root})", "give a path relative to the repo root") from None
        p = self.root / rel
        if not raw or not p.is_file():
            raise Refusal(f"there is no file {rel or path!r}", "give the doc's path relative to the repo root")
        if p.suffix.lower() != ".md":
            raise Refusal(f"{rel} is not a markdown doc", "freeze or archive only `.md` docs; move other material by hand with `git mv` (manual-mode.md § context-engine doc archive)")
        for k in self.store.config.kinds.values():
            if G._under(rel, (k.dir, *k.extra_dirs)):
                raise Refusal(f"{rel} is a {k.name} record, not a doc", "a record stays where it is (FRAMEWORK §6.7: a closed item keeps its file); its state is changed by its own operations")
        return rel, p

    @staticmethod
    def _utf8(p: Path, rel: str) -> str:
        try:
            return p.read_bytes().decode("utf-8")
        except UnicodeDecodeError:
            raise Refusal(f"{rel} is not UTF-8", "save it as UTF-8, then retry") from None

    def doc_freeze(self, path: str, note: str = "", *, session: str, actor: str) -> str:
        """FRAMEWORK §6.7 and §7.2: put `FROZEN <date> (session <key>): <note>` above the doc's
        liveness declaration, so G-D4 reads it as FROZEN; nothing else in it changes. Refused
        for a doc with no declaration in G-D4's window, one already FROZEN, one declared by a
        frontmatter `liveness:` key, and one `[guards] liveness_given` declares (its opening
        lines are not this repo's to edit)."""
        self._check(session, actor)
        rel, p = self._doc(path)
        g = self.store.config.guards
        given, _ = G.given(self)
        if rel in given:
            raise Refusal(f"{rel}'s liveness is given in config ([guards] liveness_given {given[rel][1]} = {given[rel][0]}): its opening lines are not this repo's to edit", "change the `liveness_given` entry instead, if the owner of that file agrees")
        today = self.today().isoformat()
        with self.store.lock():
            text = self._utf8(p, rel)
            flat = text.replace("\r\n", "\n")
            own = G.declared(flat, g.liveness_lines)
            if own.problem:
                raise Refusal(f"{rel}: {own.problem}", "fix the declaration by hand first (G-D4)")
            if own.word is None:
                raise Refusal(f"{rel} declares no liveness in its first {g.liveness_lines} lines, so there is no declaration to freeze above", f"write `FROZEN {today} (session {session}): <why>` as a line of its own near the top by hand (manual-mode.md § context-engine doc freeze)")
            if own.word == "FROZEN":
                raise Refusal(f"{rel} is already FROZEN (line {own.line})", "nothing to do: a frozen doc is never edited (FRAMEWORK §7.2)")
            if G.FM_LIVENESS_RE.match(flat.lstrip("\ufeff").split("\n")[own.line - 1]) and flat.lstrip("\ufeff").startswith("---"):
                raise Refusal(f"{rel} declares {own.word} in its frontmatter (`liveness:`, line {own.line}), where no line can go above it", f"set `liveness: FROZEN` by hand, and say when and why in the body (manual-mode.md § context-engine doc freeze)")
            named = list(G._named(flat, g.liveness_lines, G._board_ids(self))) if self.w.board else []
            why = note.strip() or (f"{_one(named)} closed; below, the plan as it stood" if own.word == "ACTIVE-PLAN" and named else "below, the doc as it stood")
            self.store.write_text(p, A.freeze(text, own.line, A.frozen_line(today, session, why)))
            self.store.log("doc.freeze", rel, p, session, actor, ["liveness"])
        return f"{rel}: FROZEN {today} written on line {own.line}, above its {own.word} line; G-D4 now reads it as FROZEN"

    def doc_archive(self, path: str, to: str = "", why: str = "", *, session: str, actor: str) -> str:
        """FRAMEWORK §7.3: move a tracked, committed doc, unrepaired, into the archive directory
        (`to`, else `[working] archive`), opened with `ARCHIVED <date>`, and add its row to that
        directory's redirect table (`README.md`, made by the first archive there). Not a
        milestone (DEC-36): nothing is staged, and the next commit carries the old path's
        deletion, the new file and the table with their op lines, which git shows as a rename."""
        self._check(session, actor)
        rel, p = self._doc(path)
        where = (to or self.w.archive).strip().replace("\\", "/").strip("/")
        if not where:
            raise Refusal("no archive directory given, and [working] has no `archive`", "pass --to <directory>, or set `archive = \"docs/archive\"` in [working] of context.toml")
        try:
            dest_dir = (self.root / where).resolve().relative_to(self.root.resolve()).as_posix()
        except (ValueError, OSError):
            raise Refusal(f"{where} is outside this repo's root ({self.root})", "archive into a directory inside the repo") from None
        if dest_dir in (".", ""):
            raise Refusal("the archive directory is the repo root", "archive into a directory of its own, e.g. docs/archive")
        for k in self.store.config.kinds.values():
            if G._under(dest_dir, (k.dir, *k.extra_dirs)):
                raise Refusal(f"{dest_dir} holds {k.name} records", "archive into a directory of its own, e.g. docs/archive")
        if PurePosixPath(rel).parent.as_posix() == dest_dir:
            raise Refusal(f"{rel} is already in the archive directory {dest_dir}", "nothing to do: nothing in an archive is moved again (FRAMEWORK §7.3)")
        if p.name == A.REDIRECTS:
            raise Refusal(f"{rel} has the name of an archive's redirect table ({A.REDIRECTS})", f"archive it by hand under another name (manual-mode.md § context-engine doc archive)")
        dest = self.root / dest_dir / p.name
        today = self.today().isoformat()
        name = PurePosixPath(dest_dir, p.name).as_posix()
        table = self.root / dest_dir / A.REDIRECTS
        with self.store.lock():
            # AC-83: every check and every read before the first write, so a refusal writes nothing
            if dest.exists():
                raise Refusal(f"{dest_dir}/{p.name} exists already", "archive into another directory with --to, or by hand under a dated name (manual-mode.md § context-engine doc archive)")
            if not self._git("ls-files", "--", rel).strip():
                raise Refusal(f"{rel} is not tracked by git", "commit it first (an archive moves tracked material, `git mv`, so its history follows it), or delete it if it was never worth keeping")
            if self._git("status", "--porcelain=v1", "--", rel).strip():
                raise Refusal(f"{rel} has uncommitted changes", "commit them, or undo them, first: an archive moves the material as it stands in git, never repaired (FRAMEWORK §7.3)")
            text = self._utf8(p, rel)
            if text.lstrip("\ufeff").startswith("---"):
                raise Refusal(f"{rel} opens with frontmatter, so `ARCHIVED <date>` cannot be its first line", "archive it by hand, the ARCHIVED line first after the frontmatter (manual-mode.md § context-engine doc archive)")
            old = self._utf8(table, f"{dest_dir}/{A.REDIRECTS}") if table.exists() else None
            moved = A.archived(text, today, session, rel)
            redirects = A.redirects(old, dest_dir, A.redirect_row(rel, p.name, today, session, why))
            dest.parent.mkdir(parents=True, exist_ok=True)
            self.store.write_text(dest, moved)
            p.unlink()
            self.store.write_text(table, redirects)
            self.store.log("doc.archive", rel, p, session, actor, ["moved"])
            self.store.log("doc.archive", rel, dest, session, actor, ["archived"])
            self.store.log("doc.archive", rel, table, session, actor, ["redirect"])
        cfg = (self.root / CONFIG_NAME).read_text(encoding="utf-8") if (self.root / CONFIG_NAME).exists() else ""
        warn = f"; context.toml still names {rel}: point it at {name} or drop it, or lint is red (G-R1, G-D4)" if _names_path(cfg, rel) else ""
        return f"{rel}: archived as {name} (first line ARCHIVED {today}), row added to {dest_dir}/{A.REDIRECTS}{warn}"

    # -- write-time prose checks (CE-63, INV-60) --------------------------------------------

    def _refuse_prose(self, path: Path, text: str, what: str) -> None:
        """Refuse to store ``text`` at ``path`` when it would add a failure that lint's G-D1, G-D5
        or G-D8 does not already report on the stored file (CE-63, closing INV-60; adhoc AAR
        entry 18): the same functions lint calls (``guards.prose_failures``), run on the text
        before it is written, so a write never stores what lint then rejects. A failure the file
        has already (a hand edit, a cap crossed before) is lint's to report, not this write's:
        failures are matched by guard and message with their numbers blanked, as a multiset.

        Not checked: what the other guards would say (lint, in the gate); a failure this write
        makes worse without adding one (a long note growing longer)."""
        rel = path.relative_to(self.root).as_posix()
        now = path.read_bytes().decode("utf-8", errors="replace").replace("\r\n", "\n") if path.is_file() else None
        key = lambda f: (f.guard, re.sub(r"\d+", "#", f.message))
        had = collections.Counter(key(f) for f in G.prose_failures(self, rel, now)) if now is not None else collections.Counter()
        new = []
        for f in G.prose_failures(self, rel, text.replace("\r\n", "\n")):
            if had[key(f)]:
                had[key(f)] -= 1
            else:
                new.append(f)
        if new:
            f = new[0]
            more = f" (and {len(new) - 1} more)" if len(new) > 1 else ""
            raise Refusal(f"{what} would make {rel} fail {f.guard}: {f.message}{more}", f"{f.remedy}; nothing was written, so fix the text and run it again")

    # -- banner (FRAMEWORK §5.5 rule 2) -------------------------------------------------

    @_milestone
    def banner_set(self, text: str, seen_hash: str, *, session: str, actor: str) -> str:
        """Replace the banner only if it is unchanged since ``seen_hash`` was read (AC-16)."""
        self._check(session, actor)
        if not text.strip():
            raise Refusal("an empty banner", "write what is true now")
        path = self._path("handoff")
        with self.store.lock():
            note = path.read_bytes().decode("utf-8") if path.exists() else ""
            now = L.find_banner(note)  # None: the first banner, which `seen` = "none" vouches for
            if (now.sha if now else L.NO_BANNER) != seen_hash:
                where = f"now {now.sha}, key {now.key}" if now else f"there is no banner yet, so pass --seen {L.NO_BANNER}"
                raise Refusal(f"the banner changed since you read it ({where})", "re-read it with `banner show`, merge, and pass the new hash")
            new_note = L.replace_banner(note, session, text)
            self._refuse_prose(path, new_note, "this banner")  # CE-63: refuse what lint would fail, before writing
            path.parent.mkdir(parents=True, exist_ok=True)
            self.store.write_text(path, new_note)
            self.store.log("banner.set", session, path, session, actor, ["banner"])
        new = self.banner()
        was, has = (len(now.text.splitlines()) if now else 0), len(new.text.splitlines())
        out = f"banner {'replaced' if now else 'written (the first)'} (lines {was} -> {has}), key {session}, new hash {new.sha}"
        # CE-76 (docs/evidence/adhoc-dryrun-2026-10-14.md F32): a one-line banner silently replaced
        # 113 lines of durable facts; say so when most of a long banner goes. JUDGEMENT: 10 lines
        # is a banner that holds more than the state of one session; wrong if real shrinks of
        # durable text slip under it, or routine closes trip it
        if now and was >= 10 and has * 2 < was:
            out += f"; WARNING: {was - has} of the old banner's {was} lines are gone from {self.w.handoff}: move any durable fact they held into a tracked doc (git history has the old text if it was committed)"
        try:
            cut = f"the rest: {BANNER_REST}]" in self.orient(session)
        except Refusal:  # orient needs what banner set does not (a ledger); the banner is written either way
            cut = False
        if cut:
            out +=f"; orient cuts this banner at its cap ({self.w.orient_max_bytes} bytes, after the must-act parts): trim it, or the rest is read only with `banner show`"
        return out

    # -- orient (FRAMEWORK §6.1) --------------------------------------------------------

    def orient(self, session: str | None = None) -> str:
        """The session-start read in one response, never over ``orient_max_bytes`` (AC-17)."""
        led = self.read_ledger()
        b = self.banner()
        # Shown in this order; the cap's bytes go to the must-act parts (`first`) before the rest,
        # and the banner, last in line, takes what is left (CE-75): a long banner once starved
        # the batons out of orient altogether (docs/evidence/adhoc-dryrun-2026-10-14.md F29)
        sections: list[Part] = []
        sections.append(Part(f"Banner ({b.key})" if b else "Banner", b.text if b else "no banner", BANNER_REST, rank=3))
        sections.append(Part("Batons and pauses: do these first", "\n".join(self.carried_lines(session)) or "none", "`context-engine baton list`", rank=0))

        others = [e for e in led.entries if e.kind == "open" and e.key != session]
        seen = self.last_active([e.key for e in others])
        sections.append(Part("Other open sessions: show the owner, one line each", "\n".join(f"- {e.key}, opened {e.field('opened')}" + (f"; last active {seen[e.key][0]} ({seen[e.key][1]})" if e.key in seen else "") for e in others) or "none", f'`grep -n "kind: open" {self.w.ledger}`', rank=0))

        top = [ln for ln in self.list(pri="NOW")]
        sections.append(Part("Board: NOW and NEXT", "\n".join(top + self.list(pri="NEXT")) or "empty", "`context-engine task list`", rank=1))
        due = self.rerank_due()
        if due:
            sections.append(Part("Rerank due: tell the owner", "\n".join(f"- {d}" for d in due) + "\n" + RERANK_HOW, RERANK_REST, rank=1))
        parked = self.parked_deps()
        if parked:  # CE-116
            sections.append(Part("Next work waits on parked items: tell the owner", "\n".join(parked), "`context-engine task show <id>`", rank=1))
        plans = self.plans_to_freeze()
        if plans:  # CE-97
            sections.append(Part("Plans to freeze: their items are closed", "\n".join(plans), "`context-engine lint` (G-D4)", rank=1))
        stories = self.unspecified_stories()
        if stories:  # CE-48
            sections.append(Part("Unspecified stories and the items G-T1 counts", "\n".join(stories), "`context-engine lint` (G-T1)", rank=2))
        foreign = self.foreign_lines(session)
        if foreign:  # CE-101
            sections.append(Part("Foreign commits to reconcile", "\n".join(foreign), "procedures.md § Reconciling foreign commits", rank=2))
        templates = self.unfilled_templates()
        if templates:  # CE-121
            sections.append(Part("Templates still unfilled: ask the owner", "\n".join(templates), "kit README § 2a", rank=2))
        upstream = self.upstream_lines()
        if upstream:  # CE-114
            sections.append(Part("Upstream", "\n".join(upstream), "`git status -sb`; `git reflog show @{upstream}`", rank=2))

        pending, overdue = self._pending_asks(led)
        qs = {q.id: q for q in self._questions()}
        raise_ = [f"- {i}: {qs[i].doc.get('title')} (last asked {qs[i].doc.get('last_asked') or 'never'}{', overdue' if i in overdue else ''})" for i in dict.fromkeys(pending + overdue)]
        asks = f"the {self.store.config.kind(self.w.question).prefix}- items in `context-engine task list`" if self.w.question else "`context-engine task list`"
        sections.append(Part("Raise in chat now, one line each", "\n".join(raise_) or "none", asks, rank=0))

        now = [r for r in self._open_board() if r.doc.get("pri") == "NOW"]
        if now:
            rec = self.store.get(now[0].id)
            body = rec.doc.body.replace("\r\n", "\n")
            parts = [f"brief: {rec.doc.get('brief') or 'none'}"]
            for name in ("Traps", "Read first"):
                parts.append(f"{name}:\n{okf.get_section(body, name) or 'none'}")
            sections.append(Part(f"Top item: {rec.id} {rec.doc.get('title')}", "\n\n".join(parts), f"`context-engine task show {rec.id}`", rank=2))
        else:
            sections.append(Part("Top item", "no NOW item" + (": rerank due (above)" if due else ""), "`context-engine task list`", rank=2))
        pointer = self._engine_register_line()
        if pointer:
            sections.append(Part("Engine register", pointer, "`context-engine register show --engine`", rank=2))
        # G-D0 first (CE-38): run by the SessionStart hook, orient is where a missing or stale
        # contract import is said out loud: what Claude Code does with a missing import is not
        # documented (docs/evidence/claude-code-hooks-2026-10-13.md), so nothing else may say it
        if "G-D0" not in self.store.config.guards.off and (bad := self.lint_contract()):
            sections.insert(0, Part("Contract: fix this first", "\n".join(f"- {f.path}: {f.message}. Remedy: {f.remedy}" for f in bad), "`context-engine lint`", rank=0))
        head = f"# orient {session or '(no session)'}\n"
        return fit(head, sections, self.w.orient_max_bytes)

    def last_active(self, keys: list[str]) -> dict[str, tuple[str, str]]:
        """When each session in ``keys`` last did anything, and what (CE-104; adhoc AAR entry 1,
        docs/evidence/adhoc-feedback-2026-10-21.md): the newest of its op log lines, committed or
        not (``op <op>``), and of the commits whose ``Session:`` trailer names it (``commit
        <sha>``), so a session that died without a close shows how long it has been quiet. Its
        stub's own `session.start` line counts, so only a key with no line and no commit at all
        is left out. One read of the op log and one ``git log``, bounded to commits since the
        oldest key's day.

        Not checked: work a session did outside the engine and git (an edit not yet committed,
        a test run); a commit made without the trailer (a foreign commit, CE-101); a committer
        clock so skewed that `git log --since` stops before an older commit."""
        want = set(keys)
        if not want:
            return {}
        best: dict[str, tuple[dt.datetime, str, str]] = {}

        def note(key: str, at: str, what: str) -> None:
            try:
                when = dt.datetime.fromisoformat(at.strip())
            except ValueError:
                return
            if when.tzinfo is None:
                when = when.astimezone()
            if key not in best or when > best[key][0]:
                best[key] = (when, at.strip(), what)

        log = self.root / self.store.config.oplog
        if log.is_file():
            for ln in log.read_bytes().decode("utf-8", errors="replace").splitlines():
                if not any(k in ln for k in want):
                    continue  # a cheap skip before the parse
                try:
                    o = json.loads(ln)
                except ValueError:
                    continue
                if isinstance(o, dict) and o.get("session") in want and o.get("at"):
                    note(str(o["session"]), str(o["at"]), f"op {o.get('op')}")
        since = min(keys, key=key_order)[:10]
        out = L._git(self.root, "log", f"--since={since}T00:00:00", "--format=%h%x09%cI%x09%(trailers:key=Session,valueonly,separator=%x2C)")
        for row in (out or "").splitlines():
            sha, at, who = (row.split("\t") + ["", ""])[:3]
            for k in (x.strip() for x in who.split(",")):
                if k in want:
                    note(k, at, f"commit {sha}")
        return {k: (at, what) for k, (_, at, what) in best.items()}

    def rerank_due(self) -> list[str]:
        """Why a full rerank of the board is due (procedures § Rerank; FRAMEWORK §5.2; CE-99,
        DEC-64 and its 2026-10-20f amendment): NEXT holds no task while tasks are open (the
        sprint is done). NOW does not count, and neither do owner questions on the board (they
        wait on the owner, not on a rank). Orient flags it; nothing here runs it. The charter's
        `Last rerank:` line, where `[guards] charter` is set, is only quoted, never a trigger."""
        task = self.w.task
        open_tasks = [r for r in self._open_board() if r.kind.name == task] if task else []
        if not open_tasks or any(r.doc.get("pri") == "NEXT" for r in open_tasks):
            return []
        line = f"NEXT holds no task, {len(open_tasks)} open: the sprint is done"
        rel = self.store.config.guards.charter
        path = self.root / rel if rel else None
        if path is not None and path.is_file() and (last := G.last_rerank(path.read_text(encoding="utf-8"))):
            line += f" (last rerank: {last})"
        return [line]

    def plans_to_freeze(self) -> list[str]:
        """Each ACTIVE-PLAN doc G-D4 reads whose named board items are all closed, with how to
        freeze it (CE-97): `task close` refuses to close a plan's last item, but a close by hand
        or before CE-27 leaves the plan unfrozen, and lint says so only when the gate runs; orient
        says it at session start. Off with G-D4.

        Not checked: a plan that names no board item at all (G-D4 reports it)."""
        if "G-D4" in self.store.config.guards.off:
            return []
        given, _ = G.given(self)
        out = []
        for rel, named in G.active_plans(self):
            if named and not any(named.values()):
                how = f"set its `[guards] liveness_given` entry ({given[rel][1]}) to FROZEN in {CONFIG_NAME}" if rel in given else f"`context-engine doc freeze {rel}`"
                out.append(f"- {rel}: ACTIVE-PLAN, but {_one(sorted(named, key=key_order))} {'is' if len(named) == 1 else 'are all'} closed; freeze it: {how}")
        return out

    def parked_deps(self) -> list[str]:
        """Each item the session may take up next whose `deps` it cannot meet (CE-116; adhoc AAR
        entry 28: the banner's next task waited on a SOMEDAY task and nothing said so): the open
        NOW and NEXT items and the board ids a banner line holding the word "next" names, each
        dep that is an open SOMEDAY item (parked).

        Not checked: a dep that is open at LATER (work not yet done, not parked); a dep that is
        no board item (lint's to report); a "next" the banner names without the word on its line."""
        heads = {r.id: r for r in self.board_heads()}
        wanted = [r.id for r in self._open_board() if r.doc.get("pri") in ("NOW", "NEXT")]
        b = self.banner()
        named_next = [i for ln in (b.text.splitlines() if b else []) if re.search(r"\bnext\b", ln, re.IGNORECASE) for i in ID_RE.findall(ln) if i in heads]
        out = []
        for rid in dict.fromkeys([*wanted, *named_next]):
            rec = heads[rid]
            if rec.doc.get("state") != "open":
                continue
            why = []
            for d in (str(x) for x in D.as_list(rec.doc.get("deps"))):
                dep = heads.get(d)
                if dep is not None and dep.doc.get("state") == "open" and dep.doc.get("pri") == "SOMEDAY":
                    why.append(f"{d}, which is SOMEDAY (parked)")
            if why:
                where = f"{rec.doc.get('pri')}" + (", named next in the banner" if rid in named_next else "")
                out.append(f"- {rid} ({where}) waits on {'; '.join(why)}: drop the dep, promote it, or re-rank {rid}")
        return out

    def unspecified_stories(self) -> list[str]:
        """Each `unspecified` story with the open board items that name it, the ones G-T1 counts
        (CE-48, from CE-25's review): lint prints only failures, so a passing mention that keeps
        G-T1 green is visible only here, where the session reads it at intake. Off while `[guards]
        stories` is unset.

        Not checked: whether the item is the task to specify the story (the session's judgement)."""
        if not self.store.config.guards.stories:
            return []
        board = [(r.id, r.path.read_bytes().decode("utf-8", errors="replace")) for r in self._open_board()]
        out = []
        for rid, _rel, doc in G._stories(self):
            if doc.get("story_status") != "unspecified":
                continue
            pat = re.compile(rf"(?<![\w-]){re.escape(rid)}(?![\w-])")
            by = [i for i, text in board if pat.search(text)]
            out.append(f"- {rid}: named by {_one(by)}; G-T1 counts {'it' if len(by) == 1 else 'them'}: check one is the task to specify {rid}" if by
                       else f"- {rid}: no open board item names it (G-T1 is red): `task new` the work to specify it")
        return out

    def unfilled_templates(self) -> list[str]:
        """The charter (`[guards] charter`, else the kit's `docs/charter.md`) and criteria file
        (`[working] criteria`, else `docs/criteria.md`) when still
        the kit's template, or still holding one of its `*(...)*` placeholders (CE-121; adhoc AAR
        entry 34: both were the templates a week after the cutover, with lint clean). Orient asks
        at every session start until they are filled; lint does not fail them, since every repo
        starts from the templates (kit README § 2a: init, then fill the charter).

        Not checked: a template filled with words that say nothing."""
        out = []
        for rel, kit in ((self.store.config.guards.charter or "docs/charter.md", "docs/charter.md"), (self.w.criteria or "docs/criteria.md", "docs/criteria.md")):
            p = self.root / rel if rel else None
            if p is None or not p.is_file() or not (K.KIT / kit).is_file():
                continue
            have = p.read_bytes().decode("utf-8", errors="replace").replace("\r\n", "\n").strip()
            tmpl = (K.KIT / kit).read_text(encoding="utf-8").replace("\r\n", "\n").strip()
            left = [ph for ph in dict.fromkeys(re.findall(r"\*\([^()\n]*\)\*", tmpl)) if ph in have]
            if have == tmpl:
                out.append(f"- {rel} is still the kit's template: fill it with the owner (kit README § 2a, step 1)")
            elif left:
                out.append(f"- {rel} still holds the template's {_one([f'`{x}`' for x in left])}: replace {'it' if len(left) == 1 else 'them'} with the owner's words")
        return out

    def _session_windows(self) -> list[tuple[dt.datetime, dt.datetime | None]]:
        """When each session in the op log was open: its `session.start` to its close, pause or
        abandon (None while it is still open)."""
        log = self.root / self.store.config.oplog
        start: dict[str, dt.datetime] = {}
        end: dict[str, dt.datetime] = {}
        for ln in (log.read_bytes().decode("utf-8", errors="replace").splitlines() if log.is_file() else []):
            try:
                o = json.loads(ln)
                at = dt.datetime.fromisoformat(str(o["at"]).strip())
            except (ValueError, KeyError, TypeError):
                continue
            at = at if at.tzinfo else at.astimezone()
            op = o.get("op")
            if op == "session.start":
                start.setdefault(str(o.get("session")), at)
            elif op in ("session.close", "session.pause"):
                end[str(o.get("session"))] = at
            elif op == "session.abandon":
                end[str(o.get("id"))] = at
        return [(s, end.get(k)) for k, s in start.items()]

    def upstream_lines(self) -> list[str]:
        """HEAD against its upstream branch, and whether the upstream's last push came while no
        session was open (CE-114; adhoc AAR entry 26: a push made outside any session was
        recorded nowhere, and the ledger said nothing was pushed). The push time is the local
        reflog's `update by push` entry for the upstream ref. Empty with no upstream or no git.

        Not checked: a push from another clone (this reflog never sees it; the counts show it
        after a fetch); a push inside a session that the session's close did not record."""
        up = (L._git(self.root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}") or "").strip()
        if not up:
            return []
        counts = (L._git(self.root, "rev-list", "--left-right", "--count", "HEAD...@{upstream}") or "").split()
        out = []
        if len(counts) == 2:
            ahead, behind = counts
            out.append(f"- HEAD is {ahead} commit{'s' if ahead != '1' else ''} ahead of {up} and {behind} behind (as of the last fetch)")
        ref = (L._git(self.root, "rev-parse", "--symbolic-full-name", "@{upstream}") or "").strip()
        log = L._git(self.root, "reflog", "show", "--date=iso-strict", "--format=%gd%x09%gs", ref) if ref else None
        for row in (log or "").splitlines():
            sel, _, subject = row.partition("\t")
            if not subject.startswith("update by push"):
                continue
            m = re.search(r"@\{(.+)\}$", sel)
            try:
                at = dt.datetime.fromisoformat(m.group(1)) if m else None
            except ValueError:
                at = None
            if at is None:
                break
            at = at if at.tzinfo else at.astimezone()
            if not any(s <= at and (e is None or at <= e) for s, e in self._session_windows()):
                out.append(f"- the last push to {up}, at {m.group(1)}, came while no session was open: tell the owner, and record it in this session's close (what was pushed, and whether the gate ran first)")
            break  # the newest push only
        return out

    def foreign_lines(self, session: str | None, limit: int = 8) -> list[str]:
        """The foreign commits this session reconciles (``ledger.foreign_commits``: its range,
        less those a `kind: foreign` entry names), and those of the newest abandoned sessions'
        ranges, which no one else will (CE-101; FRAMEWORK §6.10), at most ``limit`` lines each.

        Not checked: the ranges of sessions abandoned before the newest five."""
        led = self.read_ledger()
        out = []
        keys = ([session] if session else []) + [e.key for e in led.entries if e.kind == "abandoned"][:5]
        for k in keys:
            found = L.foreign_commits(self.root, led, k, self.w.ledger)
            if not found:
                continue
            whose = "this session's range" if k == session else f"abandoned {k}'s range"
            for sha, author, subject in found[:limit]:
                out.append(f"- {sha[:7]} {_short(subject, 70)} ({author}; {whose})")
            if len(found) > limit:
                out.append(f"- (+{len(found) - limit} more in {whose})")
        return out

    def carried_lines(self, session: str | None = None, why: bool = False) -> list[str]:
        """The open batons and pauses, ``session``'s own first, then pauses (work in flight, on a
        branch) before batons, each pause with its resume step; ``why`` adds a baton's reason:
        orient's must-act section, and `baton list` in full (CE-75)."""
        pause = self.w.pause
        carried = sorted(self._carried(), key=lambda r: (r.doc.get("session") != session, r.kind.name != pause, r.kind.prefix, int(r.id.rsplit("-", 1)[1])))
        lines = []
        for r in carried:
            own = " (yours)" if session and r.doc.get("session") == session else ""
            line = f"- {r.id} from {r.doc.get('session')}{own}: {r.doc.get('title')}"
            if r.doc.get("resume_step"):
                line += f"\n  resume: {r.doc.get('resume_step')} (branch {r.doc.get('branch')})"
            if why and r.doc.get("why"):
                line += f"\n  why: {r.doc.get('why')}"
            lines.append(line)
        return lines

    # -- working-state guards (FRAMEWORK §8.4) ------------------------------------------

    def lint(self, working: bool = False) -> list[Failure]:
        """Every guard (`working`: the working-state guards alone), less those `[guards] off` names."""
        found = self.lint_working() + G.tool_owned(self) if working else self.store.lint() + self.lint_working() + self.lint_routes() + self.lint_contract() + G.lint(self)
        off = set(self.store.config.guards.off)
        return [f for f in found if f.guard not in off]

    # -- routing (FRAMEWORK §2) ---------------------------------------------------------

    def routes(self) -> str:
        """Where each framework component lives and how it may change, one line each."""
        rs = self.store.config.routes
        if not rs:
            return "no [[routes]] in context.toml"
        lines = []
        for r in rs:
            where = f"{r.path.rstrip('/')}/{r.pattern}" if r.pattern else r.path
            lines.append(f"{r.component}: {where} ({r.mode})" + (f"; {r.note}" if r.note else ""))
        return "\n".join(lines)

    def lint_routes(self) -> list[Failure]:
        """G-R1: every routed path exists, so the table never points at a file that moved.

        Not checked: a route marked optional; that the path holds the component it is routed as;
        and the path's case, on a filesystem that ignores case."""
        return [
            Failure("G-R1", "context.toml", f"route {r.component!r} points at {r.path}, which does not exist", "fix the path in [[routes]], or restore the file")
            for r in self.store.config.routes
            if not r.optional and not (self.root / r.path).exists()
        ]

    def lint_contract(self, version: str = __version__) -> list[Failure]:
        """G-D0 (DEC-23): every `framework:` line in the contract, and the version in its kit
        block's begin marker, equal the installed engine's major.minor. `0.5.*` is a synonym of
        `0.5`. A missing contract, a contract with no `framework:` line, or a value that is not
        `major.minor` fails too: the pin is what says which engine the repo's rules assume.

        The kit block (CE-38): a kit block of the engine's version holds exactly the text of the
        kit's `kit/bootloader.md` (a block from before it that inlines the rules, or a hand edit, is
        red), and every file it
        `@`-imports exists and equals the installed engine's ``kit/contract.md``, line endings
        aside, since the framework owns that file and Claude Code loads nothing from a missing one.
        Not checked: a contract with no kit block (a hand-written contract, like the engine repo's
        own), whether Claude Code actually loaded the import, and the machine-local SessionStart
        hook, which lint cannot see."""
        rel = self.store.config.contract
        m = VERSION_RE.match(version)
        assert m, f"engine version {version!r} has no major.minor"
        want = f"{m['major']}.{m['minor']}"
        path = self.root / rel if rel else None
        if path is None or not path.is_file():
            return [Failure("G-D0", rel or "context.toml", f"the contract {rel or '([engine] contract is empty)'} does not exist", f"create it with a `framework: {want}` line, or point `contract` in [engine] of context.toml at the repo's contract")]
        try:  # orient runs this too, from the SessionStart hook: a crash there would be silent
            text = path.read_bytes().decode("utf-8-sig")
        except UnicodeDecodeError as e:
            return [Failure("G-D0", rel, f"is not UTF-8 ({e.reason} at byte {e.start}), so its pin cannot be read", "save it as UTF-8")]
        out: list[Failure] = []
        pins = FRAMEWORK_LINE_RE.findall(text)
        if not pins:
            out.append(Failure("G-D0", rel, "has no `framework:` line, so nothing says which framework version its rules assume", f"add `framework: {want}` on a line of its own (the installed engine is {version})"))
        for value in pins:
            v = PIN_RE.fullmatch(value)
            if not v:
                out.append(Failure("G-D0", rel, f"`framework: {value}` is not a major.minor version", f"write it as `framework: {want}` (or `{want}.*`): the framework has no patch number and no `-draft` suffix (DEC-23)"))
            elif (have := f"{v['major']}.{v['minor']}") != want:
                out.append(Failure("G-D0", rel, f"`framework: {value}` does not match the installed engine {version} (framework {want})", f"if the repo has moved to framework {want}, follow the upgrade procedure (FRAMEWORK §8.0; kit README § Upgrade) and set `framework: {want}`; otherwise run an engine {have}.x"))
        for marker in ANY_BEGIN.findall(text):
            if marker != want:
                out.append(Failure("G-D0", rel, f"holds the kit {marker} block, but the installed engine is framework {want}", f"replace the block between its markers with the engine's kit/bootloader.md block (kit README § Upgrade), or run an engine {marker}.x"))
        block = K.kit_block(text)
        if block and block[0] == want:  # a block of another version is red above
            out += self._bootloader(rel, path, want, block[1])
            out += self._kit_runbooks()
        for ph in K.gate_placeholders():  # CE-71 (audit 2026-10-14a N1): the Gate stub left unfilled
            if ph in text:
                out.append(Failure("G-D0", rel, f"still holds the kit's placeholder `{ph}`, so its gate names no command to run", f"replace it with the repo's own test command, keeping `&& context-engine lint` after it (kit README § 2a, step 2)"))
        return out

    def _kit_runbooks(self) -> list[Failure]:
        """G-D0's runbook half (CE-50, closing INV-36's gap): every runbook the installed kit ships
        (``bootstrap.FILES`` under `docs/runbooks/`) is in the repo and a `[[routes]]` entry covers
        it (its own path, or a directory above it). `init` never edits an existing context.toml,
        so a repo upgraded to a kit with a new runbook got neither, while its contract names it.
        Run only for a repo with a kit block of this engine's version and at least one route.

        Not checked: that the repo's copy matches the kit's (a repo may merge its own edits); a
        repo with no `[[routes]]` at all, which has left G-R1 nothing to check either."""
        if not self.store.config.routes:
            return []
        routes = [r.path.strip("/") for r in self.store.config.routes]
        fix = "copy its `[[routes]]` entry from the engine's kit/context.toml.template into context.toml, then run `context-engine init`, which writes a missing runbook (kit README § 4, step 2)"
        out = []
        for dst in K.FILES.values():
            if not dst.startswith("docs/runbooks/"):
                continue
            if not any(dst == r or dst.startswith(r + "/") for r in routes):
                out.append(Failure("G-D0", CONFIG_NAME, f"no [[routes]] entry covers {dst}, a runbook the installed kit ships", fix))
            if not (self.root / dst).is_file():
                out.append(Failure("G-D0", dst, "does not exist, but the installed kit ships it and the contract names it", fix))
        return out

    def _bootloader(self, rel: str, path: Path, want: str, body: str | None) -> list[Failure]:
        """G-D0's kit-block half: the kit block's text, and every file it imports."""
        if body is None:
            return [Failure("G-D0", rel, f"has the kit {want} begin marker but no end marker after it", "restore the block from the engine's kit/bootloader.md, both markers included")]
        out: list[Failure] = []
        imports = K.IMPORT_RE.findall(body)
        if body != K.bootloader_body():
            if not imports:
                out.append(Failure("G-D0", rel, f"holds a kit {want} block that copies the framework's rules instead of importing them", f"move its gate command to `## Gate` below the end marker, replace the text between the markers with the engine's kit/bootloader.md block, then run `context-engine init`, which writes {K.CONTRACT_DEST} (kit README § Upgrade)"))
            else:
                out.append(Failure("G-D0", rel, f"the text between the kit {want} markers is not the engine's kit/bootloader.md block", "copy the block from the engine's kit/bootloader.md; this repo's own rules go outside the markers"))
        want_text = (K.KIT / K.CONTRACT).read_text(encoding="utf-8").replace("\r\n", "\n")
        for target in imports:
            p = path.parent / target  # Claude Code resolves an import against the file that holds it
            try:
                shown = p.resolve().relative_to(self.root.resolve()).as_posix()
            except ValueError:
                shown = target
            if not p.is_file():
                fix = f"copy the engine's kit/contract.md to {shown}"  # init writes only the root's copy
                out.append(Failure("G-D0", rel, f"imports @{target}, which does not exist, so the framework's rules are not loaded", f"run `context-engine init`, which writes it, or {fix}" if shown == K.CONTRACT_DEST else fix))
                continue
            try:
                have = p.read_bytes().decode("utf-8-sig").replace("\r\n", "\n")
            except UnicodeDecodeError:
                have = None  # not UTF-8, so not the kit's text: the red below
            if have != want_text:
                out.append(Failure("G-D0", shown, "is not the installed engine's kit/contract.md, and the framework owns this file", f"copy the engine's kit/contract.md over it (an upgrade replaces it whole); this repo's own rules go in {rel}, outside the kit markers"))
        return out

    def lint_working(self) -> list[Failure]:
        """G-W1 to G-W6 on the stored files, then G-W12 and G-W13 (``lint_review``): the banner
        key against the newest close (G-W1); the run of pauses since the last close (G-W2); carried
        batons and pause records by age (G-W3); each board item's ``state`` against its OKF
        ``status``, and an open question carrying ``answered:`` (G-W4); the tier caps (G-W5); and
        the newest close's ``guards:``, ``read:`` and ``rows:`` lines (G-W6).

        Not checked: any close but the newest, and the ``asked:`` receipt, which ``session close``
        checks when it writes the entry; the state key against ``status`` on decisions, stories
        (G-I2 checks a retired story) and the charter; and a ledger, orientation note or board that
        ``[working]`` does not configure."""
        out: list[Failure] = []
        led = self.read_ledger() if self.w.ledger else None
        ledger_rel = self.w.ledger
        if led is not None:
            closes = [e for e in led.entries if e.kind == "close"]
            b = self.banner() if self.w.handoff else None
            if closes and self.w.handoff:
                newest_close = max((e.key for e in closes), key=key_order)
                if b is None:  # a session closed, so a banner is owed: a missing or renamed heading fails
                    out.append(Failure("G-W1", self.w.handoff, f"no `## Banner (<key>)` heading, but {newest_close} closed", "write it at clean close (`banner set`, with `--seen none` for the first)"))
                elif key_order(b.key) < key_order(newest_close):
                    out.append(Failure("G-W1", self.w.handoff, f"banner key {b.key} is older than the newest close {newest_close}", "replace the banner at clean close (`banner set`)"))
            run = 0
            for e in led.entries:
                if e.kind == "pause":
                    run += 1
                elif e.kind == "close":
                    break
            if run > self.w.max_pauses:
                out.append(Failure("G-W2", ledger_rel, f"{run} consecutive pause entries (at most {self.w.max_pauses})", "do a clean close: gate, commit, banner, ledger"))
            if closes:
                last = closes[0]
                for name in ("guards", "read"):
                    if not last.receipt(name):
                        out.append(Failure("G-W6", ledger_rel, f"the newest close ({last.key}) has no `{name}:` receipt", "receipts are written by `session close`; add the missing line"))
                if not last.field("rows"):
                    out.append(Failure("G-W6", ledger_rel, f"the newest close ({last.key}) has no `rows:` line", "name the items the session touched"))
            for r in self._carried():
                if self._age(led, r.doc.get("session")) >= self.w.baton_max_age:
                    out.append(Failure("G-W3", r.path.relative_to(self.root).as_posix(), f"{r.id} from {r.doc.get('session')} has outlived {self.w.baton_max_age} sessions", "do it and mark it done, or let housekeeping turn it into a task (`baton expire`)"))
        if self.w.board:
            open_ = []
            for r in self.board_heads():
                state, status = r.doc.get("state"), r.doc.get("status")
                rel = r.path.relative_to(self.root).as_posix()
                if (state == "closed") != (status == "deprecated"):
                    out.append(Failure("G-W4", rel, f"state {state!r} disagrees with OKF status {status!r}", "close and reopen set both; for a closed item set `status: deprecated`"))
                if state == "open" and r.doc.get("answered") and r.kind.name == self.w.question:
                    # CE-31: nothing is open and answered at once (a by-hand reopen of an answered question)
                    dec = _answered_by(r.doc.get("answered"))
                    out.append(Failure("G-W4", rel, f"{r.id} is open but carries `answered:` ({dec})", f"restore `state: closed` and `status: deprecated` from git: {self._answered_remedy(r.id, r.doc.get('answered'))}"))
                if state == "open" and r.kind.name == self.w.question and (bad := G.ask_problems(self.store.read(r.path).body)):
                    # CE-44: an open question states context, options and a recommendation; `ask new` refuses one that does not
                    more = f" (and {len(bad) - 1} more: {'; '.join(bad[1:])})" if len(bad) > 1 else ""
                    out.append(Failure("G-W4", rel, f"{r.id} is open but {bad[0]}{more}", f"{G.ASK_REMEDY}: edit its body (not owner words), or `task section {r.id} <part> \"<text>\"` for a `## <part>` section"))
                if state == "open":
                    open_.append(r)
            for pri, cap in self.w.caps.items():
                holders = [r.id for r in open_ if r.doc.get("pri") == pri]
                if pri == "NOW":
                    short = self._now_short(open_)  # shared with `close`'s warning (CE-36)
                else:
                    short = f"{pri} holds {len(holders)} ({_one(holders)}); the cap is at most {cap}" if len(holders) > cap else None
                if short:
                    # CE-70: a fresh board's first `task new` lands at LATER, so name the step, not just the verb
                    fill = pri == "NOW" and len(holders) < cap
                    one = "which open item is worked on now" if cap == 1 else f"which open items are worked on now (NOW holds exactly {cap})"
                    remedy = f"ask the owner {one}, then `task promote <id> NOW`" if fill else "re-rank with `promote`"
                    out.append(Failure("G-W5", self.store.config.kind(self.w.board[0]).dir, short, remedy))
            out += self.lint_review()
        return out


# DEC-29 (owner, 2026-10-13a), amended by DEC-69: a stub is stale after this many closes or pauses
# since its last activity. Provenance: JUDGEMENT, the owner's; wrong if a live session idles that long.
ABANDON_AFTER = 3


class Part(NamedTuple):
    """One orient section: its heading, its body, where the rest is when the body is cut, and its
    claim on the cap (lower ``rank`` is served first)."""

    title: str
    body: str
    rest: str
    rank: int = 0


TOML_STRING_RE = re.compile(r'"((?:[^"\\]|\\.)*)"|\'([^\']*)\'')  # a basic or a literal TOML string


def _unparseable_oplog(f: Failure, oplog: str) -> bool:
    """``f`` is G-W7's failure for op log lines that do not parse (guards.py::tool_owned)."""
    return f.guard == "G-W7" and f.path == oplog and G.UNPARSEABLE in f.message


def _names_path(cfg: str, rel: str) -> bool:
    """Whether a TOML string in ``cfg`` names the repo-relative path ``rel`` (CE-95): in either
    kind of quotes, with a leading `./`, a trailing space or Windows separators. Whole-line
    comments are skipped. Not checked: a path spelled with a TOML escape (`\\u002f`); a glob that
    matched it (lint says if it now matches nothing); a quoted path in a trailing comment counts,
    so the warning can be one too many."""
    for line in cfg.splitlines():
        if line.lstrip().startswith("#"):
            continue
        for m in TOML_STRING_RE.finditer(line):
            s = m.group(1).replace("\\\\", "\\") if m.group(1) is not None else m.group(2)
            if s.strip().replace("\\", "/").removeprefix("./") == rel:
                return True
    return False


def _size(s: str) -> int:
    return len(s.encode("utf-8"))


def fit(head: str, sections: list[Part], cap: int) -> str:
    """Join the sections, in the order given, in at most ``cap`` UTF-8 bytes. Every heading
    appears; a body that does not fit is cut between items and ends in a note saying where the
    rest is. Each section is first given its heading and its cut note (or its whole body, when
    that is smaller); the bytes left over then go to the sections by rank, lowest first, and
    within a rank smallest first. So a long banner (ranked last) never cuts a section a session
    must act on, and one long must-act list cannot crowd out a short one.

    Should the headings and cut notes alone pass the cap, the notes go first from the
    lowest-ranked sections; only the headings themselves can then pass it. Text UTF-8 cannot
    encode (a lone surrogate from a record) is replaced first, so what is counted is what prints."""
    head = _printable(head)
    heads = [_printable(f"\n## {p.title}\n") for p in sections]
    texts = [_printable(p.body.rstrip("\n") + "\n") for p in sections]
    notes = [_printable(_cut_note(p.rest)) for p in sections]
    floor = [_size(h) + min(_size(t), _size(n)) for h, t, n in zip(heads, texts, notes)]
    order = sorted(range(len(sections)), key=lambda i: (sections[i].rank, _size(texts[i]), i))
    spare = cap - _size(head) - sum(floor)
    for i in reversed(order):  # over the cap on headings and notes alone: drop notes, last-served first
        if spare >= 0:
            break
        spare += floor[i] - _size(heads[i])
        floor[i] = _size(heads[i])
    out = [""] * len(sections)
    for i in order:
        budget = floor[i] + max(spare, 0) - _size(heads[i])
        text = texts[i] if _size(texts[i]) <= budget else _cut(texts[i], notes[i], budget)
        out[i] = heads[i] + text
        spare -= _size(out[i]) - floor[i]
    return head + "".join(out)


def _printable(s: str) -> str:
    return s.encode("utf-8", "replace").decode("utf-8")


def _cut(text: str, note: str, budget: int) -> str:
    """``text``'s leading items that fit ``budget`` bytes with ``note`` after them, or nothing
    when the note alone does not fit. An item is a line and the indented lines under it, so a
    pause is never shown without its resume step."""
    items = re.split(r"(?<=\n)(?=[^ \t\r\n])", text)
    keep, size = [], _size(note)
    for item in items:
        if size + _size(item) > budget:
            break
        keep.append(item)
        size += _size(item)
    return "".join(keep) + note if size <= budget else ""


def _cut_note(rest: str) -> str:
    return f"[cut at the orient cap; the rest: {rest}]\n"
