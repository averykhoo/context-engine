"""The manual-mode runbook covers every engine operation, each with its reason (US-11); the
procedures runbook holds every procedure's steps in order, each step naming a real operation and its by-hand
section (US-15)."""

import argparse
import re
from pathlib import Path

import pytest

from context_engine.cli import build

RUNBOOK = Path(__file__).resolve().parents[1] / "docs" / "runbooks" / "manual-mode.md"


def _subparsers(parser: argparse.ArgumentParser) -> dict[str, argparse.ArgumentParser]:
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return dict(action.choices)
    return {}


def cli_parsers() -> dict[str, argparse.ArgumentParser]:
    """Every `context-engine <group> [<op>]` the CLI accepts -> its parser, read from the parser
    itself."""
    out = {}
    for group, gp in _subparsers(build()).items():
        subs = _subparsers(gp)
        out |= {f"context-engine {group} {op}": sp for op, sp in subs.items()} if subs else {f"context-engine {group}": gp}
    return out


def cli_operations() -> list[str]:
    return list(cli_parsers())


def runbook_sections() -> dict[str, str]:
    """`### <heading>` -> its text up to the next heading."""
    text = RUNBOOK.read_text(encoding="utf-8").replace("\r\n", "\n")
    text = re.sub(r"^[ \t]*```.*?^[ \t]*```", "", text, flags=re.MULTILINE | re.DOTALL)  # a `## ` in an example is not a heading
    parts = re.split(r"^(#{2,3} .*)$", text, flags=re.MULTILINE)
    return {parts[i][4:].strip(): parts[i + 1] for i in range(1, len(parts), 2) if parts[i].startswith("### ")}


@pytest.mark.criterion("AC-21")
def test_every_cli_operation_has_a_runbook_section_with_its_reason():
    sections = runbook_sections()
    ops = cli_operations()
    assert len(ops) >= 25, ops  # the parser walk itself must not silently find nothing
    missing = [op for op in ops if op not in sections]
    assert missing == [], f"no `### <op>` section in {RUNBOOK.name} for: {missing}"
    no_why = [op for op in ops if "**Why:**" not in sections[op]]
    assert no_why == [], f"sections without a **Why:** line: {no_why}"


def test_the_lint_section_names_every_guard_id_lint_reports():
    """CE-156: § context-engine coverage marks built "a G-id lint reports (§ lint lists them)",
    so a by-hand run reads § lint for that list; an id it never names (G-D6 was one, CE-141) is
    marked done or unowned by hand while the engine says built. Each id of config.py::LINT_IDS
    is named in bold in § lint, as each of its rules is led."""
    from context_engine.config import LINT_IDS

    lint = runbook_sections()["context-engine lint"]
    assert "**G-D4**" in lint and "**G-W1**" in lint, "the § lint read must find the section's rules"
    unnamed = [i for i in LINT_IDS if f"**{i}**" not in lint]
    assert unnamed == [], f"{RUNBOOK.name} § context-engine lint never names {unnamed} in bold (config.LINT_IDS): give each its rule, or say it checks nothing"


def _orient_titles() -> list[tuple[str, re.Pattern]]:
    """CE-200: each part heading working.py::Engine.orient can emit, in output order, as
    (title as written, a regex for it in the runbook). Read from the source, not a hand list
    (which drifts as the runbook did: CE-121, CE-136, CE-185 each added a part): a part put first
    with `sections.insert(0, ...)` leads, the rest keep source order; an f-string's `{...}`
    placeholders read as a runbook `<...>` (`Banner ({b.key})` -> `Banner (<key>)`)."""
    import inspect

    from context_engine import working

    src = inspect.getsource(working.Engine.orient)
    found = re.findall(r'(sections\.insert\(0, )?Part\((f?)"([^"]*)"', src)
    assert len(found) >= 20, found  # the source walk itself must not silently find nothing (22 on 2026-11-08)
    ordered = [f for f in found if f[0]] + [f for f in found if not f[0]]
    out = []
    for _, is_f, title in ordered:
        pat = "<[^<>]+>".join(re.escape(piece) for piece in re.split(r"\{[^}]*\}", title)) if is_f else re.escape(title)
        out.append((title, re.compile(pat)))
    return out


def _orient_section() -> str:
    return " ".join(runbook_sections()["context-engine orient"].split())  # a heading wrapped across lines still reads whole


def test_the_orient_section_names_every_part_orient_shows():
    """CE-200: a by-hand orient (§ context-engine orient) shows each part the engine's does; seven
    conditional parts (CE-112, CE-116, CE-97, CE-48, CE-6, CE-101, CE-185) were once in the
    engine and nowhere in the runbook. Each heading Engine.orient can emit is named in the section."""
    flat = _orient_section()
    missing = [title for title, pat in _orient_titles() if not pat.search(flat)]
    assert missing == [], f"{RUNBOOK.name} § context-engine orient never names these Engine.orient part headings: {missing}"


def test_the_orient_section_names_the_parts_in_the_order_orient_shows_them():
    """CE-200: the section names the parts in the order orient shows them (each heading's first
    mention), so a by-hand orient puts them in the engine's order. Non-decreasing, not increasing:
    `Top item` and `Top item: <id> <title>` match at the same place."""
    flat = _orient_section()
    seen = [(title, pat.search(flat)) for title, pat in _orient_titles()]
    at = [(title, m.start()) for title, m in seen if m]
    out_of_order = [(a, b) for (a, i), (b, j) in zip(at, at[1:]) if j < i]
    assert out_of_order == [], f"{RUNBOOK.name} § context-engine orient names these part headings out of Engine.orient's order (earlier, later): {out_of_order}"


# -- the procedures runbook: every procedure's steps, in order, in one place (US-15, CE-24) ----

PROCEDURES = RUNBOOK.with_name("procedures.md")
FRAMEWORK = RUNBOOK.parents[1] / "framework" / "FRAMEWORK.md"
MAP_HEADING = "Where each part of FRAMEWORK §6 is done"
PROCEDURE_HEADING = re.compile(r"^(?P<name>.+?) \((?P<refs>§6\.\d+(?:, §6\.\d+)*)\)$")
SECTION_REF = re.compile(r"§ ([A-Z][A-Za-z]*(?: (?:[a-z]+|[A-Z]{2,}))*)")  # `§ Clean close`, `§ Push and CI`
LINK = re.compile(r"\[[^\]]*\]\(([^)#]*)(?:#([^)]*))?\)")
NO_STEPS = ("no steps", "not designed")


def _text(path: Path) -> str:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return re.sub(r"^[ \t]*```.*?^[ \t]*```", "", text, flags=re.MULTILINE | re.DOTALL)


def h2_sections(path: Path) -> dict[str, str]:
    parts = re.split(r"^## (.*)$", _text(path), flags=re.MULTILINE)
    return {parts[i].strip(): parts[i + 1] for i in range(1, len(parts), 2)}


def procedures() -> dict[str, tuple[list[str], str]]:
    """Procedure name -> (the §6.n it cites, its text), from the `## <name> (§6.n, ...)` headings."""
    out = {}
    for heading, body in h2_sections(PROCEDURES).items():
        m = PROCEDURE_HEADING.match(heading)
        if m:
            out[m["name"]] = (re.findall(r"6\.\d+", m["refs"]), body)
    return out


def table_rows(body: str) -> list[list[str]]:
    """The body rows of every table in ``body``: each table's header (the row above its `|---|`
    line) is dropped."""
    rows: list[list[str]] = []
    for ln in body.splitlines():
        if not ln.startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-+:?", c) for c in cells):
            rows.pop()  # the header
        else:
            rows.append(cells)
    return rows


def framework_six() -> dict[str, str]:
    """`6.n` -> the text of FRAMEWORK §6.n."""
    fw = _text(FRAMEWORK)
    six = fw[fw.index("\n## 6. Procedures") : fw.index("\n## 7. ")]
    parts = re.split(r"^### (6\.\d+) .*$", six, flags=re.MULTILINE)
    return {parts[i]: parts[i + 1] for i in range(1, len(parts), 2)}


def framework_items(section: str) -> set[str]:
    """The stable item numbers of one §6 subsection: `1. ...` at the margin, and `**6a. ...**`."""
    return set(re.findall(r"^(\d+)\. ", section, re.MULTILINE)) | set(re.findall(r"\*\*(\d+[a-z])\. ", section))


def slug(heading: str) -> str:
    """GitHub's anchor for a heading."""
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def section_refs(text: str) -> list[str]:
    return SECTION_REF.findall(LINK.sub("", text))


@pytest.mark.criterion("AC-36")
def test_every_framework_procedure_has_a_procedures_section():
    six, have = framework_six(), procedures()
    assert len(six) >= 13 and len(have) >= 9, (list(six), list(have))
    rows = {r[0].split(" ", 1)[0]: r for r in table_rows(h2_sections(PROCEDURES)[MAP_HEADING])}
    missing = [f"§{n}" for n in six if f"§{n}" not in rows]
    assert missing == [], f"{PROCEDURES.name} § {MAP_HEADING} has no row for FRAMEWORK {missing}"
    for ref, (_, steps) in rows.items():
        assert ref[1:] in six, f"the map names {ref}, which FRAMEWORK §6 does not have"
        if steps.startswith(NO_STEPS):
            continue
        names = section_refs(steps)
        assert names, f"the map row for {ref} names no section and does not say `no steps`"
        assert [n for n in names if n not in have] == [], f"the map row for {ref} names a section that is not a procedure: {names}"
    for name, (cited, _) in have.items():
        assert all(c in six for c in cited), f"§ {name} cites {cited}, not all in FRAMEWORK §6"
        assert any(name in section_refs(r[1]) for r in rows.values()), f"§ {name} is not in the map"


@pytest.mark.criterion("AC-36")
def test_every_procedure_step_names_an_existing_operation_and_its_by_hand_section():
    parsers = cli_parsers()
    ops = sorted(parsers, key=len, reverse=True)
    anchors = {slug(h) for h in re.findall(r"^#{2,3} (.*)$", _text(RUNBOOK), flags=re.MULTILINE)}
    have = procedures()
    for name, (_, body) in have.items():
        rows = table_rows(body)
        assert rows, f"§ {name} has no step table"
        for row in rows:
            where = f"§ {name}, step {row[:2]}"
            assert len(row) == 5, f"{where}: a step is `| § | Do | Engine | By hand | Why |`, got {len(row)} cells"
            label, _, engine, by_hand, why = row
            assert re.fullmatch(r"—|\d+[a-z]?(?:–\d+)?", label), f"{where}: bad § label {label!r}"
            assert why and why != "—", f"{where}: no Why"
            named = []
            for span in re.findall(r"`(context-engine [^`]*)`", engine):
                op = next((o for o in ops if span == o or span.startswith(o + " ")), None)
                assert op, f"{where}: `{span}` is not an engine operation"
                flags = re.findall(r"(?<![^\s])(--?[A-Za-z][\w-]*)", span[len(op) :])
                stale = [f for f in flags if f not in parsers[op]._option_string_actions]
                assert stale == [], f"{where}: `{op}` has no option {stale}"
                named.append(op)
                anchor = slug(op)
                assert f"manual-mode.md#{anchor})" in by_hand, f"{where}: names `{op}` but its By hand does not link manual-mode.md#{anchor}"
            refs = section_refs(engine)
            assert engine.startswith("—") or named or refs, f"{where}: Engine is neither `—` (with an optional note), an operation nor a § reference"
            assert [r for r in section_refs(engine + " " + by_hand) if r not in have] == [], f"{where}: a § reference names no procedure"
    for target, anchor in LINK.findall(_text(PROCEDURES)):
        if target == "manual-mode.md" and anchor:
            assert anchor in anchors, f"{PROCEDURES.name} links manual-mode.md#{anchor}, which is not a heading there"


@pytest.mark.criterion("AC-36")
def test_every_framework_step_a_procedure_cites_exists():
    six = framework_six()
    for name, (cited, body) in procedures().items():
        labels = [r[0] for r in table_rows(body) if r[0] != "—"]
        if not labels:
            continue
        assert len(cited) == 1, f"§ {name} labels its steps but cites {cited}: which subsection do they number?"
        items = framework_items(six[cited[0]])
        for label in labels:
            lo, _, hi = label.partition("–")
            want = [str(i) for i in range(int(lo), int(hi) + 1)] if hi else [lo]
            assert set(want) <= items, f"§ {name} step {label}: FRAMEWORK §{cited[0]} has items {sorted(items)}"


@pytest.mark.criterion("AC-36")
def test_procedures_runbook_names_every_mcp_tool_its_naming_rule_misses():
    """procedures.md says the MCP tool for `context-engine <group> <verb>` is `<group>_<verb>`: every
    operation that breaks that rule must be named there, or an MCP-only agent looks for a tool
    that does not exist."""
    from context_engine import ops
    from context_engine.cli import CLI_OPS

    text = _text(PROCEDURES)
    assert set(CLI_OPS.values()) <= set(ops.OPS), "a CLI verb maps to no operation, so to no MCP tool"
    odd = {k: v for k, v in CLI_OPS.items() if v != "_".join(p for p in k if p)}
    assert odd, "the walk found no exception: has CLI_OPS changed shape?"
    unnamed = [f"{' '.join(p for p in k if p)} -> {v}" for k, v in odd.items() if f"mcp__context-engine__{v}" not in text]
    assert unnamed == [], f"{PROCEDURES.name} does not name these MCP tools: {unnamed}"
