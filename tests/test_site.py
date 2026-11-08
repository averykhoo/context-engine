"""The records as a static site, built on demand and never stored (CE-185, US-19, DEC-159), and
the stored decision index's retirement: a config that still names it loads, and orient says what
to remove (DEC-160)."""

import datetime as dt
import re
import subprocess
from pathlib import Path

import pytest

from context_engine import ops
from context_engine.errors import Refusal
from context_engine.working import Engine

from conftest import ASK_BODY, _toml

S, ACTOR = "2026-11-06a", "claude-code/test"
W = {"session": S, "actor": ACTOR}
BOARD = {"enums": {"state": ["open", "closed"], "pri": ["NOW", "NEXT", "LATER", "SOMEDAY"]}, "types": {"created": "date", "moved": "key", "updated": "key", "closed": "key", "deps": "list", "last_asked": "key"}}
CONFIG = {
    "engine": {"oplog": "ops.jsonl", "lockfile": ".context/engine.lock", "bundles": ["decisions", "stories", "tasks"], "commit": "off"},
    "kinds": {
        "task": {"type": "Task", "prefix": "CE", "dir": "tasks", "mode": "replaced", "required": ["title", "pri", "state", "created"], **BOARD},
        "question": {"type": "Question", "prefix": "ASK", "dir": "tasks", "mode": "replaced", "required": ["title", "pri", "state", "created"], **BOARD},
        "decision": {"type": "Decision", "prefix": "DEC", "dir": "decisions", "mode": "append-only", "required": ["title", "actor", "decided", "session", "decision_status"],
                     "enums": {"decision_status": ["BUILT", "PROVISIONAL", "SUPERSEDED", "REJECTED"]},
                     "types": {"decided": "date", "session": "key", "tags": "list", "supersedes": "list", "superseded_by": "list", "tasks": "list"}},
        "story": {"type": "Story", "prefix": "US", "dir": "stories", "mode": "append-only", "required": ["title", "actor", "date", "story_status"],
                  "enums": {"story_status": ["live", "unspecified", "unconfirmed", "retired"]}, "types": {"date": "date"}},
    },
    "working": {"ledger": "ledger.md", "handoff": "HANDOFF.md", "board": ["task", "question"], "task": "task", "question": "question", "decision": "decision", "register": "invariants.md"},
    "guards": {"stories": "story"},
}
REGISTER = "# Residual-risk register\n\n## INV-1: a risk that stays\n\n- **affects:** the owner\n- **control:** CE-2's guard\n- **from:** CE-2, session 2026-11-06a\n"
HREF = re.compile(r'href="([^"]*)"')


def _git(root: Path, *args: str) -> str:
    p = subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=root, capture_output=True, text=True)
    assert p.returncode == 0, (args, p.stderr)
    return p.stdout


def _repo(root: Path, config: dict = CONFIG) -> Engine:
    root.mkdir(parents=True, exist_ok=True)
    (root / "context.toml").write_text(_toml(config), encoding="utf-8")
    (root / "invariants.md").write_text(REGISTER, encoding="utf-8")
    return Engine(root, today=lambda: dt.date(2026, 11, 6))


def _records(e: Engine) -> Engine:
    """Decisions (one superseded, one rejected, tagged and not), stories, open and closed tasks, a
    question, and bodies that name ids, a URL, an id the site does not hold, and markup and `&`
    that must stay text."""
    e.new("task", "Build the parser", pri="NOW", brief="no new dependency", **W)
    e.new("task", "Pin the parser", pri="NEXT", body="Follows CE-1 and DEC-2; see https://example.org/spec.\n\n## Log\n", **W)
    e.new("task", "Done already", **W)
    e.close("CE-3", "done in abc1234", **W)
    e.ask_new("Which way?", body=ASK_BODY, **W)
    for title, status, tags in (("One way", "BUILT", "[parsing]"), ("Old way", "PROVISIONAL", ""), ("New way", "BUILT", "")):
        fields = {"actor": "owner", "decision_status": status, **({"tags": tags} if tags else {})}
        e.record_new("decision", title, f"The owner said {title.lower()}, for CE-1; not AC-9.\n", fields, **W)
    e.supersede("DEC-2", "DEC-3", **W)
    e.record_new("decision", "No way", "The owner said no: <script>alert(1)</script> & DEC-1 stays; a <b> & c.\n", {"actor": "owner", "decision_status": "REJECTED"}, **W)
    e.record_new("story", "Parse it", "The owner: parse it, as DEC-1 says.\n", {"actor": "owner", "story_status": "live"}, **W)
    return e


def _tree(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file() and ".git" not in p.parts}


def _build(e: Engine, out) -> str:
    code, line = ops.OPS["site_build"].call(e, ops.Caller(), outdir=str(out))
    assert code == 0
    return line


@pytest.mark.criterion("AC-181")
def test_the_site_holds_every_record_and_every_link_resolves(tmp_path):
    e = _records(_repo(tmp_path / "repo"))
    before = _tree(e.root)
    out = tmp_path / "site"
    line = _build(e, out)
    assert ops.OPS["site_build"].write is False
    assert _tree(e.root) == before, "the build wrote in the repo"
    pages = {p.relative_to(out).as_posix(): p.read_text(encoding="utf-8") for p in out.rglob("*.html")}
    assert line.startswith(f"site: {len(pages)} pages written to "), line

    listing = {"decision": "decisions.html", "story": "stories.html", "task": "board.html", "question": "board.html"}
    ids = []
    for kind, page in listing.items():
        for r in e.store.heads(kind):
            ids.append(r.id)
            own = f"{kind}/{r.id}.html"
            assert own in pages and f"<h1>{r.id}: " in pages[own], own
            assert f'href="{own}"' in pages[page], f"{page} does not link {r.id}"
    assert sorted(ids) == ["ASK-1", "CE-1", "CE-2", "CE-3", "DEC-1", "DEC-2", "DEC-3", "DEC-4", "US-1"]

    for rel, text in pages.items():  # every link resolves within the site, an anchor to an id on its page
        for href in HREF.findall(text):
            if href.startswith(("http://", "https://")):
                continue
            target, _, anchor = href.partition("#")
            path = (out / rel).parent / target
            assert path.is_file() and out in path.resolve().parents, f"{rel}: {href} resolves to nothing in the site"
            if anchor:
                assert f'id="{anchor}"' in path.read_text(encoding="utf-8"), f"{rel}: {href} names no anchor there"

    d = pages["decisions.html"]
    assert d.index("<h2>BUILT</h2>") < d.index("<h3>parsing</h3>") < d.index("<h3>untagged</h3>") < d.index("<h2>SUPERSEDED</h2>") < d.index("<h2>REJECTED</h2>"), "decisions are not grouped in the kind's enum order"
    assert 'superseded by <a href="decision/DEC-3.html">DEC-3</a>' in d
    b = pages["board.html"]
    assert b.index("<h2>NOW</h2>") < b.index("<h2>NEXT</h2>") < b.index("<h2>Closed</h2>") < b.index('href="task/CE-3.html"')
    body = pages["task/CE-2.html"]  # ids and URLs in a body are links; an id the site lacks stays text
    assert 'href="../task/CE-1.html"' in body and 'href="../decision/DEC-2.html"' in body
    assert '<a href="https://example.org/spec">https://example.org/spec</a>.' in body  # the sentence's full stop is not the URL's
    assert "; not AC-9." in pages["decision/DEC-1.html"]  # no page for criteria: plain text
    assert 'id="INV-1"' in pages["register.html"] and 'href="task/CE-2.html"' in pages["register.html"]
    assert "Not available here" in pages["coverage.html"]  # no [guards] coverage_spec: says why, builds the rest


@pytest.mark.criterion("AC-181")
def test_record_text_on_the_site_is_escaped_not_markup(tmp_path):
    """DEC-159: a body is shown as escaped text. The site is public, so text left unescaped between
    or after the links site.py::Site.link makes is markup injected into the page."""
    e = _records(_repo(tmp_path / "repo"))
    out = tmp_path / "site"
    _build(e, out)
    page = (out / "decision" / "DEC-4.html").read_text(encoding="utf-8")
    assert "<script>" not in page and "<b>" not in page, "a body's markup reached the page"
    # before the first link and after the last: both stretches escaped, the id still a link
    assert 'no: &lt;script&gt;alert(1)&lt;/script&gt; &amp; <a href="../decision/DEC-1.html">DEC-1</a> stays; a &lt;b&gt; &amp; c.' in page


@pytest.mark.criterion("AC-181")
def test_site_build_refuses_a_tracked_or_non_empty_directory(tmp_path):
    e = _records(_repo(tmp_path / "repo"))
    _git(e.root, "init", "-q")
    (e.root / ".gitignore").write_text("build/\n", encoding="utf-8")
    with pytest.raises(Refusal, match="git does not ignore it"):
        _build(e, "docs/site")
    with pytest.raises(Refusal, match="git does not ignore it"):
        _build(e, ".")
    assert not (e.root / "docs").exists()
    _build(e, "build/site")  # git-ignored in the repo: allowed
    assert (e.root / "build" / "site" / "index.html").is_file()
    with pytest.raises(Refusal, match="not empty"):
        _build(e, "build/site")
    (tmp_path / "file").write_text("x", encoding="utf-8")
    with pytest.raises(Refusal, match="not a directory"):
        _build(e, tmp_path / "file")


@pytest.mark.criterion("AC-183")
def test_a_deprecated_decision_index_still_loads_and_orient_names_the_remedy(tmp_path):
    cfg = {**CONFIG, "working": {**CONFIG["working"], "decision_index": "decisions/index.md"}}
    e = _repo(tmp_path / "repo", cfg)
    stored = e.root / "decisions" / "index.md"
    stored.parent.mkdir()
    stored.write_text("# Decisions\n\n- an old listing\n", encoding="utf-8")
    _records(e)
    assert stored.read_text(encoding="utf-8") == "# Decisions\n\n- an old listing\n", "a decision write rewrote the stored index"
    assert [f for f in e.lint() if f.guard == "G-D6"] == []
    text = e.orient(S)
    assert "## Deprecated config: tell the owner" in text, text
    assert "`[working] decision_index` is set" in text and "`git rm decisions/index.md`" in text
    plain = _records(_repo(tmp_path / "plain"))
    assert "Deprecated config" not in plain.orient(S)
