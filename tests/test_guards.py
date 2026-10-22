"""The guard catalogue as lint guards (CE-14, FRAMEWORK §8.2 to §8.4): each guard is red on
what it protects, green otherwise, and `[guards] off` is the only way to silence one."""

import json
import shutil
import tomllib

import pytest

from context_engine import guards as G
from context_engine import bootstrap as B
from context_engine.config import COUNT_NOUNS, from_dict
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


@pytest.mark.criterion("AC-46")
def test_g_d3_a_bare_name_never_resolves_to_a_stale_copy_under_build(tmp_path):
    """CE-41: a gitignored `build/lib/` copy of a module is not the module. Whichever copy a walk
    meets first, `NEW_RE` (only in the real file) resolves and `OLD_RE` (only in the stale one) is red."""
    import subprocess

    for kind in ("git", "plain"):  # git ignores build/ by .gitignore; outside git, the walk skips it
        root = tmp_path / kind
        root.mkdir()
        if kind == "git":
            subprocess.run(["git", "init", "-q"], cwd=root, check=True, capture_output=True)
            write(root, ".gitignore", "build/\n")
        e = make(root, links=["docs/guide.md"])
        write(root, "src/pkg/working.py", "NEW_RE = 1\n")
        write(root, "build/lib/pkg/working.py", "OLD_RE = 1\n")
        write(root, "docs/guide.md", "`working.py::NEW_RE` and `working.py::OLD_RE`\n")
        assert reds(e, "G-D3") == ["docs/guide.md: line 1: `working.py` has no `OLD_RE` (from `working.py::OLD_RE`)"], kind


def linked(tmp_path) -> Engine:
    cfg = config()
    cfg["kinds"]["decision"] = {"type": "Decision", "prefix": "DEC", "dir": "decisions", "mode": "replaced", "required": ["title"]}
    cfg["kinds"]["story"] = {"type": "Story", "prefix": "US", "dir": "stories", "mode": "replaced", "required": ["title"]}
    (tmp_path / "context.toml").write_text(_toml(cfg), encoding="utf-8")
    (tmp_path / "HANDOFF.md").write_text("# Note\n\n## Banner (2026-10-08a)\n\n- true now\n", encoding="utf-8")
    return Engine(tmp_path)


def rec(tmp_path, rid: str, **links) -> None:
    d = "decisions" if rid.startswith("DEC") else "stories"
    lines = [f"{k}: [{', '.join(v)}]" for k, v in links.items()]
    write(tmp_path, f"{d}/{rid}-x.md", "\n".join(["---", f"id: {rid}", "title: x", *lines, "---", "", "body", ""]))


def test_g_d3_supersedes_links_are_mirrored_never_self_and_never_a_cycle_for_both_kinds(tmp_path):
    e = linked(tmp_path)
    rec(tmp_path, "DEC-1", superseded_by=["DEC-2"])
    rec(tmp_path, "DEC-2", supersedes=["DEC-1"])
    rec(tmp_path, "US-1", superseded_by=["US-2"])
    rec(tmp_path, "US-2", supersedes=["US-1"])
    assert reds(e, "G-D3") == []
    # one side dropped by hand, for each kind: the record that still has its side is named, with the missing side
    rec(tmp_path, "DEC-2")
    rec(tmp_path, "US-1")
    assert reds(e, "G-D3") == [
        "decisions/DEC-1-x.md: DEC-1 `superseded_by` names DEC-2, but DEC-2 does not name DEC-1 in `supersedes`: the missing side is DEC-2's `supersedes`",
        "stories/US-2-x.md: US-2 `supersedes` names US-1, but US-1 does not name US-2 in `superseded_by`: the missing side is US-1's `superseded_by`",
    ]
    [red, *_] = [f for f in e.lint() if f.guard == "G-D3"]
    assert "`decision supersede <old> <new>` writes both sides" in red.remedy
    # a self link, and a link naming no decision
    rec(tmp_path, "DEC-2", supersedes=["DEC-2", "DEC-9"])
    rec(tmp_path, "US-1", superseded_by=["US-2"])
    assert reds(e, "G-D3") == [
        "decisions/DEC-1-x.md: DEC-1 `superseded_by` names DEC-2, but DEC-2 does not name DEC-1 in `supersedes`: the missing side is DEC-2's `supersedes`",
        "decisions/DEC-2-x.md: DEC-2 `supersedes` names DEC-2, itself",
        "decisions/DEC-2-x.md: DEC-2 `supersedes` names DEC-9, which is no decision record",
    ]
    # a cycle, every side mirrored
    rec(tmp_path, "DEC-1", superseded_by=["DEC-2"], supersedes=["DEC-3"])
    rec(tmp_path, "DEC-2", supersedes=["DEC-1"], superseded_by=["DEC-3"])
    rec(tmp_path, "DEC-3", supersedes=["DEC-2"], superseded_by=["DEC-1"])
    assert reds(e, "G-D3") == ["decisions/DEC-1-x.md: supersedes links form a cycle: DEC-1 -> DEC-2 -> DEC-3 -> DEC-1 (each is superseded by the next)"]


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
    assert reds(e, "G-D8") == ["HANDOFF.md: 2 headings carry a session key (the first: '## 2026-10-07b · kind: close'): session history in the orientation note"]
    write(tmp_path, "HANDOFF.md", good.replace("- **State:**", "- **2026-10-07b:** did a thing\n- **State:**"))
    assert reds(e, "G-D8") == ["HANDOFF.md: 1 banner lines start with a session key (the first: '- **2026-10-07b:** did a thing'): a stacked banner"]


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


def test_g_w7_an_op_line_whose_record_is_not_in_the_tree_is_red(tmp_path):
    e = make(tmp_path)
    rec = e.new("task", "a task", **W)
    e.touch(rec.id, session=S2, actor=ACTOR)
    other = e.new("task", "another task", **W)
    assert reds(e, "G-W7") == []
    rel = rec.path.relative_to(tmp_path).as_posix()
    rec.path.unlink()  # a by-hand commit carried the op log without the record
    assert reds(e, "G-W7") == [f"ops.jsonl: line 1 (new {rec.id}, session {S1}) and 1 more name {rel}, which is not in the tree: the op line was committed without the record it wrote"]
    orel = other.path.relative_to(tmp_path).as_posix()
    other.path.unlink()
    assert f"ops.jsonl: line 3 (new {other.id}, session {S1}) names {orel}, which is not in the tree: the op line was committed without the record it wrote" in reds(e, "G-W7")
    [red, *_] = [f for f in e.lint() if f.guard == "G-W7"]
    assert red.remedy.startswith(f"restore {rel} from the working copy or commit") and "never delete an op line" in red.remedy
    # what is not a record, and an archive's moved-away path, are not this check's
    log = tmp_path / "ops.jsonl"
    lines = [{"op": "banner.set", "id": "banner", "path": "gone.md", "session": S1},
             {"op": "doc.archive", "id": "docs/x.md", "path": "docs/x.md", "session": S1},
             {"op": "doc.archive", "id": "CE-9", "path": "tasks/CE-9-x.md", "session": S1}]
    log.write_text("".join(json.dumps(op) + "\n" for op in lines), encoding="utf-8")
    assert reds(e, "G-W7") == []


# -- G-D12 framework coverage ----------------------------------------------------------------

LETTERS = "ABCDEFGHIJKLMNOPQRSTU"  # 21 components, over the floor of 20
COV = {"coverage_spec": "spec/FRAMEWORK.md", "coverage_maps": "maps/coverage-*.md"}


def spec(components=LETTERS, procedures=11, gids=31, drop_section=False, procedure_head="### {n} Procedure {n}", gid="G-D{i}") -> str:
    rows = "\n".join(f"| {i} | Layer | **Component {c}** | what? |" for i, c in enumerate(components, 1))
    heads = "\n\n".join(procedure_head.format(n=n) for n in ["5.6"] + [f"6.{i}" for i in range(1, procedures)])
    guards = "\n".join(f"- **{gid.format(i=i)}:** a guard" for i in range(1, gids + 1))
    return (
        f"# Spec\n\n## {'Two' if drop_section else '2.'} Components\n\n| # | Layer | Component | Question |\n|---|---|---|---|\n{rows}\n\n"
        f"## 5. Working\n\n{heads}\n\n## 7. Records\n\n| 1 | Layer | **Not a component** | a numbered bold row outside §2 |\n\n"
        f"## 8. Guards\n\n{guards}\n\nXG-D99 and G-D98x are near misses, not guard ids.\n\n```\n- **G-Z9:** fenced, not a guard\n```\n"
    )


def cov_map(date="2026-10-12", drop=(), components=LETTERS, procedures=11, gids=31, edit=lambda row: row, column="Procedure") -> str:
    """A dated map; `column` heads the procedures' table (`Ritual` in a frozen map from before DEC-39)."""
    comps = [f"| {i} | Component {c} | §2 | EXISTING CE-1 |" for i, c in enumerate(components, 1)]
    comps[0] = comps[0].replace("Component A", "Component A (the first)")  # a component's cell may add a parenthesis
    procs = [f"| Procedure {n} | §{n} | PROSE-ONLY |" for n in ["5.6"] + [f"6.{i}" for i in range(1, procedures)]]
    gds = [f"| G-D{i} | §8 | EXISTING CE-14 |" for i in range(1, gids + 1)]

    def table(head: str, rows: list[str]) -> str:
        rows = [edit(r) for r in rows if not any(f"| {d} |" in r or f"| Component {d} |" in r for d in drop)]
        return f"| {head} |\n|{'---|' * (head.count('|') + 1)}\n" + "\n".join(rows) + "\n"

    return (
        f"# Coverage map, {date}\n\nFROZEN {date}.\n\n## Components\n\n{table('# | Component | § | Class', comps)}\n"
        f"## Procedures\n\n{table(f'{column} | § | Class', procs)}\n## Guards\n\n{table('Guard | § | Class', gds)}"
    )


def covered(tmp_path, **guards) -> Engine:
    e = make(tmp_path, **{**COV, **guards})
    write(tmp_path, "spec/FRAMEWORK.md", spec())
    write(tmp_path, "maps/coverage-2026-10-12.md", cov_map())
    return e


def unowned(label: str, map_rel: str = "maps/coverage-2026-10-12.md") -> str:
    return f"spec/FRAMEWORK.md: {label} is owned by no row of {map_rel} and named by no board item"


@pytest.mark.criterion("AC-56")
def test_g_d12_every_component_procedure_and_g_id_is_owned_by_the_map_or_a_board_item_closed_ones_included(tmp_path):
    e = covered(tmp_path)
    assert reds(e, "G-D12") == []
    write(tmp_path, "maps/coverage-2026-10-12.md", cov_map(drop=("G-D7", "§6.1", "B")))  # three map rows deleted
    assert reds(e, "G-D12") == [unowned("component 'Component B' (§2)"), unowned("procedure §6.1 'Procedure 6.1'"), unowned("guard G-D7")]
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
    write(tmp_path, "maps/coverage-2026-10-13z.md", cov_map("2026-10-13z"))
    assert reds(e, "G-D12") == []
    write(tmp_path, "maps/coverage-2026-10-13aa.md", cov_map("2026-10-13aa", drop=("G-D5",)))  # after z, as session keys order
    assert reds(e, "G-D12") == [unowned("guard G-D5", "maps/coverage-2026-10-13aa.md")]
    write(tmp_path, "maps/coverage-final.md", cov_map())
    assert reds(e, "G-D12") == ["maps/coverage-final.md: matches [guards] coverage_maps but has no date (YYYY-MM-DD) in its name, so the engine cannot tell which map is newest"]


@pytest.mark.criterion("AC-56")
def test_g_d12_is_red_when_a_class_extracts_under_its_floor_so_a_reworded_spec_cannot_pass_by_finding_nothing(tmp_path):
    e = covered(tmp_path)
    floor = "the spec's format no longer matches the pattern, so they would go unchecked"
    for text, red in [
        (spec(drop_section=True), f"0 components extracted, under the floor of 20: {floor}"),  # §2's heading reworded
        (spec(components=LETTERS[:19]), f"19 components extracted, under the floor of 20: {floor}"),
        (spec(procedure_head="### Procedure {n}"), f"0 procedures extracted, under the floor of 10: {floor}"),  # numbers dropped from headings
        (spec(gid="GD{i}"), f"0 G-ids extracted, under the floor of 30: {floor}"),  # the id format changed
    ]:
        write(tmp_path, "spec/FRAMEWORK.md", text)
        assert reds(e, "G-D12") == [f"spec/FRAMEWORK.md: {red}"]
    # the floors are the engine's: a repo whose spec they do not fit is told how to switch G-D12 off
    [red] = [f for f in e.lint() if f.guard == "G-D12"]
    assert 'a repo whose spec they do not fit switches G-D12 off (`[guards] off = ["G-D12"]`' in red.remedy


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
    # a glob that is not repo-relative is red, not a crash, and is not read outside the repo
    write(tmp_path, "spec/FRAMEWORK.md", spec())
    write(tmp_path, "maps/coverage-2026-10-12.md", cov_map())
    for glob in [(tmp_path / "maps" / "coverage-*.md").as_posix(), "/maps/coverage-*.md", "C:/maps/coverage-*.md", "../maps/coverage-*.md", "maps/../maps/coverage-*.md"]:
        [red] = [f for f in make(tmp_path, coverage_spec="spec/FRAMEWORK.md", coverage_maps=glob).lint() if f.guard == "G-D12"]
        assert f"{red.path}: {red.message}" == f"context.toml: [guards] coverage_maps ({glob}) is not a glob relative to the repo root"
        assert red.remedy.startswith("make it repo-relative with no `..`")


@pytest.mark.criterion("AC-56")
def test_g_d12_a_map_owns_a_class_only_in_its_own_key_column_and_a_near_miss_owns_nothing(tmp_path):
    e = covered(tmp_path)  # the spec's near misses `XG-D99` and `G-D98x` are not guard ids
    assert reds(e, "G-D12") == []
    three = [unowned("component 'Component B' (§2)"), unowned("procedure §6.1 'Procedure 6.1'"), unowned("guard G-D7")]
    # their own rows gone, each key sits in a cell that is not its class's key column
    elsewhere = {
        "| 1 | Component A (the first) | §2 |": "| 1 | Component A (the first) | §6.1 |",  # a component row's § cell
        "| G-D8 | §8 |": "| G-D8 | §6.1 |",  # a guard row's § cell
        "| G-D9 | §8 | EXISTING CE-14 |": "| G-D9 | §8 | G-D7 |",  # a cell past the key column
        "| Procedure 5.6 |": "| Component B |",  # a procedure row's first cell
    }
    edit = lambda row: next((row.replace(a, b) for a, b in elsewhere.items() if a in row), row)  # noqa: E731
    write(tmp_path, "maps/coverage-2026-10-12.md", cov_map(drop=("G-D7", "§6.1", "B"), edit=edit))
    assert reds(e, "G-D12") == three
    # only a component's key cell may add a parenthesis
    rows = cov_map(drop=("G-D7", "§6.1", "B")).replace("| Procedure 6.2 | §6.2 |", "| Procedure 6.2 | §6.2 |\n| Procedure 6.1 | §6.1 (start) |")
    write(tmp_path, "maps/coverage-2026-10-12.md", rows.replace("| G-D8 |", "| G-D7 (old) | §8 | x |\n| G-D8 |"))
    assert reds(e, "G-D12") == three
    # a board mention glued to a word on its left is not a mention
    e.new("task", "glued", body="Mentions XG-D7, x§6.1 and XComponent B.", **W)
    assert reds(e, "G-D12") == three


@pytest.mark.criterion("AC-56")
def test_g_d12_a_frozen_map_under_the_old_names_still_owns_what_dec_39_renamed(tmp_path):
    """DEC-39 renamed rituals to procedures and two §2 components; a frozen map is never edited, so
    its `Ritual` column and a row under a component's old name still own them."""
    e = covered(tmp_path)
    write(tmp_path, "maps/coverage-2026-10-12.md", cov_map(column="Ritual"))  # a map from before DEC-39
    assert reds(e, "G-D12") == []
    write(tmp_path, "maps/coverage-2026-10-12.md", cov_map(column="Rituals"))  # a header that is neither name
    assert unowned("procedure §6.1 'Procedure 6.1'") in reds(e, "G-D12")
    renamed = spec().replace("**Component B**", "**Residual-risk register**").replace("**Component C**", "**Non-functional requirements (NFRs)**")
    write(tmp_path, "spec/FRAMEWORK.md", renamed)
    old = cov_map().replace("| Component B |", "| Invariants (residual-risk register) |").replace("| Component C |", "| Law / NFRs |")
    write(tmp_path, "maps/coverage-2026-10-12.md", old)
    assert reds(e, "G-D12") == []
    write(tmp_path, "maps/coverage-2026-10-12.md", old.replace("| Law / NFRs |", "| Law |"))  # not an earlier name
    assert reds(e, "G-D12") == [unowned("component 'Non-functional requirements (NFRs)' (§2)")]


# -- G-D4 liveness (CE-33) -----------------------------------------------------------------

LIVE = ["docs"]


def live(tmp_path, **guards) -> Engine:
    return make(tmp_path, **{"liveness": LIVE, **guards})


@pytest.mark.criterion("AC-74")
def test_g_d4_each_declaration_form_passes_and_a_doc_without_one_is_red(tmp_path):
    e = live(tmp_path)
    write(tmp_path, "docs/a.md", "# A\n\nLIVING. What the doc is.\n")
    write(tmp_path, "docs/b.md", "---\ntype: Runbook\nmode: replaced\nliveness: FROZEN\n---\n\n# B\n")
    write(tmp_path, "docs/c.md", "# C\n\n**FROZEN 2026-10-12d.** As measured.\n")
    write(tmp_path, "docs/d.md", "ARCHIVED 2026-10-01\n\n# Pruned\n")
    t = e.new("task", "the plan", **W)
    (tmp_path / "docs/e.md").write_bytes(f"\ufeff# E\r\n\r\n_ACTIVE-PLAN_ for {t.id}\r\n".encode("utf-8"))  # a BOM and CRLF
    (tmp_path / "docs/j.md").write_bytes("\ufeff---\r\ntype: Runbook\r\nliveness: LIVING\r\n---\r\n".encode("utf-8"))  # an editor's BOM before frontmatter
    write(tmp_path, "docs/k.md", "# K\n\n> **FROZEN 2026-08-01.** Provenance, not a living document.\n")  # a blockquote banner
    write(tmp_path, "docs/l.md", '---\nliveness: "FROZEN"  # YAML quotes and a comment\n---\n')
    assert reds(e, "G-D4") == []
    # the word in passing declares nothing, and a declaration below the window is not near the top
    write(tmp_path, "docs/f.md", "# F\n\nThis is not a LIVING doc, and FROZEN means nothing here.\n")
    write(tmp_path, "docs/g.md", "# G\n" + "\n" * 10 + "LIVING.\n")
    write(tmp_path, "docs/h.md", "---\nliveness: LIVNG\n---\n")
    write(tmp_path, "docs/i.md", "# I\n\n- LIVING: a list item about the word\n")
    write(tmp_path, "docs/m.md", "# M\n\nThis archive is not a\nLIVING document, and nothing here is\n> FROZEN in place.\n")  # wrapped lines
    write(tmp_path, "docs/n.md", "# N\n\n```\n\nLIVING\n```\n")  # fenced code
    write(tmp_path, "docs/o.md", "# O\n\nLIVINGROOM notes\n")  # not the whole word
    write(tmp_path, "docs/p.md", "ARCHIVED\n\n# no date\n")
    write(tmp_path, "docs/q.md", "---\ntitle: q\n\nLIVING: true\n---\n")  # a frontmatter line is no body line
    assert reds(e, "G-D4") == [f"docs/{x}.md: declares no liveness in its first 10 lines" for x in "fg"] + [
        "docs/h.md: line 2: `liveness: LIVNG` is none of LIVING, ACTIVE-PLAN, FROZEN",
    ] + [f"docs/{x}.md: declares no liveness in its first 10 lines" for x in "imnopq"]
    [red] = [f for f in e.lint() if f.guard == "G-D4" and f.path == "docs/f.md"]
    assert red.remedy.startswith("open it with a line led by LIVING, ACTIVE-PLAN, FROZEN, or a frontmatter `liveness:` key")
    assert "docs/g.md" not in " ".join(reds(live(tmp_path, liveness_lines=12), "G-D4"))  # the window is configured


@pytest.mark.criterion("AC-74")
def test_g_d4_liveness_given_declares_docs_whose_top_the_repo_does_not_own(tmp_path):
    write(tmp_path, "docs/FRAMEWORK-v0.1.md", "# Old spec\n\nDraft, untracked.\n")
    write(tmp_path, "docs/FRAMEWORK-v0.4.md", "# Older spec\n")
    assert reds(live(tmp_path), "G-D4") == ["docs/FRAMEWORK-v0.1.md: declares no liveness in its first 10 lines", "docs/FRAMEWORK-v0.4.md: declares no liveness in its first 10 lines"]
    e = live(tmp_path, liveness_given={"docs/FRAMEWORK-v0.*.md": "FROZEN"})
    assert reds(e, "G-D4") == []
    # a glob that matches nothing has gone stale; a doc that declares otherwise contradicts it
    stale = live(tmp_path, liveness_given={"docs/FRAMEWORK-v0.*.md": "FROZEN", "docs/gone-*.md": "LIVING"})
    assert reds(stale, "G-D4") == ["context.toml: [guards] liveness_given names docs/gone-*.md, which matches no file"]
    e = live(tmp_path, liveness_given={"docs/FRAMEWORK-v0.*.md": "FROZEN"})
    write(tmp_path, "docs/FRAMEWORK-v0.4.md", "# Older spec\n\nLIVING. Kept current.\n")
    assert reds(e, "G-D4") == ["docs/FRAMEWORK-v0.4.md: declares LIVING (line 3), but [guards] liveness_given (docs/FRAMEWORK-v0.*.md) gives it FROZEN"]
    [red] = [f for f in e.lint() if f.guard == "G-D4"]
    assert red.remedy.startswith("open it with `ARCHIVED <date>` or a FROZEN line if it is an archived copy")
    write(tmp_path, "docs/FRAMEWORK-v0.4.md", "ARCHIVED 2026-10-13\n\n# Older spec\n\nLIVING. Kept current.\n")  # an archived copy (§6.12)
    assert reds(e, "G-D4") == []
    for given_, says in (
        ({"a.md": "LIVELY"}, "gives 'a.md' the liveness 'LIVELY'"),
        ({"/abs/*.md": "FROZEN"}, r"names '/abs/\*.md', which is not a glob relative"),
        ({"../x.md": "FROZEN"}, r"names '\.\./x.md', which is not a glob relative"),
        ({"C:/x.md": "FROZEN"}, "names 'C:/x.md', which is not a glob relative"),
    ):
        with pytest.raises(Refusal, match=says):
            from_dict(config(liveness=LIVE, liveness_given=given_))
    with pytest.raises(Refusal, match="`liveness_lines` is 0"):
        from_dict(config(liveness=LIVE, liveness_lines=0))


@pytest.mark.criterion("AC-74")
def test_g_d4_a_history_doc_is_frozen_or_active_plan_while_the_item_it_names_is_open(tmp_path):
    e = make(tmp_path, history=["evidence"])
    t = e.new("task", "measure it", **W)
    write(tmp_path, "evidence/run-2026-10-12.md", "# Run\n\nFROZEN 2026-10-12a. As measured.\n")
    write(tmp_path, "evidence/plan-2026-10-13.md", f"# Plan\n\nACTIVE-PLAN for {t.id}.\n")
    assert reds(e, "G-D4") == []
    write(tmp_path, "evidence/live-2026-10-13.md", "# Kept current\n\nLIVING. Updated as we go.\n")
    write(tmp_path, "evidence/orphan-2026-10-13.md", "# Orphan\n\nACTIVE-PLAN, for nothing on the board (CE-99).\n")
    assert reds(e, "G-D4") == [
        "evidence/live-2026-10-13.md: is LIVING, but it sits in a history directory ([guards] history), which holds provenance",
        "evidence/orphan-2026-10-13.md: is ACTIVE-PLAN but names no board item in its first 10 lines, so nobody can tell when its item closes",
    ]
    (tmp_path / "evidence/live-2026-10-13.md").unlink()
    (tmp_path / "evidence/orphan-2026-10-13.md").unlink()
    # the item lands: its plan must freeze. `task close` refuses while the plan is ACTIVE-PLAN
    # (CE-27, tests/test_docs.py), so the plan comes back after the close, as a hand edit would
    plan = (tmp_path / "evidence/plan-2026-10-13.md").read_bytes()
    (tmp_path / "evidence/plan-2026-10-13.md").unlink()
    e.close(t.id, "landed", **W)
    (tmp_path / "evidence/plan-2026-10-13.md").write_bytes(plan)
    assert reds(e, "G-D4") == [f"evidence/plan-2026-10-13.md: is ACTIVE-PLAN, but every item it names ({t.id}) is closed"]
    write(tmp_path, "evidence/plan-2026-10-13.md", f"# Plan\n\nFROZEN 2026-10-13a: landed.\n\nACTIVE-PLAN for {t.id}.\n")  # the topmost wins
    assert reds(e, "G-D4") == []
    # only the window names the item: an open item named further down does not keep a plan open
    u = e.new("task", "a follow-up", **W)
    write(tmp_path, "evidence/plan-2026-10-13.md", f"# Plan\n\nACTIVE-PLAN for {t.id}.\n" + "\n" * 10 + f"Follow-up: {u.id}.\n")
    assert reds(e, "G-D4") == [f"evidence/plan-2026-10-13.md: is ACTIVE-PLAN, but every item it names ({t.id}) is closed"]


@pytest.mark.criterion("AC-74")
def test_g_d4_a_history_directory_inside_a_liveness_one_and_its_path_forms(tmp_path):
    living = "# Kept current\n\nLIVING. Updated as we go.\n"
    write(tmp_path, "docs/evidence/live.md", living)
    write(tmp_path, "docs/evidence-old/live.md", living)  # a sibling with the same prefix is not inside
    write(tmp_path, "docs/a.md", "# A\n\nLIVING.\n")
    hist = "docs/evidence/live.md: is LIVING, but it sits in a history directory ([guards] history), which holds provenance"
    for h in ("docs/evidence", "./docs/evidence", "docs/evidence/", "docs/evidence/live.md"):
        assert reds(make(tmp_path, liveness=["docs"], history=[h]), "G-D4") == [hist], h
    assert G._under("docs/evidence/live.md", ("docs\\evidence",))  # a `\` path, as Windows writes one
    # history docs do not make a `liveness` list that holds no doc pass
    (tmp_path / "empty").mkdir()
    write(tmp_path, "docs/evidence/live.md", "# Run\n\nFROZEN 2026-10-12a.\n")
    assert reds(make(tmp_path, liveness=["empty"], history=["docs/evidence"]), "G-D4") == ["context.toml: [guards] liveness (empty) holds no doc, so G-D4 checks nothing there"]


@pytest.mark.criterion("AC-74")
def test_g_d4_is_off_while_both_lists_are_empty_and_red_on_a_missing_path_or_a_list_holding_no_doc(tmp_path):
    write(tmp_path, "docs/x.md", "# no declaration\n")
    assert reds(make(tmp_path), "G-D4") == []
    assert reds(live(tmp_path, off=["G-D4"]), "G-D4") == []
    assert reds(live(tmp_path), "G-D4") == ["docs/x.md: declares no liveness in its first 10 lines"]
    (tmp_path / "docs/x.md").unlink()
    (tmp_path / "empty").mkdir()
    assert reds(make(tmp_path, liveness=["empty", "nowhere.md"], history=["gone"]), "G-D4") == [
        "context.toml: [guards] liveness names nowhere.md, which does not exist",
        "context.toml: [guards] history names gone, which does not exist",
        "context.toml: [guards] liveness (empty, nowhere.md) holds no doc, so G-D4 checks nothing there",
    ]
    assert reds(make(tmp_path, history=["empty"]), "G-D4") == []  # an empty history directory is a fresh repo's


# -- G-D5 typed numbers (CE-33) ------------------------------------------------------------

COUNTED = """# Doc

LIVING. Kept current.

The 23 components by layer, and the seven steps of the round.
There are 12 open tasks, 1,157 tests and 40 new rows.
A quoted figure: `23 components`, "5 tests", \u201c9 checks\u201d.
Measured 2026-10-13c: 1157 tests pass.
A bound: at most 7 lines, at most 2 entries, more than 3 tasks, up to 4 files.
Narrative: two checks, one test; ids and sections are no counts: R6 tests, §6 rituals, G-D5 checks, 1.5 files, #3 rows.
Near misses: at most 2 rules, and the 23 checks here; 1234 tests on port 8080; nine checks, 23 Tests, 3 closed items.
Serial 123456-78-901 has 9 tasks.
> A quote holds 31 rows.
See ce33-false-reds-2026-10-13.md: 23 components.

```
40 tests in a transcript
```
"""


@pytest.mark.criterion("AC-75")
def test_g_d5_a_count_of_the_tree_typed_in_prose_is_red_and_p5_forms_pass(tmp_path):
    e = make(tmp_path, numbers=["docs"])
    write(tmp_path, "docs/a.md", COUNTED)
    assert reds(e, "G-D5") == [
        "docs/a.md: line 5: `23 components` is a hand-typed count of things in the tree",
        "docs/a.md: line 5: `seven steps` is a hand-typed count of things in the tree",
        "docs/a.md: line 6: `12 open tasks` is a hand-typed count of things in the tree",
        "docs/a.md: line 6: `1,157 tests` is a hand-typed count of things in the tree",
        "docs/a.md: line 6: `40 new rows` is a hand-typed count of things in the tree",
    ] + [f"docs/a.md: line 11: `{c}` is a hand-typed count of things in the tree" for c in ("23 checks", "1234 tests", "nine checks", "23 Tests", "3 closed items")] + [
        "docs/a.md: line 12: `9 tasks` is a hand-typed count of things in the tree",
        "docs/a.md: line 13: `31 rows` is a hand-typed count of things in the tree",
    ]
    [red, *_] = [f for f in e.lint() if f.guard == "G-D5"]
    assert red.remedy.startswith("delete the number and point at its home")
    # the nouns are configured: a research repo counts its runs
    assert reds(make(tmp_path, numbers=["docs"], count_nouns=["runs"]), "G-D5") == []
    write(tmp_path, "docs/a.md", "LIVING.\n\nWe did 14 runs.\n")
    assert reds(make(tmp_path, numbers=["docs"], count_nouns=["runs"]), "G-D5") == ["docs/a.md: line 3: `14 runs` is a hand-typed count of things in the tree"]
    for nouns, says in (([], "`count_nouns` is empty"), (["tests", "a b"], "holds 'a b', which is not a word")):
        with pytest.raises(Refusal, match=says):
            from_dict(config(numbers=["docs"], count_nouns=nouns))
    # an editor's BOM does not turn the frontmatter into prose
    (tmp_path / "docs/a.md").write_bytes("\ufeff---\nsource: the 3 tests run here\n---\nLIVING.\n".encode("utf-8"))
    assert reds(make(tmp_path, numbers=["docs"]), "G-D5") == []
    # the kit ships the engine's default nouns
    kit = tomllib.loads((B.KIT / B.TEMPLATE).read_text(encoding="utf-8"))
    assert tuple(kit["guards"]["count_nouns"]) == COUNT_NOUNS


@pytest.mark.criterion("AC-75")
def test_g_d5_a_frozen_or_active_plan_doc_is_provenance_and_a_list_of_only_those_checks_nothing(tmp_path):
    body = "\n\nThe 23 components.\n"
    write(tmp_path, "docs/frozen.md", "# F\n\nFROZEN 2026-10-12a." + body)
    write(tmp_path, "docs/plan.md", "# P\n\nACTIVE-PLAN for CE-1." + body)
    write(tmp_path, "docs/v0.1.md", "# Old" + body)
    e = make(tmp_path, numbers=["docs"], liveness_given={"docs/v0.*.md": "FROZEN"})
    assert reds(e, "G-D5") == ["context.toml: [guards] numbers (docs) holds no doc that is not FROZEN or ACTIVE-PLAN, so G-D5 checks nothing"]
    write(tmp_path, "docs/live.md", "# L\n\nLIVING." + body)
    assert reds(e, "G-D5") == ["docs/live.md: line 5: `23 components` is a hand-typed count of things in the tree"]
    assert "context.toml: [guards] numbers names gone.md, which does not exist" in reds(make(tmp_path, numbers=["docs", "gone.md"], liveness_given={"docs/v0.*.md": "FROZEN"}), "G-D5")
    assert reds(make(tmp_path), "G-D5") == [] and reds(make(tmp_path, numbers=["docs"], off=["G-D5"]), "G-D5") == []


# -- write-time prose checks (CE-63, INV-60) ---------------------------------------------------


def _set(e, text):
    return e.banner_set(text, e.banner().sha, session=S2, actor=ACTOR)


@pytest.mark.parametrize("text, guard", [
    ("- 2026-10-07b: what I did", "G-D8"),                    # a stacked banner line
    ("- the board holds 12 open tasks", "G-D5"),              # a hand-typed count
    ("- " + "a very long line " * 4, "G-D1"),                 # over the route's 40-character width
])
def test_banner_set_refuses_text_lint_would_fail_and_writes_nothing(tmp_path, text, guard):
    """Adhoc AAR entry 18: `banner set` stored a banner lint then rejected, and it took three
    more rounds to fix. The write now runs lint's own G-D1, G-D5 and G-D8 checks on the note it
    would store, and refuses, naming the guard and its remedy."""
    e = make(tmp_path, numbers=["HANDOFF.md"])
    before = (tmp_path / "HANDOFF.md").read_bytes()
    with pytest.raises(Refusal, match=rf"would make HANDOFF.md fail {guard}: .*nothing was written"):
        _set(e, text)
    assert (tmp_path / "HANDOFF.md").read_bytes() == before
    assert reds(e, guard) == []  # and lint agrees the stored note is clean


def test_banner_set_passes_a_clean_banner_and_ignores_failures_it_did_not_add(tmp_path):
    e = make(tmp_path, numbers=["HANDOFF.md"])
    out = _set(e, "- true now, again")
    assert out.startswith("banner replaced"), out
    note = tmp_path / "HANDOFF.md"
    note.write_text(note.read_text(encoding="utf-8") + "\n## 2026-10-07b old notes\n", encoding="utf-8")  # a hand edit lint reds
    assert reds(e, "G-D8")
    assert _set(e, "- still true").startswith("banner replaced")  # not this write's failure: lint reports it


def test_the_write_check_calls_lints_own_functions(tmp_path, monkeypatch):
    """One check, two callers: a change to the guard changes the refusal with it."""
    e = make(tmp_path)
    monkeypatch.setattr(G, "layer_failures", lambda rel, text: [G.Failure("G-D8", rel, "planted", "remedy")] if "planted" in text else [])
    assert reds(e, "G-D8") == []
    with pytest.raises(Refusal, match="fail G-D8: planted"):
        _set(e, "- planted")
    (tmp_path / "HANDOFF.md").write_text("# Note\n\n## Banner (2026-10-08a)\n\n- planted\n", encoding="utf-8")
    assert reds(e, "G-D8") == ["HANDOFF.md: planted"]  # lint reads the same function


def test_guards_off_switches_the_write_check_off_too(tmp_path):
    e = make(tmp_path, off=["G-D8"])
    assert _set(e, "- 2026-10-07b: what I did").startswith("banner replaced")


def test_session_close_refuses_a_digest_line_lint_would_fail(tmp_path):
    e = make(tmp_path)
    cfg = config()
    cfg["routes"].append({"component": "Ledger", "path": "ledger.md", "mode": "append-only", "max_width": 70})
    cfg["working"]["ledger"] = "ledger.md"
    (tmp_path / "context.toml").write_text(_toml(cfg), encoding="utf-8")
    e = Engine(tmp_path)
    key = e.session_start(actor=ACTOR)
    before = (tmp_path / "ledger.md").read_bytes()
    with pytest.raises(Refusal, match="would make ledger.md fail G-D1"):
        e.session_close(key, actor=ACTOR, rows="none", summary=["x" * 80], receipts={"guards": "green", "read": "board"})
    assert (tmp_path / "ledger.md").read_bytes() == before


def test_the_write_check_matches_failures_with_their_numbers_blanked_as_a_multiset(tmp_path):
    """A failure already there passes though its line number moves; one more of the same kind
    is refused; a FROZEN note is not counted, as lint does not count it."""
    e = make(tmp_path, numbers=["HANDOFF.md"])
    note = tmp_path / "HANDOFF.md"
    note.write_text("# Note\n\n## Banner (2026-10-08a)\n\n- true now\n\n## Board\n\n12 tasks\n", encoding="utf-8")  # G-D5 already red
    assert reds(e, "G-D5")
    assert _set(e, "- true now\n- and this").startswith("banner replaced")  # the old count's line moved: not new
    with pytest.raises(Refusal, match=r"fail G-D5: line \d+: `\d+ tasks`"):
        _set(e, "- 3 tasks are left")  # a second count of the same noun: one more than there was
    note.write_text("# Note\n\nFROZEN 2026-10-01: kept as it was.\n\n## Banner (2026-10-08a)\n\n- true now\n", encoding="utf-8")
    assert _set(e, "- 3 tasks are left").startswith("banner replaced") and not [r for r in reds(e, "G-D5") if r.startswith("HANDOFF.md")]


def test_a_note_still_over_its_cap_may_shrink(tmp_path):
    """The stored note is over its line cap already; a banner that shortens it is no new failure."""
    e = make(tmp_path)
    (tmp_path / "HANDOFF.md").write_text("# Note\n\n## Banner (2026-10-08a)\n\n" + "".join(f"- fact {i}\n" for i in range(6)), encoding="utf-8")
    assert reds(e, "G-D1")
    assert _set(e, "- fact 1\n- fact 2\n- fact 3\n- fact 4").startswith("banner replaced") and reds(e, "G-D1")


# -- the shared prose reader (CE-61, INV-61) ---------------------------------------------------


def _lines(text: str) -> list[str]:
    return [line for _, line in G.prose(text)]


def test_prose_reads_frontmatter_only_when_it_is_yaml_key_lines_that_close():
    assert _lines("---\ntitle: x\ndeps: []\n  - wrapped\n# a comment\n\n---\nbody\n") == ["body", ""]
    # a thematic break, then prose, then another break: all of it is prose
    assert _lines("---\nThe 23 components are listed here.\n---\nbody\n") == ["---", "The 23 components are listed here.", "---", "body", ""]
    # a key line followed by prose is not frontmatter either, nor a block with no key line, nor one never closed
    assert "a sentence" in _lines("---\nnote: x\na sentence\n---\n")
    assert _lines("---\n\n---\nbody") == ["---", "", "---", "body"]
    assert _lines("---\ntitle: x\nbody") == ["---", "title: x", "body"]


def test_prose_a_fence_closes_only_on_its_own_marker_at_least_as_long():
    assert _lines("```\n~~~\nhidden\n```\nshown") == ["shown"]
    assert _lines("~~~\n```\nhidden\n~~~\nshown") == ["shown"]
    assert _lines("````\n```\nhidden\n````\nshown") == ["shown"]
    # a fence line with an info string does not close; an inline ``` run with a backtick after it opens nothing
    assert _lines("```py\n```py\nhidden\n```\nshown") == ["shown"]
    assert _lines("``` a `b` c\nshown") == ["``` a `b` c", "shown"]


def test_a_doc_opening_with_a_thematic_break_is_still_read_by_its_guards(tmp_path):
    e = make(tmp_path, numbers=["docs"])
    write(tmp_path, "docs/a.md", "---\nThe 23 components.\n---\nLIVING.\n")
    assert reds(e, "G-D5") == ["docs/a.md: line 2: `23 components` is a hand-typed count of things in the tree"]
    write(tmp_path, "docs/a.md", "LIVING.\n\n```\n~~~\n```\nThe 23 components.\n")
    assert reds(e, "G-D5") == ["docs/a.md: line 6: `23 components` is a hand-typed count of things in the tree"]
