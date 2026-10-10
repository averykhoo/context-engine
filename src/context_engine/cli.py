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
from .working import Engine


def _fields(pairs: list[str]) -> dict[str, str]:
    out = {}
    for p in pairs or []:
        if "=" not in p:
            raise Refusal(f"--set {p!r} has no `=`", "write it as key=value")
        k, v = p.split("=", 1)
        out[k.strip()] = v
    return out


def _ids(text: str | None) -> list[str]:
    return [x.strip() for x in (text or "").replace(",", " ").split() if x.strip()]


def build() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="context-engine", description="context-engine: records and working state for agent-built repos")
    ap.add_argument("--root", default=".", help="the repo root (default: the current directory)")
    ap.add_argument("--session", default=os.environ.get("CE_SESSION"), help="the session key (or CE_SESSION)")
    ap.add_argument("--actor", default=os.environ.get("CE_ACTOR"), help="the OKF actor, e.g. claude-code/<model> (or CE_ACTOR)")
    groups = ap.add_subparsers(dest="group", required=True)

    s = groups.add_parser("session").add_subparsers(dest="op", required=True)
    s.add_parser("start")
    c = s.add_parser("close")
    c.add_argument("--rows", required=True)
    c.add_argument("--summary", action="append", required=True, help="one digest line; repeat for each")
    c.add_argument("--guards", required=True)
    c.add_argument("--read", required=True)
    c.add_argument("--asked", default="")
    c.add_argument("--owed", action="append", default=[])
    p = s.add_parser("pause")
    p.add_argument("--rows", required=True)
    p.add_argument("--deferred", required=True)

    groups.add_parser("orient")
    groups.add_parser("routes", help="where each framework component lives ([[routes]] in context.toml)")
    lint = groups.add_parser("lint")
    lint.add_argument("--working", action="store_true", help="working-state guards only")

    t = groups.add_parser("task").add_subparsers(dest="op", required=True)
    n = t.add_parser("new")
    n.add_argument("title")
    n.add_argument("--kind", default="task")
    n.add_argument("--pri", default="LATER")
    n.add_argument("--brief", default="")
    n.add_argument("--deps", default="")
    n.add_argument("--body", default="")
    st = t.add_parser("set")
    st.add_argument("id")
    st.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    st.add_argument("--unset", action="append", default=[])
    st.add_argument("--mechanical", action="store_true")
    pr = t.add_parser("promote")
    pr.add_argument("id")
    pr.add_argument("pri")
    d = t.add_parser("dep")
    d.add_argument("id")
    d.add_argument("--add", default="")
    d.add_argument("--remove", default="")
    cm = t.add_parser("comment")
    cm.add_argument("id")
    cm.add_argument("text")
    cm.add_argument("--mechanical", action="store_true")
    to = t.add_parser("touch")
    to.add_argument("id")
    to.add_argument("--mechanical", action="store_true")
    for name in ("close", "reopen"):
        x = t.add_parser(name)
        x.add_argument("id")
        x.add_argument("-m", "--msg", default="")
    se = t.add_parser("section")
    se.add_argument("id")
    se.add_argument("name")
    se.add_argument("text")
    ls = t.add_parser("list")
    ls.add_argument("--state", default="open", help="open, closed, or all")
    ls.add_argument("--pri")
    ls.add_argument("--label")
    sh = t.add_parser("show")
    sh.add_argument("id")
    sh.add_argument("--section")
    sh.add_argument("--head", type=int, default=5)

    a = groups.add_parser("ask").add_subparsers(dest="op", required=True)
    an = a.add_parser("new")
    an.add_argument("title")
    an.add_argument("--pri", default="NEXT")
    an.add_argument("--brief", default="")
    an.add_argument("--blocks", default="")
    an.add_argument("--body", default="")
    ar = a.add_parser("raised")
    ar.add_argument("ids", nargs="+")
    al = a.add_parser("later")
    al.add_argument("id")
    aa = a.add_parser("answer")
    aa.add_argument("id")
    aa.add_argument("words", help="the owner's words, verbatim")
    aa.add_argument("--title", required=True, help="the decision's title")

    b = groups.add_parser("baton").add_subparsers(dest="op", required=True)
    ba = b.add_parser("add")
    ba.add_argument("step")
    ba.add_argument("--why", default="")
    bd = b.add_parser("done")
    bd.add_argument("id")
    bd.add_argument("evidence")
    b.add_parser("expire", help="housekeeping: turn expired batons and pauses into tasks")

    pz = groups.add_parser("pause").add_subparsers(dest="op", required=True)
    po = pz.add_parser("open")
    po.add_argument("--in-flight", required=True)
    po.add_argument("--resume", required=True)
    po.add_argument("--evidence", default="")
    po.add_argument("--deferred", action="append", default=[])
    pres = pz.add_parser("resume")
    pres.add_argument("id")

    r = groups.add_parser("record", help="append-only records: decisions and stories").add_subparsers(dest="op", required=True)
    rn = r.add_parser("new")
    rn.add_argument("kind", help="an append-only kind, e.g. decision or story")
    rn.add_argument("title")
    rn.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    body = rn.add_mutually_exclusive_group(required=True)
    body.add_argument("--body")
    body.add_argument("--file", type=Path, help="read the body from a file (owner words keep their line breaks)")
    rs = r.add_parser("stamp")
    rs.add_argument("ids", nargs="+")
    ra = r.add_parser("amend")
    ra.add_argument("id")
    ra.add_argument("text")

    bn = groups.add_parser("banner").add_subparsers(dest="op", required=True)
    bn.add_parser("show")
    bs = bn.add_parser("set")
    bs.add_argument("--seen", required=True, help="the hash `banner show` printed")
    src = bs.add_mutually_exclusive_group(required=True)
    src.add_argument("--text")
    src.add_argument("--file", type=Path)
    return ap


# (group, verb) -> the operation in ``ops.OPS``. The CLI spells `context-engine <group> <verb>`.
CLI_OPS = {
    ("session", "start"): "session_start",
    ("session", "close"): "session_close",
    ("session", "pause"): "session_pause",
    ("orient", None): "orient",
    ("routes", None): "routes",
    ("lint", None): "lint",
    **{("task", v): f"task_{v}" for v in ("new", "set", "promote", "dep", "comment", "touch", "close", "reopen", "section", "list", "show")},
    **{("ask", v): f"ask_{v}" for v in ("new", "raised", "later", "answer")},
    ("baton", "add"): "baton_add",
    ("baton", "done"): "baton_done",
    ("baton", "expire"): "hk_expire_batons",
    ("pause", "open"): "pause_open",
    ("pause", "resume"): "pause_resume",
    ("record", "new"): "record_new",
    ("record", "stamp"): "record_stamp",
    ("record", "amend"): "record_amend",
    ("banner", "show"): "banner_show",
    ("banner", "set"): "banner_set",
}


def _params(args: argparse.Namespace) -> dict:
    """Turn the parsed arguments into the operation's parameters (lists, dicts, file bodies)."""
    a = vars(args)
    if "set" in a:
        a["fields"] = _fields(a["set"])
    for name in ("deps", "add", "remove", "blocks"):
        if isinstance(a.get(name), str):
            a[name] = _ids(a[name])
    if isinstance(a.get("ids"), list):
        a["ids"] = _ids(" ".join(a["ids"]))
    if a.get("file") is not None:
        a["body" if args.group == "record" else "text"] = a["file"].read_text(encoding="utf-8")
    return a


def run(argv: list[str] | None = None) -> tuple[int, str]:
    args = build().parse_args(argv)
    o = ops.OPS[CLI_OPS[(args.group, getattr(args, "op", None))]]
    a = _params(args)
    return o.fn(Engine(args.root), ops.Caller(args.session, args.actor), **{p.name: a[p.name] for p in o.params})


def main(argv: list[str] | None = None) -> int:
    try:
        code, out = run(argv)
    except Refusal as r:
        print(str(r), file=sys.stderr)
        return 2
    sys.stdout.reconfigure(encoding="utf-8")
    print(out)
    return code


if __name__ == "__main__":
    sys.exit(main())
