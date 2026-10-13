"""Retiring a story (CE-49, FRAMEWORK §3.2, §8.1): `record retire` writes the retire, its link
both ways and its reason in one write, refuses what it must, and G-I2 reds a retire made or
undone by hand, so the remedies of G-I1 and G-I2 can name it."""

import json
import subprocess

import pytest

from context_engine import mcp, ops
from context_engine.cli import main
from context_engine.errors import Refusal

from test_intent import W, all_reds, chain, edit, make, reds, story, write  # noqa: F401 (chain is a fixture)

OK = {"actor": "owner", "date": "2026-10-13", "story_status": "live", "goals": "[G-1]"}
STORIES = "docs/stories"


def doc(root, sid: str) -> str:
    return next((root / STORIES).glob(f"{sid}-*.md")).read_text(encoding="utf-8")


def oplog(root) -> list[dict]:
    p = root / "ops.jsonl"
    return [json.loads(ln) for ln in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []


def snapshot(root) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file() and ".context" not in p.parts}


# -- the operation -------------------------------------------------------------------------


@pytest.mark.criterion("AC-72")
def test_record_retire_writes_the_status_the_links_and_the_reason_in_one_write(chain):
    e = make(chain)
    again = e.record_new("story", "Again", "words", OK, **W)
    assert again.id == "US-3"
    line = e.retire("US-1", "it named the wrong goal", by="agent", superseded_by="US-3", **W)
    assert line.startswith("US-1: retired by agent (status: deprecated); superseded by US-3, which now supersedes US-1; the reason is under ## Amendments"), line
    old, new = doc(chain, "US-1"), doc(chain, "US-3")
    assert "story_status: retired\n" in old and "status: deprecated\n" in old and "superseded_by: [US-3]\n" in old
    assert old.endswith("\n## Amendments\n\n- **2026-10-13a (claude-code/test):** retired (by agent; superseded by US-3): it named the wrong goal\n")
    assert "supersedes: [US-1]\n" in new and "story_status: live\n" in new and "## Amendments" not in new
    log = [(o["op"], o["id"], o["fields"]) for o in oplog(chain)][-2:]
    assert log == [("retire", "US-1", ["story_status", "status", "superseded_by", "body"]), ("retire", "US-3", ["supersedes"])]
    assert reds(e, "G-I1") == [] and reds(e, "G-I2") == [] and not [f for f in e.lint() if f.guard == "G-D10" and "US-3" in f.path]
    # the owner withdraws a story: their words, no successor; the goal it served is now served by none
    words = "we don't need this one\nafter all"
    assert e.retire("US-2", words, by="owner", **W).startswith("US-2: retired by owner (status: deprecated); the reason")
    assert doc(chain, "US-2").endswith("- **2026-10-13a (claude-code/test):** retired (by owner): we don't need this one\n  after all\n")
    assert "superseded_by" not in doc(chain, "US-2")
    assert reds(e, "G-I1") == ["docs/charter.md: goal G-2 is served by no story"]
    assert reds(e, "G-I2") == []
    assert e.retire("US-3", "a person's call", by="human:avery", **W).startswith("US-3: retired by human:avery")


@pytest.mark.criterion("AC-72")
def test_record_retire_refuses_before_writing_anything(chain):
    e = make(chain)
    e.record_new("story", "Again", "words", OK, **W)  # US-3, stamped
    e.retire("US-2", "drop it", by="owner", **W)
    write(chain, "docs/decisions/DEC-1-x.md", "---\ntype: Decision\nid: DEC-1\ntitle: t\n---\n\nwhy\n")
    before = snapshot(chain)
    for kw, match in [
        ({"by": "claude"}, r"`by: claude` is none of `owner`, `human:<id>` or `agent`"),
        ({"by": "agent (claude-x)", "superseded_by": "US-3"}, r"is none of"),
        ({"why": " \n"}, r"no reason"),
        ({"by": "agent"}, r"an agent retires a story only when it was recorded again.*Remedy: record it again with `record new story`"),
        ({"superseded_by": "US-1"}, r"US-1 cannot supersede itself"),
        ({"superseded_by": "DEC-1"}, r"DEC-1 is not a story, so it cannot replace US-1"),
        ({"superseded_by": "US-9"}, r"no record US-9"),
        ({"superseded_by": "US-2"}, r"US-2 is retired, so it cannot replace US-1"),
        ({"id": "DEC-1"}, r"DEC-1 is not a story.*decision supersede"),
        ({"id": "US-2"}, r"US-2 is already retired \(`record retire` in session 2026-10-13a\).*a retire is final"),
    ]:
        args = {"id": "US-1", "why": "a reason", "by": "owner", **kw}
        with pytest.raises(Refusal, match=match):
            e.retire(args.pop("id"), args.pop("why"), **args, **W)
        assert snapshot(chain) == before, kw
    edit(chain, next((chain / STORIES).glob("US-3-*.md")).relative_to(chain).as_posix(), "words", "other words")
    before = snapshot(chain)
    with pytest.raises(Refusal, match=r"US-3 body above `## Amendments` changed since it was stamped"):
        e.retire("US-3", "a reason", by="owner", **W)
    assert snapshot(chain) == before
    with pytest.raises(Refusal, match=r"no kind holds the stories.*Remedy: set `stories = \"story\"`"):
        make(chain, stories="", charter="").retire("US-1", "a reason", by="owner", **W)


@pytest.mark.criterion("AC-72")
def test_a_story_is_never_born_retired(chain):
    with pytest.raises(Refusal, match=r"the story would be born `retired`, which only `record retire` sets"):
        make(chain).record_new("story", "Born retired", "words", {**OK, "story_status": "retired"}, **W)
    assert sorted(p.name for p in (chain / STORIES).iterdir()) == ["US-1-words.md", "US-2-words.md"]
    assert make(chain, off=["G-I2"]).record_new("story", "Off", "words", {**OK, "story_status": "retired"}, **W).id == "US-3"


# -- G-I2 on retires -----------------------------------------------------------------------


@pytest.mark.criterion("AC-73")
def test_g_i2_reds_a_retire_made_or_undone_by_hand_and_a_story_link_that_resolves_to_no_story(chain):
    story(chain, "US-3", status="retired")  # retired by hand: nobody recorded who or why
    e = make(chain)
    assert reds(e, "G-I2") == ["docs/stories/US-3-words.md: US-3 is `retired`, but no `record retire` of it is logged, so nothing records who retired it or why"]
    hand = next(f for f in e.lint() if f.guard == "G-I2")
    assert "`record retire US-3 --by owner --why" in hand.remedy
    e.retire("US-3", "the owner retired it in chat on 2026-10-12", by="owner", **W)  # the op takes a hand retire, recording who and why
    assert reds(e, "G-I2") == []
    edit(chain, "docs/stories/US-3-words.md", "story_status: retired", "story_status: live")  # undone by hand
    assert reds(e, "G-I2") == ["docs/stories/US-3-words.md: US-3 was retired by `record retire` in session 2026-10-13a, but its frontmatter now says `story_status: live`"]
    edit(chain, "docs/stories/US-3-words.md", "story_status: live", "story_status: retired")
    edit(chain, "docs/stories/US-3-words.md", "status: deprecated\n", "")
    assert reds(e, "G-I2") == ["docs/stories/US-3-words.md: US-3 was retired by `record retire` in session 2026-10-13a, but its frontmatter now says `status: `, not `deprecated`"]
    edit(chain, "docs/stories/US-3-words.md", "story_status: retired", "story_status: retired\nstatus: deprecated\nsuperseded_by: [US-9]")
    edit(chain, "docs/stories/US-2-words.md", "goals: [G2]", "goals: [G2]\nsuperseded_by: [US-1]\nsupersedes: [DEC-1]")
    assert reds(e, "G-I2") == [
        "docs/stories/US-2-words.md: US-2 `supersedes` names DEC-1, which is no story",
        "docs/stories/US-2-words.md: US-2 has `superseded_by` but is `live`, not retired",
        "docs/stories/US-3-words.md: US-3 `superseded_by` names US-9, which is no story",
    ]


@pytest.mark.criterion("AC-73")
def test_the_g_i1_and_g_i2_remedies_name_record_retire_and_following_them_clears_the_red(chain):
    story(chain, "US-3", actor="claude-code/x")  # wrong provenance at birth
    story(chain, "US-4", goals="[G-9]")  # a goal the charter lacks
    e = make(chain)
    reds_ = {f.guard: f for f in e.lint() if f.guard in ("G-I1", "G-I2")}
    assert "`record retire US-3 --by agent --superseded-by <new id> --why" in reds_["G-I2"].remedy
    assert "`record retire US-4 --by agent --superseded-by <new id> --why" in reds_["G-I1"].remedy
    assert "file a task" not in reds_["G-I2"].remedy + reds_["G-I1"].remedy
    e.record_new("story", "Again", "words", {**OK, "actor": "agent (claude-x, reconstructed from US-3)", "story_status": "unconfirmed"}, **W)  # US-5
    e.record_new("story", "Again", "words", OK, **W)  # US-6
    e.retire("US-3", "the actor was the agent's, not the owner's", by="agent", superseded_by="US-5", **W)
    e.retire("US-4", "G-9 is no goal; it serves G-1", by="agent", superseded_by="US-6", **W)
    assert reds(e, "G-I1") == [] and reds(e, "G-I2") == []


# -- the entry points and the commit -------------------------------------------------------


def git(root, *args) -> str:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8", check=True).stdout


@pytest.mark.criterion("AC-72")
def test_the_cli_and_the_mcp_tool_retire_and_commit_by_path(chain, capsys):
    for args in (["init", "-q", "-b", "main"], ["config", "user.email", "t@example.com"], ["config", "user.name", "t"], ["config", "core.autocrlf", "false"]):
        git(chain, *args)
    make(chain)  # writes context.toml
    git(chain, "add", "-A")
    git(chain, "commit", "-q", "-m", "base")
    (chain / "wip.md").write_text("untracked work\n", encoding="utf-8")
    (chain / "words.md").write_bytes(b"the owner's words\r\nover two lines\r\n")  # as an editor on Windows saves it
    argv = ["--root", str(chain), "--session", "2026-10-13a", "--actor", "claude-code/test"]
    assert main([*argv, "record", "retire", "US-2", "--by", "owner", "--file", str(chain / "words.md")]) == 0
    out = capsys.readouterr().out.strip()
    sha = git(chain, "rev-parse", "--short", "HEAD").strip()
    assert out.endswith(f"; committed {sha}"), out
    assert sorted(git(chain, "show", "--name-only", "--format=", "HEAD").split()) == ["docs/stories/US-2-words.md", "ops.jsonl"]
    assert doc(chain, "US-2").endswith("retired (by owner): the owner's words\n  over two lines\n")
    assert git(chain, "log", "-1", "--format=%s").strip() == "engine: retire US-2"
    state = ops.Caller("2026-10-13a", "claude-code/test")
    line = mcp.make_tool(ops.OPS["record_new"], chain, state)(kind="story", title="Again", body="words", fields=OK)
    assert line.startswith("US-3: created and stamped"), line
    line = mcp.make_tool(ops.OPS["record_retire"], chain, state)(id="US-1", by="agent", superseded_by="US-3", why="recorded again")
    sha = git(chain, "rev-parse", "--short", "HEAD").strip()
    assert line.endswith(f"; committed {sha}") and "\n" not in line, line
    assert sorted(git(chain, "show", "--name-only", "--format=", "HEAD").split()) == ["docs/stories/US-1-words.md", "docs/stories/US-3-again.md", "ops.jsonl"]
    assert "?? wip.md" in git(chain, "status", "--porcelain")
    assert main([*argv, "record", "retire", "US-1", "--by", "owner", "--why", "again"]) == 2
    assert "is already retired" in capsys.readouterr().err
