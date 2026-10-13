"""One function per operation (FRAMEWORK §8.0.2, AC-18). The CLI (``cli.run``) and the MCP
server (``mcp``) both look the operation up in ``OPS`` and run it with ``Op.call``, so neither
holds its own copy of what an operation does (nor of the commit that follows a write): they only
turn their arguments into the parameters below.

Each function takes the engine, the ``Caller`` (session key and actor), then plain parameters
(str, int, bool, lists, a str->str dict) that both entry points can supply. It returns
``(exit code, text)``: a write's text is one line (AC-19), a read's text is uncapped here and
capped by the MCP server, which points at ``Op.rest`` for what was cut.

Deliberately not here: argument parsing, reading ``--file`` paths, and printing.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from . import bootstrap
from . import ledger as L
from .commit import Outcome
from .errors import Refusal
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
    engine: bool = True  # False: the function takes the repo root (a Path) instead of an Engine, as `init` does

    def target(self, root) -> "Engine | Path":
        """What the function's first parameter gets: an Engine on ``root``, or the root itself."""
        return Engine(root) if self.engine else Path(root)

    def call(self, target: "Engine | Path", c: "Caller", /, **kw) -> tuple[int, str]:
        """Run the operation on ``target`` (from ``self.target``), as the CLI and the MCP server
        both do. A write runs in one store batch, so everything it wrote is committed once, by
        path, with its op log lines (FRAMEWORK §5.5 rule 4), and its line says what the commit did."""
        if not (self.write and self.engine):
            return self.fn(target, c, **kw)
        store = target.store
        store.last_commit = Outcome()
        try:
            with store.batch():
                code, text = self.fn(target, c, **kw)
        except Refusal as r:
            # refused after a write: what it wrote is committed too (the op log at HEAD must not
            # lag the files it names), and the refusal says what became of it
            line = store.last_commit.line()
            if line and not getattr(r, "reports_commit", False):
                raise Refusal(r.message, f"{r.remedy} (what it wrote before the refusal was{line[1:]})") from r
            raise
        return code, text + store.last_commit.line()

    @property
    def params(self) -> list[inspect.Parameter]:
        """The operation's own parameters, after the engine and the caller."""
        return list(inspect.signature(self.fn, eval_str=True).parameters.values())[2:]


OPS: dict[str, Op] = {}


def op(*, write: bool, rest: str = "", engine: bool = True):
    def register(fn):
        OPS[fn.__name__] = Op(fn.__name__, fn, write, rest, engine)
        return fn

    return register


def _rel(e: Engine, path) -> str:
    return path.relative_to(e.root).as_posix()


# -- bootstrap (FRAMEWORK §6.9) -----------------------------------------------------------


@op(write=True, engine=False)
def init(root: Path, c: Caller, prefix: dict[str, str] | None = None, dry_run: bool = False, merge_settings: bool = False, skip_settings: bool = False) -> tuple[int, str]:
    """Write the adoption kit's missing files into the repo (config, bootloader, contract, hook, skeletons); never overwrites. `prefix` maps kind -> id prefix. An existing .claude/settings.local.json without the hook refuses until the owner chooses: merge_settings (yes) or skip_settings (no)."""
    return 0, bootstrap.init(root, prefix or {}, dry_run=dry_run, merge_settings=merge_settings, skip_settings=skip_settings)


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
    failures = e.lint(working=working)
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
    """Move an item to another tier; NOW holds exactly one, NEXT at most five. Moving the NOW item down while others stay open says G-W5 is red until the owner picks one to promote."""
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
    """Close an item; `msg` says what finished it and is required. Closing the NOW item while others stay open says G-W5 is red until the owner picks one to promote."""
    return 0, e.close(id, msg, **c.kw)


@op(write=True)
def task_reopen(e: Engine, c: Caller, id: str, msg: str = "") -> tuple[int, str]:
    """Reopen a closed item; `msg` says why. An answered owner question never reopens: change its decision, or `ask_new`."""
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
    """Record the owner's answer, verbatim, as a decision titled `title`, and close the question. Answering a question at NOW while others stay open says G-W5 is red until the owner picks one to promote."""
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


@op(write=True)
def record_correct(e: Engine, c: Caller, id: str, after: str, text: str) -> tuple[int, str]:
    """Insert `[text]` right after the one place `after` occurs in a stamped record's text; insert-only and logged; body_sha keeps pinning the words as typed. A change of meaning is record_amend."""
    return 0, e.correct(id, after, text, **c.kw)


@op(write=True)
def record_retire(e: Engine, c: Caller, id: str, why: str, by: str, superseded_by: str = "") -> tuple[int, str]:
    """Retire a story: story_status retired, status deprecated, `why` as an amendment. `by` is `owner` or `human:<id>` (then `why` is their words, verbatim) or `agent` (only with `superseded_by`, the story recorded again; it gets `supersedes`). Final: a retire is never undone."""
    return 0, e.retire(id, why, by=by, superseded_by=superseded_by, **c.kw)


# -- decisions (FRAMEWORK §6.5) -----------------------------------------------------------


@op(write=True)
def decision_supersede(e: Engine, c: Caller, old: str, new: str) -> tuple[int, str]:
    """`new` replaces `old`: writes supersedes/superseded_by both ways and marks `old` SUPERSEDED."""
    return 0, e.supersede(old, new, **c.kw)


@op(write=True)
def decision_set(e: Engine, c: Caller, id: str, fields: dict[str, str] | None = None, unset: list[str] | None = None) -> tuple[int, str]:
    """Set or unset a decision's own frontmatter: decision_status (not SUPERSEDED: decision_supersede), reopen_if (REJECTED only), tags, title, description. Links, provenance (actor, decided, session, attribution, imported_from, generated, verified) and answers are refused."""
    return 0, e.decision_set(id, fields or {}, unset=tuple(unset or ()), **c.kw)


@op(write=True)
def decision_link(e: Engine, c: Caller, id: str, target: str, rel: str = "") -> tuple[int, str]:
    """Link a decision to a task, story, criterion or `file::symbol`; `rel` is tasks, creates, amends, retires, relaxes, code or refs (inferred for tasks and code)."""
    return 0, e.link(id, target, rel, **c.kw)


@op(write=True)
def decision_relink(e: Engine, c: Caller, id: str, old: str, new: str) -> tuple[int, str]:
    """Replace a current decision's `code:` link `old` with `new` (a `file::symbol` that exists) when the code moves. Only `code:` links move; a superseded decision's links are history."""
    return 0, e.relink(id, old, new, **c.kw)


@op(write=False, rest="narrow it with `status`, `tag`, `links_to` or `text`")
def decision_find(e: Engine, c: Caller, text: str = "", tag: str = "", status: str = "", links_to: str = "") -> tuple[int, str]:
    """Decisions matching every filter given, one line each: `text` searches titles and bodies."""
    return 0, "\n".join(e.find(text, tag, status, links_to)) or "no matching decisions"


@op(write=False, rest="ask for one `section`")
def decision_show(e: Engine, c: Caller, id: str, section: str | None = None) -> tuple[int, str]:
    """One decision: its status, links and text, or one `section` (e.g. Amendments)."""
    return 0, e.decision_show(id, section).rstrip("\n")


@op(write=False, rest="`context-engine decision find --links-to <target>` in a shell")
def why(e: Engine, c: Caller, target: str) -> tuple[int, str]:
    """The decisions that link a task, story, criterion, decision or `file::symbol`, each with the field that links it."""
    return 0, "\n".join(e.why(target)) or f"no decision links {target}"


@op(write=True)
def hk_regen_index(e: Engine, c: Caller) -> tuple[int, str]:
    """Housekeeping: regenerate the decision index from the decisions' frontmatter (G-D6)."""
    return 0, e.reindex(session=c.session, actor=c.actor or "process:housekeep")


@op(write=True)
def decision_import(e: Engine, c: Caller, path: str, dry_run: bool = False) -> tuple[int, str]:
    """Import a single-file decision log (`### D-n -- title *(actor, date)*`): every id and text kept, stamped; all or nothing."""
    return 0, e.import_log(path, dry_run=dry_run, **c.kw)


# -- the residual-risk register (FRAMEWORK §7.4) ------------------------------------------


@op(write=False, rest="read the register file itself")
def register_show(e: Engine, c: Caller, engine: bool = False) -> tuple[int, str]:
    """The residual-risk register's entries; `engine` reads the one shipped with the engine (the handover)."""
    return 0, e.register_show(engine=engine)


# -- the banner (FRAMEWORK §5.5) ----------------------------------------------------------


@op(write=False, rest="the note's § Banner")
def banner_show(e: Engine, c: Caller) -> tuple[int, str]:
    """The banner and its hash; pass the hash to banner_set."""
    b = e.banner()
    if b is None:
        why = "no banner yet" if (e.root / e.w.handoff).exists() else f"no note at {e.w.handoff} yet"
        return 0, f"banner none hash {L.NO_BANNER}\n\n{why}: the first `banner set --seen {L.NO_BANNER}` writes it"
    return 0, f"banner {b.key} hash {b.sha}\n\n{b.text}"


@op(write=True)
def banner_set(e: Engine, c: Caller, text: str, seen: str) -> tuple[int, str]:
    """Replace the banner; `seen` is the hash banner_show printed, so another session's banner is never overwritten."""
    return 0, e.banner_set(text, seen, **c.kw)
