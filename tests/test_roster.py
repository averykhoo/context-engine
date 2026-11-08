"""The agent roster (CE-39, FRAMEWORK §6.6): every role the session delegates is defined in the
framework, one table row each, and no row is left without what it runs as, its model, what it
writes and what it returns. The arbiter is the one role on `fable`, as one agent; a scout that
must persist is not `Explore`; the housekeeping agent works only through the `hk_` operations.
The kit ships the roster as this text, not as named agents (DEC-97).

Not checked: whether a row's wording is right (the review does that), or that a session follows
it (prompts are not read)."""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
FRAMEWORK = REPO / "docs" / "framework" / "FRAMEWORK.md"
COLUMNS = ["Role", "Runs as", "Model", "Writes", "Returns"]
ROLES = [
    "coordinator", "task owner", "builder, fixer", "verifier", "adversarial reviewer", "scout, auditor",
    "ranking agent", "watcher", "install trial", "`.scratch/` sweep auditor", "housekeeping agent", "arbiter",
]


def roster() -> tuple[list[str], dict[str, dict[str, str]]]:
    text = FRAMEWORK.read_text(encoding="utf-8").replace("\r\n", "\n")
    six = text[text.index("### 6.6 ") : text.index("\n### ", text.index("### 6.6 ") + 1)]
    block = six[six.index("**The roster:**") :]
    lines = [ln for ln in block.split("\n\n", 2)[1].splitlines() if ln.startswith("|")]
    head = [c.strip() for c in lines[0].strip("|").split("|")]
    rows = {}
    for ln in lines[2:]:
        cells = [c.strip() for c in ln.strip("|").split("|")]
        rows[cells[0]] = dict(zip(head, cells))
    return head, rows


@pytest.mark.criterion("AC-113")
def test_the_roster_defines_every_delegated_role_with_every_column_filled():
    head, rows = roster()
    assert head == COLUMNS, head
    assert list(rows) == ROLES, f"FRAMEWORK §6.6's roster must hold one row per role, in this order: {ROLES}; it has {list(rows)}"
    empty = [(role, col) for role, row in rows.items() for col in COLUMNS if not row.get(col)]
    assert not empty, f"a roster row leaves a column empty: {empty}"


@pytest.mark.criterion("AC-113")
def test_the_roster_keeps_fable_to_the_arbiter_explore_to_a_scout_that_need_not_persist_and_hk_to_its_tools():
    _, rows = roster()
    fable = [role for role, row in rows.items() if "fable" in row["Model"]]
    assert fable == ["arbiter"], f"only the arbiter runs on `fable` (the rule above the roster): {fable}"
    assert "never a fan-out" in rows["arbiter"]["Runs as"], rows["arbiter"]
    assert rows["arbiter"]["Model"].startswith("`fable` where the owner asked for it"), "the arbiter is on `fable` only where the owner asked for it"
    explore = [role for role, row in rows.items() if "`Explore`" in row["Runs as"]]
    assert explore == ["scout, auditor"] and "cannot persist" in rows["scout, auditor"]["Runs as"], explore
    hk = rows["housekeeping agent"]
    assert "its only tools are the engine's `hk_` operations" in hk["Runs as"], hk
    # DEC-290: the cell is exactly this, with or without its mechanical-log clause; any other
    # clause (one that widens it: "..., and by hand where they fall short") is red
    assert re.fullmatch(r"only through `hk_` operations(?:, each logged as mechanical)?", hk["Writes"]), hk
    # The watcher writes nothing, and a push is among what it may NOT do: a cell that only mentions
    # a push ("nothing but the fix it pushes when a run is red") must fail.
    watcher = rows["watcher"]["Writes"]
    assert re.fullmatch(r"nothing: no (?:[\w-]+, )*[\w-]+ or push", watcher), watcher


HOUSEKEEPER = REPO / ".claude" / "agents" / "housekeeper.md"


@pytest.mark.criterion("AC-203")
def test_this_repos_housekeeping_agent_names_only_hk_tools():
    """This repo's tier-1 housekeeping agent (CE-12, DEC-302, DEC-306) works only through the
    `hk_` operations (FRAMEWORK §6.11): its frontmatter has no key that could widen it (a missing
    `tools` inherits every tool; `mcpServers` adds servers), and every tool it names is an `hk_`
    operation the engine has, `hk_comment` among them. The kit ships no such file (DEC-97)."""
    from ruamel.yaml import YAML

    from context_engine import ops

    text = HOUSEKEEPER.read_text(encoding="utf-8").replace("\r\n", "\n")
    assert text.startswith("---\n"), text[:40]
    front = YAML(typ="safe").load(text[4 : text.index("\n---\n", 4)])
    assert set(front) == {"name", "description", "tools", "model"}, sorted(front)
    assert front["name"] == "housekeeper" and front["model"] == "haiku", front
    raw = front["tools"]
    tools = [t.strip() for t in (raw.split(",") if isinstance(raw, str) else raw or []) if str(t).strip()]
    assert tools, raw
    for t in tools:
        m = re.fullmatch(r"mcp__context-engine__(hk_\w+)", t)
        assert m and m.group(1) in ops.OPS, (t, sorted(o for o in ops.OPS if o.startswith("hk_")))
    assert "mcp__context-engine__hk_comment" in tools, tools
