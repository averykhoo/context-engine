"""The criterion write op (CE-42, FRAMEWORK §3.3, §6.2 step 3): `criterion new` appends one row
and `criterion set` rewrites cells of one row of `[working] criteria`, under the lock, with an op
log line, every other byte of the file unchanged (a hand-edited table is never reflowed); each
write-time refusal is the twin of a rest-time guard and calls the same check (G-T2's claim scan,
G-T6's source check), and the rest-time guards red what the write refuses (an id leading two rows,
an id two `criterion.new` lines created)."""

import json

import pytest

from context_engine import criteria as CR
from context_engine import ops
from context_engine.errors import Refusal
from context_engine.working import Engine

from conftest import _toml

ACTOR, KEY = "claude-code/test", "2026-10-30a"
W = {"session": KEY, "actor": ACTOR}
CRIT = "criterion"  # assembled, so these fixtures are not claims G-T2 reads in this repo's tests/
STATES = {"pri": ["NOW", "NEXT", "LATER", "SOMEDAY"], "state": ["open", "closed"]}
HEADER = "| id | criterion | from | status |\n|---|---|---|---|\n"
CRITERIA = (
    "# Criteria\n\nLIVING. The definition of correct.\n\n## Core\n\n" + HEADER
    + "| AC-1 | a | US-1 | tested |\n| AC-2 | b | US-1, DEC-1 | planned |\n\n"
    "## Later\n\n" + HEADER + "| AC-3 | c | DEC-1 | planned |\n"
)
TEST = f'@pytest.mark.{CRIT}("AC-1")\ndef test_a():\n    pass\n'


def config(guards=None) -> dict:
    return {
        "engine": {"oplog": "ops.jsonl", "lockfile": ".context/engine.lock"},
        "kinds": {
            "story": {"type": "Story", "prefix": "US", "dir": "docs/stories", "mode": "append-only", "required": ["title"]},
            "decision": {"type": "Decision", "prefix": "DEC", "dir": "docs/decisions", "mode": "append-only", "required": ["title"]},
            "task": {"type": "Task", "prefix": "CE", "dir": "tasks", "mode": "replaced", "required": ["title", "pri", "state"], "enums": STATES},
        },
        "working": {"board": ["task"], "task": "task", "decision": "decision", "criteria": "docs/criteria.md"},
        "guards": {"stories": "story", "tests": ["tests"], **(guards or {})},
    }


def write(root, rel: str, data) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data if isinstance(data, bytes) else data.encode("utf-8"))


@pytest.fixture
def repo(tmp_path):
    write(tmp_path, "context.toml", _toml(config()))
    write(tmp_path, "docs/criteria.md", CRITERIA)
    write(tmp_path, "tests/test_a.py", TEST)
    write(tmp_path, "docs/decisions/DEC-1-x.md", "---\ntype: Decision\nid: DEC-1\ntitle: t\n---\n\nwhy\n")
    write(tmp_path, "docs/stories/US-1-x.md", "---\ntype: Story\nid: US-1\ntitle: t\nactor: owner\ndate: 2026-10-30\nstory_status: live\n---\n\nwords\n")
    return tmp_path


def crit(root) -> bytes:
    return (root / "docs/criteria.md").read_bytes()


def oplog(root) -> list[dict]:
    p = root / "ops.jsonl"
    return [json.loads(ln) for ln in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []


def refused(root, fn, *args, **kw) -> str:
    """The refusal ``fn`` raises, after checking that it wrote nothing."""
    before, logged = crit(root), len(oplog(root))
    with pytest.raises(Refusal) as r:
        fn(*args, **kw)
    assert crit(root) == before and len(oplog(root)) == logged, "a refusal wrote"
    return r.value.message


# -- criterion new: one row, every other byte unchanged (AC-160) ------------------------------


@pytest.mark.criterion("AC-160")
@pytest.mark.parametrize("form", ["lf", "crlf", "bom", "no final newline"])
def test_new_appends_one_row_under_the_heading_and_every_other_byte_is_unchanged(repo, form):
    text = CRITERIA.replace("\n", "\r\n") if form == "crlf" else CRITERIA.rstrip("\n") if form == "no final newline" else CRITERIA
    raw = (b"\xef\xbb\xbf" if form == "bom" else b"") + text.encode("utf-8")
    write(repo, "docs/criteria.md", raw)
    nl = b"\r\n" if form == "crlf" else b"\n"
    e = Engine(repo)
    line = e.criterion_new("d holds", "US-1", under="Core", **W)
    assert line == "AC-4: planned row added to docs/criteria.md under `Core` (from US-1)", line
    after_b = b"| AC-2 | b | US-1, DEC-1 | planned |" + nl
    k = raw.index(after_b) + len(after_b)
    assert crit(repo) == raw[:k] + b"| AC-4 | d holds | US-1 | planned |" + nl + raw[k:]
    mid = crit(repo)
    assert e.criterion_new("e holds", "DEC-1", under="Later", **W).startswith("AC-5: planned row added")
    last = b"| AC-3 | c | DEC-1 | planned |"
    k = mid.index(last) + len(last)
    tail = nl + b"| AC-5 | e holds | DEC-1 | planned |" + (b"" if form == "no final newline" else nl)
    assert crit(repo) == mid[:k] + tail + mid[k + (0 if form == "no final newline" else len(nl)):]
    logged = oplog(repo)
    assert [(o["op"], o["id"], o["path"], o["fields"], o["session"], o["actor"]) for o in logged] == [
        ("criterion.new", "AC-4", "docs/criteria.md", ["row"], KEY, ACTOR),
        ("criterion.new", "AC-5", "docs/criteria.md", ["row"], KEY, ACTOR),
    ]


@pytest.mark.criterion("AC-160")
def test_the_next_id_is_above_every_row_and_every_logged_new_and_a_given_id_is_one_never_used(repo):
    e = Engine(repo)
    write(repo, "ops.jsonl", json.dumps({"session": KEY, "actor": ACTOR, "op": "criterion.new", "id": "AC-9", "path": "docs/criteria.md", "fields": ["row"]}) + "\n")
    assert e.criterion_new("f", "US-1", under="Core", **W).startswith("AC-10: ")  # AC-9's row was deleted by hand: never handed out again
    assert e.criterion_new("g", "US-1", under="Core", rid="AC-20", **W).startswith("AC-20: ")
    assert "AC-2 already leads a row" in refused(repo, e.criterion_new, "h", "US-1", under="Core", rid="AC-2", **W)
    assert "AC-9 was created by an earlier `criterion new`" in refused(repo, e.criterion_new, "h", "US-1", under="Core", rid="AC-9", **W)
    assert "in the task series" in refused(repo, e.criterion_new, "h", "US-1", under="Core", rid="CE-3", **W)
    assert "is not an id" in refused(repo, e.criterion_new, "h", "US-1", under="Core", rid="AC-021", **W)


@pytest.mark.criterion("AC-160")
def test_a_criterion_write_is_one_line_over_the_mcp_path_and_rides_along(repo):
    c = ops.Caller(KEY, ACTOR)
    code, line = ops.OPS["criterion_new"].call(Engine(repo), c, text="d", source="US-1", under="Later")
    assert code == 0 and "\n" not in line and line.startswith("AC-4: ")
    code, line = ops.OPS["criterion_set"].call(Engine(repo), c, id="AC-4", text="d, reworded")
    assert code == 0 and line == "AC-4: criterion rewritten (docs/criteria.md line 17)", line


# -- criterion set: only the cells given (AC-161) -----------------------------------------------


@pytest.mark.criterion("AC-161")
def test_set_rewrites_only_the_cells_given_and_keeps_the_rest_of_the_row_and_file(repo):
    odd = "|AC-2|  b  |US-1, DEC-1|   planned |\r\n"
    loose = "| AC-3 | c \\| d | DEC-1 | planned"  # an escaped pipe in a cell, and no closing pipe
    raw = CRITERIA.replace("| AC-2 | b | US-1, DEC-1 | planned |\n", odd).replace("| AC-3 | c | DEC-1 | planned |\n", loose + "\n")
    write(repo, "docs/criteria.md", raw)
    e = Engine(repo)
    assert e.criterion_set("AC-2", text="bee", **W) == "AC-2: criterion rewritten (docs/criteria.md line 10)"
    assert crit(repo).decode() == raw.replace(odd, "|AC-2| bee |US-1, DEC-1|   planned |\r\n")
    now = crit(repo).decode()
    assert e.criterion_set("AC-3", status="retired", source="DEC-1, US-1", **W) == "AC-3: from rewritten; status planned -> retired (docs/criteria.md line 16)"
    assert crit(repo).decode() == now.replace(loose, "| AC-3 | c \\| d | DEC-1, US-1 | retired")
    assert [(o["op"], o["id"], o["fields"]) for o in oplog(repo)] == [("criterion.set", "AC-2", ["criterion"]), ("criterion.set", "AC-3", ["from", "status"])]


@pytest.mark.criterion("AC-161")
def test_set_refuses_no_row_two_rows_and_nothing_to_change(repo):
    write(repo, "docs/criteria.md", CRITERIA.replace("| AC-3 | c | DEC-1 | planned |", "| AC-3 | c | DEC-1 | **Planned** |\n| AC-2 | again | DEC-1 | planned |"))
    e = Engine(repo)
    assert "AC-7 leads no row" in refused(repo, e.criterion_set, "AC-7", status="planned", **W)
    assert "AC-2 leads 2 rows of docs/criteria.md (lines 10, 17)" in refused(repo, e.criterion_set, "AC-2", status="retired", **W)
    assert "AC-3 already says that" in refused(repo, e.criterion_set, "AC-3", status="planned", **W)  # compared as lint reads it
    assert "nothing to set" in refused(repo, e.criterion_set, "AC-3", **W)


# -- the write-time twins of G-T2 and G-T6 (AC-162) -------------------------------------------


@pytest.mark.criterion("AC-162")
def test_tested_or_manual_is_refused_unless_g_t2_finds_a_claim(repo):
    e = Engine(repo)
    msg = refused(repo, e.criterion_set, "AC-2", status="tested", **W)
    assert msg == "AC-2 cannot be `tested`: no test or driver under tests claims it (G-T2)", msg
    assert "no test or driver" in refused(repo, e.criterion_new, "z", "US-1", status="manual", under="Core", **W)
    write(repo, "tests/test_b.py", f"# {CRIT}: AC-2\ndef drive():\n    pass\n")
    assert e.criterion_set("AC-2", status="manual", **W) == "AC-2: status planned -> manual (docs/criteria.md line 10)"
    write(repo, "context.toml", _toml(config({"tests": []})))  # G-T2 off: so is its twin, and the reply says so
    line = Engine(repo).criterion_set("AC-3", status="tested", **W)
    assert line.endswith("; claim not checked: [guards] tests is unset, so G-T2 is off"), line


@pytest.mark.criterion("AC-162")
def test_a_source_that_is_not_a_story_or_decision_a_bad_status_and_a_cell_that_breaks_the_table_are_refused(repo):
    e = Engine(repo)
    assert refused(repo, e.criterion_new, "z", "US-9", under="Core", **W) == "AC-4 comes from US-9, which is neither a story nor a decision (G-T6)"
    assert "names no source" in refused(repo, e.criterion_set, "AC-2", source="the charter", **W)
    assert "`done` is not a criterion status" in refused(repo, e.criterion_set, "AC-2", status="done", **W)
    assert "would split the cell" in refused(repo, e.criterion_new, "a | b", "US-1", under="Core", **W)
    assert "line break" in refused(repo, e.criterion_new, "a\nb", "US-1", under="Core", **W)
    assert "backslash" in refused(repo, e.criterion_set, "AC-2", text="a \\", **W)
    write(repo, "context.toml", _toml(config({"stories": "", "tests": []})))  # G-T6 off: the source need only name an id
    assert Engine(repo).criterion_new("z", "US-9", under="Core", **W).startswith("AC-4: ")


# -- where the row goes, and what the op never writes (AC-163) --------------------------------


@pytest.mark.criterion("AC-163")
def test_the_table_is_named_never_guessed_and_the_op_writes_rows_only(repo):
    e = Engine(repo)
    msg = refused(repo, e.criterion_new, "z", "US-1", **W)
    assert msg == "the criteria file has 2 criteria tables, so where the row goes is a choice", msg
    assert "no heading `Nope`" in refused(repo, e.criterion_new, "z", "US-1", under="Nope", **W)
    write(repo, "docs/criteria.md", CRITERIA + "\n## Notes\n\nprose only\n\n## Core\n\ntext\n")
    assert "2 headings `Core`" in refused(repo, e.criterion_new, "z", "US-1", under="Core", **W)
    assert "holds no criteria table" in refused(repo, e.criterion_new, "z", "US-1", under="Notes", **W)
    write(repo, "docs/criteria.md", "# Criteria\n\n| criterion | id | from | status |\n|---|---|---|---|\n")  # lint reads the first cell as the id
    assert "has no criteria table" in refused(repo, e.criterion_new, "z", "US-1", **W)


@pytest.mark.criterion("AC-163")
def test_the_kits_empty_table_takes_the_first_row_and_its_claimed_by_cell_is_filled(repo):
    kit = "# Criteria\n\nLIVING.\n\n| Id | Criterion | Story | Status | Claimed by |\n|---|---|---|---|---|\n"
    write(repo, "docs/criteria.md", kit)
    e = Engine(repo)
    assert e.criterion_new("a holds", "US-1", **W) == "AC-1: planned row added to docs/criteria.md under `Criteria` (from US-1)"
    assert crit(repo).decode() == kit + "| AC-1 | a holds | US-1 | planned |  |\n"
    assert e.criterion_set("AC-1", status="tested", **W) == "AC-1: status planned -> tested; claimed by tests/test_a.py (docs/criteria.md line 7)"
    assert crit(repo).decode() == kit + "| AC-1 | a holds | US-1 | tested | tests/test_a.py |\n"


@pytest.mark.criterion("AC-163")
def test_a_row_that_would_not_read_back_as_one_criterion_is_refused(repo, monkeypatch):
    monkeypatch.setattr(CR, "append", lambda raw, place, cells: raw + "| **" + cells[0] + "** | x | US-1 | planned |\n")
    assert "would not read back as one criterion row" in refused(repo, Engine(repo).criterion_new, "z", "US-1", under="Later", **W)


# -- the rest-time twins (AC-164) -------------------------------------------------------------


@pytest.mark.criterion("AC-164")
def test_lint_reds_an_id_leading_two_rows_and_an_id_two_criterion_new_lines_created(repo):
    write(repo, "docs/criteria.md", CRITERIA + "| AC-2 | again | DEC-1 | planned |\n")
    reds = {(f.guard, f.message) for f in Engine(repo).lint()}
    dup = "line 17: AC-2 leads a second row (the first is line 10), so its claims and links are traced to one of two criteria"
    assert {("G-T1", dup), ("G-T2", dup), ("G-T6", dup)} <= reds, reds
    write(repo, "docs/criteria.md", CRITERIA)
    line = {"session": KEY, "actor": ACTOR, "op": "criterion.new", "id": "AC-3", "path": "docs/criteria.md", "fields": ["row"]}
    write(repo, "ops.jsonl", json.dumps(line) + "\n" + json.dumps({**line, "session": "2026-10-30b"}) + "\n")
    msgs = [f.message for f in Engine(repo).lint() if f.guard == "G-D2"]
    assert any(m.startswith("AC-3 was created twice") for m in msgs), msgs
