"""The framework's build status (CE-141): `context-engine coverage` gives each component, procedure
and G-id the spec names one status, generated on demand from what G-D12 reads (the spec, the newest
coverage map), the board and the guard ids lint reports; nothing is stored, so nothing goes stale."""

import pytest

from context_engine import guards as G
from context_engine import ops
from context_engine.cli import run
from context_engine.errors import Refusal

from test_guards import COV, W, make, spec, write

MAP = """# Coverage map, 2026-10-12

FROZEN 2026-10-12.

## Components

| # | Component | § | Class | Home | Reason |
|---|---|---|---|---|---|
| 1 | Component A | §2 | EXISTING CE-2 (built) | `a.py` | built |
| 2 | Component B | §2 | EXISTING CE-2 | `b.py` | split |
| 4 | Component D | §2 | DEFERRED | none | trigger "the first law" not hit. Un-defer: the first law. |
| 5 | Component E | §2 | PROSE-ONLY | `CLAUDE.md` § Rules | a rule, no tool |
| 6 | Component F | §2 | NEW CE-99 | none | filed elsewhere |

## Procedures

| Procedure | § | Class |
|---|---|---|
| Procedure 6.1 | §6.1 | EXISTING CE-1 |

## Guards

| Guard | § | Class | Reason |
|---|---|---|---|
| G-D1 | §8 | DEFERRED | an old map's word, overtaken by the engine |
| G-D20 | §8 | DEFERRED | trigger "the suite is large" not hit |
"""


def status_repo(tmp_path):
    e = make(tmp_path, **COV)
    write(tmp_path, "spec/FRAMEWORK.md", spec().replace("## 5. Working", "G-D10 is named first.\n\n## 5. Working"))
    write(tmp_path, "maps/coverage-2026-10-12.md", MAP)
    e.new("task", "builds Component B", body="Builds Component B, G-D25 and §6.2.", **W)  # CE-1, open
    done = e.new("task", "built Component C", body="Built Component C and §6.3.", **W)  # CE-2, closed
    e.close(done.id, "done in abc123", **W)
    gone = e.new("task", "built a guard", body="Built G-D26.", **W)  # CE-3, closed
    e.close(gone.id, "done in abc124", **W)
    for i in range(6):  # CE-4 to CE-9: six open items naming G-D27, over the five a row lists
        e.new("task", f"mention {i}", body="Touches G-D27.", **W)
    return e


def by_key(e) -> dict[str, tuple[str, str, str]]:
    _, rows = G.framework_status(e)
    return {r.item.key: (r.status, r.board, r.note) for cls in rows for r in rows[cls]}


@pytest.mark.criterion("AC-170")
def test_coverage_gives_each_spec_item_the_first_status_that_holds(tmp_path):
    e = status_repo(tmp_path)
    got = by_key(e)
    # a guard lint reports is built, whatever an older map row says of it
    assert got["G-D1"] == ("built", "none", "lint reports it")
    # the map's DEFERRED and PROSE-ONLY rows, with the row's reason and home as the note
    assert got["Component D"] == ("deferred", "none", 'trigger "the first law" not hit. Un-defer: the first law.')
    assert got["G-D20"] == ("deferred", "none", 'trigger "the suite is large" not hit')
    assert got["Component E"] == ("prose-only", "none", "`CLAUDE.md` § Rules")
    # the row's item open, or any open item naming it: open work, even when the row's item closed
    assert got["§6.1"] == ("open work", "map: CE-1 (open); open: CE-1", "")
    assert got["Component B"] == ("open work", "map: CE-2 (closed); open: CE-1", "")
    assert got["§6.2"] == ("open work", "open: CE-1", "")
    assert got["G-D25"] == ("open work", "open: CE-1", "")
    # only closed items: done, from the row's item or from a closed item naming it
    assert got["Component A"] == ("done", "map: CE-2 (closed)", "")
    assert got["Component C"] == ("done", "closed: CE-2", "")
    assert got["§6.3"] == ("done", "closed: CE-2", "")
    assert got["G-D26"] == ("done", "closed: CE-3", "")
    # a row whose item this board does not hold, and nothing naming it
    assert got["Component F"] == ("map only", "none", "NEW CE-99")
    # nothing at all
    assert got["Component G"] == ("unowned", "none", "")
    assert got["G-D30"] == ("unowned", "none", "")
    # a row lists five open items, then how many more
    assert got["G-D27"] == ("open work", "open: CE-4, CE-5, CE-6, CE-7, CE-8 +1 more", "")
    # every item the spec names has exactly one row: 21 components, 11 procedures, 31 G-ids
    _, rows = G.framework_status(e)
    assert {c: len(r) for c, r in rows.items()} == {"component": 21, "procedure": 11, "G-id": 31}
    assert [r.item.key for r in rows["G-id"]][:3] == ["G-D1", "G-D2", "G-D3"]  # by number, not as the spec first names them
    assert [r.item.key for r in rows["G-id"]][9] == "G-D10"


@pytest.mark.criterion("AC-170")
def test_coverage_prints_the_totals_the_rules_and_a_table_per_class_and_stores_nothing(tmp_path):
    e = status_repo(tmp_path)
    before = sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*") if p.is_file())
    code, text = run(["--root", str(tmp_path), "--actor", W["actor"], "--session", W["session"], "coverage"])
    after = sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*") if p.is_file())
    assert code == 0
    assert before == after  # read on demand: no file is written, so none can go stale
    assert ops.OPS["coverage"].write is False
    assert "the newest coverage map (maps/coverage-2026-10-12.md)" in text
    assert "Totals: components 21: deferred 1, prose-only 1, open work 1, done 2, map only 1, unowned 15;" in text
    assert "- **built**: a guard `context-engine lint` reports" in text
    assert "| § | Procedure | Status | Board | Note |" in text
    assert "| §6.1 | Procedure 6.1 | open work | map: CE-1 (open); open: CE-1 |  |" in text
    assert "| G-D20 | deferred | none | trigger \"the suite is large\" not hit |" in text


@pytest.mark.criterion("AC-171")
def test_coverage_refuses_while_g_d12_has_no_sources_or_broken_ones(tmp_path):
    with pytest.raises(Refusal) as r:
        G.framework_status(make(tmp_path))
    assert "names no coverage_spec and coverage_maps" in r.value.message
    assert "coverage_spec = " in r.value.remedy
    e = make(tmp_path, **COV)  # set, but the spec is missing
    with pytest.raises(Refusal) as r:
        G.framework_status(e)
    assert r.value.message == "G-D12 cannot read its sources: context.toml: [guards] coverage_spec names spec/FRAMEWORK.md, which does not exist"
    assert r.value.remedy.startswith("fix the path")
    write(tmp_path, "spec/FRAMEWORK.md", spec(procedures=3))  # under the procedures' floor
    write(tmp_path, "maps/coverage-2026-10-12.md", MAP)
    with pytest.raises(Refusal) as r:
        G.framework_status(e)
    assert "procedures extracted, under the floor" in r.value.message
    write(tmp_path, "spec/FRAMEWORK.md", spec())
    assert G.framework_status(e)[0] == "maps/coverage-2026-10-12.md"
