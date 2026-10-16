"""Working-state operations: sessions, the board, owner questions, batons, pauses, the banner,
``orient()`` and the working-state guards (FRAMEWORK §5, §6.1, §6.3, §6.4, §8.4).

Every operation here is one function that the CLI and the MCP server call. Each
write goes through the store, so it is checked against its kind's schema, made under the repo
lock and logged with the session key and the actor. Every write returns one line.

Which kinds play which part is configured in ``[working]`` of ``context.toml``; an operation
whose part is not configured refuses and says so.

Deliberately not handled here: marking a dead session's stub ``abandoned`` and its window
(G-W11; housekeeping, CE-6), rotating the ledger, and the `hk_` operations other than baton
expiry and regenerating the decision index (CE-6).
"""

from __future__ import annotations

import datetime as dt
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
    **{k: _FIXED for k in ("actor", "decided", "session", "attribution", "imported_from", "generated")},
    "verified": "an owner's endorsement must be the owner's own words, which no operation can supply: record them with `record amend <id> \"<the owner's words>\"`",
    **{k: "use `decision supersede <old> <new>`: it writes both directions" for k in ("supersedes", "superseded_by")},
    "narrowed_by": "it is the backlink `relaxes` writes: run `decision link <other> <id> --rel relaxes` on the decision that narrows this one",
    **{k: "use `decision link <id> <target> --rel <field>`; no operation removes an id link (ids are never reused, so it never goes stale)" for k in D.LINK_FIELDS if k not in ("supersedes", "superseded_by", "narrowed_by", "code")},
    "code": "add one with `decision link <id> <file::symbol>`; move one when the code moves with `decision relink <id> <old> <new>`",
    ALIASES: "a decision's earlier ids are provenance, fixed when it is created (`decision import`, or `record new decision ... --set aliases=[<old id>]`)",
}


def _resolved(alias: str | None, rid: str) -> str:
    """The line that says an alias was looked up, so a reader knows which record answered."""
    return f"{alias} is an alias of {rid}\n" if alias else ""
TASK_BODY = "{summary}\n\n## Traps\n\n- none yet\n\n## Read first\n\n- none yet\n\n## Log\n"
SHOW_LOG_HEAD = 5
LINK_RELS = ("tasks", "creates", "amends", "retires", "relaxes", "code", "refs")  # what `decision link` writes
HOUSEKEEPER = "process:housekeep"
BANNER_REST = "`context-engine banner show`"  # where orient says the rest of a cut banner is


def answered_remedy(rid: str, dec: str, was: str | None = None) -> str:
    """What to do instead of reopening or re-answering an answered question (CE-31): the answer
    is a decision. ``dec`` is the decision that stands now; ``was`` the owner's answer it replaced."""
    now = f"the owner's answer was {was}, superseded by {dec}" if was and was != dec else f"the owner's answer is {dec}"
    return (f"{now}: change it with `record amend {dec} \"<words>\"` or replace it "
            f"with `decision supersede {dec} <new DEC>`; for a follow-up, `ask new \"<question>\"` citing {rid} and {dec}")


def _answered_by(answered: Any) -> str:
    """The decision id in a question's `answered:` mapping, or a placeholder."""
    return str(answered.get("decision") or "<DEC>") if isinstance(answered, dict) else "<DEC>"


def _milestone(fn):
    """The operation is a milestone (FRAMEWORK §5.5 rule 4, DEC-36): under the `milestones`
    policy its end commits its writes, with every op log line HEAD lacks and the files they
    name. Milestones are what must reach HEAD at once: a task's close, owner words (a story or
    decision recorded, amended, retired or superseded; a question answered), a hand-off to the
    next session (a baton, a pause), the session's own close or pause, and the banner, which a
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
        with a ``kind: open`` stub (AC-10)."""
        if not actor or not ACTOR_RE.match(actor):
            self._check("2000-01-01a", actor)  # raises the actor refusal
        path = self._path("ledger")
        with self.store.lock():
            led = self.read_ledger()
            b = self.banner()
            key = L.next_key(L.newest([*led.keys(), b.key if b else None]), self.today())
            led.entries.insert(0, L.Entry(key, "open", L.render_open(key, _now(), actor)))
            path.parent.mkdir(parents=True, exist_ok=True)
            self.store.write_text(path, led.render())
            self.store.log("session.start", key, path, key, actor, ["kind"])
        return key

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

        self._finalise(key, actor, lambda e: L.render_close(key, rows, receipts, summary, owed or []), "session.close", check)
        return f"session {key} closed: ledger entry written ({len(summary)}-line summary)"

    @_milestone
    def session_pause(self, key: str, *, actor: str, rows: str, deferred: str) -> str:
        """A three-line ``kind: pause`` entry over the stub (FRAMEWORK §6.4, AC-11)."""
        self._check(key, actor)
        if not rows.strip() or not deferred.strip():
            raise Refusal("a pause needs both `rows` (the items touched) and `deferred` (the steps skipped)", "name the items touched and the steps deferred (the gate, the commit, ...)")
        self._finalise(key, actor, lambda e: L.render_pause(key, rows, deferred), "session.pause")
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

    def new(self, kind: str, title: str, *, session: str, actor: str, pri: str = "LATER", brief: str = "", deps: list[str] | None = None, body: str = "", extra: dict[str, Any] | None = None, rid: str = "") -> Record:
        """File a board item with the next free id, or with ``rid`` when an import keeps a number
        (`Q8` becomes ASK-8, FRAMEWORK §11.4): an id of the kind's series that was never used."""
        self._check(session, actor)
        if kind not in self._board():
            raise Refusal(f"{kind!r} is not a board kind", f"use one of {', '.join(self._board())}")
        if len(brief) > BRIEF_MAX:
            raise Refusal(f"the brief is {len(brief)} characters", f"cut it to {BRIEF_MAX}: a constraint, not a summary")
        for d in deps or []:
            self.store.find(d)
        self._cap_check(pri)
        fields: dict[str, Any] = {"title": title}
        if brief:
            fields["brief"] = brief
        fields.update(pri=pri, state="open", deps=list(deps or []), source=f"session {session}", created=self.today(), moved=session, updated=session)
        fields.update(extra or {})
        text = body if body.strip() else TASK_BODY.format(summary=title + ".")
        if rid:
            k = self.store.config.kind(kind)
            if not k.id_re.match(rid.strip()):
                raise Refusal(f"{rid} is not an id of the {k.name} series", f"give an id of the form {k.prefix}-n, or none for the next free one")
            return self.store.create_many(kind, [(rid.strip(), fields, text)], session=session, actor=actor, op="new")[0]
        return self.store.new(kind, fields, text, session=session, actor=actor)

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
            raise Refusal(
                f"{rid} is the last open item that ACTIVE-PLAN {'doc' if len(left) == 1 else 'docs'} {docs} {'names' if len(left) == 1 else 'name'}, so closing it would turn G-D4 red (FRAMEWORK §6.7: a plan freezes when its item closes)",
                f"freeze {'it' if len(left) == 1 else 'each'} first: {'; '.join(f'`doc freeze {d}`' for d in left)}; then close {rid} again (its commit carries the freeze)",
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
        extra: dict[str, Any] = {"last_asked": None}
        if blocks:
            extra["blocks"] = list(blocks)
        text = body if body.strip() else f"**Question:** {title}\n\n**Why owner-only:**\n\n**Options:**\n\n**Recommendation:** <the option, and why in a line; or \"none cheap: <why>\" (FRAMEWORK §5.3)>\n\n**Blocks:** {_one(blocks or [])}\n\n## Log\n"
        return self.new(self._role("question"), title, session=session, actor=actor, pri=pri, brief=brief, body=text, extra=extra, rid=rid)

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
    def ask_answer(self, rid: str, words: str, *, title: str, session: str, actor: str) -> str:
        """Record the owner's words verbatim as a decision (`actor: owner`), close the question,
        and report what it unblocked."""
        self._check(session, actor)
        self._is_question(rid)
        if not words.strip():
            raise Refusal("no owner words", "pass the owner's answer verbatim")
        q = self.store.get(rid)
        if q.doc.get("state") != "open":
            raise Refusal(f"{rid} is already closed", "record a new decision instead")
        if q.doc.get("answered"):
            # CE-31: open and answered is a by-hand reopen (G-W4); a second answer would make two
            # decisions answer one question and hide the G-W4 failure.
            raise Refusal(f"{rid} was already answered by the owner ({_answered_by(q.doc.get('answered'))}), so it takes no second answer (FRAMEWORK §5.3)",
                          f"restore `state: closed` and `status: deprecated` from git; {self._answered_remedy(rid, q.doc.get('answered'))}")
        fields = {"title": title, "actor": "owner", "decided": self.today(), "session": session, "decision_status": "PROVISIONAL", "answers": rid}
        body = f'Owner, answering {rid}: *"{words.strip()}"*\n'
        dec = self.store.new(self._role("decision"), fields, body, session=session, actor=actor)
        answered = {"on": self.today(), "session": session, "decision": dec.id}
        was: list[str] = []

        def check(rec: Record) -> None:
            was.append(str(rec.doc.get("pri")))

        self._board_set(rid, {"state": "closed", "status": "deprecated", "closed": session, "last_asked": session, "answered": answered}, session=session, actor=actor, check=check, body=self._log_line(session, actor, f"answered by the owner: {dec.id}"), op="ask.answer")
        closed = {r.id for r in self.board_heads() if r.doc.get("state") == "closed"}
        freed = [r.id for r in self._open_board() if rid in (r.doc.get("deps") or []) and all(str(d) in closed for d in r.doc.get("deps"))]
        freed += [str(b) for b in (q.doc.get("blocks") or []) if str(b) not in freed]
        return f"{rid}: answered as {dec.id}, closed; unblocked {_one(freed)}{self._now_left(was)}"

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

    def commit(self, paths: list[str], message: str, *, session: str, actor: str) -> str:
        """The session's own commit (FRAMEWORK §5.5 rule 4): ``paths`` by path, with every op log
        line HEAD lacks and the files they name, so a record is never committed without its op
        line, nor a line without its record. Whatever the policy. It runs no gate: the session
        runs the gate first, as before any commit."""
        self._check(session, actor)
        if not message.strip():
            raise Refusal("a commit with no message", "give one (`-m` on the CLI) whose title leads with the task id (FRAMEWORK §6.10); the engine adds the `Session:` trailer")
        other = [k for k in C.session_trailers(message) if k != session]
        if other:
            raise Refusal(f"the message's `Session:` trailer names {other[0]}, not this session ({session})", "drop the trailer, and the engine adds this session's")
        rels = [self._commit_path(x) for x in paths]
        GATE.check_commit(self.root, self.store.config.gate, rels)  # a code path needs a green gate run on its scope (CE-78)
        out = self.store.commit_paths(message, rels, session)
        if not out.sha:
            raise Refusal(f"not committed: {out.note or 'git made no commit'}",
                          "fix what it names and run it again; by hand: manual-mode.md § context-engine commit")
        extra = []
        if out.carried:
            extra.append(f"including op lines that {', '.join(out.carried)} left uncommitted")
        if out.left_out:
            extra.append(f"left out as gitignored: {', '.join(out.left_out)}")
        n = len(out.paths)
        return f"committed {out.sha}: {n} path{'s' if n != 1 else ''}" + (f" ({'; '.join(extra)})" if extra else "")

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
        carried = C.pending(self.root, self.store.config.oplog)
        for line in self._git("status", "--porcelain=v1", "--untracked-files=all").splitlines():
            path = line[3:].split(" -> ")[-1].strip('"')
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
    def record_new(self, kind: str, title: str, body: str, raw: dict[str, str], *, session: str, actor: str) -> Record:
        """A new decision or story, stamped when it is created. A required key the caller left out
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
        known, bad = G.known_goals(self)
        if known is not None and "G-I1" not in off:
            if not known:  # the charter is missing or yields no goal: no story's goals can be checked
                raise Refusal(f"no story can be checked against the charter: {bad[0].path}: {bad[0].message}", bad[0].remedy)
            problems += G.goal_problems(fields.get("goals"), known, legacy=False)  # the charter's own failures are lint's (G-I1)
        if problems:
            raise Refusal(f"the story {problems[0]}" + (f" (and {len(problems) - 1} more)" if len(problems) > 1 else ""), "pass `--set actor=owner` (or `human:<id>`), a `date` as YYYY-MM-DD or none for today, `story_status` from live, unspecified, unconfirmed (`retired`, `status: deprecated`, `supersedes` and `superseded_by` are set only by `record retire`), and `goals=[G-n, ...]` naming goals of the charter; a goal the charter lacks is an owner question (FRAMEWORK §6.2 step 2)")

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
        planned, notes = D.plan_import(src.read_bytes().decode("utf-8-sig"), kind.prefix, self.store.ids_in_use(kind), source, amap, before)
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
                f"there was one, stays in its `{ALIASES}` (FRAMEWORK §11.4).\n\n{D.id_map(planned)}"
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
        if dest.exists():
            raise Refusal(f"{dest_dir}/{p.name} exists already", "archive into another directory with --to, or by hand under a dated name (manual-mode.md § context-engine doc archive)")
        if not self._git("ls-files", "--", rel).strip():
            raise Refusal(f"{rel} is not tracked by git", "commit it first (an archive moves tracked material, `git mv`, so its history follows it), or delete it if it was never worth keeping")
        if self._git("status", "--porcelain=v1", "--", rel).strip():
            raise Refusal(f"{rel} has uncommitted changes", "commit them, or undo them, first: an archive moves the material as it stands in git, never repaired (FRAMEWORK §7.3)")
        text = self._utf8(p, rel)
        if text.lstrip("\ufeff").startswith("---"):
            raise Refusal(f"{rel} opens with frontmatter, so `ARCHIVED <date>` cannot be its first line", "archive it by hand, the ARCHIVED line first after the frontmatter (manual-mode.md § context-engine doc archive)")
        today = self.today().isoformat()
        name = PurePosixPath(dest_dir, p.name).as_posix()
        table = self.root / dest_dir / A.REDIRECTS
        with self.store.lock():
            dest.parent.mkdir(parents=True, exist_ok=True)
            self.store.write_text(dest, A.archived(text, today, session, rel))
            p.unlink()
            old = self._utf8(table, f"{dest_dir}/{A.REDIRECTS}") if table.exists() else None
            self.store.write_text(table, A.redirects(old, dest_dir, A.redirect_row(rel, p.name, today, session, why)))
            self.store.log("doc.archive", rel, p, session, actor, ["moved"])
            self.store.log("doc.archive", rel, dest, session, actor, ["archived"])
            self.store.log("doc.archive", rel, table, session, actor, ["redirect"])
        cfg = (self.root / CONFIG_NAME).read_text(encoding="utf-8") if (self.root / CONFIG_NAME).exists() else ""
        warn = f"; context.toml still names {rel}: point it at {name} or drop it, or lint is red (G-R1, G-D4)" if f'"{rel}"' in cfg else ""
        return f"{rel}: archived as {name} (first line ARCHIVED {today}), row added to {dest_dir}/{A.REDIRECTS}{warn}"

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
            path.parent.mkdir(parents=True, exist_ok=True)
            self.store.write_text(path, L.replace_banner(note, session, text))
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
        sections.append(Part("Other open sessions: show the owner, one line each", "\n".join(f"- {e.key}, opened {e.field('opened')}" for e in others) or "none", f'`grep -n "kind: open" {self.w.ledger}`', rank=0))

        top = [ln for ln in self.list(pri="NOW")]
        sections.append(Part("Board: NOW and NEXT", "\n".join(top + self.list(pri="NEXT")) or "empty", "`context-engine task list`", rank=1))

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
            sections.append(Part("Top item", "no NOW item", "`context-engine task list`", rank=2))
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


class Part(NamedTuple):
    """One orient section: its heading, its body, where the rest is when the body is cut, and its
    claim on the cap (lower ``rank`` is served first)."""

    title: str
    body: str
    rest: str
    rank: int = 0


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
