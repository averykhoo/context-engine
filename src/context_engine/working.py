"""Working-state operations: sessions, the board, owner questions, batons, pauses, the banner,
``orient()`` and the working-state guards (FRAMEWORK §5, §6.1, §6.3, §6.4, §8.4).

Every operation here is one function that the CLI (and, in CE-3, the MCP server) calls. Each
write goes through the store, so it is checked against its kind's schema, made under the repo
lock and logged with the session key and the actor. Every write returns one line.

Which kinds play which part is configured in ``[working]`` of ``context.toml``; an operation
whose part is not configured refuses and says so.

Deliberately not handled here: marking a dead session's stub ``abandoned`` and its window
(G-W11; housekeeping, CE-6), rotating the ledger, and the `hk_` operations other than baton
expiry (CE-6).
"""

from __future__ import annotations

import datetime as dt
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Callable

from . import __version__
from . import decisions as D
from . import guards as G
from . import ledger as L
from . import okf
from . import review as R
from .bootstrap import ANY_BEGIN  # the kit block's begin marker, any version
from .config import Config
from .errors import Refusal
from .store import ACTOR_RE, Failure, Record, Store, _now, amended, coerce, key_order

ID_RE = re.compile(r"\b[A-Z]+-\d+\b")
CRITERION_ROW_RE = re.compile(r"^\|\s*([A-Z]+-\d+)\s*\|", re.MULTILINE)
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
TASK_BODY = "{summary}\n\n## Traps\n\n- none yet\n\n## Read first\n\n- none yet\n\n## Log\n"
SHOW_LOG_HEAD = 5
LINK_RELS = ("tasks", "creates", "amends", "retires", "relaxes", "code", "refs")  # what `decision link` writes
HOUSEKEEPER = "process:housekeep"


def answered_remedy(rid: str, dec: str) -> str:
    """What to do instead of reopening an answered question (CE-31): the answer is a decision."""
    return (f"the owner's answer is {dec}: change it with `record amend {dec} \"<words>\"` or replace it "
            f"with `decision supersede {dec} <new DEC>`; for a follow-up, `ask new \"<question>\"` citing {rid} and {dec}")


def _answered_by(answered: Any) -> str:
    """The decision id in a question's `answered:` mapping, or a placeholder."""
    return str(answered.get("decision") or "<DEC>") if isinstance(answered, dict) else "<DEC>"


def _one(items) -> str:
    return ", ".join(items) if items else "none"


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
            raise Refusal(f"no kind plays the {role} part", f"set `{role} = \"<kind>\"` in [working] of context.toml")
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

    def session_pause(self, key: str, *, actor: str, rows: str, deferred: str) -> str:
        """A three-line ``kind: pause`` entry over the stub (FRAMEWORK §6.4, AC-11)."""
        self._check(key, actor)
        if not rows.strip() or not deferred.strip():
            raise Refusal("a pause needs rows and deferred", "name the items touched and the steps deferred (the gate, the commit, ...)")
        self._finalise(key, actor, lambda e: L.render_pause(key, rows, deferred), "session.pause")
        return f"session {key} paused: ledger entry written"

    # -- the board (FRAMEWORK §5.2) -----------------------------------------------------

    def _cap_check(self, pri: str, exclude: str | None = None) -> None:
        cap = self.w.caps.get(pri)
        if cap is None:
            return
        holders = [r.id for r in self._open_board() if r.doc.get("pri") == pri and r.id != exclude]
        if len(holders) >= cap:
            raise Refusal(f"{pri} already holds {len(holders)} of {cap} ({_one(holders)})", f"demote one with `promote <id> LATER` first")

    def new(self, kind: str, title: str, *, session: str, actor: str, pri: str = "LATER", brief: str = "", deps: list[str] | None = None, body: str = "", extra: dict[str, Any] | None = None) -> Record:
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
        check = None
        if "review" in changes or "review" in unset:
            review = None if "review" in unset else changes["review"]

            def check(rec: Record) -> None:
                if not review:
                    self._review_kept(rec)
                else:
                    self._review_ready_at_now(rec, rec.doc.body, review)

        self._board_set(rid, changes, session=session, actor=actor, unset=unset, check=check, mechanical=mechanical)
        return f"{rid}: set {_one([*raw, *unset])}"

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
        return f"{rid}: {old[0]} -> {pri}"

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

    def close(self, rid: str, msg: str, *, session: str, actor: str) -> str:
        """``state: closed`` and the derived OKF ``status: deprecated``, in place (AC-12)."""
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

        def check(rec: Record) -> None:
            if rec.doc.get("state") == "closed":
                raise Refusal(f"{rid} is already closed", "nothing to do; `reopen` it if it is not done")
            if rec.doc.get("review"):
                filed.extend(self._file_residuals(rec, session, actor))

        changes = {"state": "closed", "status": "deprecated", "closed": session, "moved": session}
        self._board_set(rid, changes, session=session, actor=actor, check=check, body=self._log_line(session, actor, f"closed: {msg.strip()}"), op="close")
        moved = f"; residuals filed as {', '.join(filed)}" if filed else ""
        return f"{rid}: closed ({msg.strip().splitlines()[0][:80]}){moved}"

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
                raise Refusal(f"{rid} was answered by the owner, and an answered question never reopens (FRAMEWORK §5.3)", answered_remedy(rid, _answered_by(answered)))

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
        rec = self.store.get(rid)
        d = rec.doc
        top = f"{rid} · {d.get('pri')} · {d.get('state')} · {d.get('title')}\n"
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

    def ask_new(self, title: str, *, session: str, actor: str, pri: str = "NEXT", brief: str = "", body: str = "", blocks: list[str] | None = None) -> Record:
        extra: dict[str, Any] = {"last_asked": None}
        if blocks:
            extra["blocks"] = list(blocks)
        text = body if body.strip() else f"**Question:** {title}\n\n**Why owner-only:**\n\n**Options:**\n\n**Blocks:** {_one(blocks or [])}\n\n## Log\n"
        return self.new(self._role("question"), title, session=session, actor=actor, pri=pri, brief=brief, body=text, extra=extra)

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
                raise Refusal(f"session {session} closed while raising", "record the receipt by hand in the ledger entry")
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
        fields = {"title": title, "actor": "owner", "decided": self.today(), "session": session, "decision_status": "PROVISIONAL", "answers": rid}
        body = f'Owner, answering {rid}: *"{words.strip()}"*\n'
        dec = self.store.new(self._role("decision"), fields, body, session=session, actor=actor)
        answered = {"on": self.today(), "session": session, "decision": dec.id}
        self._board_set(rid, {"state": "closed", "status": "deprecated", "closed": session, "last_asked": session, "answered": answered}, session=session, actor=actor, body=self._log_line(session, actor, f"answered by the owner: {dec.id}"), op="ask.answer")
        closed = {r.id for r in self.board_heads() if r.doc.get("state") == "closed"}
        freed = [r.id for r in self._open_board() if rid in (r.doc.get("deps") or []) and all(str(d) in closed for d in r.doc.get("deps"))]
        freed += [str(b) for b in (q.doc.get("blocks") or []) if str(b) not in freed]
        return f"{rid}: answered as {dec.id}, closed; unblocked {_one(freed)}"

    # -- batons and pauses (FRAMEWORK §5.4) ---------------------------------------------

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

    def _git(self, *args: str) -> str:
        try:
            p = subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True, encoding="utf-8")
        except FileNotFoundError:
            raise Refusal("git is not installed", "install git, or write the pause block by hand") from None
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
        for line in self._git("status", "--porcelain=v1", "--untracked-files=all").splitlines():
            path = line[3:]
            dirty.append(path.split(" -> ")[-1].strip('"'))
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
        rec = self.store.new(self._role("pause"), fields, body, session=session, actor=actor)
        rel = rec.path.relative_to(self.root).as_posix()
        self._git("add", "--", rel)
        # every agent commit ends with a `Session:` trailer (DEC-22); the second -m is its own paragraph
        self._git("commit", "-q", "--only", "-m", f"pause {rec.id} ({session}): {fields['title'][:60]}", "-m", f"Session: {session}", "--", rel)
        sha = self._git("rev-parse", "--short", "HEAD").strip()
        return f"{rec.id}: pause recorded on {branch} ({len(dirty)} uncommitted paths), committed {sha}"

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

    def record_new(self, kind: str, title: str, body: str, raw: dict[str, str], *, session: str, actor: str) -> Record:
        """A new decision or story, stamped at birth. A required key the caller left out is filled
        when it can only mean now: a date-typed key with today, a key-typed one with this session."""
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
        return self.store.new(kind, fields, body.strip("\n") + "\n", session=session, actor=actor)

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

    def amend(self, rid: str, text: str, *, session: str, actor: str) -> str:
        """Append a dated entry under ``## Amendments``; the text above it never changes."""
        self.store.amend(rid, text, session=session, actor=actor)
        return f"{rid}: amendment added under ## Amendments"

    def correct(self, rid: str, after: str, text: str, *, session: str, actor: str) -> str:
        """A bracketed insertion into an append-only record (DEC-13): insert-only and logged; the
        stamp is kept, since it pins the words as typed."""
        _, inserted = self.store.correct(rid, after, text, session=session, actor=actor)
        return f"{rid}: inserted {inserted!r} after {after[-40:]!r}; `corrected:` logged under ## Amendments; body_sha unchanged (the words as typed)"

    # -- decisions (FRAMEWORK §6.5, CE-5) -----------------------------------------------

    def _decision_kind(self) -> str:
        return self._role("decision")

    def _is_decision(self, rid: str) -> None:
        if self.store.config.kind_for_id(rid).name != self._decision_kind():
            raise Refusal(f"{rid} is not a decision", f"name a {self.store.config.kind(self._decision_kind()).prefix}-n record")

    def supersede(self, old: str, new: str, *, session: str, actor: str) -> str:
        """``new`` replaces ``old``: both directions are written under one lock, and ``old``
        becomes SUPERSEDED with the derived OKF ``status: deprecated``."""
        self._check(session, actor)
        self._is_decision(old)
        self._is_decision(new)
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
        return f"{old}: SUPERSEDED by {new} (status: deprecated); {new} supersedes {old}"

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
        """A `file` or `file::symbol` link: the file exists, case-exact, and names each part of the symbol."""
        file, _, symbol = target.partition("::")
        here = G.Files(self.root).case_exact(file)
        if here is None:
            raise Refusal(f"{file} does not exist (case-exact) in the repo", "link a file that exists, with its exact case")
        missing = G.symbol_missing(here, symbol) if symbol else None
        if missing:
            raise Refusal(f"{file} has no {missing!r}", "grep for the symbol and link the name that exists")

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
        self._is_decision(rid)
        target = target.strip()
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
        return f"{rid}: {rel} + {target}" + (f"; {target}: narrowed_by + {rid}" if rel == "relaxes" else "")

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
        recs = self.store.records(kind) if text else self.store.heads(kind)
        for r in sorted(recs, key=lambda r: int(r.id.rsplit("-", 1)[1])):
            d = r.doc
            if status and str(d.get(D.STATUS_KEY)).upper() != status.upper():
                continue
            if tag and tag not in D.as_list(d.get("tags")):
                continue
            if links_to and not self._links_to(d, links_to):
                continue
            if text and text.lower() not in " ".join(str(x) for x in (r.id, d.get("title"), d.get("description") or "", d.body)).lower():
                continue
            out.append(self._row(r))
        return out

    def decision_show(self, rid: str, section: str | None = None) -> str:
        """One decision: a head line, its links, then its body or one `## section` (`decision.show`)."""
        self._is_decision(rid)
        rec = self.store.get(rid)
        d = rec.doc
        top = f"{rid} · {d.get(D.STATUS_KEY)} · {d.get('title')}\n"
        top += "".join(f"{k}: {d.get(k)}\n" for k in ("actor", "decided", "session") if d.get(k))
        top += "".join(f"{k}: {', '.join(D.as_list(d.get(k)))}\n" for k in (*D.LINK_FIELDS, "tags", "answers") if D.as_list(d.get(k)))
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
            raise Refusal("why what?", "name a task, criterion, decision or `file::symbol`")
        out = []
        for r in sorted(self.store.heads(self._decision_kind()), key=lambda r: int(r.id.rsplit("-", 1)[1])):
            via = self._links_to(r.doc, target)
            if via:
                out.append(f"{self._row(r)}  via {', '.join(via)}")
        return out

    def reindex(self, *, session: str, actor: str) -> str:
        changed = self.store.reindex(session=session, actor=actor)
        return f"{self.w.decision_index}: {'regenerated' if changed else 'already current'}"

    def import_log(self, path: str, *, session: str, actor: str, dry_run: bool = False) -> str:
        """Import a single-file decision log (FRAMEWORK §11.4): every entry keeps its id and its
        text, stamped; the rejected table's rows become REJECTED records. All or nothing."""
        self._check(session, actor)
        kind = self.store.config.kind(self._decision_kind())
        src = Path(path) if Path(path).is_absolute() else self.root / path
        if not src.is_file():
            raise Refusal(f"no file {path}", "give the path of the single-file log (a copy, for a trial)")
        try:
            source = src.resolve().relative_to(self.root).as_posix()
        except ValueError:
            source = src.name
        planned, notes = D.plan_import(src.read_bytes().decode("utf-8-sig"), kind.prefix, self.store.ids_in_use(kind), source)
        items = []
        for e in planned:
            f = e.fields
            fields: dict[str, Any] = {"title": f["title"], "actor": f["actor"], "decided": f["decided"], "session": session, D.STATUS_KEY: f["decision_status"]}
            if f["decision_status"] == "SUPERSEDED":
                fields["status"] = "deprecated"
            fields.update({k: e.links[k] for k in D.LINK_FIELDS if e.links.get(k)})
            fields.update({k: f[k] for k in ("attribution", "imported_from") if f.get(k)})
            body = amended(e.body, f"imported heading note: {e.note}", session, actor) if e.note else e.body
            items.append((e.id, fields, body))
        summary = "; ".join(notes)
        if dry_run:
            return f"dry run, nothing written: would import {summary} into {kind.dir}"
        self.store.create_many(kind.name, items, session=session, actor=actor, op="import")
        return f"imported {summary} into {kind.dir}, each stamped" + (f"; index {self.w.decision_index} regenerated" if self.w.decision_index else "")

    # -- banner (FRAMEWORK §5.5 rule 2) -------------------------------------------------

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
        return f"banner {'replaced' if now else 'written (the first)'}, key {session}, new hash {self.banner().sha}"

    # -- orient (FRAMEWORK §6.1) --------------------------------------------------------

    def orient(self, session: str | None = None) -> str:
        """The session-start read in one response, never over ``orient_max_bytes`` (AC-17)."""
        led = self.read_ledger()
        b = self.banner()
        sections: list[tuple[str, str, str]] = []  # (heading, body, where the rest is)
        note = self.w.handoff or "the note"
        sections.append((f"Banner ({b.key})" if b else "Banner", b.text if b else "no banner", f"{note} § Banner"))

        carried = sorted(self._carried(), key=lambda r: (r.doc.get("session") != session, r.kind.prefix, int(r.id.rsplit("-", 1)[1])))
        lines = []
        for r in carried:
            own = " (yours)" if session and r.doc.get("session") == session else ""
            line = f"- {r.id} from {r.doc.get('session')}{own}: {r.doc.get('title')}"
            if r.doc.get("resume_step"):
                line += f"\n  resume: {r.doc.get('resume_step')} (branch {r.doc.get('branch')})"
            lines.append(line)
        sections.append(("Batons and pauses: do these first", "\n".join(lines) or "none", "`context-engine task show <id>` on each"))

        others = [e for e in led.entries if e.kind == "open" and e.key != session]
        sections.append(("Other open sessions: show the owner, one line each", "\n".join(f"- {e.key}, opened {e.field('opened')}" for e in others) or "none", self.w.ledger))

        top = [ln for ln in self.list(pri="NOW")]
        sections.append(("Board: NOW and NEXT", "\n".join(top + self.list(pri="NEXT")) or "empty", "`context-engine task list`"))

        pending, overdue = self._pending_asks(led)
        qs = {q.id: q for q in self._questions()}
        raise_ = [f"- {i}: {qs[i].doc.get('title')} (last asked {qs[i].doc.get('last_asked') or 'never'}{', overdue' if i in overdue else ''})" for i in dict.fromkeys(pending + overdue)]
        sections.append(("Raise in chat now, one line each", "\n".join(raise_) or "none", "`context-engine task list --pri NEXT`"))

        now = [r for r in self._open_board() if r.doc.get("pri") == "NOW"]
        if now:
            rec = self.store.get(now[0].id)
            body = rec.doc.body.replace("\r\n", "\n")
            parts = [f"brief: {rec.doc.get('brief') or 'none'}"]
            for name in ("Traps", "Read first"):
                parts.append(f"{name}:\n{okf.get_section(body, name) or 'none'}")
            sections.append((f"Top item: {rec.id} {rec.doc.get('title')}", "\n\n".join(parts), f"`context-engine task show {rec.id}`"))
        else:
            sections.append(("Top item", "no NOW item", "`context-engine task list`"))
        pointer = self._engine_register_line()
        if pointer:
            sections.append(("Engine register", pointer, "`context-engine register show --engine`"))
        head = f"# orient {session or '(no session)'}\n"
        return fit(head, sections, self.w.orient_max_bytes)

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
        """G-R1: every routed path exists, so the table never points at a file that moved."""
        return [
            Failure("G-R1", "context.toml", f"route {r.component!r} points at {r.path}, which does not exist", "fix the path in [[routes]], or restore the file")
            for r in self.store.config.routes
            if not r.optional and not (self.root / r.path).exists()
        ]

    def lint_contract(self, version: str = __version__) -> list[Failure]:
        """G-D0 (DEC-23): every `framework:` line in the contract, and the version in its kit
        block's begin marker, equal the installed engine's major.minor. `0.5.*` is a synonym of
        `0.5`. A missing contract, a contract with no `framework:` line, or a value that is not
        `major.minor` is a red too: the pin is what says which engine the repo's rules assume."""
        rel = self.store.config.contract
        m = VERSION_RE.match(version)
        assert m, f"engine version {version!r} has no major.minor"
        want = f"{m['major']}.{m['minor']}"
        path = self.root / rel if rel else None
        if path is None or not path.is_file():
            return [Failure("G-D0", rel or "context.toml", f"the contract {rel or '([engine] contract is empty)'} does not exist", f"create it with a `framework: {want}` line, or point `contract` in [engine] of context.toml at the repo's contract")]
        text = path.read_bytes().decode("utf-8-sig")
        out: list[Failure] = []
        pins = FRAMEWORK_LINE_RE.findall(text)
        if not pins:
            out.append(Failure("G-D0", rel, "has no `framework:` line, so nothing says which framework version its rules assume", f"add `framework: {want}` on a line of its own (the installed engine is {version})"))
        for value in pins:
            v = PIN_RE.fullmatch(value)
            if not v:
                out.append(Failure("G-D0", rel, f"`framework: {value}` is not a major.minor version", f"write it as `framework: {want}` (or `{want}.*`): the framework has no patch number and no `-draft` suffix (DEC-23)"))
            elif (have := f"{v['major']}.{v['minor']}") != want:
                out.append(Failure("G-D0", rel, f"`framework: {value}` does not match the installed engine {version} (framework {want})", f"if the repo has moved to framework {want}, follow the upgrade ritual (FRAMEWORK §8.0; kit README § Upgrade) and set `framework: {want}`; otherwise run an engine {have}.x"))
        for marker in ANY_BEGIN.findall(text):
            if marker != want:
                out.append(Failure("G-D0", rel, f"holds the kit {marker} contract block, but the installed engine is framework {want}", f"replace the block between its markers with the engine's kit/contract.md (kit README § Upgrade), or run an engine {marker}.x"))
        return out

    def lint_working(self) -> list[Failure]:
        out: list[Failure] = []
        led = self.read_ledger() if self.w.ledger else None
        ledger_rel = self.w.ledger
        if led is not None:
            closes = [e for e in led.entries if e.kind == "close"]
            b = self.banner() if self.w.handoff else None
            if closes and self.w.handoff:
                newest_close = max((e.key for e in closes), key=key_order)
                if b is None:  # a session closed, so a banner is owed: a missing or renamed heading is a red
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
                    out.append(Failure("G-W4", rel, f"{r.id} is open but carries `answered:` ({dec})", f"restore `state: closed` and `status: deprecated` from git: {answered_remedy(r.id, dec)}"))
                if state == "open":
                    open_.append(r)
            for pri, cap in self.w.caps.items():
                holders = [r.id for r in open_ if r.doc.get("pri") == pri]
                if len(holders) > cap or (pri == "NOW" and open_ and len(holders) != cap):
                    rule = f"exactly {cap}" if pri == "NOW" else f"at most {cap}"
                    out.append(Failure("G-W5", self.store.config.kind(self.w.board[0]).dir, f"{pri} holds {len(holders)} ({_one(holders)}); the cap is {rule}", "re-rank with `promote`"))
            out += self.lint_review()
        return out


def fit(head: str, sections: list[tuple[str, str, str]], cap: int) -> str:
    """Join the sections under ``cap`` bytes. Every heading always appears; a body that does not
    fit is cut at a line and says where the rest is. Earlier sections are served first."""
    out = head
    for i, (title, body, rest) in enumerate(sections):
        heading = f"\n## {title}\n"
        reserve = sum(len(f"\n## {t}\n".encode()) + len(_cut_note(r).encode()) for t, _, r in sections[i + 1 :])
        budget = cap - len(out.encode()) - len(heading.encode()) - reserve
        text = body.rstrip("\n") + "\n"
        if len(text.encode()) > budget:
            note = _cut_note(rest)
            keep = []
            size = len(note.encode())
            for line in text.splitlines(keepends=True):
                if size + len(line.encode()) > budget:
                    break
                keep.append(line)
                size += len(line.encode())
            text = "".join(keep) + note if size <= budget else ""
        out += heading + text
    return out


def _cut_note(rest: str) -> str:
    return f"[cut at the orient cap; the rest: {rest}]\n"
