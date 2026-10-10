"""One function per operation (FRAMEWORK §8.0.2, AC-18). The CLI (``cli.run``) and the MCP
server (``mcp``) both look the operation up in ``OPS`` and call it, so neither holds its own
copy of what an operation does: they only turn their arguments into the parameters below.

Each function takes the engine, the ``Caller`` (session key and actor), then plain parameters
(str, int, bool, lists, a str->str dict) that both entry points can supply. It returns
``(exit code, text)``: a write's text is one line (AC-19), a read's text is uncapped here and
capped by the MCP server, which points at ``Op.rest`` for what was cut.

Deliberately not here: argument parsing, reading ``--file`` paths, and printing.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Callable

from .working import Engine


@dataclass
class Caller:
    """Who is calling. ``session_start`` fills ``session`` in, so the MCP server can remember it."""

    session: str | None = None
    actor: str | None = None

    @property
    def kw(self) -> dict[str, str | None]:
        return {"session": self.session, "actor": self.actor}


@dataclass(frozen=True)
class Op:
    name: str  # the MCP tool name: `<group>_<verb>`, underscored (DEC-15)
    fn: Callable[..., tuple[int, str]]
    write: bool
    rest: str = ""  # reads: where to get what the MCP cap cut

    @property
    def params(self) -> list[inspect.Parameter]:
        """The operation's own parameters, after the engine and the caller."""
        return list(inspect.signature(self.fn, eval_str=True).parameters.values())[2:]


OPS: dict[str, Op] = {}


def op(*, write: bool, rest: str = ""):
    def register(fn):
        OPS[fn.__name__] = Op(fn.__name__, fn, write, rest)
        return fn

    return register


def _rel(e: Engine, path) -> str:
    return path.relative_to(e.root).as_posix()


# -- sessions (FRAMEWORK §6.1, §6.3, §6.4) ---------------------------------------------


@op(write=True)
def session_start(e: Engine, c: Caller) -> tuple[int, str]:
    """Open a framework session: mint its key and write the ledger stub. Call it first, every session."""
    c.session = e.session_start(actor=c.actor)
    return 0, f"session {c.session} opened (stub written to {e.w.ledger}); pass --session {c.session} or set CE_SESSION={c.session}"


@op(write=True)
def session_close(e: Engine, c: Caller, rows: str, summary: list[str], guards: str, read: str, asked: str = "", owed: list[str] | None = None) -> tuple[int, str]:
    """Clean close: finalise this session's ledger stub. `summary` is the owner digest, at most 7 lines."""
    receipts = {"guards": guards, "read": read, "asked": asked}
    return 0, e.session_close(c.session, actor=c.actor, rows=rows, summary=summary, receipts=receipts, owed=owed or [])


@op(write=True)
def session_pause(e: Engine, c: Caller, rows: str, deferred: str) -> tuple[int, str]:
    """Pause: write a pause entry instead of a clean close; `deferred` names what was skipped."""
    return 0, e.session_pause(c.session, actor=c.actor, rows=rows, deferred=deferred)


# -- reads ------------------------------------------------------------------------------


@op(write=False)
def orient(e: Engine, c: Caller) -> tuple[int, str]:
    """The session-start read in one capped response: banner, batons and pauses, the board's NOW and NEXT, questions to raise, the top item."""
    return 0, e.orient(c.session).rstrip("\n")


@op(write=False, rest="`context-engine routes` in a shell")
def routes(e: Engine, c: Caller) -> tuple[int, str]:
    """Where each framework component lives and how it may change, one line each."""
    return 0, e.routes()


@op(write=False, rest="`context-engine lint` in a shell")
def lint(e: Engine, c: Caller, working: bool = False) -> tuple[int, str]:
    """Failures only, each with its remedy; `working` runs the working-state guards alone."""
    failures = e.lint_working() if working else e.lint()
    return (1 if failures else 0), "\n".join(map(str, failures)) or "lint: clean"


# -- the board (FRAMEWORK §5.2) -----------------------------------------------------------


@op(write=True)
def task_new(e: Engine, c: Caller, title: str, kind: str = "task", pri: str = "LATER", brief: str = "", deps: list[str] | None = None, body: str = "") -> tuple[int, str]:
    """File a board item. `brief` is a constraint, not a summary (at most 120 characters)."""
    rec = e.new(kind, title, pri=pri, brief=brief, deps=deps or [], body=body, **c.kw)
    return 0, f"{rec.id}: created at {pri} ({_rel(e, rec.path)})"


@op(write=True)
def task_set(e: Engine, c: Caller, id: str, fields: dict[str, str] | None = None, unset: list[str] | None = None, mechanical: bool = False) -> tuple[int, str]:
    """Set or unset frontmatter fields the operations do not own (e.g. brief, labels)."""
    return 0, e.set(id, fields or {}, unset=tuple(unset or ()), mechanical=mechanical, **c.kw)


@op(write=True)
def task_promote(e: Engine, c: Caller, id: str, pri: str) -> tuple[int, str]:
    """Move an item to another tier; NOW holds exactly one, NEXT at most five."""
    return 0, e.promote(id, pri, **c.kw)


@op(write=True)
def task_dep(e: Engine, c: Caller, id: str, add: list[str] | None = None, remove: list[str] | None = None) -> tuple[int, str]:
    """Add or remove dependencies by id."""
    return 0, e.dep(id, add=add or [], remove=remove or [], **c.kw)


@op(write=True)
def task_comment(e: Engine, c: Caller, id: str, text: str, mechanical: bool = False) -> tuple[int, str]:
    """Append one dated line to the item's ## Log."""
    return 0, e.comment(id, text, mechanical=mechanical, **c.kw)


@op(write=True)
def task_touch(e: Engine, c: Caller, id: str, mechanical: bool = False) -> tuple[int, str]:
    """Mark the item as moved this session without changing anything else."""
    return 0, e.touch(id, mechanical=mechanical, **c.kw)


@op(write=True)
def task_close(e: Engine, c: Caller, id: str, msg: str = "") -> tuple[int, str]:
    """Close an item; `msg` says what finished it and is required."""
    return 0, e.close(id, msg, **c.kw)


@op(write=True)
def task_reopen(e: Engine, c: Caller, id: str, msg: str = "") -> tuple[int, str]:
    """Reopen a closed item; `msg` says why."""
    return 0, e.reopen(id, msg, **c.kw)


@op(write=True)
def task_section(e: Engine, c: Caller, id: str, name: str, text: str) -> tuple[int, str]:
    """Replace one named ## section of the item's body (not ## Log: use task_comment)."""
    return 0, e.section(id, name, text, **c.kw)


@op(write=False, rest="narrow it with `pri`, `state` or `label`")
def task_list(e: Engine, c: Caller, state: str = "open", pri: str | None = None, label: str | None = None) -> tuple[int, str]:
    """The board, one line per item, by tier then id. `state` is open, closed or all."""
    rows = e.list(state=None if state == "all" else state, pri=pri, label=label)
    return 0, "\n".join(rows) or "no matching items"


@op(write=False, rest="ask for one `section`, or a smaller `head`")
def task_show(e: Engine, c: Caller, id: str, section: str | None = None, head: int = 5) -> tuple[int, str]:
    """One item: its head line, then its body or one `section`; ## Log shows the newest `head` entries (0 for all)."""
    return 0, e.show(id, section=section, head=head).rstrip("\n")


# -- owner questions (FRAMEWORK §5.3) -----------------------------------------------------


@op(write=True)
def ask_new(e: Engine, c: Caller, title: str, pri: str = "NEXT", brief: str = "", blocks: list[str] | None = None, body: str = "") -> tuple[int, str]:
    """File an owner question (ASK-n); raise it in chat this session."""
    rec = e.ask_new(title, pri=pri, brief=brief, body=body, blocks=blocks or [], **c.kw)
    return 0, f"{rec.id}: question created at {pri}; raise it in chat this session"


@op(write=True)
def ask_raised(e: Engine, c: Caller, ids: list[str]) -> tuple[int, str]:
    """Record that these questions were raised in chat this session."""
    return 0, e.ask_raised(ids, **c.kw)


@op(write=True)
def ask_later(e: Engine, c: Caller, id: str) -> tuple[int, str]:
    """The owner deferred the question: stop it counting as overdue for now."""
    return 0, e.ask_later(id, **c.kw)


@op(write=True)
def ask_answer(e: Engine, c: Caller, id: str, words: str, title: str) -> tuple[int, str]:
    """Record the owner's answer, verbatim, as a decision titled `title`, and close the question."""
    return 0, e.ask_answer(id, words, title=title, **c.kw)


# -- batons and pauses (FRAMEWORK §5.4) --------------------------------------------------


@op(write=True)
def baton_add(e: Engine, c: Caller, step: str, why: str = "") -> tuple[int, str]:
    """Hand a skipped step to the next session."""
    return 0, e.baton_add(step, why, **c.kw)


@op(write=True)
def baton_done(e: Engine, c: Caller, id: str, evidence: str) -> tuple[int, str]:
    """Close a baton (any session may); `evidence` says how it was done."""
    return 0, e.baton_done(id, evidence, **c.kw)


@op(write=True)
def hk_expire_batons(e: Engine, c: Caller) -> tuple[int, str]:
    """Housekeeping: turn batons and pauses older than two sessions into tasks."""
    return 0, e.expire_batons(session=c.session, actor=c.actor or "process:housekeep")


@op(write=True)
def pause_open(e: Engine, c: Caller, in_flight: str, resume: str, evidence: str = "", deferred: list[str] | None = None) -> tuple[int, str]:
    """Record a pause block (branch and dirty paths from git) and commit it."""
    return 0, e.pause_open(in_flight, resume, evidence=evidence, deferred=deferred or [], **c.kw)


@op(write=True)
def pause_resume(e: Engine, c: Caller, id: str) -> tuple[int, str]:
    """Pick a pause back up and mark it done."""
    return 0, e.pause_resume(id, **c.kw)


# -- append-only records (FRAMEWORK §8.0.1) ----------------------------------------------


@op(write=True)
def record_new(e: Engine, c: Caller, kind: str, title: str, body: str, fields: dict[str, str] | None = None) -> tuple[int, str]:
    """A new decision or story, stamped at birth. Owner words go in `body` verbatim; set actor=owner in `fields`."""
    rec = e.record_new(kind, title, body, fields or {}, **c.kw)
    return 0, f"{rec.id}: created and stamped ({_rel(e, rec.path)})"


@op(write=True)
def record_stamp(e: Engine, c: Caller, ids: list[str]) -> tuple[int, str]:
    """Stamp `body_sha` on unstamped append-only records; all or nothing."""
    return 0, e.stamp(ids, **c.kw)


@op(write=True)
def record_amend(e: Engine, c: Caller, id: str, text: str) -> tuple[int, str]:
    """Append a dated entry under ## Amendments: the only change an append-only body takes."""
    return 0, e.amend(id, text, **c.kw)


# -- the banner (FRAMEWORK §5.5) ----------------------------------------------------------


@op(write=False, rest="the note's § Banner")
def banner_show(e: Engine, c: Caller) -> tuple[int, str]:
    """The banner and its hash; pass the hash to banner_set."""
    b = e.banner()
    if b is None:
        return 0, f"no note at {e.w.handoff}"
    return 0, f"banner {b.key} hash {b.sha}\n\n{b.text}"


@op(write=True)
def banner_set(e: Engine, c: Caller, text: str, seen: str) -> tuple[int, str]:
    """Replace the banner; `seen` is the hash banner_show printed, so another session's banner is never overwritten."""
    return 0, e.banner_set(text, seen, **c.kw)
