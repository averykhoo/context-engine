"""The records as a static HTML site, built on demand and never stored (FRAMEWORK §6.5, §9.3;
CE-185, US-19, DEC-159).

``build`` writes one page per decision, story and board item, and listing pages: the decisions
grouped as the stored index once was (``decisions.groups``), the stories by status, the board
(open items by tier, then every closed one), the coverage table (``guards.framework_status``)
and the residual-risk register (``review.entries``). Every record id a page names that the site
holds becomes a link, and so does every URL. Bodies are shown as their markdown text, escaped and
wrapped, not rendered: the engine takes no markdown library (DEC-159).

It is a read: it takes no lock, writes no op log line and nothing in the repo. The output
directory must be new or empty, and outside the repo or git-ignored in it, so the site is never
committed (a stored copy would be the stored index again). CI publishes it
(``.github/workflows/pages.yml``); a repo on another host wraps the same op.

Deliberately not here: rendering markdown, search, and pages for kinds the site does not list
(batons, pauses, criteria rows): their ids stay plain text.
"""

from __future__ import annotations

import html
import re
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from . import __version__
from . import decisions as D
from . import guards as GD
from . import review as R
from .errors import Refusal

if TYPE_CHECKING:
    from .store import Record
    from .working import Engine

# a URL ends before trailing punctuation (`see https://x.org/a.` links `https://x.org/a`)
LINKABLE = re.compile(r"(?P<url>https?://[^\s<>\"'`)\]]*[^\s<>\"'`)\].,;:!?])|(?<![\w-])(?P<id>[A-Z]+-[0-9]+)(?![\w-])")
STYLE = """body{font:15px/1.5 system-ui,sans-serif;margin:0;color:#1f2328;background:#fff}
nav{padding:.6em 1.2em;background:#f6f8fa;border-bottom:1px solid #d0d7de}nav a{margin-right:1em}
main{max-width:64em;padding:0 1.2em 2em}footer{padding:1em 1.2em;color:#59636e;font-size:.85em}
pre{white-space:pre-wrap;word-wrap:break-word;background:#f6f8fa;padding:1em;border-radius:6px}
table{border-collapse:collapse}td,th{border:1px solid #d0d7de;padding:.25em .5em;vertical-align:top;text-align:left}
a{color:#0969da}.muted{color:#59636e}"""
LISTINGS = (("decisions.html", "Decisions"), ("stories.html", "Stories"), ("board.html", "Board"), ("coverage.html", "Coverage"), ("register.html", "Register"))


def build(e: "Engine", outdir: str) -> str:
    """Write the site into ``outdir`` (relative to the repo root, or absolute); one line back."""
    out = _target(e.root, outdir)
    pages = Site(e).pages()
    for rel, text in pages.items():
        path = out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
    return f"site: {len(pages)} pages written to {out.as_posix()} ({Site.counts(pages)}); nothing stored in the repo"


def _target(root: Path, outdir: str) -> Path:
    """The output directory, refused when the site would land in the tracked tree or on files."""
    if not outdir.strip():
        raise Refusal("no output directory given", "name a new or empty directory outside the repo, e.g. `$RUNNER_TEMP/site` in CI")
    root = root.resolve()
    out = Path(outdir)
    out = (out if out.is_absolute() else root / out).resolve()
    if out == root or root in out.parents:
        rel = out.relative_to(root).as_posix()
        if out == root or not _ignored(root, rel):
            raise Refusal(f"`{rel or '.'}` is in the repo and git does not ignore it, so the site would be committed: a stored index again (CE-185)",
                          "build it outside the repo (CI uses `$RUNNER_TEMP/site`), or in a git-ignored directory such as `.scratch/site`")
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise Refusal(f"{out.as_posix()} is {'not a directory' if not out.is_dir() else 'not empty'}",
                      "give a new or empty directory; to rebuild, delete the old build first (the site writes over nothing)")
    return out


def _ignored(root: Path, rel: str) -> bool:
    try:
        p = subprocess.run(["git", "check-ignore", "-q", "--", rel], cwd=root, capture_output=True)
    except FileNotFoundError:
        return False
    return p.returncode == 0


def _commit(root: Path) -> str:
    try:
        p = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=root, capture_output=True, text=True)
    except FileNotFoundError:
        return ""
    return p.stdout.strip() if p.returncode == 0 else ""


def esc(text: object) -> str:
    return html.escape(str(text), quote=True)


class Site:
    """The pages of one repo's site, keyed by their path in the site (``decision/DEC-1.html``)."""

    def __init__(self, e: "Engine"):
        self.e = e
        cfg = e.store.config
        self.decision = e.w.decision or ""
        self.story = cfg.guards.stories or ("story" if "story" in cfg.kinds else "")
        self.board = tuple(e.w.board)
        self.kinds = tuple(dict.fromkeys(k for k in (self.decision, self.story, *self.board) if k))
        self.records: dict[str, list[Record]] = {k: sorted(e.store.records(k), key=lambda r: int(r.id.rsplit("-", 1)[1])) for k in self.kinds}
        self.links = {r.id: f"{k}/{r.id}.html" for k, rs in self.records.items() for r in rs}
        self.register = self._register()
        self.links |= {x.id: f"register.html#{x.id}" for x in self.register}
        self.name = e.root.name
        self.commit = _commit(e.root)

    @staticmethod
    def counts(pages: dict[str, str]) -> str:
        per: dict[str, int] = {}
        for rel in pages:
            if "/" in rel:
                per[rel.split("/")[0]] = per.get(rel.split("/")[0], 0) + 1
        return ", ".join(f"{n} {k}" for k, n in per.items()) or "no records"

    def _register(self) -> list[R.Entry]:
        rel = self.e.w.register
        path = self.e.root / rel if rel else None
        return R.entries(path.read_bytes().decode("utf-8")) if path is not None and path.is_file() else []

    # -- pieces ------------------------------------------------------------------------------

    def link(self, text: str, depth: int) -> str:
        """``text`` escaped, with each URL and each id the site holds as a link."""
        up = "../" * depth
        out, at = [], 0
        for m in LINKABLE.finditer(text):
            out.append(esc(text[at : m.start()]))
            if m["url"]:
                out.append(f'<a href="{esc(m["url"])}">{esc(m["url"])}</a>')
            elif m["id"] in self.links:
                out.append(f'<a href="{up}{self.links[m["id"]]}">{m["id"]}</a>')
            else:
                out.append(esc(m["id"]))
            at = m.end()
        out.append(esc(text[at:]))
        return "".join(out)

    def ref(self, rid: str, depth: int) -> str:
        return f'<a href="{"../" * depth}{self.links[rid]}">{esc(rid)}</a>' if rid in self.links else esc(rid)

    def page(self, title: str, body: str, depth: int) -> str:
        up = "../" * depth
        nav = [f'<a href="{up}index.html">{esc(self.name)}</a>'] + [f'<a href="{up}{href}">{label}</a>' for href, label in LISTINGS]
        made = f"Built by <code>context-engine site build</code> (engine {esc(__version__)})" + (f" from commit {esc(self.commit)}" if self.commit else "")
        return (f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
                f'<meta name="viewport" content="width=device-width, initial-scale=1">'
                f"<title>{esc(title)} · {esc(self.name)}</title><style>{STYLE}</style></head>\n"
                f"<body><nav>{' '.join(nav)}</nav>\n<main><h1>{esc(title)}</h1>\n{body}\n</main>\n"
                f"<footer>{made}. Generated from the records on demand; nothing here is stored in the repo.</footer></body></html>\n")

    def record_page(self, r: "Record") -> str:
        rows = []
        for key, value in r.doc.data.items():
            text = ", ".join(str(v) for v in value) if isinstance(value, (list, tuple)) else str(value)
            rows.append(f"<tr><th>{esc(key)}</th><td>{self.link(text, 1)}</td></tr>")
        path = r.path.relative_to(self.e.root).as_posix()
        body = (f'<p class="muted">{esc(path)}</p>\n<table>{"".join(rows)}</table>\n'
                f'<pre>{self.link(r.doc.body.replace(chr(13) + chr(10), chr(10)).strip(chr(10)), 1)}</pre>')
        return self.page(f"{r.id}: {r.doc.get('title') or ''}", body, 1)

    # -- listings ----------------------------------------------------------------------------

    def decisions_page(self) -> str:
        if not self.decision:
            return self.page("Decisions", "<p>No decision kind is configured (<code>[working] decision</code>).</p>", 0)
        rows = [D.Row(r.id, self.links[r.id], dict(r.doc.data)) for r in self.records[self.decision]]
        statuses = self.e.store.config.kind(self.decision).enums.get(D.STATUS_KEY, ())
        out = [f"<p>{len(rows)} decisions, grouped by status, then by first tag (FRAMEWORK §6.5).</p>"]
        for status, tagged in D.groups(rows, statuses):
            out.append(f"<h2>{esc(status)}</h2>")
            for tag, group in tagged:
                out.append(f"<h3>{esc(tag)}</h3>\n<ul>")
                for row in group:
                    text, who, later = D.line_parts(row)
                    line = f"<li>{self.ref(row.id, 0)}: {self.link(text, 0)}" + (f" <em>({self.link(who, 0)})</em>" if who else "")
                    if later:
                        line += "; superseded by " + ", ".join(self.ref(x, 0) for x in later)
                    out.append(line + "</li>")
                out.append("</ul>")
        return self.page("Decisions", "\n".join(out), 0)

    def stories_page(self) -> str:
        if not self.story:
            return self.page("Stories", "<p>No story kind is configured.</p>", 0)
        recs = self.records[self.story]
        order = list(self.e.store.config.kind(self.story).enums.get("story_status", ()))
        order += sorted({str(r.doc.get("story_status")) for r in recs} - set(order))
        out = [f"<p>{len(recs)} stories: the owner's words, verbatim (FRAMEWORK §3.2).</p>"]
        for status in order:
            group = [r for r in recs if str(r.doc.get("story_status")) == status]
            if group:
                out.append(f"<h2>{esc(status)}</h2>\n<ul>")
                out += [f"<li>{self.ref(r.id, 0)}: {self.link(str(r.doc.get('title') or ''), 0)} <em>({esc(r.doc.get('actor') or '')}, {esc(r.doc.get('date') or '')})</em></li>" for r in group]
                out.append("</ul>")
        return self.page("Stories", "\n".join(out), 0)

    def board_page(self) -> str:
        if not self.board:
            return self.page("Board", "<p>No board kinds are configured (<code>[working] board</code>).</p>", 0)
        recs = [r for k in self.board for r in self.records[k]]
        tiers = list(self.e.store.config.kind(self.board[0]).enums.get("pri", ()))
        is_open = [r for r in recs if r.doc.get("state") == "open"]
        tiers += sorted({str(r.doc.get("pri")) for r in is_open} - set(tiers))
        num = lambda r: (r.kind.prefix, int(r.id.rsplit("-", 1)[1]))
        item = lambda r, extra: f"<li>{self.ref(r.id, 0)}: {self.link(str(r.doc.get('title') or ''), 0)}{extra}</li>"
        out = [f"<p>{len(is_open)} open, {len(recs) - len(is_open)} closed (FRAMEWORK §5.2).</p>"]
        for tier in tiers:
            group = sorted((r for r in is_open if str(r.doc.get("pri")) == tier), key=num)
            if group:
                out.append(f"<h2>{esc(tier)}</h2>\n<ul>")
                out += [item(r, f' <span class="muted">— {self.link(str(r.doc.get("brief")), 0)}</span>' if r.doc.get("brief") else "") for r in group]
                out.append("</ul>")
        closed = sorted((r for r in recs if r.doc.get("state") != "open"), key=num)
        if closed:
            out.append("<h2>Closed</h2>\n<ul>")
            out += [item(r, f' <span class="muted">({esc(r.doc.get("closed"))})</span>' if r.doc.get("closed") else "") for r in closed]
            out.append("</ul>")
        return self.page("Board", "\n".join(out), 0)

    def coverage_page(self) -> str:
        try:
            source, by_cls = GD.framework_status(self.e)
        except Refusal as r:
            return self.page("Coverage", f"<p>Not available here: {esc(r.message)}.</p>", 0)
        out = [f"<p>FRAMEWORK's components, procedures and guards with their build status, from {esc(source)}, the board and lint (<code>context-engine coverage</code>).</p>"]
        for cls, heading, cols in GD.STATUS_TABLES:
            out.append(f"<h2>{esc(heading)}</h2>\n<table><tr>" + "".join(f"<th>{esc(c)}</th>" for c in (*cols, "Status", "Board", "Note")) + "</tr>")
            for s in by_cls.get(cls, []):
                lead = (s.item.key, s.item.name) if cls == "procedure" else (s.item.key,)
                out.append("<tr>" + "".join(f"<td>{self.link(str(c), 0)}</td>" for c in (*lead, s.status, s.board, s.note)) + "</tr>")
            out.append("</table>")
        return self.page("Coverage", "\n".join(out), 0)

    def register_page(self) -> str:
        if not self.register:
            why = "No register is configured (<code>[working] register</code>)." if not self.e.w.register else "No residual risk is filed yet."
            return self.page("Residual-risk register", f"<p>{why}</p>", 0)
        out = [f"<p>{len(self.register)} residual risks (FRAMEWORK §7.4).</p>"]
        for x in self.register:
            fields = "".join(f"<tr><th>{esc(k)}</th><td>{self.link(v, 0)}</td></tr>" for k, v in x.fields.items())
            out.append(f'<h2 id="{esc(x.id)}">{esc(x.id)}: {self.link(x.head or x.risk, 0)}</h2>\n<table>{fields}</table>')
        return self.page("Residual-risk register", "\n".join(out), 0)

    def index_page(self) -> str:
        n = {k: len(v) for k, v in self.records.items()}
        lines = [f'<li><a href="{href}">{label}</a></li>' for href, label in LISTINGS]
        held = ", ".join(f"{c} {k}" for k, c in n.items())
        body = (f"<p>The records of {esc(self.name)}, published by its CI from the repo's OKF records ({esc(held)}). "
                f"The records themselves are the markdown files in the repo; this site is generated from them and never stored.</p>\n<ul>{''.join(lines)}</ul>")
        return self.page(self.name, body, 0)

    def pages(self) -> dict[str, str]:
        out = {"index.html": self.index_page(), "decisions.html": self.decisions_page(), "stories.html": self.stories_page(),
               "board.html": self.board_page(), "coverage.html": self.coverage_page(), "register.html": self.register_page()}
        for rs in self.records.values():
            out |= {self.links[r.id]: self.record_page(r) for r in rs}
        return out
