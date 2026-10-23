"""The command line: one subcommand per operation in ``ops.OPS`` (FRAMEWORK §8.0.2, AC-18).

``context-engine [--root DIR] [--session KEY] [--actor ACTOR] <group> <op> ...``. The session key and the
actor may also come from ``CE_SESSION`` and ``CE_ACTOR``. A refusal prints its remedy to stderr
and exits 2; lint exits 1 when anything fails.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from . import ops
from .errors import Refusal


def _fields(pairs: list[str], flag: str = "--set") -> dict[str, str]:
    out = {}
    for p in pairs or []:
        if "=" not in p:
            raise Refusal(f"{flag} {p!r} has no `=`", "write it as key=value")
        k, v = p.split("=", 1)
        out[k.strip()] = v
    return out


def _read(path: Path) -> str:
    """A file argument's text: UTF-8, with any BOM dropped (PowerShell 5.1 writes one), which is
    no part of the words."""
    try:
        return path.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        raise Refusal(f"there is no file {path}", "check the path") from None
    except UnicodeDecodeError:
        raise Refusal(f"{path} is not UTF-8", "save it as UTF-8 (PowerShell 5.1: `Out-File -Encoding utf8` or `Set-Content -Encoding utf8`)") from None


def _ids(text: str | None) -> list[str]:
    return [x.strip() for x in (text or "").replace(",", " ").split() if x.strip()]


def _sub(subs: argparse._SubParsersAction, name: str, help: str, **kw) -> argparse.ArgumentParser:
    """A subcommand whose one line in its group's list (`help`) is also its own `--help`
    description, so `context-engine <group> <op> --help` says what the operation does (CE-72)."""
    return subs.add_parser(name, help=help, description=help, **kw)


def build() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="context-engine", description="context-engine: records and working state for agent-built repos")
    ap.add_argument("--root", default=".", help="the repo root (default: the current directory)")
    ap.add_argument("--session", default=os.environ.get("CE_SESSION"), help="the session key (or CE_SESSION)")
    ap.add_argument("--actor", default=os.environ.get("CE_ACTOR"), help="the OKF actor, e.g. claude-code/<model> (or CE_ACTOR)")
    groups = ap.add_subparsers(dest="group", required=True)

    ini = _sub(groups, "init", "write the adoption kit's missing files into the repo (FRAMEWORK §6.9) and gitignore .context-engine/; never overwrites")
    ini.add_argument("--prefix", action="append", default=[], metavar="KIND=PREFIX", help="a kind's id prefix, e.g. task=PRJ; repeat for each")
    ini.add_argument("--dry-run", action="store_true", help="say what would be written, write nothing")
    ini.add_argument("--merge-settings", action="store_true", help="the owner said yes: add the SessionStart hook to an existing .claude/settings.local.json")
    ini.add_argument("--skip-settings", action="store_true", help="the owner said no: leave an existing .claude/settings.local.json alone; with none, write no hook (the Claude Code plugin runs orient)")

    s = _sub(groups, "session", "open, close or pause a framework session (FRAMEWORK §6.1, §6.3, §6.4)").add_subparsers(dest="op", required=True)
    _sub(s, "start", "open a session: mint its key and write the ledger stub; run it first, every session")
    c = _sub(s, "close", "clean close: write this session's ledger entry over its stub")
    c.add_argument("--rows", required=True, help="the items this session touched and how each ended, e.g. `CE-2 (closed); AC-10 (tested)`")
    c.add_argument("--summary", action="append", required=True, help="one line of the owner digest; repeat for each, 1 to 7 lines")
    c.add_argument("--guards", required=True, help="receipt: the gate and lint results, verbatim")
    c.add_argument("--read", required=True, help="receipt: what was read to start work")
    c.add_argument("--asked", default="", help="receipt: the owner questions raised in chat; must name each one at NOW or NEXT (default: those `ask raised` recorded)")
    c.add_argument("--owed", action="append", default=[], help="one thing still owed (an answer, a check, a push); repeat for each (default: nothing)")
    ab = _sub(s, "abandon", "mark another session's stale open stub abandoned, with a baton for what it left in flight (housekeeping: --stale)")
    ab.add_argument("key", nargs="?", default="", help="the stub's session key, as orient lists it")
    ab.add_argument("--stale", action="store_true", help="every other stub with 3 or more closes or pauses since its last activity")
    ab.add_argument("--force", action="store_true", help="abandon a stub short of that window, on the owner's word")
    p = _sub(s, "pause", "pause: write a pause entry over this session's stub instead of a clean close")
    p.add_argument("--rows", required=True, help="the items this session touched")
    p.add_argument("--deferred", required=True, help="the steps skipped (the gate, the commit, ...)")

    _sub(groups, "orient", "the session-start read in one capped response: banner, batons and pauses, the board's NOW and NEXT, questions to raise, the top item")
    _sub(groups, "routes", "where each framework component lives ([[routes]] in context.toml)")
    lint = _sub(groups, "lint", "run the guards: failures only, each with its remedy; exits 1 when any fails")
    lint.add_argument("--working", action="store_true", help="working-state guards only")

    t = _sub(groups, "task", "the board: file, move, comment on, close and read board items (FRAMEWORK §5.2)").add_subparsers(dest="op", required=True)
    n = _sub(t, "new", "file a board item with the next free id (or --id)")
    n.add_argument("title", help="the item's title")
    n.add_argument("--kind", default="task", help="a board kind from context.toml (default: task)")
    n.add_argument("--pri", default="LATER", help="its tier, e.g. NOW, NEXT, LATER (default: LATER); NOW holds exactly one, NEXT at most five")
    n.add_argument("--brief", default="", help="a constraint, not a summary; at most 120 characters")
    n.add_argument("--deps", default="", help="the ids it depends on, comma- or space-separated")
    n.add_argument("--body", default="", help="the item's body (default: the title, then empty ## Traps, ## Read first and ## Log)")
    n.add_argument("--id", default="", help="keep an imported number: a never-used id of the kind's series (default: the next free one)")
    n.add_argument("--goals", default="", help="the charter goals it serves, e.g. G-2,G-7; required where [guards] task_goals names the kind")
    st = _sub(t, "set", "set or unset frontmatter fields no operation owns (e.g. brief, labels, aliases)")
    st.add_argument("id", help="the item's id")
    st.add_argument("--set", action="append", default=[], metavar="KEY=VALUE", help="a field to set; repeat for each")
    st.add_argument("--unset", action="append", default=[], metavar="KEY", help="a field to remove; repeat for each")
    st.add_argument("--mechanical", action="store_true", help="log the write as mechanical (housekeeping), not progress")
    pr = _sub(t, "promote", "move an item to another tier; NOW holds exactly one, NEXT at most five")
    pr.add_argument("id", help="the item's id")
    pr.add_argument("pri", help="the new tier, e.g. NOW, NEXT, LATER")
    d = _sub(t, "dep", "add or remove an item's dependencies")
    d.add_argument("id", help="the item's id")
    d.add_argument("--add", default="", help="ids to depend on, comma- or space-separated")
    d.add_argument("--remove", default="", help="ids to stop depending on, comma- or space-separated")
    cm = _sub(t, "comment", "append one dated line to the item's ## Log")
    cm.add_argument("id", help="the item's id")
    cm.add_argument("text", help="the line to append")
    cm.add_argument("--mechanical", action="store_true", help="log the write as mechanical (housekeeping), not progress")
    to = _sub(t, "touch", "mark the item as moved this session, changing nothing else")
    to.add_argument("id", help="the item's id")
    to.add_argument("--mechanical", action="store_true", help="bump only `updated`, not `moved`: housekeeping is not progress")
    for name, what in (("close", "close an item; the engine commits it with `Closes: <id>`"), ("reopen", "reopen a closed item")):
        x = _sub(t, name, what)
        x.add_argument("id", help="the item's id")
        x.add_argument("-m", "--msg", default="", help="what finished it (required)" if name == "close" else "why it reopens")
        if name == "close":
            cb = x.add_mutually_exclusive_group()
            cb.add_argument("--body", default="", help="the close commit's message body: the Sabotage: and receipt lines")
            cb.add_argument("--body-file", type=Path, help="read --body from a file")
    se = _sub(t, "section", "replace one named ## section of an item's body (not ## Log: use `task comment`)")
    se.add_argument("id", help="the item's id")
    se.add_argument("name", help="the section's heading, without ##")
    se.add_argument("text", help="the section's new text")
    ls = _sub(t, "list", "the board, one line per item, by tier then id")
    ls.add_argument("--state", default="open", help="open, closed, or all")
    ls.add_argument("--pri", help="only items in this tier")
    ls.add_argument("--label", help="only items carrying this label")
    sh = _sub(t, "show", "one item: its head line, then its body or one section")
    sh.add_argument("id", help="the item's id, or an alias (an earlier id)")
    sh.add_argument("--section", help="show only this ## section")
    sh.add_argument("--head", type=int, default=5, help="how many of the newest ## Log entries to show (0: all; default: 5)")

    a = _sub(groups, "ask", "owner questions, ASK-n (FRAMEWORK §5.3)").add_subparsers(dest="op", required=True)
    an = _sub(a, "new", "file an owner question; raise it in chat this session")
    an.add_argument("title", help="the question, in one line")
    an.add_argument("--pri", default="NEXT", help="its tier (default: NEXT)")
    an.add_argument("--brief", default="", help="a constraint, not a summary; at most 120 characters")
    an.add_argument("--blocks", default="", help="the ids it blocks, comma- or space-separated")
    an.add_argument("--body", default="", help="the question's body (default: a Question, Options, Recommendation skeleton)")
    an.add_argument("--id", default="", help="keep an imported number, e.g. ASK-8 for Q8 (default: the next free one)")
    ar = _sub(a, "raised", "record that these questions were raised in chat this session")
    ar.add_argument("ids", nargs="+", help="the question ids, comma- or space-separated")
    al = _sub(a, "later", "the owner deferred the question: stop it counting as overdue for now")
    al.add_argument("id", help="the question's id")
    aa = _sub(a, "answer", "record the owner's answer, verbatim, as a decision titled --title, and close the question")
    aa.add_argument("id", help="the question's id")
    aa.add_argument("words", nargs="?", help="the owner's words, verbatim (or --file)")
    aa.add_argument("--file", type=Path, help="read the owner's words from a file (they keep their line breaks)")
    aa.add_argument("--title", required=True, help="the decision's title")
    aa.add_argument("--ruled-by", default="", help="the owner delegated the ruling: who made it (an agent's actor, never owner); needs --ruling, and the words are then the owner's delegating words")
    ru = aa.add_mutually_exclusive_group()
    ru.add_argument("--ruling", default="", help="the ruling made on the owner's delegation (needs --ruled-by); recorded under ## Ruling, apart from the owner's words")
    ru.add_argument("--ruling-file", type=Path, help="read --ruling from a file")

    b = _sub(groups, "baton", "batons: skipped steps handed to the next session (FRAMEWORK §5.4)").add_subparsers(dest="op", required=True)
    ba = _sub(b, "add", "hand a skipped step to the next session")
    ba.add_argument("step", help="the step, as the next session should do it")
    ba.add_argument("--why", default="", help="why it was skipped")
    bd = _sub(b, "done", "close a baton (any session may)")
    bd.add_argument("id", help="the baton's id")
    bd.add_argument("evidence", help="how it was done")
    _sub(b, "list", "the open batons and pause records, yours first")
    _sub(b, "expire", "housekeeping: turn expired batons and pauses into tasks")

    pz = _sub(groups, "pause", "pause records: work left in flight, with its exact resume step (FRAMEWORK §5.4)").add_subparsers(dest="op", required=True)
    po = _sub(pz, "open", "write a pause record (branch and uncommitted paths from git) and commit it")
    po.add_argument("--in-flight", required=True, help="what was in flight; its first line is the record's title")
    po.add_argument("--resume", required=True, help="the exact step that picks the work back up")
    po.add_argument("--evidence", default="", help="where the evidence so far is (default: none)")
    po.add_argument("--deferred", action="append", default=[], help="one step deferred; repeat for each")
    pres = _sub(pz, "resume", "pick a pause back up and mark it done")
    pres.add_argument("id", help="the pause record's id")

    r = _sub(groups, "record", "append-only records: decisions and stories").add_subparsers(dest="op", required=True)
    rn = _sub(r, "new", "a new decision or story, stamped when it is created; owner words verbatim, with --set actor=owner")
    rn.add_argument("kind", help="an append-only kind, e.g. decision or story")
    rn.add_argument("title", help="the record's title")
    rn.add_argument("--set", action="append", default=[], metavar="KEY=VALUE", help="a frontmatter field, e.g. actor=owner; repeat for each")
    body = rn.add_mutually_exclusive_group(required=True)
    body.add_argument("--body", help="the record's text (owner words verbatim)")
    body.add_argument("--file", type=Path, help="read the body from a file (owner words keep their line breaks)")
    rs = _sub(r, "stamp", "stamp body_sha on unstamped append-only records; all or nothing")
    rs.add_argument("ids", nargs="+", help="the record ids, comma- or space-separated")
    ra = _sub(r, "amend", "append a dated entry under ## Amendments: the only change an append-only body takes")
    ra.add_argument("id", help="the record's id")
    ra.add_argument("text", nargs="?", help="the amendment; owner words verbatim (or --file)")
    ra.add_argument("--file", type=Path, help="read the amendment from a file (owner words keep their line breaks)")
    rc = _sub(r, "correct", "insert [text] after one unique anchor in a stamped record (DEC-13)")
    rc.add_argument("id", help="the record's id")
    rc.add_argument("--after", required=True, help="the words the insertion goes right after; must occur once")
    rc.add_argument("--text", required=True, help="the text to insert; it is written as [text]")
    rr = _sub(r, "retire", "retire a story: who retired it and why, recorded with it; never undone")
    rr.add_argument("id", help="the story's id")
    rr.add_argument("--by", required=True, help="owner or human:<id> (then --why holds their words verbatim), or agent (only with --superseded-by)")
    rr.add_argument("--superseded-by", default="", help="the replacement story (a new record with the same words)")
    why = rr.add_mutually_exclusive_group(required=True)
    why.add_argument("--why", help="the owner's words verbatim, or what was wrong with the story")
    why.add_argument("--file", type=Path, help="read `why` from a file (owner words keep their line breaks)")
    rf = _sub(r, "confirm", "confirm a story an agent reconstructed: unconfirmed to live, with the owner's words")
    rf.add_argument("id", help="the story's id")
    rf.add_argument("words", nargs="?", help="the owner's words confirming it, verbatim (or --file)")
    rf.add_argument("--file", type=Path, help="read the words from a file (owner words keep their line breaks)")
    rf.add_argument("--by", default="owner", help="whose words: owner (the default) or human:<id>; never an agent")
    rf.add_argument("--status", default="live", help="live (the default), or unspecified while no criterion comes from the story")

    dc = _sub(groups, "decision", "decision records (FRAMEWORK §6.5)").add_subparsers(dest="op", required=True)
    ds = _sub(dc, "supersede", "NEW replaces OLD: link them both ways and mark OLD SUPERSEDED")
    ds.add_argument("old", help="the decision being replaced, or an alias")
    ds.add_argument("new", help="the decision that replaces it, or an alias")
    dset = _sub(dc, "set", "a decision's own frontmatter: decision_status, reopen_if, tags, title, description")
    dset.add_argument("id", help="the decision's id")
    dset.add_argument("--set", action="append", default=[], metavar="KEY=VALUE", help="a field to set; repeat for each")
    dset.add_argument("--unset", action="append", default=[], metavar="KEY", help="a field to remove; repeat for each")
    dl = _sub(dc, "link", "link a decision to a task, story, criterion, decision or file::symbol")
    dl.add_argument("id", help="the decision's id")
    dl.add_argument("target", help="a task, story, criterion or decision id, or file::symbol")
    dl.add_argument("--rel", default="", help="tasks, creates, amends, retires, relaxes, code or refs")
    drl = _sub(dc, "relink", "move a decision's code: link when the code moves")
    drl.add_argument("id", help="the decision's id")
    drl.add_argument("old", help="the code: link to replace")
    drl.add_argument("new", help="the file::symbol it moved to")
    df = _sub(dc, "find", "decisions matching every filter given, one line each")
    df.add_argument("query", nargs="?", default="", help="the text to search titles and bodies for, as --text")
    df.add_argument("--text", default="", help="the text to search titles and bodies for")
    df.add_argument("--tag", default="", help="only decisions with this tag")
    df.add_argument("--status", default="", help="only decisions with this decision_status, e.g. PROVISIONAL")
    df.add_argument("--links-to", default="", help="only decisions that link this id or file::symbol")
    dsh = _sub(dc, "show", "one decision: its status, links and text, or one section")
    dsh.add_argument("id", help="the decision's id, or an alias (an earlier id)")
    dsh.add_argument("--section", help="show only this section, e.g. Amendments")
    _sub(dc, "index", "housekeeping: regenerate the decision index (G-D6)")
    di = _sub(dc, "import", "turn a single-file log into records: each number and text kept, an id in another prefix renamed to the kind's with its old id kept in `aliases`")
    di.add_argument("path", help="the single-file log, e.g. docs/decisions.md (on a branch first)")
    di.add_argument("--dry-run", action="store_true", help="write nothing; print the summary and the id map, a doc to save as evidence before the import")

    co = _sub(groups, "commit", "commit the given paths, plus this session's op-log lines not yet in HEAD and the files those lines name (another session's stay out, and are named); runs no gate (run it first)")
    co.add_argument("--sweep", action="store_true", help="take every uncommitted op-log line, whoever wrote it: for a session known dead")
    co.add_argument("paths", nargs="*", help="files or directories, relative to the root; none: only the op log's uncommitted lines and the files they name")
    msg = co.add_mutually_exclusive_group(required=True)
    msg.add_argument("-m", "--message", action="append", help="a paragraph of the message, as `git commit -m`; repeat for each")
    msg.add_argument("-F", "--message-file", type=Path, help="read the message from a file")

    ga = _sub(groups, "gate", "the scoped gate: run the repo's gate command and record its result per scope (FRAMEWORK §8.5 G-V1)").add_subparsers(dest="op", required=True)
    gr = _sub(ga, "run", "run [gate] `command` and append its result to the run ledger")
    gr.add_argument("--readers", action="store_true", help="run only the scopes' readers: the tests that read files outside a scope")
    gs = _sub(ga, "status", "each scope's id here and whether a green run covers it")
    gs.add_argument("--require", default="", metavar="SCOPE", help="exit 1 unless this scope is covered; <scope>+readers: its readers too")

    wy = _sub(groups, "why", "the decisions that link a task, criterion or file::symbol")
    wy.add_argument("target", help="a task, story, criterion or decision id, or file::symbol")

    dd = _sub(groups, "doc", "freeze or archive a hand-written doc (FRAMEWORK §6.7, §7.3)").add_subparsers(dest="op", required=True)
    df_ = _sub(dd, "freeze", "write a FROZEN line with the date above the doc's liveness line (G-D4 then reads it as FROZEN)")
    df_.add_argument("path", help="the doc, relative to the root")
    df_.add_argument("--note", default="", help="why it is frozen (default: the board items it names closed)")
    da = _sub(dd, "archive", "move a committed doc into an archive directory, unrepaired, first line ARCHIVED <date>, with a row in that directory's redirect table")
    da.add_argument("path", help="the doc, relative to the root")
    da.add_argument("--to", default="", help="the archive directory (default: [working] archive)")
    da.add_argument("--why", default="", help="the redirect row's reason, e.g. `over its cap (G-D1)`")

    rg = _sub(groups, "register", "the residual-risk register (FRAMEWORK §7.4)").add_subparsers(dest="op", required=True)
    rgs = _sub(rg, "show", "the register's entries")
    rgs.add_argument("--engine", action="store_true", help="the engine's own register, shipped with the package")

    bn = _sub(groups, "banner", "the handoff banner: what is true now (FRAMEWORK §5.5)").add_subparsers(dest="op", required=True)
    _sub(bn, "show", "the banner and its hash; pass the hash to `banner set --seen`")
    bs = _sub(bn, "set", "replace the banner, unless another session changed it since you read it")
    bs.add_argument("--seen", required=True, help="the hash `banner show` printed")
    src = bs.add_mutually_exclusive_group(required=True)
    src.add_argument("--text", help="the new banner")
    src.add_argument("--file", type=Path, help="read the new banner from a file")
    return ap


# (group, verb) -> the operation in ``ops.OPS``. The CLI spells `context-engine <group> <verb>`.
CLI_OPS = {
    ("init", None): "init",
    ("session", "start"): "session_start",
    ("session", "close"): "session_close",
    ("session", "pause"): "session_pause",
    ("session", "abandon"): "session_abandon",
    ("orient", None): "orient",
    ("routes", None): "routes",
    ("lint", None): "lint",
    **{("task", v): f"task_{v}" for v in ("new", "set", "promote", "dep", "comment", "touch", "close", "reopen", "section", "list", "show")},
    **{("ask", v): f"ask_{v}" for v in ("new", "raised", "later", "answer")},
    ("baton", "list"): "baton_list",
    ("baton", "add"): "baton_add",
    ("baton", "done"): "baton_done",
    ("baton", "expire"): "hk_expire_batons",
    ("pause", "open"): "pause_open",
    ("pause", "resume"): "pause_resume",
    ("record", "new"): "record_new",
    ("record", "stamp"): "record_stamp",
    ("record", "amend"): "record_amend",
    ("record", "correct"): "record_correct",
    ("record", "retire"): "record_retire",
    ("record", "confirm"): "record_confirm",
    ("decision", "supersede"): "decision_supersede",
    ("decision", "set"): "decision_set",
    ("decision", "link"): "decision_link",
    ("decision", "relink"): "decision_relink",
    ("decision", "find"): "decision_find",
    ("decision", "show"): "decision_show",
    ("decision", "index"): "hk_regen_index",
    ("decision", "import"): "decision_import",
    ("commit", None): "commit",
    ("gate", "run"): "gate_run",
    ("gate", "status"): "gate_status",
    ("why", None): "why",
    ("doc", "freeze"): "doc_freeze",
    ("doc", "archive"): "doc_archive",
    ("register", "show"): "register_show",
    ("banner", "show"): "banner_show",
    ("banner", "set"): "banner_set",
}


def _params(args: argparse.Namespace) -> dict:
    """Turn the parsed arguments into the operation's parameters (lists, dicts, file bodies)."""
    a = vars(args)
    if a.get("query"):  # `decision find <text>`: the positional is --text (CE-76)
        if a.get("text") and a["text"] != a["query"]:
            raise Refusal(f"two search texts, {a['query']!r} and --text {a['text']!r}", "give the text once, as the argument or as --text")
        a["text"] = a["query"]
    if "set" in a:
        a["fields"] = _fields(a["set"])
    if isinstance(a.get("prefix"), list):
        a["prefix"] = _fields(a["prefix"], "--prefix")
    for name in ("deps", "add", "remove", "blocks", "goals"):
        if isinstance(a.get(name), str):
            a[name] = _ids(a[name])
    if isinstance(a.get("ids"), list):
        a["ids"] = _ids(" ".join(a["ids"]))
    if args.group == "commit":
        a["message"] = _read(a["message_file"]) if a.get("message_file") else "\n\n".join(a["message"])
    if a.get("body_file") is not None:
        a["body"] = _read(a["body_file"])
    if a.get("ruling_file") is not None:
        a["ruling"] = _read(a["ruling_file"])
    words = WORDS.get((args.group, a.get("op")))
    if words and (a[words] is None) == (a.get("file") is None):  # CE-73: the words come one way, exactly
        raise Refusal(f"`{args.group} {a['op']}` got its {words} {'both as an argument and with --file' if a[words] is not None else 'neither as an argument nor with --file'}", f"give the {words} one way: as the argument, or written to a file and passed with --file")
    if a.get("file") is not None:
        into = {("record", "retire"): "why", ("record", "new"): "body", ("ask", "answer"): "words", ("record", "confirm"): "words"}.get((args.group, a.get("op")), "text")
        a[into] = _read(a["file"])
    return a


# (group, verb) -> the optional positional that --file stands in for (CE-73)
WORDS = {("record", "amend"): "text", ("ask", "answer"): "words", ("record", "confirm"): "words"}


def _parse(argv: list[str] | None) -> argparse.Namespace:
    """``parse_args``, except that the owner's words after an option (`ask answer ASK-1 --title T
    "<words>"`) still land: argparse before 3.12.7 or so fills an optional positional too early,
    with nothing, and then calls the words unrecognized. Anything else unrecognized is the usual
    usage error."""
    ap = build()
    args, extra = ap.parse_known_args(argv)
    words = WORDS.get((args.group, getattr(args, "op", None)))
    if extra and words and getattr(args, words) is None and len(extra) == 1 and not extra[0].startswith("-"):
        setattr(args, words, extra[0])
    elif extra:
        ap.error(f"unrecognized arguments: {' '.join(extra)}")
    return args


def run(argv: list[str] | None = None) -> tuple[int, str]:
    args = _parse(argv)
    o = ops.OPS[CLI_OPS[(args.group, getattr(args, "op", None))]]
    a = _params(args)
    return o.call(o.target(args.root), ops.Caller(args.session, args.actor), **{p.name: a[p.name] for p in o.params})


def main(argv: list[str] | None = None) -> int:
    try:
        code, out = run(argv)
    except Refusal as r:
        sys.stderr.reconfigure(encoding="utf-8")  # as stdout below: a remedy may say "§"
        print(str(r), file=sys.stderr)
        return 2
    # UTF-8 with LF line ends, on Windows too: a capped read (orient's `orient_max_bytes`) is
    # counted in UTF-8 bytes with LF, and a CRLF translation added a byte a line past the cap
    # (CE-75, docs/evidence/adhoc-dryrun-2026-10-14.md F30)
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    print(out)
    return code


if __name__ == "__main__":
    sys.exit(main())
