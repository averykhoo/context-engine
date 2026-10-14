"""CE-64: an agent commit's `Session:` trailer sits where git reads it, the message's last
paragraph, so procedures § Reconciling foreign commits never counts a session's own commit as
foreign. Git, not the engine's own parser, reads every message back: the engine's commits, a
message written to the documented template, and the template itself wherever a doc shows one."""

import re
import subprocess
from pathlib import Path

from context_engine import commit as C

from test_commit import git, mrepo, run, start  # noqa: F401 (mrepo is a fixture)

REPO = Path(__file__).resolve().parents[1]
KIT = REPO / "src" / "context_engine" / "kit"
MARK = "<!-- commit-message-template -->"
AUTHOR = "Claude <noreply@anthropic.com>"


def reconcile_format() -> str:
    """The `git log --format` procedures § Reconciling foreign commits finds foreign commits with."""
    text = (KIT / "docs" / "runbooks" / "procedures.md").read_text(encoding="utf-8")
    found = re.findall(r"`git log --format='([^']*%\(trailers:key=Session[^']*)' <sha>\.\.HEAD`", text)
    assert len(found) == 1, found
    return found[0]


def trailers(root, rev="HEAD") -> list[str]:
    msg = git(root, "log", "-1", "--format=%B", rev)
    # bytes, not text: text mode on Windows sends `\r\n` (CE-67)
    p = subprocess.run(["git", "interpret-trailers", "--parse"], cwd=root, input=msg.encode("utf-8"), capture_output=True, check=True)
    return p.stdout.decode("utf-8").splitlines()


def template() -> str:
    """The commit message template manual-mode § context-engine commit gives."""
    text = (KIT / "docs" / "runbooks" / "manual-mode.md").read_text(encoding="utf-8")
    assert text.count(MARK) == 1, "manual-mode.md marks exactly one commit message template"
    m = re.compile(r"```text\n(.*?)```", re.S).match(text, text.index("```", text.index(MARK)))
    assert m, "the template mark is followed by a ```text block"
    return m.group(1)


def fill(t: str, key: str) -> str:
    t = t.replace("<key>", key).replace("<name> <email>", "\0").replace("<id>", "CE-1")
    return re.sub(r"<[^<>\n]+>", "words", t).replace("\0", AUTHOR)


def test_every_engine_commit_carries_session_where_reconciling_reads_it(mrepo):
    """Each kind of commit the engine makes, read back with the very `git log` reconciling runs:
    none shows `[]`, the mark of a foreign commit."""
    base = git(mrepo, "rev-parse", "HEAD").strip()
    c = start(mrepo)
    run(mrepo, "task_new", c, title="Build the parser")
    run(mrepo, "task_close", c, id="CE-1", msg="done in abc1234", body="Sabotage: dropped the check -> test_parser red")
    run(mrepo, "record_new", c, kind="decision", title="Kept", body="Owner words.", fields={"actor": "owner", "decision_status": "BUILT"})
    run(mrepo, "baton_add", c, step="a step", why="no time")
    (mrepo / "a.py").write_text("a = 1\n", encoding="utf-8")
    run(mrepo, "commit", c, paths=["a.py"], message=f"CE-1: a\n\nSabotage: x -> test_y red\n\nCo-Authored-By: {AUTHOR}\n")
    assert trailers(mrepo) == [f"Co-Authored-By: {AUTHOR}", f"Session: {c.session}"]
    run(mrepo, "session_close", c, rows="CE-1", summary=["built"], guards="green", read="board")
    log = git(mrepo, "log", f"--format={reconcile_format()}", f"{base}..HEAD").splitlines()
    assert len(log) == 5, log
    assert [ln for ln in log if not ln.endswith(f"[{c.session}]")] == [], log


def test_a_message_written_to_the_documented_template_carries_its_trailers(tmp_path, mrepo):
    """By hand: git reads `Session:`, `Closes:` and `Co-Authored-By:` from the template as written.
    Through the engine, with `Session:` left out as the doc says: the engine adds it to that paragraph."""
    key = "2026-10-14z"
    root = tmp_path / "plain"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.email", "t@example.com")
    git(root, "config", "user.name", "t")
    (root / "a.py").write_text("a = 1\n", encoding="utf-8")
    (root / "msg.txt").write_bytes(fill(template(), key).encode("utf-8"))
    git(root, "add", "a.py")
    git(root, "commit", "-q", "-F", "msg.txt")
    read = lambda k: git(root, "log", "-1", f"--format=%(trailers:key={k},valueonly)").strip()  # noqa: E731
    assert (read("Session"), read("Closes"), read("Co-Authored-By")) == (key, "CE-1", AUTHOR)
    assert not [t for t in trailers(root) if t.startswith("Sabotage:")], "the Sabotage lines are body, not trailers"

    c = start(mrepo)
    (mrepo / "a.py").write_text("a = 1\n", encoding="utf-8")
    msg = "\n".join(ln for ln in fill(template(), c.session).split("\n") if not ln.startswith("Session:"))
    run(mrepo, "commit", c, paths=["a.py"], message=msg)
    assert trailers(mrepo) == ["Closes: CE-1", f"Co-Authored-By: {AUTHOR}", f"Session: {c.session}"]


def _docs() -> list[Path]:
    """Every living text that prescribes how a commit message ends (frozen FRAMEWORK-v*.md excepted)."""
    files = [REPO / "CLAUDE.md", REPO / "docs" / "framework" / "FRAMEWORK.md", REPO / "docs" / "framework" / "contract.md"]
    files += sorted((REPO / "docs" / "runbooks").glob("*.md"))
    files += sorted(p for p in KIT.rglob("*.md") if "__pycache__" not in p.parts)
    return files


def test_no_documented_commit_message_puts_session_outside_the_last_paragraph():
    """A fenced message with a `Session:` line ends in one trailer paragraph holding it; an inline
    `git commit ... -m "Session: <key>"` has no `-m` after it (each `-m` is a paragraph). So the
    docs cannot drift back to `Session:`, a blank line, then `Co-Authored-By:`."""
    bad, blocks = [], 0
    for path in _docs():
        text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        where = path.relative_to(REPO).as_posix()
        for block in re.findall(r"```[^\n]*\n(.*?)```", text, re.S):
            if not re.search(r"^Session: ", block, re.M):
                continue
            blocks += 1
            paras = C._paragraphs(block)
            last = paras[-1]
            if not (C._is_trailers(last) and re.search(r"^Session: ", last, re.M)):
                bad.append(f"{where}: a fenced message whose last paragraph is not trailers holding Session:")
            if any(re.search(r"^Session: ", p, re.M) for p in paras[:-1]):
                bad.append(f"{where}: a fenced message with a Session: line before its last paragraph")
        for m in re.finditer(r'-m "Session: [^"]*"([^`\n]*)', text):
            if re.search(r"(^|\s)-m\s", m.group(1)):
                bad.append(f"{where}: an inline commit with a -m after its Session: paragraph: {m.group(0)[:80]}")
    assert blocks >= 2, "the template (kit manual-mode and its copy) is among the fenced messages, so the scan is not vacuous"
    assert bad == [], "\n".join(bad)
