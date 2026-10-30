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
from . import gate as G
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
    mcp: bool = True  # False: no MCP tool, only the CLI (gate runs are out of the MCP's scope, FRAMEWORK §8.0.2)

    def target(self, root) -> "Engine | Path":
        """What the function's first parameter gets: an Engine on ``root``, or the root itself."""
        return Engine(root) if self.engine else Path(root)

    def call(self, target: "Engine | Path", c: "Caller", /, **kw) -> tuple[int, str]:
        """Run the operation on ``target`` (from ``self.target``), as the CLI and the MCP server
        both do. A write runs in one store batch, so whatever commit the policy makes after it
        (FRAMEWORK §5.5 rule 4: at a milestone, after every write, or only a pause's) is made
        once, by path, with its op log lines, and its reply says what the commit did. A dry run
        writes nothing, so it takes no batch: the batch's lock would create the lock file (CE-98)."""
        if not (self.write and self.engine) or kw.get("dry_run"):
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


def op(*, write: bool, rest: str = "", engine: bool = True, mcp: bool = True):
    def register(fn):
        OPS[fn.__name__] = Op(fn.__name__, fn, write, rest, engine, mcp)
        return fn

    return register


def _rel(e: Engine, path) -> str:
    return path.relative_to(e.root).as_posix()


# -- bootstrap (FRAMEWORK §6.9) -----------------------------------------------------------


@op(write=True, engine=False)
def init(root: Path, c: Caller, prefix: dict[str, str] | None = None, dry_run: bool = False, merge_settings: bool = False, skip_settings: bool = False) -> tuple[int, str]:
    """Write the adoption kit's missing files into the repo (config, kit block, contract, hook, skeletons, `.context-engine/` appended to the repo's .gitignore, and the op log's merge=union line to its .gitattributes); never overwrites. `prefix` maps kind -> id prefix. An existing .claude/settings.local.json without the hook refuses until the owner chooses: merge_settings (yes) or skip_settings (no)."""
    return 0, bootstrap.init(root, prefix or {}, dry_run=dry_run, merge_settings=merge_settings, skip_settings=skip_settings)


# -- sessions (FRAMEWORK §6.1, §6.3, §6.4) ---------------------------------------------


@op(write=True)
def session_start(e: Engine, c: Caller) -> tuple[int, str]:
    """Open a framework session: mint its key and write the ledger stub. Call it first, every session."""
    c.session = e.session_start(actor=c.actor)
    out = f"session {c.session} opened (stub written to {e.w.ledger}); pass --session {c.session} or set CE_SESSION={c.session}"
    other = e.actor_spellings(c.actor or "")
    if other:  # CE-122: one agent keeps one spelling, so a query for it finds all its lines
        known = ", ".join(f"`{a}` ({n} op line{'s' if n != 1 else ''})" for a, n in other[:3])
        out += (f"\nwarning: the op log already signs this agent as {known}, not `{c.actor}`; unless this is another model, "
                f"set CE_ACTOR={other[0][0]} (or pass --actor) for this session's writes")
    return 0, out


@op(write=True)
def session_close(e: Engine, c: Caller, rows: str, summary: list[str], guards: str, read: str, asked: str = "", owed: list[str] | None = None) -> tuple[int, str]:
    """Clean close: finalise this session's ledger stub. `summary` is the owner digest, at most 7 lines."""
    receipts = {"guards": guards, "read": read, "asked": asked}
    return 0, e.session_close(c.session, actor=c.actor, rows=rows, summary=summary, receipts=receipts, owed=owed or [])


@op(write=True)
def session_pause(e: Engine, c: Caller, rows: str, deferred: str) -> tuple[int, str]:
    """Pause: write a pause entry instead of a clean close; `deferred` names what was skipped."""
    return 0, e.session_pause(c.session, actor=c.actor, rows=rows, deferred=deferred)


@op(write=True)
def session_abandon(e: Engine, c: Caller, key: str = "", force: bool = False, stale: bool = False) -> tuple[int, str]:
    """Mark another session's stale `kind: open` stub `kind: abandoned`, keep its lines, add the `abandoned:` line and file a baton for what it left uncommitted. `stale`: every stub with 3 or more closes or pauses since its last activity (start-of-session housekeeping; list what it did in the close digest). A single `key` short of that is refused unless `force`, on the owner's word; the session's own key always is."""
    return 0, e.session_abandon(key, session=c.session, actor=c.actor, force=force, stale=stale)


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
def task_new(e: Engine, c: Caller, title: str, kind: str = "task", pri: str = "LATER", brief: str = "", deps: list[str] | None = None, body: str = "", id: str = "", goals: list[str] | None = None) -> tuple[int, str]:
    """File a board item. `brief` is a constraint, not a summary (at most 120 characters). `id` is one this session reserved (`id_reserve`), or keeps an imported number (a never-used id of the kind's series); none takes the next. `goals` names the charter goals (G-n) a task serves; required where `[guards] task_goals` names the kind."""
    rec = e.new(kind, title, pri=pri, brief=brief, deps=deps or [], body=body, rid=id, goals=goals or [], **c.kw)
    return 0, f"{rec.id}: created at {pri} ({_rel(e, rec.path)})"


@op(write=True)
def task_set(e: Engine, c: Caller, id: str, fields: dict[str, str] | None = None, unset: list[str] | None = None, mechanical: bool = False) -> tuple[int, str]:
    """Set or unset frontmatter fields the operations do not own (e.g. brief, labels, `aliases`: the item's earlier ids, e.g. aliases=[1h])."""
    return 0, e.set(id, fields or {}, unset=tuple(unset or ()), mechanical=mechanical, **c.kw)


@op(write=True)
def task_promote(e: Engine, c: Caller, id: str, pri: str) -> tuple[int, str]:
    """Move an item to another tier; NOW holds exactly one, NEXT at most five. Moving the NOW item down while others stay open: the reply warns that G-W5 is red until the owner picks one to promote."""
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
def task_close(e: Engine, c: Caller, id: str, msg: str = "", body: str = "") -> tuple[int, str]:
    """Close an item; `msg` says what finished it and is required. A milestone: the engine commits it with `Closes: <id>`, and `body` goes in that commit's message (the `Sabotage:` and receipt lines). Closing the NOW item while others stay open: the reply warns that G-W5 is red until the owner picks one to promote."""
    return 0, e.close(id, msg, body=body, **c.kw)


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
    """One item: its head line, then its body or one `section`; ## Log shows the newest `head` entries (0 for all). `id` may be an alias (an earlier id); the reply says which record it named."""
    return 0, e.show(id, section=section, head=head).rstrip("\n")


# -- ids (FRAMEWORK §8.3 G-D2, CE-105, CE-119) -----------------------------------------------


@op(write=True)
def id_reserve(e: Engine, c: Caller, kind: str, count: int = 1) -> tuple[int, str]:
    """Reserve the next `count` ids (1 to 20) of a board or append-only kind's series for this session, before writing a batch of records that cite each other, or a draft that cites a record not yet written: cite the ids, then write each with `task_new`, `ask_new` or `record_new` `id=`. No other write hands a reserved id out, and another session's `id=` is refused; one never written stays a gap (ids are never reused). Never cite a guessed id or a `DEC-<NEW>` placeholder."""
    return 0, e.reserve(kind, count, **c.kw)


# -- owner questions (FRAMEWORK §5.3) -----------------------------------------------------


@op(write=True)
def ask_new(e: Engine, c: Caller, title: str, pri: str = "NEXT", brief: str = "", blocks: list[str] | None = None, body: str = "", id: str = "", answered: str = "", decision_title: str = "", ruling: str = "", ruled_by: str = "") -> tuple[int, str]:
    """File an owner question (ASK-n); raise it in chat this session. `id` is one this session reserved (`id_reserve`), or keeps an imported number (Q8 as ASK-8; then `task_set` aliases=[Q8]). `answered`: the owner already answered it in chat (a question with no ask record behind it): their words, verbatim; the question is filed closed and the words recorded as a decision titled `decision_title`, as ask_answer does (with `ruling` and `ruled_by` for a delegated ruling), in one milestone."""
    if answered or decision_title or ruling or ruled_by:
        return 0, e.ask_answered(title, answered, title=decision_title, pri=pri, brief=brief, body=body, blocks=blocks or [], rid=id, ruling=ruling, ruled_by=ruled_by, **c.kw)
    rec = e.ask_new(title, pri=pri, brief=brief, body=body, blocks=blocks or [], rid=id, **c.kw)
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
def ask_answer(e: Engine, c: Caller, id: str, words: str, title: str, ruling: str = "", ruled_by: str = "") -> tuple[int, str]:
    """Record the owner's answer, verbatim, as a decision titled `title`, and close the question. If the owner delegated the ruling, `words` are their delegating words, `ruling` the ruling and `ruled_by` who made it (both or neither): the decision is `actor: owner asked` with `ruled_by`, and the ruling sits under `## Ruling`, apart from the owner's words. Answering a question at NOW while others stay open: the reply warns that G-W5 is red until the owner picks one to promote."""
    return 0, e.ask_answer(id, words, title=title, ruling=ruling, ruled_by=ruled_by, **c.kw)


# -- batons and pauses (FRAMEWORK §5.4) --------------------------------------------------


@op(write=False, rest="open the records in the baton and pause directories (`state: open`)")
def baton_list(e: Engine, c: Caller) -> tuple[int, str]:
    """The open batons and pause records, the caller's own first, then pauses, each pause with its resume step and each baton with why it was skipped: orient's must-act section in full."""
    return 0, "\n".join(e.carried_lines(c.session, why=True)) or "no open batons or pauses"


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
    """Write a pause record (branch and dirty paths from git) and commit it."""
    return 0, e.pause_open(in_flight, resume, evidence=evidence, deferred=deferred or [], **c.kw)


@op(write=True)
def pause_resume(e: Engine, c: Caller, id: str) -> tuple[int, str]:
    """Pick a pause back up and mark it done."""
    return 0, e.pause_resume(id, **c.kw)


# -- append-only records (FRAMEWORK §8.0.1) ----------------------------------------------


@op(write=True)
def record_new(e: Engine, c: Caller, kind: str, title: str, body: str, fields: dict[str, str] | None = None, id: str = "") -> tuple[int, str]:
    """A new decision or story, stamped when it is created, with the next free id or `id` (one this session reserved with `id_reserve`). Owner words go in `body` verbatim; set actor=owner in `fields`. A ruling made on the owner's delegation: `ruled_by` (who ruled) and an actor that is not the owner alone (`owner asked`) in `fields`, and a body of the owner's delegating words verbatim, then a `## Ruling` section holding the ruling."""
    rec = e.record_new(kind, title, body, fields or {}, rid=id, **c.kw)
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
    """Retire a story: story_status retired, status deprecated, `why` as an amendment. `by` is `owner` or `human:<id>` (then `why` is their words, verbatim) or `agent` (only with `superseded_by`, the replacement story, a new record with the same words; it gets `supersedes`). A retirement is final: it is never undone."""
    return 0, e.retire(id, why, by=by, superseded_by=superseded_by, **c.kw)


@op(write=True)
def record_confirm(e: Engine, c: Caller, id: str, words: str, by: str = "owner", status: str = "live") -> tuple[int, str]:
    """Confirm a story an agent reconstructed: story_status unconfirmed to `status` (`live`, or `unspecified` while no criterion comes from it), the confirmer's `words` verbatim as an amendment. `by` is `owner` or `human:<id>`; an agent never confirms. Not redone once logged. A successor is confirmed in new words, never those that confirmed a story it replaces."""
    return 0, e.confirm(id, words, by=by, status=status, **c.kw)


# -- decisions (FRAMEWORK §6.5) -----------------------------------------------------------


@op(write=True)
def decision_supersede(e: Engine, c: Caller, old: str, new: str) -> tuple[int, str]:
    """`new` replaces `old`: writes supersedes/superseded_by both ways and marks `old` SUPERSEDED. Either may be an alias (an earlier id)."""
    return 0, e.supersede(old, new, **c.kw)


@op(write=True)
def decision_set(e: Engine, c: Caller, id: str, fields: dict[str, str] | None = None, unset: list[str] | None = None) -> tuple[int, str]:
    """Set or unset a decision's own frontmatter: decision_status (not SUPERSEDED: decision_supersede), reopen_if (REJECTED only), tags, title, description. Links, provenance (actor, decided, session, attribution, imported_from, generated, ruled_by, verified) and answers are refused."""
    return 0, e.decision_set(id, fields or {}, unset=tuple(unset or ()), **c.kw)


@op(write=True)
def decision_link(e: Engine, c: Caller, id: str, target: str, rel: str = "") -> tuple[int, str]:
    """Link a decision to a task, story, criterion or `file::symbol`; `rel` is tasks, creates, amends, retires, relaxes, code or refs (inferred for tasks and code). An alias (an earlier id) is linked as the record it names."""
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
    """One decision: its status, links and text, or one `section` (e.g. Amendments). `id` may be an alias (an earlier id, e.g. D-27); the reply says which record it named."""
    return 0, e.decision_show(id, section).rstrip("\n")


@op(write=False, rest="`context-engine decision find --links-to <target>` in a shell")
def why(e: Engine, c: Caller, target: str) -> tuple[int, str]:
    """The decisions that link a task, story, criterion, decision or `file::symbol`, each with the field that links it. An alias (an earlier id) is looked up as the record it names."""
    return 0, "\n".join(e.why(target)) or f"no decision links {target}"


@op(write=True)
def hk_regen_index(e: Engine, c: Caller) -> tuple[int, str]:
    """Housekeeping: regenerate the decision index from the decisions' frontmatter (G-D6)."""
    return 0, e.reindex(session=c.session, actor=c.actor or "process:housekeep")


@op(write=True)
def decision_import(e: Engine, c: Caller, path: str, dry_run: bool = False) -> tuple[int, str]:
    """Import a single-file decision log (`### D-n -- title *(actor, date)*`): every text and number kept, stamped; an id in another prefix is renamed to the kind's and keeps its old id in `aliases`; all or nothing. `dry_run` also prints the id map to save as an evidence doc."""
    return 0, e.import_log(path, dry_run=dry_run, **c.kw)


# -- the session's own commits (FRAMEWORK §5.5 rule 4) --------------------------------------


@op(write=True)
def commit(e: Engine, c: Caller, message: str, paths: list[str] | None = None, sweep: bool = False) -> tuple[int, str]:
    """Commit `paths` by path (`git commit -o`) with this session's op log lines HEAD lacks and the files they name, so a record never goes without its op line; adds the `Session:` trailer. Another session's lines stay uncommitted unless they name a file the commit carries, and the reply says whose and how many were left; `sweep` takes every line (for a session known dead). It runs no gate: run the gate first. With no paths it commits only the op log's uncommitted lines and their files."""
    return 0, e.commit(paths or [], message, sweep=sweep, **c.kw)


# -- the scoped gate (FRAMEWORK §8.5 G-V1, CE-78) ---------------------------------------------


@op(write=False, mcp=False)
def gate_run(e: Engine, c: Caller, readers: bool = False) -> tuple[int, str]:
    """Run the repo's gate command ([gate] `command`) and record its result in the run ledger against the id of every gate scope, taken before and after the run (an id whose files moved while it ran is left out of the row; the run counts for nothing only when every id moved). `readers` runs only the scopes' readers, the tests that read files outside a scope. Exits as the gate did. CLI only: a gate run is out of the MCP's scope."""
    return G.run(e.root, e.store.config.gate, readers=readers, session=c.session, actor=c.actor)


@op(write=False, rest="`context-engine gate status` in a shell")
def gate_status(e: Engine, c: Caller, require: str = "") -> tuple[int, str]:
    """Each gate scope's id in the work tree and whether a green run covers it; `require` names a scope that must be covered (`code`: what `commit` checks), or a scope with its readers (`code+readers`: after a hand edit to a file the scope leaves out), or the exit code is 1."""
    return G.status(e.root, e.store.config.gate, require=require)


# -- docs: freeze and archive (FRAMEWORK §6.7, §7.2, §7.3, CE-27) ----------------------------


@op(write=True)
def doc_freeze(e: Engine, c: Caller, path: str, note: str = "") -> tuple[int, str]:
    """Freeze a doc (FRAMEWORK §6.7: an ACTIVE-PLAN doc freezes when its item closes): write `FROZEN <date> (session <key>): <note>` above its liveness line, so G-D4 reads it as FROZEN; nothing else changes. Do it before `task_close` of the last open item the plan names, which refuses until then. `note` says why (default: the items it names closed)."""
    return 0, e.doc_freeze(path, note, **c.kw)


@op(write=True)
def doc_archive(e: Engine, c: Caller, path: str, to: str = "", why: str = "") -> tuple[int, str]:
    """Archive a tracked, committed `.md` doc (FRAMEWORK §7.3): move it unrepaired into the archive directory `to` (default `[working] archive`), its first line `ARCHIVED <date>`, and add a row (old path, new link, date, `why`) to that directory's redirect table, README.md. Not a milestone: the next commit carries the move (git shows a rename). The reply names any context.toml entry still pointing at the old path."""
    return 0, e.doc_archive(path, to, why, **c.kw)


# -- the residual-risk register (FRAMEWORK §7.4) ------------------------------------------


@op(write=False, rest="read the register file itself")
def register_show(e: Engine, c: Caller, engine: bool = False) -> tuple[int, str]:
    """The residual-risk register's entries; `engine` reads the one shipped with the engine (the risks it hands over to every repo that adopts it)."""
    return 0, e.register_show(engine=engine)


# -- the banner (FRAMEWORK §5.5) ----------------------------------------------------------


@op(write=False, rest="the orientation note's § Banner")
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
