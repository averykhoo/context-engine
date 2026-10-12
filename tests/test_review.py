"""Design review and the residual-risk register (CE-23, FRAMEWORK P17, P18, §5.2, §7.4):
the promotion refusal above the threshold, the move on close, G-W12 and G-W13, and the handover."""

import json
import re
from pathlib import Path

import pytest

import context_engine
from context_engine import review as R
from context_engine.cli import main
from context_engine.errors import Refusal
from context_engine.working import Engine

from conftest import _toml
from test_working import ACTOR, CONFIG, LEDGER, NOTE, TODAY, kw

REPO = Path(__file__).resolve().parents[1]
RUNBOOK = REPO / "docs" / "runbooks" / "manual-mode.md"
TRIGGERS = ["record-kind", "guard", "write-op", "git-loss", "long-lived", "shipped"]
GOOD = """affects: the building session, the next session, every deployed repo
- eliminated: two writers lose each other's change | rung: eliminate
- reduced: a stale read under the lock | rung: reduce | control: the re-read inside store.set
- residual: a dead process holds the lock | rung: individual | why: the OS owns the lock file | control: runbook § lock
- residual: an actor is misattributed | rung: collective | why: an actor is self-declared | control: G-W7
F: housekeeping checks the lock each session
A: a markdown file, fixed by hand
M: one format, written by one function
E: one runbook section"""


def _config(register="docs/invariants.md"):
    kinds = {k: dict(v) for k, v in CONFIG["kinds"].items()}
    for name in ("task", "question"):
        kinds[name]["types"] = {**kinds[name]["types"], "review": "list"}
    working = {**CONFIG["working"], "review_triggers": TRIGGERS}
    if register:
        working["register"] = register
    return {**CONFIG, "kinds": kinds, "working": working}


def _repo(tmp_path, register="docs/invariants.md"):
    (tmp_path / "context.toml").write_text(_toml(_config(register)), encoding="utf-8")
    (tmp_path / "ledger.md").write_text(LEDGER, encoding="utf-8")
    (tmp_path / "HANDOFF.md").write_text(NOTE.format(key="2026-10-07b"), encoding="utf-8")
    e = Engine(tmp_path, today=lambda: TODAY)
    return e, e.session_start(actor=ACTOR)


@pytest.fixture
def eng(tmp_path):
    return _repo(tmp_path)


def _reviewed(e, key, text=GOOD, review="[write-op, long-lived]"):
    rid = e.new("task", "Reviewed work", **kw(key)).id
    e.set(rid, {"review": review}, **kw(key))
    if text is not None:
        e.section(rid, R.SECTION, text, **kw(key))
    return rid


def _guards(e, guard):
    return [f for f in e.lint() if f.guard == guard]


# -- (a) promotion to NOW refuses an unready review -------------------------------------------


@pytest.mark.criterion("AC-26")
@pytest.mark.parametrize(
    "text, reason",
    [
        (None, "there is no `## Design review` section"),
        (R.TEMPLATE, "the template's placeholder text is still there"),
        (GOOD.replace("M: one format, written by one function\n", ""), "no `M:` line"),
        (GOOD.replace(" | control: runbook § lock", ""), "has no `control:`"),
        (GOOD.replace("affects: the building session, the next session, every deployed repo\n", ""), "no `affects:` line"),
        (GOOD.replace(" | rung: collective", ""), "has no rung"),
        (GOOD.replace("- residual: an actor", "- leftover: an actor"), "not one of eliminated, reduced, residual"),
    ],
    ids=["no-section", "placeholder", "no-M", "residual-without-control", "no-affects", "no-rung", "bad-class"],
)
def test_promote_to_now_refuses_a_task_above_the_threshold_without_a_ready_review(eng, text, reason):
    e, key = eng
    rid = _reviewed(e, key, text)
    with pytest.raises(Refusal) as r:
        e.promote(rid, "NOW", **kw(key))
    assert reason in r.value.message
    assert "task section" in r.value.remedy and "manual-mode.md" in r.value.remedy
    assert e.store.get(rid).doc.get("pri") == "LATER"  # nothing written


@pytest.mark.criterion("AC-26")
def test_promote_allows_a_ready_review_no_review_field_and_any_tier_below_now(eng):
    e, key = eng
    unready = _reviewed(e, key, None)
    assert e.promote(unready, "NEXT", **kw(key)) == f"{unready}: LATER -> NEXT"  # only NOW is gated
    plain = e.new("task", "Below the threshold", **kw(key)).id
    assert e.promote(plain, "NOW", **kw(key)) == f"{plain}: LATER -> NOW"  # no `review`: no ceremony (P8)
    e.promote(plain, "LATER", **kw(key))
    ready = _reviewed(e, key)
    assert e.promote(ready, "NOW", **kw(key)) == f"{ready}: LATER -> NOW"


@pytest.mark.criterion("AC-26")
def test_a_review_trigger_outside_the_configured_list_is_refused(eng):
    e, key = eng
    rid = e.new("task", "T", **kw(key)).id
    with pytest.raises(Refusal) as r:
        e.set(rid, {"review": "[guard, big]"}, **kw(key))
    assert "'big'" in r.value.message and "long-lived" in r.value.remedy
    assert e.store.get(rid).doc.get("review") is None


# -- (b) close moves the residuals into the register, once ----------------------------------


@pytest.mark.criterion("AC-27")
def test_close_files_each_residual_once_and_a_reclose_adds_no_duplicate(eng):
    e, key = eng
    rid = _reviewed(e, key)
    out = e.close(rid, "done", **kw(key))
    assert out.endswith("residuals filed as INV-1, INV-2")
    reg = e.root / "docs/invariants.md"
    es = R.entries(reg.read_text(encoding="utf-8"))
    assert [(x.id, x.risk) for x in es] == [("INV-1", "a dead process holds the lock"), ("INV-2", "an actor is misattributed")]
    assert es[0].fields == {"affects": "the building session, the next session, every deployed repo", "why not eliminated": "the OS owns the lock file", "control": "individual: runbook § lock", "from": f"{rid}, session {key}"}
    e.reopen(rid, "one more thing", **kw(key))
    assert "residuals filed" not in e.close(rid, "done again", **kw(key))
    assert [x.id for x in R.entries(reg.read_text(encoding="utf-8"))] == ["INV-1", "INV-2"]
    log = [json.loads(ln) for ln in (e.root / "ops.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [(x["op"], x["id"], x["fields"]) for x in log if x["op"] == "register.append"] == [("register.append", rid, ["INV-1", "INV-2"])]
    other = _reviewed(e, key, GOOD.replace("an actor is misattributed", "a third risk"))
    assert e.close(other, "done", **kw(key)).endswith("residuals filed as INV-3, INV-4")  # the same text from another task is its own entry
    assert _guards(e, "G-W13") == []


@pytest.mark.criterion("AC-27")
def test_close_refuses_residuals_with_no_register_and_an_unready_review(tmp_path):
    e, key = _repo(tmp_path, register=None)
    rid = _reviewed(e, key)
    with pytest.raises(Refusal) as r:
        e.close(rid, "done", **kw(key))
    assert "no register is configured" in r.value.message and "register = " in r.value.remedy
    broken = _reviewed(e, key, GOOD.replace("E: one runbook section", ""))
    with pytest.raises(Refusal) as r:
        e.close(broken, "done", **kw(key))
    assert "no `E:` line" in r.value.message
    assert {e.store.get(x).doc.get("state") for x in (rid, broken)} == {"open"}
    no_residual = _reviewed(e, key, "\n".join(ln for ln in GOOD.splitlines() if not ln.startswith("- residual")))
    assert e.close(no_residual, "done", **kw(key)) == f"{no_residual}: closed (done)"


# -- (c) G-W12 and G-W13 at rest --------------------------------------------------------------


def _hand_edit(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert text.count(old) == 1, old
    path.write_text(text.replace(old, new), encoding="utf-8")


@pytest.mark.criterion("AC-28")
def test_g_w12_reports_a_now_item_whose_review_was_broken_by_hand(eng):
    e, key = eng
    rid = _reviewed(e, key)
    e.promote(rid, "NOW", **kw(key))
    assert _guards(e, "G-W12") == []
    _hand_edit(e.store.find(rid), "F: housekeeping checks the lock each session\n", "")
    fails = _guards(e, "G-W12")
    assert len(fails) == 1 and rid in fails[0].message and "no `F:` line" in fails[0].message
    e.promote(rid, "LATER", **kw(key))
    assert _guards(e, "G-W12") == []  # below NOW it is not yet owed


@pytest.mark.criterion("AC-28")
def test_g_w13_reports_a_residual_missing_from_the_register_and_a_malformed_entry(eng):
    e, key = eng
    rid = _reviewed(e, key)
    e.close(rid, "done", **kw(key))
    reg = e.root / "docs/invariants.md"
    assert _guards(e, "G-W13") == []
    good = reg.read_text(encoding="utf-8")
    _hand_edit(reg, "## INV-2: an actor is misattributed", "## INV-2: an actor was renamed by hand")
    fails = _guards(e, "G-W13")
    assert len(fails) == 1 and "'an actor is misattributed'" in fails[0].message and rid in fails[0].message
    reg.write_text(good.replace("## INV-2:", "## INV-1:"), encoding="utf-8")
    assert [f.message for f in _guards(e, "G-W13")] == ["INV-1 is used by two entries"]
    reg.write_text(good.replace("- **why not eliminated:** the OS owns the lock file\n", ""), encoding="utf-8")
    assert [f.message for f in _guards(e, "G-W13")] == ["INV-1 has no `why not eliminated:` line"]


# -- (d) the handover: the engine's register ships with it -------------------------------------


@pytest.mark.criterion("AC-29")
def test_register_show_engine_reads_the_packaged_register(eng, capsys):
    e, key = eng
    pkg = R.packaged()
    assert pkg.parent == Path(context_engine.__file__).parent and pkg.name == "REGISTER.md" and pkg.exists()
    ids = re.findall(r"^## (INV-\d+):", pkg.read_text(encoding="utf-8"), flags=re.MULTILINE)
    assert main(["--root", str(e.root), "register", "show", "--engine"]) == 0
    out = capsys.readouterr().out
    assert out.startswith(f"register engine {context_engine.__version__}: {len(ids)} residual risk")
    assert all(f"\n{i}: " in out for i in ids)
    rid = _reviewed(e, key)
    e.close(rid, "done", **kw(key))
    assert main(["--root", str(e.root), "register", "show"]) == 0
    mine = capsys.readouterr().out
    assert mine.startswith("register docs/invariants.md: 2 residual risks") and "INV-2: an actor is misattributed" in mine
    assert "control: individual: runbook § lock" in mine


@pytest.mark.criterion("AC-29")
def test_orient_points_at_the_engine_register_in_a_foreign_repo_only(eng):
    e, key = eng
    n = len(R.entries(R.packaged().read_text(encoding="utf-8")))
    out = e.orient(key)
    assert f"## Engine register\nEngine register ({context_engine.__version__}): {n} residual risks, `context-engine register show --engine`" in out
    assert len(out.encode()) <= e.w.orient_max_bytes
    assert "## Engine register" not in Engine(REPO).orient()  # the engine's own repo is not foreign


def test_register_show_without_a_register_refuses_with_its_remedy(tmp_path):
    e, _ = _repo(tmp_path, register=None)
    with pytest.raises(Refusal) as r:
        e.register_show()
    assert "--engine" in r.value.remedy


def test_the_runbook_carries_the_review_template_verbatim():
    """One template (P18 E): the runbook's block is the one the placeholder check knows."""
    assert R.TEMPLATE in RUNBOOK.read_text(encoding="utf-8").replace("\r\n", "\n")
