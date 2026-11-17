"""`record waive` (CE-239, DEC-347, AC-212): one exact text one guard fails, signed off in one stamped append-only record,
as a `waived:` amendment backed by a `waive` op line; lint G-D3 skips it there, on the lines up to the entry only, and
G-D10 fails an entry the op did not write."""

import datetime as dt
import json

import pytest

from context_engine import okf
from context_engine.cli import main
from context_engine.errors import Refusal
from context_engine.working import Engine

from conftest import ASK_BODY, _toml
from test_decisions import CONFIG as DECISIONS_CONFIG

S, ACTOR = "2026-11-17a", "claude-code/test"
W = {"session": S, "actor": ACTOR}
CONFIG = {**DECISIONS_CONFIG, "kinds": {**DECISIONS_CONFIG["kinds"], "story": {**DECISIONS_CONFIG["kinds"]["story"], "prefix": "S"}}}  # `S-3` is a series id, as in adhoc
FORMULA = "(M-4)(S-3) >= 6"
BODY = f"**Finding.** Counting gives\n{FORMULA}, so five phones need nine talkers.\n\nS-7 stands alone.\n"
REASON = "a formula, not citations"
OWNED = {"actor": "owner", "decision_status": "BUILT"}


def config(tmp_path, **guards):
    (tmp_path / "context.toml").write_text(_toml({**CONFIG, "guards": {"stories": "story", **guards}}), encoding="utf-8")
    return Engine(tmp_path, today=lambda: dt.date(2026, 11, 17))


def build(tmp_path, bodies, amendments=()):
    """A seed decision D-1, then one decision per body (D-2, ...), written while G-D3 is off (they hold reds lint now fails),
    and the amendments (id, text) the same way; the engine returned has G-D3 on."""
    e = config(tmp_path, off=["G-D3"])
    e.record_new("decision", "Seed", "Seed.\n", OWNED, **W)
    for body in bodies:
        e.record_new("decision", "Subject", body, OWNED, **W)
    for rid, text in amendments:
        e.amend(rid, text, **W)
    return config(tmp_path)


@pytest.fixture
def waiving(tmp_path):
    e = build(tmp_path, [BODY])
    assert {m.split(": names ")[1].split(",")[0] for m in g_d3(e, "D-2")} >= {"S-3", "S-7"}
    return e


def g_d3(e, rid=None):
    return [f.message for f in e.lint() if f.guard == "G-D3" and (rid is None or f.path.endswith(path_of(e, rid).name))]


def g_d10(e):
    return [f for f in e.lint() if f.guard == "G-D10"]


def files(root) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file() and ".context" not in p.parts}


def ops(e):
    return [json.loads(ln) for ln in (e.root / "ops.jsonl").read_text(encoding="utf-8").splitlines()]


def path_of(e, rid):
    return e.store.get(rid).path


def waived_lines(e, rid):
    return [(n, ln) for n, ln in enumerate(path_of(e, rid).read_text(encoding="utf-8").split("\n"), 1) if "waived:" in ln]


# -- the waiver signs off one text, for one guard, in one record ---------------------------------


@pytest.mark.criterion("AC-212")
def test_a_waiver_signs_off_one_exact_text_one_guard_in_one_record(waiving):
    e = waiving
    stamp = e.store.get("D-2").doc.get("body_sha")
    reply = e.waive("D-2", "G-D3", FORMULA, REASON, **W)
    assert reply == f"D-2: waived G-D3 on {FORMULA!r} (1 in the body above it); `waived:` logged under ## Amendments; G-D3 left in D-2: 1"
    text = path_of(e, "D-2").read_text(encoding="utf-8")
    assert text.endswith(f'- **{S} ({ACTOR}):** waived: G-D3 x1 (+15) "{FORMULA}" because: {REASON}\n')
    assert e.store.get("D-2").doc.get("body_sha") == stamp
    last = ops(e)[-1]
    assert (last["op"], last["id"], last["guard"], last["text"], last["fields"]) == ("waive", "D-2", "G-D3", FORMULA, ["body"])
    left = g_d3(e, "D-2")
    assert len(left) == 1 and "names S-7" in left[0], left  # S-7 stays red; the formula and the entry's echo of it do not
    assert g_d10(e) == []
    assert okf.waivers(text)[0].line == len(text.split("\n")) - 1  # the entry's line number is lint's: the file's last line


@pytest.mark.criterion("AC-212")
def test_a_waiver_never_covers_text_added_after_it(waiving):
    e = waiving
    e.waive("D-2", "G-D3", FORMULA, REASON, **W)
    before = files(e.root)
    with pytest.raises(Refusal, match="names S-3"):  # the write-time twin: a new line repeating the text is a new red
        e.amend("D-2", f"Again: {FORMULA}.", **W)
    assert files(e.root) == before
    path = path_of(e, "D-2")
    text = path.read_text(encoding="utf-8")
    path.write_text(text + f"\n- **2026-11-17b (x/y):** again {FORMULA}\n", encoding="utf-8")
    again = len(text.split("\n")) + 1  # the blank line, then the new amendment
    s7 = next(n for n, ln in enumerate(text.split("\n"), 1) if ln.startswith("S-7"))
    assert sorted(int(m.split(":")[0].removeprefix("line ")) for m in g_d3(e, "D-2")) == [s7, again]  # the new line is red; the entry and what it covers are not
    assert any(m.startswith(f"line {again}: names S-3") for m in g_d3(e, "D-2"))
    assert g_d10(e) == []  # the entry is still valid: it only covers what is above it


@pytest.mark.criterion("AC-212")
def test_a_waiver_covers_only_its_own_record(tmp_path):
    e = build(tmp_path, [BODY, BODY])
    e.waive("D-2", "G-D3", FORMULA, REASON, **W)
    assert not any("names S-3" in m for m in g_d3(e, "D-2"))
    assert any("names S-3" in m for m in g_d3(e, "D-3"))


@pytest.mark.criterion("AC-212")
def test_a_waiver_covers_an_earlier_amendment_and_every_occurrence_above_it(tmp_path):
    body = BODY + f"\nAnd once more, {FORMULA}.\n"
    e = build(tmp_path, [body], amendments=[("D-2", f"Note: {FORMULA}.")])
    assert sum("names S-3" in m for m in g_d3(e, "D-2")) == 3
    reply = e.waive("D-2", "G-D3", FORMULA, REASON, **W)
    assert "(3 in the body above it)" in reply and "x3" in path_of(e, "D-2").read_text(encoding="utf-8")
    assert not any("names S-3" in m for m in g_d3(e, "D-2"))
    assert g_d10(e) == []


# -- what `record waive` refuses ---------------------------------------------------------------


def _off(e):
    return config(e.root, off=["G-D3"])


def _unstamp(e):
    path = path_of(e, "D-2")
    path.write_text("".join(ln for ln in path.read_text(encoding="utf-8").splitlines(True) if not ln.startswith("body_sha:")), encoding="utf-8")
    return e


REFUSALS = [
    ("D-2", "G-D3", "(M-5)", REASON, None, "is not in D-2's body", "not from lint's line"),
    ("D-2", "G-D4", FORMULA, REASON, None, "G-D4 cannot be waived", "G-D3"),
    ("D-2", "G-X9", FORMULA, REASON, None, "G-X9 cannot be waived", "G-D3"),
    ("D-2", "G-D3", "five phones", REASON, None, "fails nothing", "a waiver signs off only a text the guard fails"),
    ("ASK-1", "G-D3", FORMULA, REASON, None, "replaced record", "record waive"),
    ("D-2", "G-D3", f"{FORMULA}\nmore", REASON, None, "each one line", "one text at a time"),
    ("D-2", "G-D3", FORMULA, "", None, "no reason", "--reason"),
    ("D-2", "G-D3", FORMULA, "why\nnot", None, "each one line", "one text at a time"),
    ("D-2", "G-D3", " ", REASON, None, "an empty waived text", "copied from the record"),
    ("D-2", "G-D3", FORMULA, REASON, _off, "is off here", "turn it on"),
    ("D-2", "G-D3", FORMULA, "because S-9", None, "the waiver's own line would add line", "Nothing was written"),
    ("D-2", "G-D3", FORMULA, REASON, _unstamp, "is not stamped yet", "record stamp"),
]


@pytest.mark.criterion("AC-212")
@pytest.mark.parametrize("rid,guard,text,reason,arrange,says,remedy", REFUSALS, ids=[f"{i}-{r[5]}" for i, r in enumerate(REFUSALS)])
def test_record_waive_refuses_and_writes_nothing(waiving, rid, guard, text, reason, arrange, says, remedy):
    e = waiving
    e.ask_new("Which way?", body=ASK_BODY, **W)
    if arrange:
        e = arrange(e)
    before = files(e.root)
    with pytest.raises(Refusal) as got:
        e.waive(rid, guard, text, reason, **W)
    assert says in str(got.value) and remedy in got.value.remedy, (str(got.value), got.value.remedy)
    assert files(e.root) == before  # no entry, no op line


# -- lint G-D10 fails a waiver the op did not write -------------------------------------------


def _hand(e, edit):
    """Rewrite the last waived: line of D-2 with ``edit``."""
    path = path_of(e, "D-2")
    lines = path.read_text(encoding="utf-8").split("\n")
    n = waived_lines(e, "D-2")[-1][0]
    lines[n - 1] = edit(lines[n - 1])
    path.write_text("\n".join(lines), encoding="utf-8")


def _log(e, **op):
    with open(e.root / "ops.jsonl", "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({"at": "2026-11-17T00:00:00Z", "session": S, "actor": ACTOR, "op": "waive", "id": "D-2", "path": "", "fields": ["body"], "mechanical": False, **op}) + "\n")


def _copy(e, count):
    path = path_of(e, "D-2")
    entry = waived_lines(e, "D-2")[-1][1]
    path.write_text(path.read_text(encoding="utf-8") + entry.replace("x1", f"x{count}") + "\n", encoding="utf-8")


HAND = [
    ("shape", lambda e: _hand(e, lambda ln: ln.replace(" (+15)", "")), "a `waived:` entry not in the op's shape"),
    ("count", lambda e: _hand(e, lambda ln: ln.replace(" x1 ", " x2 ")), f"waives {FORMULA!r} for G-D3 x2, but the body above it holds it 1 times"),
    ("text", lambda e: _hand(e, lambda ln: ln.replace(f'"{FORMULA}"', '"(S-3)"').replace("(+15)", "(+5)")), f"no `waive` op line of session {S} logs this waiver of '(S-3)' for G-D3"),
    ("guard", lambda e: (_hand(e, lambda ln: ln.replace("G-D3", "G-D4")), _log(e, guard="G-D4", text=FORMULA)), "waives G-D4, which cannot be waived (only G-D3)"),
    ("session key", lambda e: _hand(e, lambda ln: ln.replace(f"**{S} ", "**2026-11-17z ")), f"no `waive` op line of session 2026-11-17z logs this waiver of {FORMULA!r} for G-D3"),  # the key is part of what a waiver covers
    ("copied verbatim", lambda e: _copy(e, 1), f"waives {FORMULA!r} for G-D3 x1, but the body above it holds it 2 times"),  # the first entry's echo counts above the copy
    ("copied with its count fixed", lambda e: _copy(e, 2), f"no `waive` op line of session {S} logs this waiver of {FORMULA!r} for G-D3"),  # one op line backs one entry
]


@pytest.mark.criterion("AC-212")
@pytest.mark.parametrize("name,arrange,says", HAND, ids=[h[0] for h in HAND])
def test_lint_g_d10_fails_a_waiver_not_written_by_the_op(waiving, name, arrange, says):
    e = waiving
    e.waive("D-2", "G-D3", FORMULA, REASON, **W)
    assert g_d10(e) == []
    arrange(e)
    bad = g_d10(e)
    assert len(bad) == 1 and bad[0].path.endswith(path_of(e, "D-2").name), [str(b) for b in bad]
    n = waived_lines(e, "D-2")[-1][0]
    assert bad[0].message == f"line {n}: {says}" or bad[0].message.startswith(f"line {n}: {says}"), bad[0].message
    assert "record waive" in bad[0].remedy
    assert any("names S-3" in m for m in g_d3(e, "D-2"))  # an invalid waiver waives nothing


@pytest.mark.criterion("AC-212")
def test_a_waived_entry_written_by_hand_in_another_record_is_red_and_waives_nothing(tmp_path):
    e = build(tmp_path, [BODY, BODY])
    e.waive("D-2", "G-D3", FORMULA, REASON, **W)
    path = path_of(e, "D-3")
    path.write_text(path.read_text(encoding="utf-8") + f'\n## Amendments\n\n- **{S} ({ACTOR}):** waived: G-D3 x1 (+15) "{FORMULA}" because: {REASON}\n', encoding="utf-8")
    bad = g_d10(e)
    assert len(bad) == 1 and bad[0].path.endswith(path_of(e, "D-3").name) and "no `waive` op line" in bad[0].message, [str(b) for b in bad]
    assert any("names S-3" in m for m in g_d3(e, "D-3"))
    assert not any("names S-3" in m for m in g_d3(e, "D-2"))


# -- the CLI and the MCP tool -----------------------------------------------------------------


@pytest.mark.criterion("AC-212")
def test_record_waive_runs_from_the_cli_and_a_section_sign_round_trips(tmp_path):
    e = build(tmp_path, [BODY, "Detail is in D-1 §9, which has no such section.\n"])
    argv = ["--root", str(tmp_path), "--session", S, "--actor", ACTOR, "record", "waive"]
    assert main([*argv, "D-2", "G-D3", FORMULA, "--reason", REASON]) == 0
    assert f'waived: G-D3 x1 (+15) "{FORMULA}" because: {REASON}' in path_of(e, "D-2").read_text(encoding="utf-8")
    assert any("names no heading of D-1" in m for m in g_d3(e, "D-3"))
    assert main([*argv, "D-3", "G-D3", "D-1 §9", "--reason", "a section of another document"]) == 0
    assert 'waived: G-D3 x1 (+6) "D-1 §9" because: a section of another document' in path_of(e, "D-3").read_text(encoding="utf-8")
    assert g_d3(e, "D-3") == [] and g_d10(e) == []
    assert main([*argv, "D-3", "G-D3", "D-1 §9", "--reason", "again"]) == 2  # nothing left to waive: a refusal exits 2
