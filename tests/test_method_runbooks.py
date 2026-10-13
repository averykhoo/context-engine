"""The method runbooks (CE-26, FRAMEWORK §7.5): gate, sabotage, fan-out and release ship in the
kit beside the two by-hand runbooks; FRAMEWORK §7.5 and the kit name the same set; each declares
its liveness (P2), is routed on its own with caps, here and in the kit's config template; and
the fan-out runbook's build rounds are FRAMEWORK §6.6's steps.

Byte equality with the kit copies and the leak check are tests/test_kit.py's (AC-37, AC-33), which
read every kit file. Not checked here: whether a runbook's method is right (the review does that),
and rituals.md and manual-mode.md's liveness lines (they have none yet; G-D4 is CE-33)."""

import re
import tomllib
from pathlib import Path

import pytest

from context_engine import bootstrap as B
from context_engine.working import Engine

REPO = Path(__file__).resolve().parents[1]
FRAMEWORK = REPO / "docs" / "framework" / "FRAMEWORK.md"
METHOD = ("gate.md", "sabotage.md", "fan-out.md", "release.md")
CHANGE_MODES = {"replaced", "append-only", "generated", "stamped"}  # P2
LIVENESS = {"LIVING", "ACTIVE-PLAN", "FROZEN"}  # P2


def _section(text: str, start: str, end: str) -> str:
    text = text.replace("\r\n", "\n")
    i = text.index(start)
    return text[i : text.index(end, i + len(start))]


def _frontmatter(text: str) -> dict[str, str]:
    m = re.match(r"---\n(.*?)\n---\n", text.replace("\r\n", "\n"), re.DOTALL)
    assert m, "no frontmatter"
    return dict(ln.split(": ", 1) for ln in m.group(1).splitlines() if ": " in ln)


def _routes(toml_text: str) -> dict[str, dict]:
    return {r["path"]: r for r in tomllib.loads(toml_text).get("routes", [])}


@pytest.mark.criterion("AC-71")
def test_framework_7_5_and_the_kit_name_the_same_runbooks():
    named = set(re.findall(r"`docs/runbooks/([\w.-]+\.md)`", _section(FRAMEWORK.read_text(encoding="utf-8"), "### 7.5 ", "\n## 8.")))
    shipped = {p.name for p in (B.KIT / "docs" / "runbooks").iterdir() if p.is_file()}
    copied = {dst.rsplit("/", 1)[1] for dst in B.FILES.values() if dst.startswith("docs/runbooks/")}
    assert named == shipped == copied, f"FRAMEWORK §7.5 names {sorted(named)}; the kit ships {sorted(shipped)}; init copies {sorted(copied)}"
    assert set(METHOD) <= shipped


@pytest.mark.criterion("AC-71")
@pytest.mark.parametrize("name", METHOD)
def test_each_method_runbook_declares_how_it_changes_and_how_alive_it_is(name):
    fm = _frontmatter((REPO / "docs" / "runbooks" / name).read_text(encoding="utf-8"))
    assert fm.get("type") == "Runbook", fm
    assert fm.get("mode") in CHANGE_MODES, f"{name}: `mode:` must be one of {sorted(CHANGE_MODES)} (P2), not {fm.get('mode')!r}"
    assert fm.get("liveness") in LIVENESS, f"{name}: `liveness:` must be one of {sorted(LIVENESS)} (P2), not {fm.get('liveness')!r}"


@pytest.mark.criterion("AC-71")
@pytest.mark.parametrize("config", ["context.toml", "src/context_engine/kit/context.toml.template"])
@pytest.mark.parametrize("name", METHOD)
def test_each_method_runbook_has_its_own_route_with_caps(config, name):
    routes = _routes((REPO / config).read_text(encoding="utf-8"))
    route = routes.get(f"docs/runbooks/{name}")
    assert route, f"{config} has no [[routes]] entry for docs/runbooks/{name}, so G-R1 cannot see it go"
    assert route.get("max_lines", 0) > 0 and route.get("max_bytes", 0) > 0, f"{config}: the route for {name} has no G-D1 caps, so nothing keeps it short"


@pytest.mark.criterion("AC-71")
@pytest.mark.parametrize("name", METHOD)
def test_an_adopted_repo_that_loses_a_method_runbook_or_outgrows_it_is_red(tmp_path, name):
    B.init(tmp_path)
    rel = f"docs/runbooks/{name}"
    assert [f for f in Engine(tmp_path).lint() if f.guard in ("G-R1", "G-D1")] == []
    path = tmp_path / rel
    text = path.read_text(encoding="utf-8")
    path.unlink()
    assert any(f.guard == "G-R1" and rel in f.message for f in Engine(tmp_path).lint()), "a lost method runbook must fail G-R1"
    path.write_text(text + "\nfiller\n" * 200, encoding="utf-8")
    assert any(f.guard == "G-D1" and f.path == rel for f in Engine(tmp_path).lint()), "an overgrown method runbook must fail G-D1"


def _steps(rows: list[str]) -> list[tuple[str, str]]:
    def norm(s: str) -> str:
        return re.sub(r"\s+", " ", s.replace("**", "")).strip().rstrip(";.").lower()

    return [(n, norm(step)) for n, step in rows]


@pytest.mark.criterion("AC-71")
def test_the_fan_out_build_rounds_are_framework_6_6s_steps():
    six = _section(FRAMEWORK.read_text(encoding="utf-8"), "**Build rounds:**", "\n\n")
    spec = re.findall(r"^(\d+)\. (.+)$", six, re.MULTILINE)
    runbook = _section((REPO / "docs" / "runbooks" / "fan-out.md").read_text(encoding="utf-8"), "## Build rounds", "\n## ")
    rows = [tuple(c.strip() for c in ln.strip("|").split("|")[:2]) for ln in runbook.splitlines() if re.match(r"\|\s*\d+\s*\|", ln)]
    assert len(spec) == 7, spec
    assert _steps(rows) == _steps(spec), "fan-out.md § Build rounds must be FRAMEWORK §6.6's steps, in its order and with its numbers"
