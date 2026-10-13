"""Retiring a story (CE-49, FRAMEWORK §3.2, §8.1): `record retire` writes the retire, its link
both ways and its reason in one write, refuses what it must, and G-I2 reds a retire made or
undone by hand, so the remedies of G-I1 and G-I2 can name it."""

import json
import subprocess

import pytest

from context_engine import mcp, ops
from context_engine.cli import main
from context_engine.errors import Refusal
from context_engine.store import Store

from test_intent import W, chain, edit, make, reds, story, write  # noqa: F401 (chain is a fixture)

OK = {"actor": "owner", "date": "2026-10-13", "story_status": "live", "goals": "[G-1]"}
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


@pytest.mark.criterion("AC-72")
def test_record_retire_writes_the_status_the_links_and_the_reason_in_one_write(chain):
    e = make(chain)
    again = e.record_new("story", "Again", "words", OK, **W)
    assert again.id == "US-3"
    line = e.retire("US-1", "it named the wrong goal", by="agent", superseded_by="US-3", **W)
    assert line.startswith("US-1: retired by agent (status: deprecated); superseded by US-3, which now supersedes US-1; the reason is under ## Amendments"), line
    old, new = doc(chain, "US-1"), doc(chain, "US-3")
    head = old.split("\n---\n", 1)[0]
    assert head.endswith("story_status: retired\ngoals: [G-1]\nstatus: deprecated\nsuperseded_by: [US-3]"), head  # new keys last, in the runbook's order
    assert old.endswith("\n## Amendments\n\n- **2026-10-13a (claude-code/test):** retired (by agent; superseded by US-3): it named the wrong goal\n")
    assert "supersedes: [US-1]\n" in new and "story_status: live\n" in new and "## Amendments" not in new
    log = [(o["op"], o["id"], o["fields"]) for o in oplog(chain)][-2:]
    assert log == [("retire", "US-3", ["supersedes"]), ("retire", "US-1", ["story_status", "status", "superseded_by", "body"])]  # the successor first
    assert reds(e, "G-I1") == [] and reds(e, "G-I2") == [] and not [f for f in e.lint() if f.guard == "G-D10" and "US-3" in f.path]
    # the owner withdraws a story: their words, no successor; the goal it served is now served by none
    words = "we don't need this one\nafter all"
    assert e.retire("US-2", words, by="owner", **W).startswith("US-2: retired by owner (status: deprecated); the reason")
    assert doc(chain, "US-2").endswith("- **2026-10-13a (claude-code/test):** retired (by owner): we don't need this one\n  after all\n")
    assert "superseded_by" not in doc(chain, "US-2")
    assert reds(e, "G-I1") == ["docs/charter.md: goal G-2 is served by no story"]
    assert reds(e, "G-I2") == []
    assert e.retire("US-3", "a person's call", by="human:avery", **W).startswith("US-3: retired by human:avery")


@pytest.fixture
def refusing(chain):
    """US-1 and US-2 live; US-3 recorded again with US-1's words; US-4 other words; US-5
    retired by the op; US-6 retired by the op and then made live again by hand; DEC-1."""
    e = make(chain)
    e.record_new("story", "Again", "words", OK, **W)  # US-3, stamped
    e.record_new("story", "Other", "other words", OK, **W)  # US-4
    e.record_new("story", "Gone", "words", OK, **W)  # US-5
    e.record_new("story", "Undone", "words", OK, **W)  # US-6
    e.retire("US-5", "drop it", by="owner", **W)
    e.retire("US-6", "drop it", by="owner", **W)
    edit(chain, rel(chain, "US-6"), "story_status: retired", "story_status: live")
    return e


REFUSALS = {
    "by-vocabulary": ({"by": "claude"}, r"`by: claude` is none of `owner`, `human:<id>` or `agent`"),
    "by-agent-with-a-model": ({"by": "agent (claude-x)", "superseded_by": "US-3"}, r"`by: agent \(claude-x\)` is none of"),
    "no-reason": ({"why": " \n"}, r"no reason"),
    "agent-without-successor": ({"by": "agent"}, r"an agent retires a story only when it was recorded again.*Remedy: record it again with `record new story`"),
    "agent-other-words": ({"by": "agent", "superseded_by": "US-4"}, r"US-4 does not carry US-1's words as typed.*Remedy: record US-1 again with its body as it is"),
    "self": ({"superseded_by": "US-1"}, r"US-1 cannot supersede itself"),
    "successor-not-a-story": ({"superseded_by": "DEC-1"}, r"DEC-1 is not a story, so it cannot replace US-1"),
    "successor-missing": ({"superseded_by": "US-9"}, r"no record US-9"),
    "successor-retired": ({"superseded_by": "US-5"}, r"US-5 is retired, so it cannot replace US-1"),
    "not-a-story": ({"id": "DEC-1"}, r"DEC-1 is not a story.*decision supersede"),
    "already-retired": ({"id": "US-5"}, r"US-5 is already retired \(`record retire` in session 2026-10-13a\).*a retire is final"),
    "undone-by-hand": ({"id": "US-6"}, r"US-6 was retired by `record retire` in session 2026-10-13a, and a hand edit has since made it `live`.*restore `story_status: retired`"),
}


@pytest.mark.criterion("AC-72")
@pytest.mark.parametrize("case", sorted(REFUSALS))
def test_record_retire_refuses_before_writing_anything(refusing, chain, case):
    write(chain, "docs/decisions/DEC-1-x.md", "---\ntype: Decision\nid: DEC-1\ntitle: t\n---\n\nwhy\n")
    kw, match = REFUSALS[case]
    args = {"id": "US-1", "why": "a reason", "by": "owner", **kw}
    before = snapshot(chain)
    with pytest.raises(Refusal, match=match):
        refusing.retire(args.pop("id"), args.pop("why"), **args, **W)
    assert snapshot(chain) == before


@pytest.mark.criterion("AC-72")
def test_record_retire_refuses_a_hash_mismatch_a_record_that_fails_its_schema_and_a_repo_with_no_stories(chain):
    e = make(chain)
    e.record_new("story", "Again", "words", OK, **W)  # US-3, stamped
    edit(chain, rel(chain, "US-3"), "words", "other words")
    before = snapshot(chain)
    with pytest.raises(Refusal, match=r"US-3 body above `## Amendments` changed since it was stamped"):
        e.retire("US-3", "a reason", by="owner", **W)
    assert snapshot(chain) == before
    # the story fails its schema once changed, so neither record is written, not even the successor
    write(chain, "docs/stories/US-4-x.md", "---\ntype: Story\nid: US-4\nactor: owner\ndate: 2026-10-13\nstory_status: live\ngoals: [G-1]\n---\n\nwords\n")
    write(chain, "docs/stories/US-5-x.md", "---\ntype: Story\nid: US-5\ntitle: t\nactor: owner\ndate: 2026-10-13\nstory_status: live\ngoals: [G-1]\n---\n\nwords\n")
    before = snapshot(chain)
    with pytest.raises(Refusal, match=r"US-4-x\.md has no `title`"):
        e.retire("US-4", "a reason", by="agent", superseded_by="US-5", **W)
    assert snapshot(chain) == before
    with pytest.raises(Refusal, match=r"no kind holds the stories.*Remedy: set `stories` in \[guards\] of context\.toml to the kind holding the stories"):
        make(chain, stories="", charter="").retire("US-1", "a reason", by="owner", **W)


@pytest.mark.criterion("AC-72")
def test_a_retire_whose_second_write_fails_is_completed_by_a_retry(chain, monkeypatch):
    e = make(chain)
    e.record_new("story", "Again", "words", OK, **W)  # US-3
    real = Store._write

    def fails_on_us1(self, path, d):
        if path.name.startswith("US-1-"):
            raise Refusal("could not replace docs/stories/US-1-words.md", "close whatever has the file open, then retry")
        return real(self, path, d)

    monkeypatch.setattr(Store, "_write", fails_on_us1)
    with pytest.raises(Refusal, match="could not replace"):
        e.retire("US-1", "recorded again", by="agent", superseded_by="US-3", **W)
    assert "supersedes: [US-1]" in doc(chain, "US-3") and "story_status: live" in doc(chain, "US-1")  # half done: the successor only
    monkeypatch.setattr(Store, "_write", real)
    e.retire("US-1", "recorded again", by="agent", superseded_by="US-3", **W)  # the retry the remedy asks for
    assert "supersedes: [US-1]\n" in doc(chain, "US-3") and "superseded_by: [US-3]" in doc(chain, "US-1")
    assert reds(e, "G-I2") == []


@pytest.mark.criterion("AC-72")
def test_the_store_amends_only_append_only_records_and_never_with_nothing(chain):
    e = make(chain)
    write(chain, "tasks/CE-1-x.md", "---\ntype: Task\nid: CE-1\ntitle: t\npri: LATER\nstate: open\n---\n\nbody\n")
    with pytest.raises(Refusal, match=r"CE-1 is a replaced record.*only append-only records take amendments"):
        e.store.update(["CE-1"], lambda recs: {}, op="x", amend={"CE-1": "why"}, **W)
    with pytest.raises(Refusal, match=r"empty amendment"):
        e.store.update(["US-1"], lambda recs: {}, op="x", amend={"US-1": " \n"}, **W)
    assert oplog(chain) == []


@pytest.mark.criterion("AC-72")
@pytest.mark.parametrize("field, value, match", [
    ("story_status", "retired", r"would be born `retired`, which only `record retire` sets"),
    ("status", "deprecated", r"would be born with `status: deprecated`, which only `record retire` writes"),
    ("superseded_by", "[US-1]", r"would be born with `superseded_by`, which only `record retire` writes"),
    ("supersedes", "[US-1]", r"would be born with `supersedes`, which only `record retire` writes"),
], ids=["retired", "deprecated", "superseded_by", "supersedes"])
def test_a_story_is_never_born_retired_deprecated_or_linked(chain, field, value, match):
    with pytest.raises(Refusal, match=match):
        make(chain).record_new("story", "Born", "words", {**OK, field: value}, **W)
    assert sorted(p.name for p in (chain / STORIES).iterdir()) == ["US-1-words.md", "US-2-words.md"]
    assert make(chain, off=["G-I2"]).record_new("story", "Off", "words", {**OK, field: value}, **W).id == "US-3"


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
    got = "\n".join(reds(e, "G-I2"))
    assert "US-3 `superseded_by` names US-9, which is no story" in got and "US-2 `supersedes` names DEC-1, which is no story" in got
    assert "US-2 has `superseded_by` but is `live`, not retired" in got
    assert reds(e, "G-I2") == [
        "docs/stories/US-2-words.md: US-2 `supersedes` names DEC-1, which is no story",
        "docs/stories/US-2-words.md: US-2 has `superseded_by` but is `live`, not retired",
        "docs/stories/US-3-words.md: US-3 `superseded_by` names US-9, which is no story",
    ]
    edit(chain, "docs/stories/US-2-words.md", "superseded_by: [US-1]\nsupersedes: [DEC-1]", "status: deprecated")  # deprecated, not retired
    edit(chain, "docs/stories/US-3-words.md", "superseded_by: [US-9]\n", "")
    assert reds(e, "G-I2") == ["docs/stories/US-2-words.md: US-2 is `status: deprecated` but `live`: only a retired story is deprecated, so readers would skip it as history"]


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


@pytest.mark.criterion("AC-73")
def test_g_t1_tells_a_successor_to_take_over_the_criteria_of_the_story_it_replaced(chain):
    e = make(chain)
    e.record_new("story", "Again", "words", OK, **W)  # US-3
    e.retire("US-1", "recorded again", by="agent", superseded_by="US-3", **W)
    t1 = [f for f in e.lint() if f.guard == "G-T1"]
    assert [f.message for f in t1] == ["US-3 is live but no criterion comes from it"]
    assert t1[0].remedy.startswith("it replaced US-1: add US-3 to the `from` cell of the criteria that come from US-1 in docs/criteria.md"), t1[0].remedy
    edit(chain, "docs/criteria.md", "| AC-1 | a | US-1 | tested |", "| AC-1 | a | US-1, US-3 | tested |")
    assert reds(e, "G-T1") == []


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
    (chain / "words.md").write_bytes("﻿the owner's words\r\nover two lines\r\n".encode())  # as PowerShell 5.1 saves it: a BOM, CRLF
    argv = ["--root", str(chain), "--session", "2026-10-13a", "--actor", "claude-code/test"]
    assert main([*argv, "record", "retire", "US-2", "--by", "owner", "--file", str(chain / "words.md")]) == 0
    out = capsys.readouterr().out.strip()
    sha = git(chain, "rev-parse", "--short", "HEAD").strip()
    assert out.endswith(f"; committed {sha}"), out
    assert sorted(git(chain, "show", "--name-only", "--format=", "HEAD").split()) == ["docs/stories/US-2-words.md", "ops.jsonl"]
    assert doc(chain, "US-2").endswith("**2026-10-13a (claude-code/test):** retired (by owner): the owner's words\n  over two lines\n")
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
