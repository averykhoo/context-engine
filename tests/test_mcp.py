"""The MCP server (CE-3): one implementation per operation (AC-18), one-line writes and capped
reads (AC-19), the remembered caller, refusals with their remedy, and the stdio entry point."""

import asyncio
import functools
import json
import sys

import pytest
from mcp import Client, StdioServerParameters

from context_engine import cli, ops
from context_engine.cli import main
from context_engine.mcp import cap, server
from context_engine.working import Engine

from conftest import ASK_BODY, _toml
from test_working import CONFIG, LEDGER, NOTE

ACTOR = "claude-code/test"

# One call per operation: (the CLI's argv after the global flags, the MCP tool's arguments).
# Both must reach the operation's function with the same parameters.
CALLS = {
    "init": (["--prefix", "task=PRJ", "--prefix", "decision=DEC", "--dry-run", "--merge-settings"], {"prefix": {"task": "PRJ", "decision": "DEC"}, "dry_run": True, "merge_settings": True}),
    "session_start": ([], {}),
    "session_close": (["--rows", "r", "--summary", "s1", "--summary", "s2", "--guards", "g", "--read", "x", "--asked", "ASK-1", "--owed", "o"], {"rows": "r", "summary": ["s1", "s2"], "guards": "g", "read": "x", "asked": "ASK-1", "owed": ["o"]}),
    "session_pause": (["--rows", "r", "--deferred", "d"], {"rows": "r", "deferred": "d"}),
    "session_abandon": (["2026-10-01a", "--force"], {"key": "2026-10-01a", "force": True}),
    "orient": ([], {}),
    "routes": ([], {}),
    "lint": (["--working"], {"working": True}),
    "task_new": (["T", "--kind", "question", "--pri", "NEXT", "--brief", "b", "--deps", "CE-1, CE-2", "--body", "x", "--id", "ASK-9"], {"title": "T", "kind": "question", "pri": "NEXT", "brief": "b", "deps": ["CE-1", "CE-2"], "body": "x", "id": "ASK-9"}),
    "task_set": (["CE-1", "--set", "brief=b", "--set", "labels=[x]", "--unset", "y", "--mechanical"], {"id": "CE-1", "fields": {"brief": "b", "labels": "[x]"}, "unset": ["y"], "mechanical": True}),
    "task_promote": (["CE-1", "NOW"], {"id": "CE-1", "pri": "NOW"}),
    "task_dep": (["CE-1", "--add", "CE-2 CE-3", "--remove", "CE-4"], {"id": "CE-1", "add": ["CE-2", "CE-3"], "remove": ["CE-4"]}),
    "task_comment": (["CE-1", "words", "--mechanical"], {"id": "CE-1", "text": "words", "mechanical": True}),
    "task_touch": (["CE-1"], {"id": "CE-1"}),
    "task_close": (["CE-1", "-m", "done", "--body", "Sabotage: x -> y red"], {"id": "CE-1", "msg": "done", "body": "Sabotage: x -> y red"}),
    "task_reopen": (["CE-1", "-m", "again"], {"id": "CE-1", "msg": "again"}),
    "task_section": (["CE-1", "Traps", "t"], {"id": "CE-1", "name": "Traps", "text": "t"}),
    "task_list": (["--state", "all", "--pri", "NOW", "--label", "l"], {"state": "all", "pri": "NOW", "label": "l"}),
    "task_show": (["CE-1", "--section", "Log", "--head", "0"], {"id": "CE-1", "section": "Log", "head": 0}),
    "ask_new": (["Q", "--pri", "LATER", "--brief", "b", "--blocks", "CE-1", "--body", "x", "--id", "ASK-8", "--answered", "w", "--decision-title", "D", "--ruling", "r", "--ruled-by", "claude-code/fable"], {"title": "Q", "pri": "LATER", "brief": "b", "blocks": ["CE-1"], "body": "x", "id": "ASK-8", "answered": "w", "decision_title": "D", "ruling": "r", "ruled_by": "claude-code/fable"}),
    "ask_raised": (["ASK-1", "ASK-2,ASK-3"], {"ids": ["ASK-1", "ASK-2", "ASK-3"]}),
    "ask_later": (["ASK-1"], {"id": "ASK-1"}),
    "ask_answer": (["ASK-1", "the words", "--title", "T", "--ruling", "r", "--ruled-by", "claude-code/fable"], {"id": "ASK-1", "words": "the words", "title": "T", "ruling": "r", "ruled_by": "claude-code/fable"}),
    "baton_list": ([], {}),
    "baton_add": (["step", "--why", "w"], {"step": "step", "why": "w"}),
    "baton_done": (["BTN-1", "e"], {"id": "BTN-1", "evidence": "e"}),
    "hk_expire_batons": ([], {}),
    "pause_open": (["--in-flight", "i", "--resume", "r", "--evidence", "e", "--deferred", "d"], {"in_flight": "i", "resume": "r", "evidence": "e", "deferred": ["d"]}),
    "pause_resume": (["PAU-1"], {"id": "PAU-1"}),
    "record_new": (["decision", "T", "--body", "words", "--set", "actor=owner", "--id", "DEC-7"], {"kind": "decision", "title": "T", "body": "words", "fields": {"actor": "owner"}, "id": "DEC-7"}),
    "id_reserve": (["decision", "--count", "3"], {"kind": "decision", "count": 3}),
    "record_stamp": (["DEC-1", "DEC-2"], {"ids": ["DEC-1", "DEC-2"]}),
    "record_amend": (["DEC-1", "more"], {"id": "DEC-1", "text": "more"}),
    "record_correct": (["DEC-1", "--after", "a", "--text", "b"], {"id": "DEC-1", "after": "a", "text": "b"}),
    "record_retire": (["US-1", "--by", "agent", "--superseded-by", "US-2", "--why", "w"], {"id": "US-1", "by": "agent", "superseded_by": "US-2", "why": "w"}),
    "record_confirm": (["US-1", "--by", "human:avery", "--status", "unspecified", "the words"], {"id": "US-1", "by": "human:avery", "status": "unspecified", "words": "the words"}),
    "decision_supersede": (["DEC-1", "DEC-2"], {"old": "DEC-1", "new": "DEC-2"}),
    "decision_set": (["DEC-1", "--set", "tags=a", "--unset", "reopen_if"], {"id": "DEC-1", "fields": {"tags": "a"}, "unset": ["reopen_if"]}),
    "decision_link": (["DEC-1", "CE-1", "--rel", "tasks"], {"id": "DEC-1", "target": "CE-1", "rel": "tasks"}),
    "decision_relink": (["DEC-1", "a.py::f", "b.py::f"], {"id": "DEC-1", "old": "a.py::f", "new": "b.py::f"}),
    "decision_find": (["--text", "t", "--tag", "g", "--status", "BUILT", "--links-to", "CE-1"], {"text": "t", "tag": "g", "status": "BUILT", "links_to": "CE-1"}),
    "decision_show": (["DEC-1", "--section", "Amendments"], {"id": "DEC-1", "section": "Amendments"}),
    "commit": (["a.py", "src/b.py", "-m", "CE-1: title", "-m", "the body"], {"paths": ["a.py", "src/b.py"], "message": "CE-1: title\n\nthe body"}),
    "why": (["CE-1"], {"target": "CE-1"}),
    "hk_regen_index": ([], {}),
    "decision_import": (["log.md", "--dry-run"], {"path": "log.md", "dry_run": True}),
    "doc_freeze": (["docs/plan.md", "--note", "CE-1 closed"], {"path": "docs/plan.md", "note": "CE-1 closed"}),
    "doc_archive": (["docs/old.md", "--to", "docs/archive", "--why", "over its cap"], {"path": "docs/old.md", "to": "docs/archive", "why": "over its cap"}),
    "register_show": (["--engine"], {"engine": True}),
    "banner_show": ([], {}),
    "banner_set": (["--seen", "abc", "--text", "new"], {"seen": "abc", "text": "new"}),
    "gate_run": (["--readers"], {"readers": True}),
    "gate_status": (["--require", "code"], {"require": "code"}),
}
TOOLS = {n for n, o in ops.OPS.items() if o.mcp}  # every operation but the CLI-only ones (gate runs, FRAMEWORK §8.0.2)
CLI_VERB = {name: verb for verb, name in cli.CLI_OPS.items()}


def _cli_subcommands() -> set[tuple[str, str | None]]:
    """Every (group, verb) the CLI's parser accepts, read from the parser itself."""
    out = set()
    groups = next(a for a in cli.build()._actions if a.dest == "group")
    for g, p in groups.choices.items():
        verbs = [a for a in p._actions if a.dest == "op"]
        out |= {(g, v) for v in verbs[0].choices} if verbs else {(g, None)}
    return out


def call(srv, name, args=None):
    async def go():
        async with Client(srv) as c:
            return await c.call_tool(name, args or {})

    return asyncio.run(go())


def text(result) -> str:
    return result.content[0].text


@pytest.fixture
def root(tmp_path):
    (tmp_path / "context.toml").write_text(_toml(CONFIG), encoding="utf-8")
    (tmp_path / "ledger.md").write_text(LEDGER, encoding="utf-8")
    (tmp_path / "HANDOFF.md").write_text(NOTE.format(key="2026-10-07b"), encoding="utf-8")
    return tmp_path


# -- one implementation per operation (AC-18) ----------------------------------------------


@pytest.mark.criterion("AC-18")
def test_every_cli_subcommand_is_one_operation_and_every_operation_one_tool(root):
    assert _cli_subcommands() == set(cli.CLI_OPS)
    assert sorted(cli.CLI_OPS.values()) == sorted(ops.OPS) == sorted(CALLS)

    async def names():
        async with Client(server(root)) as c:
            return {t.name for t in (await c.list_tools()).tools}

    assert asyncio.run(names()) == TOOLS
    assert set(ops.OPS) - TOOLS == {"gate_run"}, "only a gate run is kept out of the MCP (FRAMEWORK §8.0.2)"


def _same(params: dict) -> dict:
    """An absent optional and an empty one mean the same: drop None, '', [] and {}."""
    return {k: v for k, v in params.items() if v not in (None, "", [], {}, False)}


@pytest.mark.criterion("AC-18")
@pytest.mark.parametrize("name", sorted(CALLS))
def test_the_cli_and_the_tool_call_the_same_function_with_the_same_parameters(name, root, monkeypatch):
    seen = []
    o = ops.OPS[name]

    @functools.wraps(o.fn)
    def spy(e, c, **kw):
        seen.append(_same(kw))
        return 0, "ok"

    monkeypatch.setitem(ops.OPS, name, ops.Op(name, spy, o.write, o.rest, o.engine, o.mcp))
    argv, args = CALLS[name]
    g, verb = CLI_VERB[name]
    assert main(["--root", str(root), "--actor", ACTOR, "--session", "2026-10-08a", g, *([verb] if verb else []), *argv]) == 0
    if not o.mcp:  # CLI only: the server has no tool to call
        assert seen == [_same(args)], seen
        return
    result = call(server(root), name, args)
    assert not result.is_error, text(result)
    assert len(seen) == 2 and seen[0] == seen[1], seen
    assert seen[0] == _same(args)  # nothing dropped or invented on the way


# -- one-line writes, capped reads (AC-19) -------------------------------------------------


@pytest.mark.criterion("AC-19")
def test_every_write_in_a_session_returns_one_line(root):
    srv = server(root)
    writes = []

    def w(tool, **args):
        r = call(srv, tool, args)
        assert not r.is_error, text(r)
        writes.append(tool)
        assert "\n" not in text(r), (tool, text(r))
        return text(r)

    key = w("session_start", actor=ACTOR).split()[1]
    w("task_new", title="First", pri="NOW", brief="b")
    w("task_new", title="Second", body="Summary.\n\n## Traps\n\n- none yet\n\n## Log\n")
    w("task_set", id="CE-2", fields={"brief": "c"})
    w("task_dep", id="CE-2", add=["CE-1"])
    w("task_comment", id="CE-2", text="a note")
    w("task_touch", id="CE-2")
    w("task_section", id="CE-2", name="Traps", text="- one")
    w("task_close", id="CE-2", msg="done")
    w("task_reopen", id="CE-2", msg="not yet")
    w("task_promote", id="CE-2", pri="NEXT")
    w("ask_new", title="Which way?", body=ASK_BODY)
    w("id_reserve", kind="task", count=2)
    w("ask_raised", ids=["ASK-1"])
    w("ask_later", id="ASK-1")
    w("ask_answer", id="ASK-1", words="this way", title="This way")
    w("record_new", kind="decision", title="Kept", body="Owner words.", fields={"actor": "owner", "decision_status": "BUILT"})
    w("record_amend", id="DEC-2", text="widened")
    w("record_correct", id="DEC-2", after="Owner", text="sic")
    w("decision_link", id="DEC-2", target="CE-1")
    for f in ("a.py", "b.py"):
        (root / f).write_text("def f():\n    pass\n", encoding="utf-8")
    w("decision_link", id="DEC-2", target="a.py::f")
    w("decision_relink", id="DEC-2", old="a.py::f", new="b.py::f")
    w("decision_set", id="DEC-2", fields={"tags": "a, b"}, unset=["reopen_if"])
    w("baton_add", step="a step", why="no time")
    w("baton_done", id="BTN-1", evidence="did it")
    w("hk_expire_batons")
    sha = text(call(srv, "banner_show")).split()[3]
    w("banner_set", text="- Where things stand.", seen=sha)
    w("session_close", rows="CE-1, CE-2", summary=["built it"], guards="green", read="board")
    assert key in (root / "ledger.md").read_text(encoding="utf-8")
    untested = {o.name for o in ops.OPS.values() if o.write} - set(writes)
    # one-line by the same code paths; covered in test_working (session_abandon, which needs a stale stub; init: test_kit; the decision ops: test_decisions; record_retire: test_retire; record_confirm: test_confirm; commit, which needs git: test_commit; the doc ops: test_docs)
    assert untested == {"session_pause", "session_abandon", "pause_open", "pause_resume", "record_stamp", "init", "decision_supersede", "hk_regen_index", "decision_import", "record_retire", "record_confirm", "commit", "doc_freeze", "doc_archive"}


@pytest.mark.criterion("AC-19")
def test_a_read_over_the_cap_is_cut_at_a_line_and_says_where_the_rest_is(root):
    cfg = {**CONFIG, "working": {**CONFIG["working"], "read_max_bytes": 400}}
    (root / "context.toml").write_text(_toml(cfg), encoding="utf-8")
    srv = server(root)
    call(srv, "session_start", {"actor": ACTOR})
    for i in range(30):
        call(srv, "task_new", {"title": f"Item number {i} with a reasonably long title"})
    full = "\n".join(Engine(root).list())
    out = text(call(srv, "task_list"))
    assert len(full.encode()) > 400 >= len(out.encode())
    assert out.endswith("the rest: narrow it with `pri`, `state` or `label`]")
    shown = out.rsplit("\n", 1)[0]
    assert full.startswith(shown + "\n")  # whole lines, in order
    assert f"of {len(full.splitlines())} lines" in out
    assert text(call(srv, "task_list", {"pri": "NOW"})) == "no matching items"  # a narrow read is not cut


@pytest.mark.parametrize("limit", [60, 100, 333, 1000])
def test_cap_never_exceeds_its_limit(limit):
    body = "\n".join(f"line {i} " + "Ã©" * (i % 7) for i in range(200))
    out = cap(body, limit, "elsewhere")
    assert len(out.encode()) <= limit
    assert cap("short", limit, "x") == "short"


# -- the caller ------------------------------------------------------------------------------


def test_session_start_is_remembered_and_a_subagent_can_name_its_own_actor(root, monkeypatch):
    monkeypatch.delenv("CE_SESSION", raising=False)
    monkeypatch.delenv("CE_ACTOR", raising=False)
    srv = server(root)
    r = call(srv, "task_new", {"title": "Too early"})
    assert r.is_error and "Remedy:" in text(r)  # no session yet: refused, with its remedy
    key = text(call(srv, "session_start", {"actor": ACTOR})).split()[1]
    assert not call(srv, "task_new", {"title": "Parent's"}).is_error
    assert not call(srv, "task_new", {"title": "Subagent's", "actor": "claude-code/sub"}).is_error
    assert not call(srv, "task_new", {"title": "Parent's again"}).is_error
    log = [json.loads(line) for line in (root / "ops.jsonl").read_text(encoding="utf-8").splitlines()]
    news = [(x["id"], x["session"], x["actor"]) for x in log if x["op"] == "new"]
    assert news == [("CE-1", key, ACTOR), ("CE-2", key, "claude-code/sub"), ("CE-3", key, ACTOR)]


# -- the entry point ---------------------------------------------------------------------------


def _stdio(root) -> StdioServerParameters:
    """The server over stdio, running the code under test: without PYTHONPATH the child would
    import whatever install the interpreter finds (in a worktree, the main checkout's)."""
    import os

    import context_engine
    from mcp.client.stdio import get_default_environment

    env = {**get_default_environment(), "PYTHONPATH": os.path.dirname(os.path.dirname(context_engine.__file__))}
    return StdioServerParameters(command=sys.executable, args=["-m", "context_engine.mcp", "--root", str(root)], env=env)


def test_python_dash_m_context_engine_mcp_serves_over_stdio(root):
    params = _stdio(root)

    async def go():
        async with Client(params) as c:
            tools = {t.name for t in (await c.list_tools()).tools}
            return tools, text(await c.call_tool("orient", {}))

    tools, out = asyncio.run(go())
    assert tools == TOOLS
    assert out.startswith("# orient") and "## Banner (2026-10-07b)" in out  # the --root repo, not the cwd


def test_the_server_instructions_reach_the_client_and_ask_for_ultracode_without_granting_it(root):
    """DEC-30: the instructions tell an agent to ask the owner for ultracode; they never grant it."""
    params = _stdio(root)

    async def go():
        async with Client(params) as c:
            return c.instructions

    said = asyncio.run(go())
    assert said.startswith("Records and working state for this repo. Start every session with session_start")
    assert 'ask the owner to opt in by typing "ultracode"' in said
    assert "do not already approve one" in said
    assert not any(w in said.lower() for w in ("standing approval", "is approved", "you may use"))
