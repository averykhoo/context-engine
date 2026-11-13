"""The plan-citation check (CE-225, DEC-327 idea 2, DEC-341): `plan check <plan>` lists each
backticked path and `file::symbol` a plan cites that does not resolve, by G-D3's own resolution,
before a builder starts (FRAMEWORK §6.6, the build ladder)."""

from pathlib import Path

import pytest

from context_engine import guards as G
from context_engine import mcp, ops
from context_engine.cli import main
from context_engine.errors import Refusal

from test_guards import make, write

ACTOR = "claude-code/test"
REPO = Path(__file__).resolve().parents[1]

PLAN = """# Plan

First: `tests/test_new.py::test_two` comes before its mark.
Change `src/pkg/mod.py::Thing.method` and `mod.py::Thing`; read `docs/guide.md` and `src/pkg/`.
Create `tests/test_new.py` (new) with `tests/test_new.py::test_one`, and add `src/pkg/mod.py::Thing.fresh` (new).
Later: `test_new.py` and `src/pkg/mod.py::Thing.fresh.inner` need nothing.
Not citations: `*.md`, `<path>.md`, `.scratch/x.md`, `/etc/hosts`, `C:/Users/x.py`, `context-engine plan check`, `a b.md`, `https://example.com/x.py`.
```
`fenced/gone.py::nope` and `fenced/gone.md`
```
"""
DEAD = PLAN + """Dead: `src/pkg/mod.py::Thing.gone`, `src/pkg/Mod.py`, `docs/missing.md`, `src/pkg/nope.py::X`.
Ambiguous: `dup.py` and `dup.py::X`.
"""
MARKS = """# Marks

`docs/a.md` (new), `docs/b.md`(new), `docs/c.md`  (new), `docs/d.md` is (new), `docs/e.md` (New).
"""
SIBLINGS = """# Siblings

Create `src/pkg/new.py` (new), `src/gen/` (new) and `src/pkg/mod.py::Thing.fresh` (new).
Not covered: `src/pkg/other.py`, `src/generated.py`, `src/pkg/mod.py::Thing.stale`, `src/pkg/mod.py::Thing.freshly`.
"""
EXISTING = """# Plan

Add to `src/pkg/mod.py` (new): `src/pkg/mod.py::no_such_qq` and `src/pkg/mod.py::Thing.method`.
"""
BARE = """# Plan

Add `mod.py` (new) with `src/pkg/mod.py::no_such_qq` and `mod.py::Thing.gone`.
"""
EMPTY = "# Plan\n\nWrite the thing.\n\n```\n`src/pkg/mod.py`\n```\n"
ONLY_NEW = "# Plan\n\nCreate `tests/test_new.py` (new).\n"
SAME = """# Plan

`src/pkg/mod.py::Thing.gone`, `src/pkg/Mod.py`, `notes/sibling.md`, `notes/gone.md`, `dup.py`, `dup.py::X`, `mod.py::Thing`.
"""
AMB = "`dup.py` names 2 files whose texts are not all one (a/dup.py, b/dup.py), so which one is meant is a guess"


def _repo(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    make(root)
    write(root, "src/pkg/mod.py", "class Thing:\n    def method(self): ...\n")
    write(root, "docs/guide.md", "# Guide\n")
    write(root, "a/dup.py", "X = 1\n")
    write(root, "b/dup.py", "X = 2\n")  # both name X, so only the ambiguity is red, whichever a walk meets first
    write(root, "plans/notes/sibling.md", "# Sibling\n")
    return root


def check(root: Path, rel: str, text: str) -> tuple[int, str]:
    write(root, rel, text)
    return G.plan_check(root, rel)


@pytest.mark.criterion("AC-210")
def test_plan_check_passes_a_plan_whose_every_citation_resolves(tmp_path):
    """Fenced code, placeholders, globs, URLs, commands and dot paths are no citations; a `(new)`
    mark exempts its path, the bare name and the symbols under it, before or after the mark."""
    assert check(_repo(tmp_path), "plans/plan.md", PLAN) == (0, "plan check: plans/plan.md: 4 cited, all resolve; 6 marked (new), not checked")


@pytest.mark.criterion("AC-210")
def test_plan_check_lists_each_dead_or_ambiguous_citation_by_line_and_exits_1(tmp_path):
    code, out = check(_repo(tmp_path), "plans/plan.md", DEAD)
    assert code == 1 and out.splitlines() == [
        "plan check: plans/plan.md: 6 of 10 cited fail",
        "line 11: `src/pkg/mod.py` has no `gone` (from `src/pkg/mod.py::Thing.gone`)",
        "line 11: `src/pkg/Mod.py` names no file or directory of this repo (case-exact)",
        "line 11: `docs/missing.md` names no file or directory of this repo (case-exact)",
        "line 11: `src/pkg/nope.py` does not exist (case-exact)",
        f"line 12: {AMB}",
        f"line 12: {AMB}",
        f"remedy: {G.PLAN_REMEDY}",
    ], out


@pytest.mark.criterion("AC-210")
def test_a_plan_that_cites_nothing_fails_and_one_that_only_creates_passes(tmp_path):
    root = _repo(tmp_path)
    assert check(root, "plans/empty.md", EMPTY) == (1, "plan check: plans/empty.md: cites no path or file::symbol in backticks outside fenced code, so nothing was checked\nremedy: " + G.PLAN_EMPTY_REMEDY)
    assert check(root, "plans/new.md", ONLY_NEW) == (0, "plan check: plans/new.md: 0 cited, all resolve; 1 marked (new), not checked")


@pytest.mark.criterion("AC-210")
def test_the_new_mark_is_the_span_then_at_most_one_space_then_lower_case_new(tmp_path):
    code, out = check(_repo(tmp_path), "plans/marks.md", MARKS)
    assert code == 1 and out.splitlines() == [
        "plan check: plans/marks.md: 3 of 3 cited fail",
        "line 3: `docs/c.md` names no file or directory of this repo (case-exact)",
        "line 3: `docs/d.md` names no file or directory of this repo (case-exact)",
        "line 3: `docs/e.md` names no file or directory of this repo (case-exact)",
        f"remedy: {G.PLAN_REMEDY}",
    ], out


@pytest.mark.criterion("AC-210")
def test_a_new_mark_exempts_only_its_own_path_what_is_under_it_and_its_dotted_names(tmp_path):
    code, out = check(_repo(tmp_path), "plans/siblings.md", SIBLINGS)
    assert code == 1 and out.splitlines() == [
        "plan check: plans/siblings.md: 4 of 4 cited fail",
        "line 4: `src/pkg/other.py` names no file or directory of this repo (case-exact)",
        "line 4: `src/generated.py` names no file or directory of this repo (case-exact)",
        "line 4: `src/pkg/mod.py` has no `stale` (from `src/pkg/mod.py::Thing.stale`)",
        "line 4: `src/pkg/mod.py` has no `freshly` (from `src/pkg/mod.py::Thing.freshly`)",
        f"remedy: {G.PLAN_REMEDY}",
    ], out


@pytest.mark.criterion("AC-210")
def test_a_new_mark_on_a_path_that_exists_exempts_nothing_and_fails_itself(tmp_path):
    """verify-1 finding 1 (DEC-341 amended): a plan that adds to an existing file marks each new
    symbol, not the file; marking the file would hide every dead symbol cited in it."""
    code, out = check(_repo(tmp_path), "plans/plan.md", EXISTING)
    assert code == 1 and out.splitlines() == [
        "plan check: plans/plan.md: 2 of 3 cited fail",
        "line 3: `src/pkg/mod.py` is marked (new) but exists: mark the new symbols (or files) in it instead",
        "line 3: `src/pkg/mod.py` has no `no_such_qq` (from `src/pkg/mod.py::no_such_qq`)",
        f"remedy: {G.PLAN_REMEDY}",
    ], out


@pytest.mark.criterion("AC-210")
def test_a_new_mark_on_a_bare_name_that_names_a_repo_file_exempts_nothing(tmp_path):
    """verify-1 finding 2: `mod.py` (new) names `src/pkg/mod.py`, which exists, so it is no new
    file and exempts neither that file's symbols nor the bare name's."""
    code, out = check(_repo(tmp_path), "plans/plan.md", BARE)
    assert code == 1 and out.splitlines() == [
        "plan check: plans/plan.md: 3 of 3 cited fail",
        "line 3: `mod.py` is marked (new) but exists: mark the new symbols (or files) in it instead",
        "line 3: `src/pkg/mod.py` has no `no_such_qq` (from `src/pkg/mod.py::no_such_qq`)",
        "line 3: `mod.py` has no `gone` (from `mod.py::Thing.gone`)",
        f"remedy: {G.PLAN_REMEDY}",
    ], out


@pytest.mark.criterion("AC-210")
def test_a_path_resolves_from_the_plan_s_own_directory_only_for_a_plan_inside_the_repo(tmp_path):
    root = _repo(tmp_path / "repo")
    text = "# Plan\n\nRead `notes/sibling.md`.\n"
    assert check(root, "plans/plan.md", text) == (0, "plan check: plans/plan.md: 1 cited, all resolve; 0 marked (new), not checked")
    assert G.plan_check(root, str(root / "plans" / "plan.md"))[1].startswith("plan check: plans/plan.md: ")  # absolute, inside: shown from the root
    write(tmp_path, "outside/notes/sibling.md", "# Sibling\n")
    write(tmp_path, "outside/plan.md", text)
    code, out = G.plan_check(root, str(tmp_path / "outside" / "plan.md"))
    assert code == 1 and out.splitlines()[1:] == ["line 3: `notes/sibling.md` names no file or directory of this repo (case-exact)", f"remedy: {G.PLAN_REMEDY}"], out


@pytest.mark.criterion("AC-210")
def test_plan_check_refuses_a_path_that_names_no_file(tmp_path):
    root = _repo(tmp_path)
    for bad in ("plans/none.md", "plans", ""):
        with pytest.raises(Refusal) as r:
            G.plan_check(root, bad)
        assert r.value.message == f"there is no plan file at {bad}", bad


@pytest.mark.criterion("AC-210")
def test_plan_check_reports_what_g_d3_reports_for_the_same_text(tmp_path):
    """One resolution (DEC-341 call 2): the plan's problems are G-D3's for the same doc listed in
    both `[guards] links` and `paths`, a path from the doc's own directory included."""
    _repo(tmp_path)
    write(tmp_path, "plans/plan.md", SAME)
    e = make(tmp_path, links=["plans/plan.md"], paths=["plans/plan.md"])
    gd3 = sorted(f.message for f in e.lint() if f.guard == "G-D3" and f.path == "plans/plan.md")
    _, _, problems = G.plan_problems(G.Files(tmp_path), SAME, tmp_path / "plans")
    assert len(gd3) == 5 and sorted(problems) == gd3, (problems, gd3)


@pytest.mark.criterion("AC-210")
def test_plan_check_is_one_read_operation_with_the_exit_code_on_the_cli(tmp_path, capsys):
    root = _repo(tmp_path)
    write(root, "plans/plan.md", DEAD)
    write(root, "plans/clean.md", PLAN)
    o = ops.OPS["plan_check"]
    assert (o.write, o.mcp) == (False, True)
    assert main(["--root", str(root), "plan", "check", "plans/plan.md"]) == 1
    assert capsys.readouterr().out.startswith("plan check: plans/plan.md: 6 of 10 cited fail\n")
    assert main(["--root", str(root), "plan", "check", "plans/clean.md"]) == 0
    assert capsys.readouterr().out == "plan check: plans/clean.md: 4 cited, all resolve; 6 marked (new), not checked\n"
    assert main(["--root", str(root), "plan", "check", "plans/none.md"]) == 2
    assert "there is no plan file at plans/none.md" in capsys.readouterr().err
    out = mcp.make_tool(o, root, ops.Caller(None, ACTOR))(path="plans/plan.md")
    assert out.startswith("plan check: plans/plan.md: 6 of 10 cited fail\nline 11: "), out


@pytest.mark.criterion("AC-210")
def test_the_build_ladder_runs_plan_check_between_the_planner_and_the_builder():
    text = (REPO / "docs" / "framework" / "FRAMEWORK.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    six = text[text.index("### 6.6 "): text.index("\n### ", text.index("### 6.6 ") + 1)]
    ladder = " ".join(six[six.index("Above the floor, every task runs the build ladder:"): six.index("**The roster:**")].split())
    step1 = ladder[ladder.index("1. a planner"): ladder.index("2. a builder")]
    assert "`plan.check` (CLI `plan check <plan>`)" in step1 and "goes back to the planner before any builder starts" in step1, step1
    row = " ".join(text[text.index("| Checks |"):].split("\n", 1)[0].split())
    assert "`plan.check(path)`" in row, row
