"""A subagent's lane under the coordinator's session key (CE-126, DEC-84 option B): a subagent
working one task writes its op lines with ``lane`` (its task id, from CE_AGENT, the CLI's
``--agent`` or the MCP ``agent``), so its commits take only its own lines and the coordinator's
take only the lines with no lane; the session's close, pause and pause record take every lane.

The 8291569 case (ASK-21): a subagent's commit carried the coordinator's uncommitted
`baton.done BTN-5` line, because both ran under one key and a commit split lines by session
only (CE-125)."""

import asyncio
import json
from pathlib import Path

import pytest
from mcp import Client

from context_engine import cli, ops
from context_engine import commit as C
from context_engine.errors import Refusal
from context_engine.mcp import server
from context_engine.working import Engine

from conftest import _toml
from test_commit import _template, files_at, git, head, mrepo, repo, run, start  # noqa: F401 (fixtures)
from test_working import ACTOR, CONFIG, LEDGER, NOTE, TODAY

S = "2026-11-07e"
OTHER = "2026-11-07d"
SUB = "claude-code/sub"


def line(**o) -> str:
    return json.dumps(o)


def oplog(root: Path) -> list[dict]:
    return [json.loads(ln) for ln in (root / "ops.jsonl").read_text(encoding="utf-8").splitlines() if ln.strip()]


def sub(c: ops.Caller, lane: str = "CE-2") -> ops.Caller:
    """A subagent under the coordinator's key, working the task ``lane``."""
    return ops.Caller(c.session, SUB, lane)


def task_file(root: Path, rid: str) -> str:
    return next(p for p in (root / "tasks").iterdir() if p.name.startswith(f"{rid}-")).relative_to(root).as_posix()


def _setup(root: Path) -> ops.Caller:
    """The coordinator's session, with CE-1 (its own) and CE-2 (the subagent's), all committed."""
    c = start(root)
    run(root, "task_new", c, title="Mine")
    run(root, "task_new", c, title="Sub's")
    run(root, "commit", c, message="setup")
    assert git(root, "status", "--porcelain").strip() == ""
    return c


# -- select: by session and lane -------------------------------------------------------------


@pytest.mark.criterion("AC-197")
def test_select_takes_by_session_and_lane():
    coord = line(session=S, op="comment", id="CE-79", path="tasks/CE-79.md")
    sub9 = line(session=S, lane="CE-9", op="set", id="CE-9", path="tasks/CE-9.md")
    sub7 = line(session=S, lane="CE-7", op="set", id="CE-7", path="tasks/CE-7.md")
    other9 = line(session=OTHER, lane="CE-9", op="set", id="CE-3", path="tasks/CE-3.md")
    lines = [coord, sub9, sub7, other9]
    assert C.select(lines, S) == ([coord], [sub9, sub7, other9])  # the coordinator: the lines with no lane
    assert C.select(lines, S, lane="CE-9") == ([sub9], [coord, sub7, other9])  # the 8291569 case; never another session's lane CE-9
    assert C.select(lines, S, lane=C.EVERY_LANE) == ([coord, sub9, sub7], [other9])  # a close: every lane, never another session
    assert C.select(lines, S, lane="CE-9", sweep=True) == (lines, [])
    shared = line(session=S, op="comment", id="CE-9", path="tasks/CE-9.md")  # the coordinator's line on the lane's file
    assert C.select([sub9, shared], S, lane="CE-9") == ([sub9, shared], [])
    assert C.select([sub9, shared], S) == ([sub9, shared], [])
    for blank in ("", None, "  "):  # an empty, null or blank lane is the coordinator's
        mine = line(session=S, lane=blank, op="comment", id="CE-79", path="tasks/CE-79.md")
        assert C.select([mine], S) == ([mine], []) and C.select([mine], S, lane="CE-9") == ([], [mine])
    odd = line(session=S, lane=5, op="comment", id="CE-79", path="tasks/CE-79.md")  # not a str: the coordinator's (G-W7 reds it)
    assert C.select([odd], S) == ([odd], [])


def test_an_unparseable_line_stays_with_its_lane():
    """CE-128 extended: a line cut short names its session and lane in its text (the engine writes
    `lane` right after `session`), so it stays with that lane's lines."""
    trunc9 = '{"at": "2026-11-07T10:00:00+08:00", "session": "2026-11-07e", "lane": "CE-9", "actor": "claude-code/sub", "op": "new", "id": "CE-4", "pa'
    truncS = '{"at": "2026-11-07T10:00:01+08:00", "session": "2026-11-07e", "actor": "claude-code/x", "op": "set", "id": "CE-5"'
    lines = [trunc9, truncS, "not json"]
    assert C.select(lines, S) == ([truncS, "not json"], [trunc9])
    assert C.select(lines, S, lane="CE-9") == ([trunc9, "not json"], [truncS])
    assert C.select(lines, S, lane=C.EVERY_LANE) == (lines, [])
    assert C.lane_of(trunc9) == "CE-9" and C.lane_of(truncS) is None and C.lane_of("not json") is None
    assert C._whose([trunc9]) == (("2026-11-07e lane CE-9", 1),)


# -- the op line -----------------------------------------------------------------------------


@pytest.mark.criterion("AC-197")
def test_a_lanes_op_line_names_it_right_after_session(repo):
    c = start(repo)
    run(repo, "task_new", c, title="Mine")
    run(repo, "task_new", sub(c), title="Sub's")
    mine, theirs = oplog(repo)[-2:]
    assert "lane" not in mine and list(mine)[:3] == ["at", "session", "actor"]  # no lane: the line as before CE-126
    assert list(theirs)[:3] == ["at", "session", "lane"] and theirs["lane"] == "CE-2" and theirs["actor"] == SUB


# -- commits ---------------------------------------------------------------------------------


@pytest.mark.criterion("AC-197")
def test_a_lanes_commit_leaves_the_coordinators_lines_out(mrepo):
    """The 8291569 case: the coordinator's uncommitted line stays out of the subagent's commit,
    and the coordinator's own commit later takes it, so the op log converges."""
    c = _setup(mrepo)
    run(mrepo, "task_comment", c, id="CE-1", text="the coordinator's note")  # not a milestone: uncommitted
    run(mrepo, "task_comment", sub(c), id="CE-2", text="the sub's note")
    (mrepo / "a.py").write_text("a = 1\n", encoding="utf-8")
    _, reply = run(mrepo, "commit", sub(c), paths=["a.py"], message="CE-2: a")
    assert reply.startswith(f"committed {head(mrepo)}") and f"left uncommitted: 1 op line of {c.session}, with" in reply, reply
    one, two = task_file(mrepo, "CE-1"), task_file(mrepo, "CE-2")
    assert "a.py" in files_at(mrepo) and two in files_at(mrepo) and one not in files_at(mrepo)
    at_head = [json.loads(ln) for ln in git(mrepo, "show", "HEAD:ops.jsonl").splitlines() if ln.strip()]
    assert any(o.get("lane") == "CE-2" and o["op"] == "comment" for o in at_head)
    assert not any(o["op"] == "comment" and o["id"] == "CE-1" for o in at_head)
    _, reply = run(mrepo, "commit", c, message="CE-1: note")
    assert "left uncommitted" not in reply and one in files_at(mrepo), reply
    assert git(mrepo, "show", "HEAD:ops.jsonl").encode() == (mrepo / "ops.jsonl").read_bytes()
    assert git(mrepo, "status", "--porcelain").strip() == ""


@pytest.mark.criterion("AC-197")
def test_a_coordinators_milestone_leaves_a_lanes_lines_out(mrepo):
    c = _setup(mrepo)
    run(mrepo, "task_comment", sub(c), id="CE-2", text="the sub's half-done note")
    _, reply = run(mrepo, "task_close", c, id="CE-1", msg="done")  # a milestone: it commits
    assert f"; committed {head(mrepo)}" in reply, reply
    assert f"left uncommitted: 1 op line of {c.session} lane CE-2" in reply and "its session's close takes every lane" in reply, reply
    assert task_file(mrepo, "CE-2") not in files_at(mrepo)


@pytest.mark.criterion("AC-197")
@pytest.mark.parametrize("end", ["close", "pause"])
def test_the_session_close_and_pause_take_every_lane(mrepo, end):
    """A dead subagent's lines, never committed, go in with the session's close or pause."""
    c = _setup(mrepo)
    run(mrepo, "task_comment", sub(c), id="CE-2", text="the sub's note; then it died")
    if end == "close":
        _, reply = run(mrepo, "session_close", c, rows="CE-1, CE-2", summary=["built it"], guards="gate 3 passed", read="board")
    else:
        _, reply = run(mrepo, "session_pause", c, rows="CE-1, CE-2", deferred="everything")
    assert f"; committed {head(mrepo)}" in reply and "left uncommitted" not in reply, reply
    assert task_file(mrepo, "CE-2") in files_at(mrepo)
    assert git(mrepo, "show", "HEAD:ops.jsonl").encode() == (mrepo / "ops.jsonl").read_bytes()
    assert git(mrepo, "status", "--porcelain").strip() == ""


@pytest.mark.criterion("AC-197")
def test_a_pause_record_takes_every_lane(mrepo):
    c = _setup(mrepo)
    run(mrepo, "task_comment", sub(c), id="CE-2", text="the sub's note; then it died")
    two = task_file(mrepo, "CE-2")
    run(mrepo, "pause_open", c, in_flight="half done", resume="finish it")
    rec = next(Engine(mrepo, today=lambda: TODAY).store.records("pause"))
    assert two not in (rec.doc.get("uncommitted") or []), rec.doc.get("uncommitted")
    assert two in files_at(mrepo)
    assert git(mrepo, "status", "--porcelain").strip() == ""


# -- refusals before any write ----------------------------------------------------------------


@pytest.mark.criterion("AC-197")
def test_the_coordinators_own_ops_refuse_a_lane(mrepo):
    c = _setup(mrepo)
    before = (mrepo / "ops.jsonl").read_bytes()
    calls = {
        "session_start": (ops.Caller(actor=ACTOR, lane="CE-2"), {}),
        "session_close": (sub(c), dict(rows="CE-1", summary=["s"], guards="gate 3 passed", read="board")),
        "session_pause": (sub(c), dict(rows="CE-1", deferred="d")),
        "pause_open": (sub(c), dict(in_flight="half done", resume="finish it")),
    }
    assert set(calls) == set(ops.COORDINATOR_ONLY)
    for name, (caller, kw) in calls.items():
        with pytest.raises(Refusal, match="coordinator's") as r:
            run(mrepo, name, caller, **kw)
        assert "CE_AGENT" in r.value.remedy, name
        assert (mrepo / "ops.jsonl").read_bytes() == before, name
    assert git(mrepo, "status", "--porcelain").strip() == ""


@pytest.mark.criterion("AC-197")
def test_a_lane_is_checked_before_anything_is_written(mrepo):
    c = _setup(mrepo)
    for blank in ("", "  "):  # no lane: the coordinator
        run(mrepo, "task_comment", ops.Caller(c.session, ACTOR, blank), id="CE-1", text="no lane")
        assert "lane" not in oplog(mrepo)[-1]
    before = (mrepo / "ops.jsonl").read_bytes()
    for bad in ("CE 9", "*", "a/b", "x" * 65, "-x", "CE-9\nx"):
        with pytest.raises(Refusal, match="not a lane id"):
            run(mrepo, "task_comment", ops.Caller(c.session, ACTOR, bad), id="CE-1", text="refused")
        assert (mrepo / "ops.jsonl").read_bytes() == before, bad
    run(mrepo, "task_comment", ops.Caller(c.session, ACTOR, " CE-9 "), id="CE-1", text="trimmed")
    assert oplog(mrepo)[-1]["lane"] == "CE-9"
    run(mrepo, "task_comment", ops.Caller(c.session, ACTOR, "x" * 64), id="CE-1", text="the longest lane")
    assert oplog(mrepo)[-1]["lane"] == "x" * 64


# -- the CLI and the MCP tools ----------------------------------------------------------------


@pytest.fixture
def plain(tmp_path, monkeypatch):
    """A target with no git (commits say nothing) and no caller in the environment."""
    for v in ("CE_SESSION", "CE_ACTOR", "CE_AGENT"):
        monkeypatch.delenv(v, raising=False)
    (tmp_path / "context.toml").write_text(_toml(CONFIG), encoding="utf-8")
    (tmp_path / "ledger.md").write_text(LEDGER, encoding="utf-8")
    (tmp_path / "HANDOFF.md").write_text(NOTE.format(key="2026-10-07b"), encoding="utf-8")
    return tmp_path


def _call(srv, name, args):
    async def go():
        async with Client(srv) as c:
            return await c.call_tool(name, args)

    return asyncio.run(go())


def _schemas(srv) -> dict[str, dict]:
    async def go():
        async with Client(srv) as c:
            return {t.name: t.input_schema for t in (await c.list_tools()).tools}

    return asyncio.run(go())


def test_the_cli_carries_the_lane_from_ce_agent_or_agent(plain, monkeypatch, capsys):
    base = ["--root", str(plain), "--actor", ACTOR]
    assert cli.main([*base, "session", "start"]) == 0
    key = capsys.readouterr().out.split()[1]
    assert cli.main([*base, "--session", key, "task", "new", "One"]) == 0
    assert "lane" not in oplog(plain)[-1]  # unset: the coordinator
    monkeypatch.setenv("CE_AGENT", "CE-1")
    assert cli.main([*base, "--session", key, "task", "comment", "CE-1", "x"]) == 0
    assert oplog(plain)[-1]["lane"] == "CE-1"
    assert cli.main([*base, "--session", key, "--agent", "CE-7", "task", "comment", "CE-1", "y"]) == 0
    assert oplog(plain)[-1]["lane"] == "CE-7"  # --agent beats CE_AGENT
    assert cli.main([*base, "session", "start"]) == 2  # a lane on the coordinator's own op: refused
    assert "coordinator's" in capsys.readouterr().err


def test_the_mcp_tools_take_agent_per_call_and_never_remember_it(plain, monkeypatch):
    monkeypatch.setenv("CE_AGENT", "CE-9")  # the server never reads it: one process serves every agent
    srv = server(plain)
    assert not _call(srv, "session_start", {"actor": ACTOR}).is_error
    assert not _call(srv, "task_new", {"title": "Sub's", "agent": "CE-1", "actor": SUB}).is_error
    assert oplog(plain)[-1]["lane"] == "CE-1" and oplog(plain)[-1]["actor"] == SUB
    assert not _call(srv, "task_new", {"title": "Parent's"}).is_error
    assert "lane" not in oplog(plain)[-1]  # not remembered, and CE_AGENT ignored
    r = _call(srv, "task_new", {"title": "Bad", "agent": "a b"})
    assert r.is_error and "not a lane id" in r.content[0].text
    schemas = _schemas(srv)
    assert "agent" in schemas["task_new"]["properties"] and "agent" in schemas["commit"]["properties"]
    for name in (*ops.COORDINATOR_ONLY, "task_list", "orient"):  # the coordinator's own ops, and reads
        assert "agent" not in schemas[name].get("properties", {}), name


# -- lint ------------------------------------------------------------------------------------


def test_g_w7_reds_a_malformed_lane(mrepo):
    c = _setup(mrepo)
    run(mrepo, "task_comment", sub(c), id="CE-2", text="a lane's line")
    log = mrepo / "ops.jsonl"
    good = log.read_text(encoding="utf-8")
    lw7 = lambda: [f.message for f in Engine(mrepo, today=lambda: TODAY).lint() if f.guard == "G-W7"]
    assert lw7() == []
    last = json.loads(good.splitlines()[-1])
    n = len(good.splitlines())
    for bad in (5, "a b", "", None, "*"):
        log.write_text(good + json.dumps({**last, "lane": bad}) + "\n", encoding="utf-8")
        assert lw7() == [f"1 op line carries a `lane` that is not a lane id like CE-126 (the first: line {n + 1})"], bad
    log.write_text(good + json.dumps({**last, "lane": "CE-2"}) + "\n", encoding="utf-8")
    assert lw7() == []


# -- what the replies and messages say --------------------------------------------------------


def test_left_behind_names_a_lane_and_keeps_its_old_words():
    assert C.left_behind((("2026-11-07d", 2),)) == (
        "left uncommitted: 2 op lines of 2026-11-07d, with the files they name; that session commits them, "
        "or once it is known dead, `context-engine commit --sweep` takes them")
    lane = C.left_behind((("2026-11-07e lane CE-2", 1),))
    assert lane.startswith("left uncommitted: 1 op line of 2026-11-07e lane CE-2, with the files they name;"), lane
    assert "its session's close takes every lane" in lane and "--sweep" in lane, lane
    coord = {"session": S, "op": "comment", "id": "CE-79", "path": "tasks/CE-79.md"}
    theirs = {"session": S, "lane": "CE-2", "op": "set", "id": "CE-2", "path": "tasks/CE-79.md"}
    msg = C.message([theirs, coord], S, None)
    assert msg.splitlines()[0] == "engine: comment CE-79", msg
    assert "Also carries 1 op log line left uncommitted by session 2026-11-07e lane CE-2, with the files they name." in msg, msg
    assert C._others([theirs, coord], S) == ("2026-11-07e lane CE-2",) and C._others([theirs, coord], S, "CE-2") == ("2026-11-07e",)
    assert C._others([theirs, coord], S, C.EVERY_LANE) == ()
