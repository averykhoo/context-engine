"""Confirming a story (CE-58, FRAMEWORK §3.2, §8.1, §11.4): `record confirm` moves an agent's
reconstruction from `unconfirmed` to `live` (or `unspecified`) with the owner's words in one
write, refuses what it must, and G-I2 reds a reconstruction confirmed or unconfirmed by hand, so
INV-51's commonest case is no longer a hand edit lint cannot tell from any other."""

import json
import subprocess

import pytest

from context_engine import mcp, ops
from context_engine.cli import main
from context_engine.errors import Refusal

from test_intent import W, chain, edit, make, reds, story, write  # noqa: F401 (chain is a fixture)

OK = {"actor": "owner", "date": "2026-10-13", "story_status": "live", "goals": "[G-1]"}
AGENT = "agent (claude-x, reconstructed from the PRD)"
RECON = {**OK, "actor": AGENT, "story_status": "unconfirmed"}
STORIES = "docs/stories"


def doc(root, sid: str) -> str:
    return next((root / STORIES).glob(f"{sid}-*.md")).read_text(encoding="utf-8")


def rel(root, sid: str) -> str:
    return next((root / STORIES).glob(f"{sid}-*.md")).relative_to(root).as_posix()


def oplog(root) -> list[dict]:
    p = root / "ops.jsonl"
    return [json.loads(ln) for ln in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []


def snapshot(root) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file() and ".context" not in p.parts}


# -- the operation -------------------------------------------------------------------------


@pytest.mark.criterion("AC-84")
def test_record_confirm_moves_a_reconstruction_on_with_the_owners_words_in_one_write(chain):
    e = make(chain)
    assert e.record_new("story", "Rebuilt", "words", RECON, **W).id == "US-3"
    assert e.record_new("story", "Later", "more words", RECON, **W).id == "US-4"
    words = "yes, that is what I meant\nkeep it"
    line = e.confirm("US-3", words, **W)
    assert line == "US-3: confirmed by owner (story_status: live); their words are under ## Amendments", line
    text = doc(chain, "US-3")
    head = text.split("\n---\n", 1)[0]
    assert "\nstory_status: live\n" in head and f"\nactor: {AGENT}\n" in head, head  # the provenance stays the agent's
    assert text.endswith("\n## Amendments\n\n- **2026-10-13a (claude-code/test):** confirmed (by owner): yes, that is what I meant\n  keep it\n"), text
    assert [(o["op"], o["id"], o["fields"]) for o in oplog(chain)][-1] == ("confirm", "US-3", ["story_status", "body"])
    # a human the charter names, and a story with no criterion yet: `unspecified`
    assert e.confirm("US-4", "right", by="human:avery", status="unspecified", **W).startswith("US-4: confirmed by human:avery (story_status: unspecified)")
    assert "\nstory_status: unspecified\n" in doc(chain, "US-4")
    assert doc(chain, "US-4").endswith("confirmed (by human:avery; unspecified): right\n")
    assert reds(e, "G-I2") == [] and not [f for f in e.lint() if f.guard == "G-D10" and "US-3" in f.path]


@pytest.fixture
def refusing(chain):
    """US-1 and US-2 the owner's, live; US-3 unconfirmed; US-4 confirmed by the op; US-5 confirmed by
    the op and made unconfirmed again by hand; US-6 a reconstruction retired; US-7 a reconstruction
    with a status outside the vocabulary; DEC-1."""
    e = make(chain)
    for title in ("Three", "Four", "Five", "Six"):
        e.record_new("story", title, "words", RECON, **W)
    e.confirm("US-4", "yes", **W)
    e.confirm("US-5", "yes", **W)
    edit(chain, rel(chain, "US-5"), "story_status: live", "story_status: unconfirmed")
    e.retire("US-6", "not wanted", by="owner", **W)
    story(chain, "US-7", actor=AGENT, status="draft")  # a status outside the vocabulary, by hand
    return e


REFUSALS = {
    "by-agent": ({"by": "agent"}, r"`by: agent` is neither `owner` nor `human:<id>`.*an agent never confirms intent"),
    "by-vocabulary": ({"by": "claude"}, r"`by: claude` is neither"),
    "no-words": ({"words": " \n"}, r"no words"),
    "status-vocabulary": ({"status": "retired"}, r"`status: retired` is neither `live` nor `unspecified`"),
    "not-a-story": ({"id": "DEC-1"}, r"DEC-1 is not a story.*decision set"),
    "missing": ({"id": "US-9"}, r"no record US-9"),
    "owners-story": ({"id": "US-1"}, r"US-1's actor is `owner`, not an agent's reconstruction, so there is nothing to confirm"),
    "retired": ({"id": "US-6"}, r"US-6 is retired.*a retirement is final"),
    "already-confirmed": ({"id": "US-4"}, r"US-4 is already confirmed \(`record confirm` in session 2026-10-13a\)"),
    "unknown-status": ({"id": "US-7"}, r"US-7 is `story_status: draft`, none of unconfirmed, live, unspecified"),
    "undone-by-hand": ({"id": "US-5"}, r"US-5 was confirmed by `record confirm` in session 2026-10-13a, and a hand edit has since made it `unconfirmed`.*a confirmation stands"),
}


@pytest.mark.criterion("AC-84")
@pytest.mark.parametrize("case", sorted(REFUSALS))
def test_record_confirm_refuses_before_writing_anything(refusing, chain, case):
    kw, match = REFUSALS[case]
    args = {"id": "US-3", "words": "yes", "by": "owner", **kw}
    before = snapshot(chain)
    with pytest.raises(Refusal, match=match):
        refusing.confirm(args.pop("id"), args.pop("words"), **args, **W)
    assert snapshot(chain) == before


@pytest.mark.criterion("AC-84")
def test_record_confirm_refuses_a_hash_mismatch_and_a_repo_with_no_stories(chain):
    e = make(chain)
    e.record_new("story", "Rebuilt", "words", RECON, **W)  # US-3, stamped
    edit(chain, rel(chain, "US-3"), "words", "other words")
    before = snapshot(chain)
    with pytest.raises(Refusal, match=r"US-3 body above `## Amendments` changed since it was stamped"):
        e.confirm("US-3", "yes", **W)
    assert snapshot(chain) == before
    with pytest.raises(Refusal, match=r"no kind holds the stories.*Remedy: set `stories` in \[guards\]"):
        make(chain, stories="", charter="").confirm("US-3", "yes", **W)


@pytest.mark.criterion("AC-84")
@pytest.mark.parametrize("status", ["live", "unspecified"])
def test_a_reconstruction_is_never_created_live_or_unspecified(chain, status):
    with pytest.raises(Refusal, match=rf"would be created `{status}` with an agent's actor.*only `record confirm` moves it on"):
        make(chain).record_new("story", "Born", "words", {**RECON, "story_status": status}, **W)
    assert sorted(p.name for p in (chain / STORIES).iterdir()) == ["US-1-words.md", "US-2-words.md"]
    assert make(chain, off=["G-I2"]).record_new("story", "Off", "words", {**RECON, "story_status": status}, **W).id == "US-3"


# -- G-I2 on confirmations -----------------------------------------------------------------


@pytest.mark.criterion("AC-85")
def test_g_i2_reds_a_reconstruction_confirmed_or_unconfirmed_by_hand(chain):
    story(chain, "US-3", actor=AGENT)  # made live by hand: nothing records who confirmed it
    story(chain, "US-4", actor=AGENT, status="unspecified")
    story(chain, "US-5", actor=AGENT, status="unconfirmed")  # waits on the owner: green
    e = make(chain)
    assert reds(e, "G-I2") == [
        "docs/stories/US-3-words.md: US-3 is `live` with an agent's actor, but no `record confirm` of it is logged, so nothing records who confirmed the reconstruction or in what words",
        "docs/stories/US-4-words.md: US-4 is `unspecified` with an agent's actor, but no `record confirm` of it is logged, so nothing records who confirmed the reconstruction or in what words",
    ]
    hand = next(f for f in e.lint() if f.guard == "G-I2")
    assert "`record confirm US-3 --by owner --file <their words>`" in hand.remedy and "restore `story_status: unconfirmed` from git" in hand.remedy
    e.confirm("US-3", "the owner confirmed it in chat on 2026-10-12", **W)  # the op takes a hand confirmation, recording whose words
    e.confirm("US-4", "yes", status="unspecified", **W)
    assert "\nstory_status: live\n" in doc(chain, "US-3")
    assert reds(e, "G-I2") == []
    edit(chain, "docs/stories/US-3-words.md", "story_status: live", "story_status: unconfirmed")  # undone by hand
    assert reds(e, "G-I2") == ["docs/stories/US-3-words.md: US-3 was confirmed by `record confirm` in session 2026-10-13a, but its frontmatter now says `story_status: unconfirmed`"]
    edit(chain, "docs/stories/US-3-words.md", "story_status: unconfirmed", "story_status: unspecified")  # live to unspecified: not checked
    assert reds(e, "G-I2") == []
    e.retire("US-5", "not wanted", by="owner", **W)  # a retired reconstruction is history, confirmed or not
    assert reds(e, "G-I2") == []


# -- the entry points and the commit -------------------------------------------------------


def git(root, *args) -> str:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8", check=True).stdout


@pytest.mark.criterion("AC-84")
def test_the_cli_and_the_mcp_tool_confirm_and_commit_by_path(chain, capsys):
    for args in (["init", "-q", "-b", "main"], ["config", "user.email", "t@example.com"], ["config", "user.name", "t"], ["config", "core.autocrlf", "false"]):
        git(chain, *args)
    story(chain, "US-3", actor=AGENT, status="unconfirmed")
    story(chain, "US-4", actor=AGENT, status="unconfirmed")
    make(chain)  # writes context.toml
    git(chain, "add", "-A")
    git(chain, "commit", "-q", "-m", "base")
    (chain / "wip.md").write_text("untracked work\n", encoding="utf-8")
    (chain / "words.md").write_bytes("﻿the owner's words\r\nover two lines\r\n".encode())  # as PowerShell 5.1 saves it: a BOM, CRLF
    argv = ["--root", str(chain), "--session", "2026-10-13a", "--actor", "claude-code/test"]
    assert main([*argv, "record", "confirm", "US-3", "--file", str(chain / "words.md")]) == 0
    out = capsys.readouterr().out.strip()
    sha = git(chain, "rev-parse", "--short", "HEAD").strip()
    assert out.endswith(f"; committed {sha}"), out
    assert sorted(git(chain, "show", "--name-only", "--format=", "HEAD").split()) == ["docs/stories/US-3-words.md", "ops.jsonl"]
    assert doc(chain, "US-3").endswith("**2026-10-13a (claude-code/test):** confirmed (by owner): the owner's words\n  over two lines\n")
    assert git(chain, "log", "-1", "--format=%s").strip() == "engine: confirm US-3"
    state = ops.Caller("2026-10-13a", "claude-code/test")
    line = mcp.make_tool(ops.OPS["record_confirm"], chain, state)(id="US-4", words="yes", by="human:avery")
    sha = git(chain, "rev-parse", "--short", "HEAD").strip()
    assert line.endswith(f"; committed {sha}") and "\n" not in line, line
    assert sorted(git(chain, "show", "--name-only", "--format=", "HEAD").split()) == ["docs/stories/US-4-words.md", "ops.jsonl"]
    assert "?? wip.md" in git(chain, "status", "--porcelain")
    assert main([*argv, "record", "confirm", "US-3", "again"]) == 2
    assert "is already confirmed" in capsys.readouterr().err
