"""CE-64: an agent commit's `Session:` trailer sits where git reads it, the message's last
paragraph, so procedures § Reconciling foreign commits never counts a session's own commit as
foreign. Git, not the engine's own parser, reads every message back: the engine's commits, a
message written to the documented template, and the template itself wherever a doc shows one.
CE-197 (DEC-170): that paragraph also names the co-author, `Co-Authored-By:`, on every engine commit."""

import re
import subprocess
from pathlib import Path

import pytest

from context_engine import commit as C
from context_engine import ops
from context_engine.errors import Refusal

from test_commit import git, mrepo, run, start  # noqa: F401 (mrepo is a fixture)

REPO = Path(__file__).resolve().parents[1]
KIT = REPO / "src" / "context_engine" / "kit"
MARK = "<!-- commit-message-template -->"
AUTHOR = "Claude <noreply@anthropic.com>"


def reconcile_format() -> str:
    """The `git log --format` procedures § Reconciling foreign commits finds foreign commits with."""
    text = (KIT / "docs" / "runbooks" / "procedures.md").read_text(encoding="utf-8")
    found = re.findall(r"`git log --format='([^']*%\(trailers:key=Session[^']*)' <sha>\.\.<end>`", text)
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
    run(mrepo, "session_close", c, rows="CE-1", summary=["built"], guards="gate 3 passed", read="board")
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


def test_a_work_commit_to_the_template_keeps_its_sabotage_lines_as_body(mrepo):
    """CE-197: a work commit has no `Closes:` (FRAMEWORK §6.10 item 1), so the template with the
    lines the doc says to leave out ends in its `Sabotage:` paragraph. Through the engine, git reads
    `Session:` and `Co-Authored-By:` as the trailers and the `Sabotage:` lines stay body."""
    c = start(mrepo)
    (mrepo / "a.py").write_text("a = 1\n", encoding="utf-8")
    drop = ("Closes:", "Session:", "Co-Authored-By:")
    msg = "\n".join(ln for ln in fill(template(), c.session).split("\n") if not ln.startswith(drop))
    assert C._paragraphs(msg)[-1].startswith("Sabotage: "), "the message ends in the Sabotage paragraph"
    run(mrepo, "commit", c, paths=["a.py"], message=msg)
    assert trailers(mrepo) == [f"Session: {c.session}", f"Co-Authored-By: {AUTHOR}"]
    assert re.search(r"^Sabotage: ", git(mrepo, "log", "-1", "--format=%b"), re.M), "the Sabotage line is still in the body"


@pytest.mark.parametrize("last, joined", [
    ("Sabotage: a -> test_b red", False),
    ("Sabotage: a -> test_b red\nRefs: CE-1", False),
    ("Signed-off-by: A <a@example.com>", True),
    ("Sabotage: a -> test_b red\nCloses: CE-1", True),
    ("CO-AUTHORED-BY: B <b@example.com>", True),
])
def test_the_engine_adds_to_a_closing_trailer_paragraph_only(last, joined):
    """`session_message` puts `Session:` and `Co-Authored-By:` in the last paragraph only when that
    paragraph already holds a closing trailer (`Session:`, `Closes:`, a `<who>-by:`); otherwise
    they open a paragraph of their own, so `Token: value` body lines never turn into trailers."""
    out = C._paragraphs(C.session_message(f"CE-1: x\n\nwhy\n\n{last}\n", [], "k", AUTHOR))
    ours = f"Session: k\nCo-Authored-By: {AUTHOR}"
    assert out[2:] == ([f"{last}\n{ours}"] if joined else [last, ours]), out


def test_the_engine_joins_a_last_paragraph_holding_only_session(tmp_path):
    """A message whose last paragraph is its own `Session:` trailer is closing: `Co-Authored-By:`
    joins it rather than opening a paragraph after it, which would leave git reading no `Session:`
    and the commit foreign."""
    msg = C.session_message("CE-1: x\n\nwhy\n\nSession: k\n", [], "k", AUTHOR)
    assert C._paragraphs(msg)[2:] == [f"Session: k\nCo-Authored-By: {AUTHOR}"], msg
    p = subprocess.run(["git", "interpret-trailers", "--parse"], cwd=tmp_path, input=msg.encode("utf-8"),
                       capture_output=True, check=True)
    assert p.stdout.decode("utf-8").splitlines() == ["Session: k", f"Co-Authored-By: {AUTHOR}"]


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


def test_every_by_hand_commit_recipe_ends_in_session_and_co_author(tmp_path):
    """CE-197: manual mode's inline `git commit --only` recipes (Commit the write, pause open),
    run as written, give a commit git reads `Session:` and `Co-Authored-By:` from, so committing by
    hand does not drop the line the engine writes."""
    import shlex
    text = (KIT / "docs" / "runbooks" / "manual-mode.md").read_text(encoding="utf-8")
    recipes = [r for r in re.findall(r"`(git commit --only [^`]*)`", text) if "Session: <key>" in r]
    assert len(recipes) >= 2, recipes
    key = "2026-10-14z"
    root = tmp_path / "plain"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.email", "t@example.com")
    git(root, "config", "user.name", "t")
    for n, recipe in enumerate(recipes):
        argv = shlex.split(recipe)
        argv = argv[2:argv.index("--")]  # drop `git commit`, and the paths: a file of our own stands in
        argv = [fill(a, key) for a in argv]
        (root / "a.py").write_text(f"a = {n}\n", encoding="utf-8")
        git(root, "add", "a.py")
        git(root, "commit", "-q", *argv, "--", "a.py")
        assert trailers(root) == [f"Session: {key}", f"Co-Authored-By: {AUTHOR}"], recipe


# -- CE-197 (DEC-170): every engine commit names its co-author, in the same trailer paragraph -----

OPUS = "Claude Opus 5.5 <noreply@anthropic.com>"


def _log(root, base: str) -> list[str]:
    """`<Session> | <Co-Authored-By>` per commit after ``base``, as git itself reads the trailers."""
    fmt = "%(trailers:key=Session,valueonly,separator=%x2C) | %(trailers:key=Co-Authored-By,valueonly,separator=%x2C)"
    return git(root, "log", f"--format={fmt}", f"{base}..HEAD").splitlines()


def test_every_engine_commit_names_the_actors_model_beside_session(mrepo):
    """The milestone commits (a task close, owner words, a baton, a session close) and the
    session's own commit each end in one trailer paragraph that git reads both lines from, the
    co-author named from the actor's model id."""
    base = git(mrepo, "rev-parse", "HEAD").strip()
    c = run_start(mrepo, "claude-code/claude-opus-5-5")
    run(mrepo, "task_new", c, title="Build the parser")
    run(mrepo, "task_close", c, id="CE-1", msg="done in abc1234", body="Sabotage: dropped the check -> test_parser red")
    run(mrepo, "record_new", c, kind="decision", title="Kept", body="Owner words.", fields={"actor": "owner", "decision_status": "BUILT"})
    run(mrepo, "baton_add", c, step="a step", why="no time")
    (mrepo / "a.py").write_text("a = 1\n", encoding="utf-8")
    run(mrepo, "commit", c, paths=["a.py"], message="CE-1: a")
    assert trailers(mrepo) == [f"Session: {c.session}", f"Co-Authored-By: {OPUS}"]
    run(mrepo, "session_close", c, rows="CE-1", summary=["built"], guards="gate 3 passed", read="board")
    log = _log(mrepo, base)
    assert len(log) == 5, log
    assert log == [f"{c.session} | {OPUS}"] * 5, log


def run_start(root, actor):
    c = ops.Caller(actor=actor)
    run(root, "session_start", c)
    return c


def test_a_human_actors_commit_claims_no_co_author(mrepo):
    """A person (`human:<id>`) running the engine commits with `Session:` alone."""
    base = git(mrepo, "rev-parse", "HEAD").strip()
    c = run_start(mrepo, "human:avery")
    run(mrepo, "task_new", c, title="Build the parser")
    run(mrepo, "task_close", c, id="CE-1", msg="done")
    (mrepo / "a.py").write_text("a = 1\n", encoding="utf-8")
    run(mrepo, "commit", c, paths=["a.py"], message="CE-1: a")
    assert _log(mrepo, base) == [f"{c.session} | "] * 2


@pytest.mark.parametrize("model, name", [
    ("claude-opus-5-5", "Claude Opus 5.5"),
    ("claude-sonnet-4-5-20250929", "Claude Sonnet 4.5"),
    ("claude-opus-4", "Claude Opus 4"),
    ("claude-3-5-haiku-20241022", "Claude 3.5 Haiku"),
    ("claude-opus-5-5[1m]", "Claude Opus 5.5"),
    ("us.anthropic.claude-sonnet-4-5-20250929-v1:0", "Claude Sonnet 4.5"),
    ("claude-opus-4-1@20250805", "Claude Opus 4.1"),
    ("opus", "Claude Opus"),
    ("claude-x9z", "Claude"),
    ("gpt-5", None),
    ("test", None),
])
def test_a_model_id_reads_as_its_name(model, name):
    assert C.model_name(model) == name


def test_the_co_author_comes_from_the_flag_then_the_model_then_the_env_then_the_actor(monkeypatch):
    actor = "claude-code/claude-opus-5-5"
    assert C.co_author(actor) == OPUS
    assert C.co_author("claude-code/test") == "Claude <noreply@anthropic.com>"  # a Claude harness, a model it cannot read
    assert C.co_author("codex/gpt-5") is None  # no address to give: CE_CO_AUTHOR or --co-author names one
    assert C.co_author("human:avery") is None and C.co_author("process:ci") is None
    monkeypatch.setenv(C.CO_AUTHOR_ENV, "Env Bot <env@example.com>")
    assert C.co_author(actor) == "Env Bot <env@example.com>"
    assert C.co_author(actor, model="claude-haiku-4-5") == "Claude Haiku 4.5 <noreply@anthropic.com>"
    assert C.co_author(actor, given="A B <a@b.c>", model="claude-haiku-4-5") == "A B <a@b.c>"
    assert C.co_author(actor, given="none") is None
    monkeypatch.setenv(C.CO_AUTHOR_ENV, "none")
    assert C.co_author(actor) is None
    monkeypatch.setenv(C.CO_AUTHOR_ENV, "not an address")
    with pytest.raises(Refusal, match="CE_CO_AUTHOR is 'not an address'"):
        C.co_author(actor)
    assert C.co_author(actor, strict=False) == OPUS  # a milestone commit reads the actor instead
    with pytest.raises(Refusal, match="not `<name> <email>`"):
        C.co_author(actor, given="Claude")
    with pytest.raises(Refusal, match="not a Claude model id"):
        C.co_author(actor, model="gpt-5")


def test_the_session_commit_takes_the_co_author_it_is_given_once(mrepo, monkeypatch):
    c = run_start(mrepo, "claude-code/claude-opus-5-5")
    n = 0

    def commit(**kw):
        nonlocal n
        n += 1
        (mrepo / "a.py").write_text(f"a = {n}\n", encoding="utf-8")
        run(mrepo, "commit", c, paths=["a.py"], **kw)
        return git(mrepo, "log", "-1", "--format=%B")

    commit(message="CE-1: one", co_author="A B <a@b.c>")
    assert trailers(mrepo) == [f"Session: {c.session}", "Co-Authored-By: A B <a@b.c>"]
    commit(message="CE-1: two", model="claude-sonnet-4-5")
    assert trailers(mrepo) == [f"Session: {c.session}", "Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"]
    msg = commit(message="CE-1: three", co_author="none")
    assert trailers(mrepo) == [f"Session: {c.session}"] and "Co-Authored-By" not in msg
    monkeypatch.setenv(C.CO_AUTHOR_ENV, "Env Bot <env@example.com>")
    commit(message="CE-1: four")
    assert trailers(mrepo) == [f"Session: {c.session}", "Co-Authored-By: Env Bot <env@example.com>"]
    monkeypatch.delenv(C.CO_AUTHOR_ENV)
    # the old by-hand layout: the line as the message's last paragraph; the engine's address is the same, so it is not doubled
    msg = commit(message=f"CE-1: five\n\nSabotage: x -> test_y red\n\nCo-Authored-By: {OPUS}\n")
    assert msg.count("Co-Authored-By:") == 1, msg
    assert trailers(mrepo) == [f"Co-Authored-By: {OPUS}", f"Session: {c.session}"], msg
    msg = commit(message="CE-1: six\n\nco-authored-by: Claude <NOREPLY@anthropic.com>")  # any case, another name: the message's line stands
    assert msg.lower().count("co-authored-by:") == 1, msg
    with pytest.raises(Refusal, match="both --co-author and --model"):
        commit(message="CE-1: seven", co_author="A B <a@b.c>", model="claude-opus-5-5")
    with pytest.raises(Refusal, match="not `<name> <email>`"):
        commit(message="CE-1: eight", co_author="Claude")


def test_a_bad_ce_co_author_never_stops_a_milestone_commit(mrepo, monkeypatch):
    """A milestone commit follows a write already made, so a malformed `CE_CO_AUTHOR` cannot refuse
    it: the commit names the actor's model instead. The session's own commit, which writes nothing
    first, refuses it (above)."""
    c = run_start(mrepo, "claude-code/claude-opus-5-5")
    monkeypatch.setenv(C.CO_AUTHOR_ENV, "not an address")
    run(mrepo, "task_new", c, title="Build the parser")
    _, line = run(mrepo, "task_close", c, id="CE-1", msg="done")
    assert "; committed " in line, line
    assert trailers(mrepo) == ["Closes: CE-1", f"Session: {c.session}", f"Co-Authored-By: {OPUS}"]
