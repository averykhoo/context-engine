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
        (GOOD.replace(" | why: the OS owns the lock file", ""), "has no `why:`"),
        ("\n".join(ln for ln in GOOD.splitlines() if not ln.startswith("- ")), "no risk line"),
        (GOOD.replace(" | rung: reduce | control: the re-read", " | control: the re-read"), "has no rung"),
        (GOOD.replace("| rung: collective | why: an actor", "| rung: eliminate | why: an actor"), "is at rung eliminate, so it is not residual"),
        (GOOD.replace(" | control: G-W7", " | control: G-W7 | owner: nobody"), "unknown field 'owner'"),
        (GOOD.replace("- eliminated: two writers lose each other's change | rung: eliminate", "- eliminated:"), "a eliminated line names no risk"),
        (GOOD.replace("| rung: reduce | control: the re-read", "| rung: individual | control: the re-read"), "controlled only at rung individual, so it is residual"),
    ],
    ids=["no-section", "placeholder", "no-M", "residual-without-control", "no-affects", "no-rung", "bad-class",
         "residual-without-why", "no-risk-line", "reduced-without-rung", "residual-at-eliminate", "unknown-field", "empty-risk", "reduced-at-individual"],
)
def test_promote_to_now_refuses_a_task_above_the_threshold_without_a_ready_review(eng, text, reason):
    e, key = eng
    rid = _reviewed(e, key, text)
    with pytest.raises(Refusal) as r:
        e.promote(rid, "NOW", **kw(key))
    assert reason in r.value.message
    assert "manual-mode.md" in r.value.remedy
    assert e.store.get(rid).doc.get("pri") == "LATER"  # nothing written
    command = re.search(r"`task (section .*?)`", r.value.remedy).group(1).replace('"<text>"', '"F: x"')
    assert main(["--root", str(e.root), "--session", key, "--actor", ACTOR, "task", *_split(command)]) == 0  # the remedy runs as written


@pytest.mark.criterion("AC-26")
def test_the_promote_refusal_names_every_reason(eng):
    e, key = eng
    text = GOOD.replace("M: one format, written by one function\n", "").replace("E: one runbook section", "") + "\nA: <how it is read and fixed without the engine>"
    rid = _reviewed(e, key, text)
    with pytest.raises(Refusal) as r:
        e.promote(rid, "NOW", **kw(key))
    assert all(x in r.value.message for x in ("the template's placeholder text is still there", "no `M:` line", "no `E:` line"))


@pytest.mark.criterion("AC-26")
def test_set_and_section_on_a_now_item_refuse_an_unready_review(eng):
    """The gate on NOW holds for writes after the promotion, not only for the promotion."""
    e, key = eng
    plain = e.new("task", "Promoted before it was reviewed", **kw(key)).id
    e.promote(plain, "NOW", **kw(key))
    with pytest.raises(Refusal) as r:
        e.set(plain, {"review": "[guard]"}, **kw(key))
    assert "there is no `## Design review` section" in r.value.message and "manual-mode.md" in r.value.remedy
    assert e.store.get(plain).doc.get("review") is None
    e.section(plain, R.SECTION, GOOD, **kw(key))
    e.set(plain, {"review": "[guard]"}, **kw(key))  # a ready review: allowed
    with pytest.raises(Refusal) as r:
        e.section(plain, R.SECTION, GOOD.replace("A: a markdown file, fixed by hand\n", ""), **kw(key))
    assert "no `A:` line" in r.value.message
    assert "A: a markdown file" in e.store.get(plain).doc.body  # nothing written
    e.section(plain, "Traps", "- one", **kw(key))  # another section of a ready item: allowed
    e.promote(plain, "LATER", **kw(key))
    e.section(plain, R.SECTION, "affects: x", **kw(key))  # below NOW the review is not yet owed
    assert _guards(e, "G-W12") == []


@pytest.mark.criterion("AC-27")
def test_review_cannot_be_unset_while_the_design_review_lists_residuals(eng):
    e, key = eng
    rid = _reviewed(e, key)
    for how in ({"unset": ("review",)}, {"raw": {"review": "[]"}}):
        with pytest.raises(Refusal) as r:
            e.set(rid, how.get("raw", {}), unset=how.get("unset", ()), **kw(key))
        assert "2 residual risks" in r.value.message and "task section" in r.value.remedy
        assert e.store.get(rid).doc.get("review") == ["write-op", "long-lived"]
    assert e.close(rid, "done", **kw(key)).endswith("residuals filed as INV-1, INV-2")
    none = _reviewed(e, key, "\n".join(ln for ln in GOOD.splitlines() if not ln.startswith("- residual")))
    assert e.set(none, {}, unset=("review",), **kw(key)) == f"{none}: set review"  # nothing to file: allowed


def _split(command: str) -> list[str]:
    import shlex

    return shlex.split(command)


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
    _hand_edit(reg, "## INV-2: an actor is misattributed", "## INV-2: an  actor is\tmisattributed")
    e.reopen(rid, "again", **kw(key))
    assert "residuals filed" not in e.close(rid, "done", **kw(key))  # whitespace does not make it a new risk
    assert _guards(e, "G-W13") == []


@pytest.mark.criterion("AC-27")
def test_an_inv_id_deleted_from_the_register_is_not_handed_out_again(eng):
    e, key = eng
    first = _reviewed(e, key)
    e.close(first, "done", **kw(key))
    reg = e.root / "docs/invariants.md"
    reg.write_text(reg.read_text(encoding="utf-8").split("\n## INV-2:")[0] + "\n", encoding="utf-8")  # the last entry cut by hand
    second = _reviewed(e, key, GOOD.replace("a dead process", "a second process").replace("an actor is", "an actor was"))
    assert e.close(second, "done", **kw(key)).endswith("residuals filed as INV-3, INV-4")
    assert [x.id for x in R.entries(reg.read_text(encoding="utf-8"))] == ["INV-1", "INV-3", "INV-4"]


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


# -- (b2) close states the residual risk of any item, and the register starts on first use (CE-120) --

STATED = "the register is edited by hand | rung: individual | why: plain git cannot be refused | control: G-W13 | affects: the next session"


@pytest.mark.criterion("AC-127")
def test_close_files_a_stated_residual_of_an_unreviewed_item_creating_the_register(eng, capsys):
    """Adhoc AAR entry 33: no close had ever filed a residual, and `register show` refused. Any
    item's close states one (`--residual`), it is filed once as the next INV-n in a register made
    on first use, and the item's Log records the answer, `none` included."""
    e, key = eng
    reg = e.root / "docs/invariants.md"
    assert e.register_show() == "register docs/invariants.md: 0 residual risks (no file yet: the first `task close` that files a residual, from a design review or `--residual`, creates it)"
    rid = e.new("task", "Plain work", **kw(key)).id
    assert main(["--root", str(e.root), "--session", key, "--actor", ACTOR, "task", "close", rid, "-m", "done", "--residual", STATED]) == 0
    assert "residuals filed as INV-1" in capsys.readouterr().out
    [x] = R.entries(reg.read_text(encoding="utf-8"))
    assert (x.id, x.risk) == ("INV-1", "the register is edited by hand")
    assert x.fields == {"affects": "the next session", "why not eliminated": "plain git cannot be refused", "control": "individual: G-W13", "from": f"{rid}, session {key}"}
    assert f"closed: done\n  residual risk: INV-1" in e.store.get(rid).doc.body
    assert e.register_show().startswith("register docs/invariants.md: 1 residual risk\n")
    e.reopen(rid, "again", **kw(key))
    assert "residuals filed" not in e.close(rid, "done", residuals=[STATED], **kw(key))  # filed once
    assert len(R.entries(reg.read_text(encoding="utf-8"))) == 1
    other = e.new("task", "Other work", **kw(key)).id
    assert e.close(other, "done", residuals=["None"], **kw(key)) == f"{other}: closed (done)"
    assert "closed: done\n  residual risk: none" in e.store.get(other).doc.body
    assert _guards(e, "G-W13") == []


@pytest.mark.criterion("AC-127")
@pytest.mark.parametrize(
    "given, reason",
    [
        ([STATED.replace(" | why: plain git cannot be refused", "")], "has no `why:`"),
        ([STATED.replace("rung: individual", "rung: eliminate")], "at rung eliminate"),
        ([STATED.replace(" | affects: the next session", "")], "no `affects:` field"),
        ([STATED.replace("control:", "contrl:")], "unknown field 'contrl'"),
        (["none", STATED], "`--residual none` and a residual risk"),
        ([STATED + "\n- residual: a second risk | rung: reduce | why: w | control: c | affects: a"], "runs over more than one line"),
    ],
)
def test_close_refuses_a_malformed_stated_residual_and_stays_open(eng, given, reason):
    e, key = eng
    rid = e.new("task", "Plain work", **kw(key)).id
    with pytest.raises(Refusal) as r:
        e.close(rid, "done", residuals=given, **kw(key))
    assert reason in r.value.message, r.value.message
    assert e.store.get(rid).doc.get("state") == "open" and not (e.root / "docs/invariants.md").exists()


@pytest.mark.criterion("AC-127")
def test_a_reviewed_close_logs_every_residual_it_files_and_refuses_none(eng):
    """Review of CE-120: `--residual none` on an item whose design review lists residuals logged
    `residual risk: none` while the close filed them. The close refuses that `none`, and its Log
    names every INV id the close files, the review's included, and those a re-close finds
    already in the register."""
    e, key = eng
    rid = _reviewed(e, key)
    with pytest.raises(Refusal) as r:
        e.close(rid, "done", residuals=["none"], **kw(key))
    assert "design review lists 2 residual risks" in r.value.message and "without `--residual none`" in r.value.remedy
    assert e.store.get(rid).doc.get("state") == "open" and not (e.root / "docs/invariants.md").exists()
    assert e.close(rid, "done", **kw(key)).endswith("residuals filed as INV-1, INV-2")
    assert "closed: done\n  residual risk: INV-1, INV-2\n" in e.store.get(rid).doc.body + "\n"
    e.reopen(rid, "one more", **kw(key))
    assert e.close(rid, "again", residuals=[STATED], **kw(key)).endswith("residuals filed as INV-3")
    assert "closed: again\n  residual risk: INV-3; already in the register: INV-1, INV-2\n" in e.store.get(rid).doc.body + "\n"
    e.reopen(rid, "and more", **kw(key))
    e.close(rid, "third", residuals=[STATED], **kw(key))
    assert "closed: third\n  residual risk: already in the register: INV-1, INV-2, INV-3\n" in e.store.get(rid).doc.body + "\n"
    assert _guards(e, "G-W13") == []


@pytest.mark.criterion("AC-127")
def test_a_close_that_states_no_residual_asks_for_one_where_a_register_is_configured(eng, tmp_path):
    e, key = eng
    rid = e.new("task", "Plain work", **kw(key)).id
    out = e.close(rid, "done", **kw(key))
    assert out.startswith(f"{rid}: closed (done); residual risk not stated: say `--residual none`"), out
    assert "manual-mode.md § context-engine task close" in out and "residual risk:" not in e.store.get(rid).doc.body
    (tmp_path / "none").mkdir()
    off, key2 = _repo(tmp_path / "none", register=None)  # no register: nothing to ask about
    plain = off.new("task", "Plain work", **kw(key2)).id
    assert off.close(plain, "done", **kw(key2)) == f"{plain}: closed (done)"
    with pytest.raises(Refusal, match="no register is configured"):
        off.close(off.new("task", "Risky", **kw(key2)).id, "done", residuals=[STATED], **kw(key2))


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
    reg.write_text(good.replace("## INV-2: an actor is misattributed", "## INV-2:"), encoding="utf-8")
    assert "INV-2 names no risk" in [f.message for f in _guards(e, "G-W13")]


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
