"""The guard catalogue as lint guards (CE-14, FRAMEWORK §8.2 to §8.4): each guard is red on
what it protects, green otherwise, and `[guards] off` is the only way to silence one."""

import json
import shutil

import pytest

from context_engine import guards as G
from context_engine.config import from_dict
from context_engine.errors import Refusal
from context_engine.working import Engine

from conftest import _toml

S1, S2, S3 = "2026-10-08a", "2026-10-08b", "2026-10-09a"
ACTOR = "claude-code/test"
W = {"session": S1, "actor": ACTOR}
STATES = {"pri": ["NOW", "NEXT", "LATER", "SOMEDAY"], "state": ["open", "closed"]}
TYPES = {"created": "date", "moved": "key", "updated": "key", "closed": "key", "deps": "list"}


def config(**guards) -> dict:
    return {
        "routes": [
            {"component": "Note", "path": "HANDOFF.md", "mode": "replaced", "max_lines": 6, "max_bytes": 400, "max_width": 40},
            {"component": "Docs", "path": "docs", "mode": "replaced", "max_lines": 3},
        ],
        "engine": {"oplog": "ops.jsonl", "lockfile": ".context/engine.lock"},
        "kinds": {"task": {"type": "Task", "prefix": "CE", "dir": "tasks", "mode": "replaced", "required": ["title", "pri", "state", "created"], "enums": STATES, "types": TYPES}},
        "working": {"handoff": "HANDOFF.md", "board": ["task"], "task": "task"},
        "guards": guards,
    }


def make(tmp_path, **guards) -> Engine:
    (tmp_path / "context.toml").write_text(_toml(config(**guards)), encoding="utf-8")
    (tmp_path / "HANDOFF.md").write_text("# Note\n\n## Banner (2026-10-08a)\n\n- true now\n", encoding="utf-8")
    (tmp_path / "docs").mkdir(exist_ok=True)
    return Engine(tmp_path)


def reds(e: Engine, guard: str) -> list[str]:
    return [f"{f.path}: {f.message}" for f in e.lint() if f.guard == guard]


def write(tmp_path, rel: str, text: str) -> None:
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


# -- switches -----------------------------------------------------------------------------


@pytest.mark.criterion("AC-43")
def test_guards_off_silences_only_the_named_guard_and_an_unknown_id_is_refused(tmp_path):
    e = make(tmp_path)
    write(tmp_path, "docs/long.md", "1\n2\n3\n4\n")
    assert reds(e, "G-D1") == ["docs/long.md: 4 lines, over the Docs cap of 3"]
    quiet = make(tmp_path, off=["G-D1"])
    assert reds(quiet, "G-D1") == [] and [f for f in quiet.lint() if f.guard == "G-D1"] == []
    with pytest.raises(Refusal, match=r"`off` names 'G-Z9'.*Remedy: use guard ids lint reports: schema, G-D0"):
        from_dict(config(off=["G-Z9"]))
    with pytest.raises(Refusal, match=r"\[guards\] has unknown key 'link'"):
        from_dict(config(link=["docs"]))
    gone = make(tmp_path, links=["docs/nowhere.md"], existence=["nope"], signals=["gone"])
    assert reds(gone, "G-D3") == ["context.toml: [guards] links names docs/nowhere.md, which does not exist"]
    assert reds(gone, "G-T3") == ["context.toml: [guards] existence names nope, which does not exist"]
    assert reds(gone, "G-D7") == ["context.toml: [guards] signals names gone, which does not exist"]


# -- G-D1 ----------------------------------------------------------------------------------


@pytest.mark.criterion("AC-44")
def test_g_d1_caps_lines_bytes_and_width_of_a_routed_file_and_each_md_under_a_routed_directory(tmp_path):
    e = make(tmp_path)
    assert reds(e, "G-D1") == []
    write(tmp_path, "HANDOFF.md", "# Note\n\n" + "| a table row is wider than forty characters, and exempt |\n" + "x" * 41 + "\n" + "y" * 300 + "\n1\n2\n3\n")
    assert reds(e, "G-D1") == [
        "HANDOFF.md: 8 lines, over the Note cap of 6",
        "HANDOFF.md: 416 bytes, over the Note cap of 400",
        "HANDOFF.md: 2 lines wider than 40 characters (the first: line 4, 41)",
    ]
    write(tmp_path, "docs/a.md", "1\n2\n3\n")
    write(tmp_path, "docs/sub/b.md", "1\r\n2\r\n3\r\n4\r\n")
    write(tmp_path, "docs/c.txt", "1\n2\n3\n4\n")  # not markdown
    assert [r for r in reds(e, "G-D1") if r.startswith("docs")] == ["docs/sub/b.md: 4 lines, over the Docs cap of 3"]


# -- G-D2 ----------------------------------------------------------------------------------


@pytest.mark.criterion("AC-45")
def test_g_d2_two_files_with_one_id_and_an_id_created_twice_are_red(tmp_path):
    e = make(tmp_path)
    rec = e.new("task", "first", **W)
    assert reds(e, "G-D2") == []
    shutil.copy(rec.path, tmp_path / "tasks" / "CE-1-copy.md")
    assert reds(e, "G-D2") == ["tasks/CE-1-copy.md: id CE-1 is carried by 2 files (tasks/CE-1-copy.md, tasks/CE-1-first.md)"]
    (tmp_path / "tasks" / "CE-1-copy.md").unlink()
    text = (tmp_path / "tasks" / "CE-1-first.md").read_text(encoding="utf-8")
    write(tmp_path, "tasks/CE-2-renamed.md", text)  # a second file whose `id:` still says CE-1
    assert "id CE-1 is carried by 2 files" in reds(e, "G-D2")[0]
    (tmp_path / "tasks" / "CE-2-renamed.md").unlink()
    log = tmp_path / "ops.jsonl"
    first = log.read_text(encoding="utf-8").splitlines()[0]
    log.write_text(log.read_text(encoding="utf-8") + json.dumps({**json.loads(first), "session": S2}) + "\n", encoding="utf-8")
    assert reds(e, "G-D2") == [f"ops.jsonl: CE-1 was created twice (sessions {S1} and {S2}, op log line 2): an id was reused"]


# -- G-D3 ----------------------------------------------------------------------------------

DOC = """# Top heading

[ok](other.md) [up](../README.md) [anchor](other.md#real-heading) [self](#top-heading) [web](https://example.com/x)
![img](pic.png) `[not a link](nowhere.md)` and `src/mod.py::Thing.method`, `mod.py::Thing`, `file::symbol`
[case](Other.md)
[gone](missing.md)
[noanchor](other.md#nope)
`mod.py::Thing.gone` and `src/Mod.py::Thing`

```
[in a fence](nowhere.md) `fenced.py::X`
```

[ref]: missing-ref.md
"""


@pytest.mark.criterion("AC-46")
def test_g_d3_links_anchors_and_file_symbol_resolve_case_exact(tmp_path):
    e = make(tmp_path, links=["docs/guide.md"])
    write(tmp_path, "docs/README.md", "x\n")
    write(tmp_path, "docs/guide/other.md", "# Real heading\n")
    write(tmp_path, "docs/guide/pic.png", "")
    write(tmp_path, "src/mod.py", "class Thing:\n    def method(self): ...\n")
    write(tmp_path, "docs/guide.md", "")
    assert reds(e, "G-D3") == []
    write(tmp_path, "docs/guide/guide.md", DOC)  # links are relative to the doc's own directory
    (tmp_path / "tasks").mkdir()
    e = make(tmp_path, links=["docs/guide/guide.md", "tasks"])
    assert reds(e, "G-D3") == [
        "docs/guide/guide.md: line 5: link `Other.md` points at nothing (case-exact)",
        "docs/guide/guide.md: line 6: link `missing.md` points at nothing (case-exact)",
        "docs/guide/guide.md: line 7: link `other.md#nope` names no heading of other.md",
        "docs/guide/guide.md: line 8: `mod.py` has no `gone` (from `mod.py::Thing.gone`)",
        "docs/guide/guide.md: line 8: `src/Mod.py` does not exist (case-exact)",
        "docs/guide/guide.md: line 14: link `missing-ref.md` points at nothing (case-exact)",
    ]
    rec = e.new("task", "cites code", body="See `src/gone.py::X`.\n", **W)
    assert reds(e, "G-D3")[-1] == f"{rec.path.relative_to(tmp_path).as_posix()}: line 14: `src/gone.py` does not exist (case-exact)"
    e.close(rec.id, "done", **W)  # a closed task is history: status deprecated, not checked
    assert len(reds(e, "G-D3")) == 6


# -- G-T3 ----------------------------------------------------------------------------------

CRITERIA = """# Criteria

| AC-1 | `src/mod.py` and `src/mod.py::Thing` and `mod.py` exist; `docs/` is a directory | tested |
| AC-2 | `src/gone.py` and `src/mod.py::Gone` do not | tested |
> quoted history: `src/old.py`
- *HISTORY —* `src/old.py` was removed
`.md`, `/clear`, `<repo>/x.py`, `src/*.py`, `two words.py` are not names of files
"""


@pytest.mark.criterion("AC-47")
def test_g_t3_files_and_symbols_named_in_normative_text_exist_and_history_is_exempt(tmp_path):
    e = make(tmp_path, existence=["docs/criteria.md"])
    write(tmp_path, "src/mod.py", "class Thing: ...\n")
    write(tmp_path, "docs/criteria.md", CRITERIA)
    assert reds(e, "G-T3") == [
        "docs/criteria.md: line 4: `src/gone.py` does not exist (case-exact)",
        "docs/criteria.md: line 4: `src/mod.py` has no `Gone` (from `src/mod.py::Gone`)",
    ]
    write(tmp_path, "docs/criteria.md", CRITERIA.replace("| AC-2 |", "| AC-2 | *HISTORY —*"))
    assert reds(e, "G-T3") == []
    # frontmatter is data, not prose: a record's `code:` links are checked as links (decision_code)
    write(tmp_path, "docs/criteria.md", "---\ntitle: `src/gone.py`\n---\n" + CRITERIA.replace("| AC-2 |", "| AC-2 | *HISTORY —*"))
    assert reds(e, "G-T3") == []


# -- G-D7 ----------------------------------------------------------------------------------


@pytest.mark.criterion("AC-48")
def test_g_d7_signal_budgets_and_retired_glyphs(tmp_path):
    e = make(tmp_path, signals=["docs"], warn_max=2, bold_caps_max=2, retired_glyphs=["\U0001f534"])
    write(tmp_path, "docs/a.md", "⚠ one ⚠ two\n**NEVER** and **ACTIVE-PLAN:** and **G-D10** and **Mostly**\n```\n⚠ \U0001f534 **FENCED**\n```\n")
    assert reds(e, "G-D7") == []
    write(tmp_path, "docs/a.md", "⚠ ⚠ ⚠\n**NEVER** **ALWAYS** **STOP**\nold \U0001f534\n")
    assert reds(e, "G-D7") == [
        "docs/a.md: 3 ⚠ signals (at most 2)",
        "docs/a.md: 3 bold all-caps spans (at most 2; the first: **NEVER**)",
        "docs/a.md: uses the retired glyph '\U0001f534'",
    ]


# -- G-D8 ----------------------------------------------------------------------------------


@pytest.mark.criterion("AC-49")
def test_g_d8_one_banner_no_session_layers_and_dated_facts_are_fine(tmp_path):
    e = make(tmp_path)
    good = "# Note\n\n## Banner (2026-10-08a)\n\n- **State:** done since 2026-10-07b,\n  2026-10-07b wrapped here\n\n## Facts (dated)\n\n- **2026-10-07b, a fact:** kept\n"
    write(tmp_path, "HANDOFF.md", good)
    assert reds(e, "G-D8") == []
    write(tmp_path, "HANDOFF.md", good + "\n## Banner (2026-10-07b)\n\nold\n")
    assert reds(e, "G-D8") == ["HANDOFF.md: 2 banner headings (2026-10-08a, 2026-10-07b)"]
    write(tmp_path, "HANDOFF.md", good + "\n## 2026-10-07b · kind: close\n\n### Session 2026-10-07a\n")
    assert reds(e, "G-D8") == ["HANDOFF.md: 2 headings carry a session key (the first: '## 2026-10-07b · kind: close'): session history in the note"]
    write(tmp_path, "HANDOFF.md", good.replace("- **State:**", "- **2026-10-07b:** did a thing\n- **State:**"))
    assert reds(e, "G-D8") == ["HANDOFF.md: 1 banner lines start with a session key (the first: '- **2026-10-07b:** did a thing'): a layered banner"]


# -- G-D9 ----------------------------------------------------------------------------------


@pytest.mark.criterion("AC-50")
def test_g_d9_every_number_in_the_config_carries_provenance_and_no_example(tmp_path):
    text = """[working]
orient_max_bytes = 4000
read_max_bytes = 4000   # provenance: JUDGEMENT, why
ask_overdue_days = 7    # provenance: MEASURED 2026-10-12, from the FRAMEWORK example; wrong if x
max_pauses = 2          # provenance: MEASURED 2026-10-12, 40 sessions; wrong if real work needs more
baton_max_age = 3       # provenance: JUDGEMENT, same; wrong as above
ledger = "2"            # a string, not a tuned number
[working.caps]
NEXT = 5                # no provenance here
"""
    got = [(t.line, t.key, t.problem.split(" ")[0]) for t in G.provenance_problems(text)]
    assert got == [(2, "orient_max_bytes", "has"), (3, "read_max_bytes", "says"), (4, "ask_overdue_days", "cites"), (5, "max_pauses", ""), (6, "baton_max_age", ""), (9, "NEXT", "has")]
    assert [t.key for t in G.provenance_problems('a = { s = "x # y = 2", NOW = 1 }  # provenance: JUDGEMENT, y; wrong if z\nb = [1, 2]\n')] == ["NOW"]
    e = make(tmp_path)  # the fixture writes its routes as one line of inline tables, with no notes
    assert reds(e, "G-D9") == [f"context.toml: `{k}` (line 1) has no `provenance: MEASURED` or `provenance: JUDGEMENT` note" for k in ("max_lines", "max_bytes", "max_width", "max_lines")]


# -- G-W7 ----------------------------------------------------------------------------------


@pytest.mark.criterion("AC-51")
def test_g_w7_session_keyed_owned_keys_match_the_op_log(tmp_path):
    e = make(tmp_path)
    rec = e.new("task", "a task", **W)
    e.touch(rec.id, session=S2, actor=ACTOR)
    assert reds(e, "G-W7") == []
    path = rec.path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(f"moved: {S2}", f"moved: {S3}"), encoding="utf-8")  # a hand edit
    [red] = reds(e, "G-W7")
    assert red.startswith(f"{path.relative_to(tmp_path).as_posix()}: `moved: {S3}`, but the newest operation that wrote it (touch, ") and red.endswith(f") was in session {S2}")
    path.write_text(text.replace("state: open", f"state: open\nclosed: {S3}"), encoding="utf-8")  # no op wrote it
    assert reds(e, "G-W7") == [f"{path.relative_to(tmp_path).as_posix()}: `closed: {S3}`, but no logged operation wrote it"]
    path.write_text(text.replace("state: open", "state: open\nclosed: 2026-10-01a"), encoding="utf-8")  # before the log began
    assert reds(e, "G-W7") == []
    log = tmp_path / "ops.jsonl"
    log.write_text(log.read_text(encoding="utf-8") + "{not json\n", encoding="utf-8")
    assert reds(e, "G-W7") == ["ops.jsonl: 1 lines do not parse as JSON (the first: line 3)"]
    assert [f.guard for f in e.lint(working=True) if f.guard == "G-W7"] == ["G-W7"]  # `lint --working` runs it


# -- G-D12 framework coverage ----------------------------------------------------------------

LETTERS = "ABCDEFGHIJKLMNOPQRSTU"  # 21 components, over the floor of 20
COV = {"coverage_spec": "spec/FRAMEWORK.md", "coverage_maps": "maps/coverage-*.md"}


def spec(components=LETTERS, rituals=11, gids=31, drop_section=False, ritual_head="### {n} Ritual {n}", gid="G-D{i}") -> str:
    rows = "\n".join(f"| {i} | Layer | **Component {c}** | what? |" for i, c in enumerate(components, 1))
    heads = "\n\n".join(ritual_head.format(n=n) for n in ["5.6"] + [f"6.{i}" for i in range(1, rituals)])
    guards = "\n".join(f"- **{gid.format(i=i)}:** a guard" for i in range(1, gids + 1))
    return (
        f"# Spec\n\n## {'Two' if drop_section else '2.'} Components\n\n| # | Layer | Component | Question |\n|---|---|---|---|\n{rows}\n\n"
        f"## 5. Working\n\n{heads}\n\n## 7. Records\n\n| 1 | Layer | **Not a component** | a numbered bold row outside §2 |\n\n"
        f"## 8. Guards\n\n{guards}\n\n```\n- **G-Z9:** fenced, not a guard\n```\n"
    )


def cov_map(date="2026-10-12", drop=(), components=LETTERS, rituals=11, gids=31) -> str:
    rows = [f"| {i} | Component {c} | §2 | EXISTING CE-1 |" for i, c in enumerate(components, 1)]
    rows[0] = rows[0].replace("Component A", "Component A (the first)")  # a component's cell may add a parenthesis
    rows += [f"| Ritual | §{n} | PROSE-ONLY |" for n in ["5.6"] + [f"6.{i}" for i in range(1, rituals)]]
    rows += [f"| G-D{i} | §8 | EXISTING CE-14 |" for i in range(1, gids + 1)]
    rows = [r for r in rows if not any(f"| {d} |" in r or f"| Component {d} |" in r for d in drop)]
    return f"# Coverage map, {date}\n\nFROZEN {date}.\n\n| Key | § | Class |\n|---|---|---|\n" + "\n".join(rows) + "\n"


def covered(tmp_path, **guards) -> Engine:
    e = make(tmp_path, **{**COV, **guards})
    write(tmp_path, "spec/FRAMEWORK.md", spec())
    write(tmp_path, "maps/coverage-2026-10-12.md", cov_map())
    return e


def unowned(label: str, map_rel: str = "maps/coverage-2026-10-12.md") -> str:
    return f"spec/FRAMEWORK.md: {label} is owned by no row of {map_rel} and named by no board item"


@pytest.mark.criterion("AC-56")
def test_g_d12_every_component_ritual_and_g_id_is_owned_by_the_map_or_a_board_item_closed_ones_included(tmp_path):
    e = covered(tmp_path)
    assert reds(e, "G-D12") == []
    write(tmp_path, "maps/coverage-2026-10-12.md", cov_map(drop=("G-D7", "§6.1", "B")))  # three map rows deleted
    assert reds(e, "G-D12") == [unowned("component 'Component B' (§2)"), unowned("ritual §6.1 'Ritual 6.1'"), unowned("guard G-D7")]
    # a near miss is not a mention: `§6.10` does not name §6.1, `G-D70` does not name G-D7
    t = e.new("task", "near misses", body="Covers §6.10 and G-D70 and Component BB.", **W)
    assert len(reds(e, "G-D12")) == 3
    # a board item naming them owns them, and still does once it is closed
    e.comment(t.id, "Builds G-D7 and §6.1 for Component B.", **W)
    e.close(t.id, "done in abc123", **W)
    assert e.store.read(t.path).get("state") == "closed"
    assert reds(e, "G-D12") == []
    # a G-id the spec gains that nothing owns
    write(tmp_path, "spec/FRAMEWORK.md", spec().replace("## 8. Guards\n", "## 8. Guards\n\n- **G-Q1:** new and unowned\n"))
    [red] = [f for f in e.lint() if f.guard == "G-D12"]
    assert f"{red.path}: {red.message}" == unowned("guard G-Q1")
    assert red.remedy.startswith("file a board item that names G-Q1 (`task new`), or write a new dated coverage map")
    assert reds(make(tmp_path, off=["G-D12"], **COV), "G-D12") == []


@pytest.mark.criterion("AC-56")
def test_g_d12_reads_the_newest_dated_map_and_refuses_an_undated_one(tmp_path):
    e = covered(tmp_path)
    write(tmp_path, "maps/coverage-2026-10-13.md", cov_map("2026-10-13", drop=("G-D7",)))  # newer, a row short
    assert reds(e, "G-D12") == [unowned("guard G-D7", "maps/coverage-2026-10-13.md")]
    write(tmp_path, "maps/coverage-2026-10-13b.md", cov_map("2026-10-13b"))  # a later session the same day
    assert reds(e, "G-D12") == []
    write(tmp_path, "maps/coverage-2026-10-13b.md", cov_map("2026-10-13b", drop=("G-D9",)))
    assert reds(e, "G-D12") == [unowned("guard G-D9", "maps/coverage-2026-10-13b.md")]
    write(tmp_path, "maps/coverage-final.md", cov_map())
    assert reds(e, "G-D12") == ["maps/coverage-final.md: matches [guards] coverage_maps but has no date (YYYY-MM-DD) in its name, so the newest map cannot be told"]


@pytest.mark.criterion("AC-56")
def test_g_d12_is_red_when_a_class_extracts_under_its_floor_so_a_reworded_spec_cannot_pass_by_finding_nothing(tmp_path):
    e = covered(tmp_path)
    floor = "the spec's format no longer matches the pattern, so they would go unchecked"
    for text, red in [
        (spec(drop_section=True), f"0 components extracted, under the floor of 20: {floor}"),  # §2's heading reworded
        (spec(components=LETTERS[:19]), f"19 components extracted, under the floor of 20: {floor}"),
        (spec(ritual_head="### Ritual {n}"), f"0 rituals extracted, under the floor of 10: {floor}"),  # numbers dropped from headings
        (spec(gid="GD{i}"), f"0 G-ids extracted, under the floor of 30: {floor}"),  # the id format changed
    ]:
        write(tmp_path, "spec/FRAMEWORK.md", text)
        assert reds(e, "G-D12") == [f"spec/FRAMEWORK.md: {red}"]


@pytest.mark.criterion("AC-56")
def test_g_d12_is_off_while_both_paths_are_unset_and_red_on_one_unset_or_a_missing_path(tmp_path):
    e = make(tmp_path)  # neither set: off, though there is no spec and no map
    assert reds(e, "G-D12") == []
    assert reds(make(tmp_path, coverage_spec="spec/FRAMEWORK.md"), "G-D12") == ["context.toml: [guards] sets coverage_spec but not coverage_maps"]
    assert reds(make(tmp_path, coverage_maps="maps/*.md"), "G-D12") == ["context.toml: [guards] sets coverage_maps but not coverage_spec"]
    assert reds(make(tmp_path, **COV), "G-D12") == [
        "context.toml: [guards] coverage_spec names spec/FRAMEWORK.md, which does not exist",
        "context.toml: [guards] coverage_maps matches no file (maps/coverage-*.md)",
    ]
