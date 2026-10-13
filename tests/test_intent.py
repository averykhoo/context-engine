"""The intent chain as lint guards (CE-25, FRAMEWORK §3.1 to §3.4, §8.1, §8.2): G-I1 goals and
stories, G-I2 story provenance, G-T1 stories specified, G-T2 criteria claimed, G-T6 criteria
sourced. Each is red on what it protects, off while a source it needs is unset, and red when a
set source yields nothing, so a reworded table cannot pass by finding nothing (DEC-33)."""

import pytest

from context_engine.config import from_dict
from context_engine.errors import Refusal
from context_engine.working import Engine

from conftest import _toml

ACTOR = "claude-code/test"
W = {"session": "2026-10-13a", "actor": ACTOR}
# The claim marker is assembled, so this file's fixtures are not claims G-T2 reads in this repo's tests/.
CRIT = "criterion"
CHARTER = "# Charter\n\n## Goals\n\n| # | Goal |\n|---|---|\n| G-1 | one |\n| G-2 | two |\n"
CRITERIA = (
    "# Criteria\n\n| id | criterion | from | status |\n|---|---|---|---|\n"
    "| AC-1 | a | US-1 | tested |\n| AC-2 | b | US-2, DEC-1 | planned |\n| AC-3 | c | DEC-1 | manual |\n"
)
TEST = f'@pytest.mark.{CRIT}("AC-1")\ndef test_a():\n    pass\n\n\n# {CRIT}: AC-3\ndef drive():\n    pass\n'
STATES = {"pri": ["NOW", "NEXT", "LATER", "SOMEDAY"], "state": ["open", "closed"]}
SOURCES = {"charter": "docs/charter.md", "stories": "story", "tests": ["tests"]}


def config(working=None, **guards) -> dict:
    return {
        "engine": {"oplog": "ops.jsonl", "lockfile": ".context/engine.lock"},
        "kinds": {
            "story": {"type": "Story", "prefix": "US", "dir": "docs/stories", "mode": "append-only", "required": ["title"], "types": {"goals": "list"}},
            "decision": {"type": "Decision", "prefix": "DEC", "dir": "docs/decisions", "mode": "append-only", "required": ["title"]},
            "task": {"type": "Task", "prefix": "CE", "dir": "tasks", "mode": "replaced", "required": ["title", "pri", "state"], "enums": STATES},
        },
        "working": {"board": ["task"], "task": "task", "decision": "decision", "criteria": "docs/criteria.md", **(working or {})},
        "guards": {**SOURCES, **guards},
    }


def write(root, rel: str, text: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def story(root, sid: str, goals: str = "[G-1]", status: str = "live", actor: str = "owner", date: str = "2026-10-13") -> None:
    write(root, f"docs/stories/{sid}-words.md", f"---\ntype: Story\nid: {sid}\ntitle: t\nactor: {actor}\ndate: {date}\nstory_status: {status}\ngoals: {goals}\n---\n\nwords\n")


def task(root, tid: str, body: str, state: str = "open") -> None:
    status = "deprecated" if state == "closed" else "draft"
    write(root, f"tasks/{tid}-x.md", f"---\ntype: Task\nid: {tid}\ntitle: t\npri: LATER\nstate: {state}\nstatus: {status}\n---\n\n{body}\n")


def make(tmp_path, working=None, **guards) -> Engine:
    (tmp_path / "context.toml").write_text(_toml(config(working, **guards)), encoding="utf-8")
    return Engine(tmp_path)


@pytest.fixture
def chain(tmp_path):
    """A repo whose intent chain is whole: two goals, two live stories (US-2 names its goal in
    the legacy form), a decision, three criteria and the claims of the two that need one."""
    write(tmp_path, "docs/charter.md", CHARTER)
    write(tmp_path, "docs/criteria.md", CRITERIA)
    write(tmp_path, "tests/test_a.py", TEST)
    write(tmp_path, "docs/decisions/DEC-1-x.md", "---\ntype: Decision\nid: DEC-1\ntitle: t\n---\n\nwhy\n")
    story(tmp_path, "US-1")
    story(tmp_path, "US-2", goals="[G2]")
    return tmp_path


def reds(e: Engine, guard: str) -> list[str]:
    return [f"{f.path}: {f.message}" for f in e.lint() if f.guard == guard]


INTENT = ("G-I1", "G-I2", "G-T1", "G-T2", "G-T6")


def all_reds(e: Engine) -> dict[str, list[str]]:
    return {g: r for g in INTENT if (r := reds(e, g))}


def edit(root, rel: str, old: str, new: str) -> None:
    p = root / rel
    text = p.read_text(encoding="utf-8")
    assert text.count(old) == 1, old
    p.write_text(text.replace(old, new), encoding="utf-8")


def test_a_whole_chain_is_green(chain):
    assert all_reds(make(chain)) == {}


# -- G-I1 ----------------------------------------------------------------------------------


@pytest.mark.criterion("AC-65")
def test_g_i1_every_goal_has_a_story_and_every_story_names_goals_of_the_charter(chain):
    story(chain, "US-3", goals="[G-9, X1]")
    story(chain, "US-4", goals="[]")
    story(chain, "US-5", goals="[G-7]", status="retired")  # history: not checked
    assert reds(make(chain), "G-I1") == [
        "docs/stories/US-3-words.md: US-3 `goals` names G-9, which is not a goal of the charter",
        "docs/stories/US-3-words.md: US-3 `X1` in `goals` is not a goal id (G-n)",
        "docs/stories/US-4-words.md: US-4 names no goal (`goals` is empty)",
    ]
    for sid in ("US-3", "US-4"):
        (chain / f"docs/stories/{sid}-words.md").unlink()
    story(chain, "US-2", goals="[G-1]", status="retired")  # a retired story serves no goal
    assert reds(make(chain), "G-I1") == ["docs/charter.md: goal G-2 is served by no story"]


@pytest.mark.criterion("AC-65")
def test_g_i1_reds_a_charter_goal_id_not_in_the_one_form_twice_or_missing_and_a_charter_with_no_goals(chain):
    edit(chain, "docs/charter.md", "| G-2 | two |", "| G2 | two |\n| G-1 | again |")
    assert reds(make(chain), "G-I1") == [
        "docs/charter.md: line 8: goal id G2 is not in the one id form",
        "docs/charter.md: line 9: goal id G-1 leads two rows",
    ]
    write(chain, "docs/charter.md", "# Charter\n\n| # | Goal |\n|---|---|\n| Goal 1 | reworded |\n")
    assert reds(make(chain), "G-I1") == ["docs/charter.md: no goal rows: no table row starts with a goal id (`| G-1 | ... |`), so no story's goals can be checked"]
    assert reds(make(chain, charter="docs/gone.md"), "G-I1") == ["context.toml: [guards] charter names docs/gone.md, which does not exist"]
    assert reds(make(chain, charter=""), "G-I1") == []  # off while unset
    write(chain, "docs/charter.md", CHARTER)
    half = "context.toml: [guards] charter is set but `stories` is not, so no story is checked against the charter"
    assert all_reds(make(chain, stories="")) == {"G-I1": [half]}  # half set: red, not a silent off; G-I2, G-T1 and G-T6 are off
    assert all_reds(make(chain, stories="", charter="docs/NOPE.md")) == {"G-I1": [half, "context.toml: [guards] charter names docs/NOPE.md, which does not exist"]}
    assert all_reds(make(chain, stories="", charter="", tests=[])) == {}  # all unset: off


# -- G-I2 and the write-time twins ---------------------------------------------------------


@pytest.mark.criterion("AC-66")
def test_g_i2_a_story_has_an_actor_a_date_and_a_status_from_the_vocabulary(chain):
    story(chain, "US-3", actor="claude-code/x", date="soon")
    story(chain, "US-4", status="done")
    story(chain, "US-5", status="unconfirmed")
    story(chain, "US-6", status="unconfirmed", actor="agent (claude-x, reconstructed from US-1 notes)")
    story(chain, "US-7", actor="human:avery")
    assert reds(make(chain), "G-I2") == [
        "docs/stories/US-3-words.md: US-3: `actor: claude-code/x` is none of `owner`, `human:<id>` or `agent (reconstructed from ...)`",
        "docs/stories/US-3-words.md: US-3: `date: soon` is not a date (YYYY-MM-DD)",
        "docs/stories/US-4-words.md: US-4: `story_status: done` is none of live, unspecified, unconfirmed, retired",
        "docs/stories/US-5-words.md: US-5: `unconfirmed` is for a story an agent reconstructed, but its actor is `owner`",
    ]


@pytest.mark.criterion("AC-66")
def test_record_new_story_refuses_bad_provenance_and_goals_before_writing(chain):
    e = make(chain)
    ok = {"actor": "owner", "date": "2026-10-13", "story_status": "live", "goals": "[G-1, G-2]"}
    for bad, match in [
        ({"goals": "[G-3]"}, r"names G-3, which is not a goal of the charter"),
        ({"goals": "[G1]"}, r"`G1` in `goals` is not in the one id form; write G-1"),
        ({"goals": "[]"}, r"names no goal"),
        ({"actor": "claude-code/x"}, r"`actor: claude-code/x` is none of"),
        ({"story_status": "unconfirmed"}, r"`unconfirmed` is for a story an agent reconstructed"),
    ]:
        with pytest.raises(Refusal, match=match):
            e.record_new("story", "New", "words", {**ok, **bad}, **W)
        assert sorted(p.name for p in (chain / "docs/stories").iterdir()) == ["US-1-words.md", "US-2-words.md"]
    rec = e.record_new("story", "New", "words", ok, **W)
    assert rec.id == "US-3" and rec.doc.get("goals") == ["G-1", "G-2"]
    off = make(chain, off=["G-I1", "G-I2"])
    assert off.record_new("story", "Off", "words", {**ok, "goals": "[G-3]", "actor": "claude-code/x"}, **W).id == "US-4"


@pytest.mark.criterion("AC-66")
def test_record_new_story_leaves_the_charters_own_reds_to_lint_unless_no_goal_can_be_read(chain):
    """A legacy or doubled charter goal id is lint's red against the charter, not a refusal of a
    sound story; a charter that yields no goal refuses, naming the charter and its remedy."""
    ok = {"actor": "owner", "date": "2026-10-13", "story_status": "live", "goals": "[G-1]"}
    edit(chain, "docs/charter.md", "| G-2 | two |", "| G2 | two |\n| G-1 | again |")
    assert make(chain).record_new("story", "Sound", "words", ok, **W).id == "US-3"
    write(chain, "docs/charter.md", "# Charter\n\n| # | Goal |\n|---|---|\n| Goal 1 | reworded |\n")
    with pytest.raises(Refusal, match=r"no story can be checked against the charter: docs/charter\.md: no goal rows.*Remedy: give each goal a row led by its id"):
        make(chain).record_new("story", "Blocked", "words", ok, **W)
    with pytest.raises(Refusal, match=r"context\.toml: \[guards\] charter names docs/gone\.md, which does not exist\. Remedy: fix the path"):
        make(chain, charter="docs/gone.md").record_new("story", "Blocked", "words", ok, **W)
    assert sorted(p.name for p in (chain / "docs/stories").iterdir()) == ["US-1-words.md", "US-2-words.md", "US-3-sound.md"]


@pytest.mark.criterion("AC-66")
def test_record_new_story_without_a_date_is_dated_today_before_the_checks_run(chain):
    """The intake command passes no date (CLAUDE.md § Rituals): a required date-typed key is
    filled with today (AC-25) before G-I2's write-time twin reads it, so it is not refused."""
    cfg = config()
    cfg["kinds"]["story"].update(required=["title", "date"], types={"goals": "list", "date": "date"})
    (chain / "context.toml").write_text(_toml(cfg), encoding="utf-8")
    e = Engine(chain)
    rec = e.record_new("story", "Undated", "words", {"actor": "owner", "story_status": "live", "goals": "[G-1]"}, **W)
    assert rec.id == "US-3" and str(rec.doc.get("date")) == str(e.today())
    assert reds(e, "G-I2") == []


# -- G-T1 ----------------------------------------------------------------------------------


@pytest.mark.criterion("AC-67")
def test_g_t1_a_live_story_has_a_criterion_and_an_unspecified_one_a_board_item(chain):
    story(chain, "US-3")
    story(chain, "US-4", status="unspecified")
    story(chain, "US-5", status="unconfirmed", actor="agent (reconstructed from notes)")  # waits on the owner
    edit(chain, "docs/criteria.md", "| AC-3 | c | DEC-1 | manual |", "| AC-3 | c | DEC-1 | manual |\n| AC-4 | d | US-3 | retired |")
    assert reds(make(chain), "G-T1") == [
        "docs/stories/US-3-words.md: US-3 is live but no criterion comes from it",
        "docs/stories/US-4-words.md: US-4 is unspecified and no open board item names it",
    ]
    task(chain, "CE-1", "Specify US-4 with the owner.", state="closed")
    task(chain, "CE-2", "Mentions US-40 and XUS-4 only.")
    assert len(reds(make(chain), "G-T1")) == 2
    task(chain, "CE-3", "Specify US-4.")
    edit(chain, "docs/criteria.md", "| AC-4 | d | US-3 | retired |", "| AC-4 | d | US-3 | planned |")
    assert reds(make(chain), "G-T1") == []


# -- G-T2 ----------------------------------------------------------------------------------


@pytest.mark.criterion("AC-68")
def test_g_t2_tested_and_manual_criteria_are_claimed_and_every_claim_resolves(chain):
    assert reds(make(chain), "G-T2") == []  # AC-1 by a marker, AC-3 by a comment: both claim
    edit(chain, "tests/test_a.py", f"# {CRIT}: AC-3", "# no claim")
    edit(chain, "docs/criteria.md", "| AC-2 | b | US-2, DEC-1 | planned |", "| AC-2 | b | US-2, DEC-1 | done |")
    write(chain, "tests/sub/test_b.py", f'@pytest.mark.{CRIT}("AC-9")\ndef test_b():\n    pass\n')
    assert reds(make(chain), "G-T2") == [
        "docs/criteria.md: line 6: AC-2 has status `done`, none of planned, tested, manual, deviates, retired",
        "docs/criteria.md: line 7: AC-3 is `manual` but no test or driver claims it",
        "tests/sub/test_b.py: line 1: claims AC-9, which is not a row of docs/criteria.md",
    ]
    edit(chain, "tests/test_a.py", f'{CRIT}("AC-1")', 'skip("AC-1")')
    assert "docs/criteria.md: line 5: AC-1 is `tested` but no test or driver claims it" in reds(make(chain), "G-T2")


@pytest.mark.criterion("AC-68")
def test_g_t2_claim_pattern_is_configurable_and_needs_exactly_one_group(chain):
    write(chain, "tests/test_a.py", "// covers AC-1\n// covers AC-3\n")
    assert len(reds(make(chain), "G-T2")) == 1  # the default pattern finds nothing: red, not green
    assert reds(make(chain, claim="covers (AC-[0-9]+)"), "G-T2") == []
    for bad, match in [("covers AC-[0-9]+", "has 0 groups"), ("(covers) (AC-[0-9]+)", "has 2 groups"), ("covers (AC-[0-9]+", "not a regular expression")]:
        with pytest.raises(Refusal, match=match):
            from_dict(config(claim=bad))
    with pytest.raises(Refusal, match=r"`stories` names kind 'tale', which is not declared"):
        from_dict(config(stories="tale"))


# -- G-T6 ----------------------------------------------------------------------------------


@pytest.mark.criterion("AC-69")
def test_g_t6_every_criterion_comes_from_a_story_or_decision_that_exists(chain):
    task(chain, "CE-1", "a task")
    edit(chain, "docs/criteria.md", "| AC-3 | c | DEC-1 | manual |", "| AC-3 | c | the owner | manual |\n| AC-4 | d | CE-1, US-9 | planned |\n| AC-5 | e | DEC-1 | retired |")
    assert reds(make(chain), "G-T6") == [
        "docs/criteria.md: line 7: AC-3 names no source (`the owner`)",
        "docs/criteria.md: line 8: AC-4 comes from CE-1, which is no story or decision",
        "docs/criteria.md: line 8: AC-4 comes from US-9, which is no story or decision",
    ]


# -- empty and missing sources -------------------------------------------------------------


@pytest.mark.criterion("AC-70")
def test_a_criteria_file_that_is_missing_unreadable_or_empty_is_red_for_each_guard_reading_it(chain):
    (chain / "docs/criteria.md").unlink()
    missing = "context.toml: [working] criteria names docs/criteria.md, which does not exist"
    assert all_reds(make(chain)) == {"G-T1": [missing], "G-T2": [missing], "G-T6": [missing]}
    write(chain, "docs/criteria.md", CRITERIA.replace("| status |", "| state |"))
    nostatus = "docs/criteria.md: line 5: a table of criteria has no `status` column, so its 3 rows cannot be read"
    assert {g: r[:1] for g, r in all_reds(make(chain)).items() if g != "G-T1"} == {"G-T2": [nostatus], "G-T6": [nostatus]}
    write(chain, "docs/criteria.md", CRITERIA.replace("| from |", "| origin |"))
    assert reds(make(chain), "G-T6")[0].endswith("has no source column (`from`, `story` or `source`), so its 3 rows cannot be read")
    write(chain, "docs/criteria.md", CRITERIA.replace("| AC-", "| AC "))  # the id format changed under the pattern
    empty = "docs/criteria.md: no criterion rows: no table row starts with an id (`| AC-1 | ... |`), so nothing is traced"
    reds_ = all_reds(make(chain))
    assert empty in reds_["G-T1"] and empty in reds_["G-T6"] and empty in reds_["G-T2"]


@pytest.mark.criterion("AC-70")
def test_a_row_of_a_criteria_table_not_led_by_a_plain_id_is_red_and_a_legacy_id_is_read_verbatim(chain):
    """Partial extraction: a row the id pattern drops must not pass every guard unread, while the
    other rows parse. An id stamped before the one form (`AC-05`, `DEC-0007`) is read as written (P3)."""
    write(chain, "docs/decisions/DEC-0007-x.md", "---\ntype: Decision\nid: DEC-0007\ntitle: t\n---\n\nwhy\n")
    edit(chain, "docs/criteria.md", "| AC-3 | c | DEC-1 | manual |", "| AC-3 | c | DEC-1 | manual |\n| **AC-4** | d | US-1 | tested |\n| AC-05 | e | US-99 | planned |\n| AC 6 | f | nobody | tested |\n| AC-7 | g | DEC-0007 | planned |")
    stray = [
        "docs/criteria.md: line 8: a row of a table of criteria is led by `**AC-4**`, which is not an id, so the row is not read",
        "docs/criteria.md: line 10: a row of a table of criteria is led by `AC 6`, which is not an id, so the row is not read",
    ]
    assert all_reds(make(chain)) == {"G-T1": stray, "G-T2": stray, "G-T6": [*stray, "docs/criteria.md: line 9: AC-05 comes from US-99, which is no story or decision"]}
    from context_engine import guards as G, working
    for cell in ("AC-4", "AC-05", "**AC-4**", "AC 6", "`AC-4`", "ac-4", "AC-"):
        assert bool(G.ROW_ID_RE.fullmatch(cell)) == bool(working.CRITERION_ROW_RE.match(f"| {cell} |")), cell


@pytest.mark.criterion("AC-65")
def test_a_row_of_the_goal_table_not_led_by_a_goal_id_is_red(chain):
    edit(chain, "docs/charter.md", "| G-2 | two |", "| G-2 | two |\n| G 3 | three |\n| G-04 | four |\n| Goal-5 | five |")
    assert reds(make(chain), "G-I1") == [
        "docs/charter.md: line 9: a row of the goal table is led by `G 3`, which is not a goal id, so it is no goal",
        "docs/charter.md: line 10: a row of the goal table is led by `G-04`, which is not a goal id, so it is no goal",
        "docs/charter.md: line 11: a row of the goal table is led by `Goal-5`, which is not a goal id, so it is no goal",
    ]


@pytest.mark.criterion("AC-70")
def test_an_escaped_pipe_stays_inside_its_cell(chain):
    edit(chain, "docs/criteria.md", "| AC-2 | b | US-2, DEC-1 | planned |", "| AC-2 | `a \\| b` pipes are escaped | US-2, DEC-1 | planned |")
    assert all_reds(make(chain)) == {}


@pytest.mark.criterion("AC-70")
def test_g_t2_is_red_on_a_missing_tests_path_or_no_claim_and_off_while_tests_is_unset(chain):
    assert reds(make(chain, tests=["tests", "drivers"]), "G-T2") == ["context.toml: [guards] tests names drivers, which does not exist"]
    write(chain, "tests/test_a.py", "def test_a():\n    pass\n")
    assert reds(make(chain), "G-T2") == ["context.toml: [guards] claim matched nothing under tests, so no test is traced"]
    assert reds(make(chain, tests=[]), "G-T2") == []
    half = "context.toml: [guards] tests is set but [working] criteria is not, so no claim is traced"
    assert all_reds(make(chain, working={"criteria": ""})) == {"G-T2": [half]}  # half set: red; G-T1 and G-T6 are off
    assert all_reds(make(chain, working={"criteria": ""}, tests=["nope"])) == {"G-T2": [half, "context.toml: [guards] tests names nope, which does not exist"]}
    assert all_reds(make(chain, working={"criteria": ""}, tests=[])) == {}  # no criteria file, no tests: the trace guards are off
