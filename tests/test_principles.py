"""The framework's principles (FRAMEWORK §1, P3): numbered from P1 with no gap or repeat, the
ones code and the contract cite keep their numbers, the section table names the range, and P19
makes a green gate the whole release decision (US-20, AC-184), with P7, §3.3 and §7.4 pointing
at it.

Not checked: whether the wording is right (the review does that), or that any repo follows P19:
no lint enforces it yet (CE-206)."""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
FRAMEWORK = REPO / "docs" / "framework" / "FRAMEWORK.md"
# principles cited by number elsewhere (review.py: P17, P18; the contract: P7, P8): renumbering breaks them
PINNED = {
    1: "One home per statement",
    3: "Stable ids",
    7: "Every tracked text component has a schema and a cap",
    8: "Owner attention is the scarcest resource",
    17: "Design for safety",
    18: "Design for maintainability",
    19: "A green gate is the whole release decision",
}
# AC-184's words, as P19 must carry them (bold dropped, whitespace collapsed, lower case)
P19_SAYS = (
    "a green gate is the whole release decision",
    "a check only a human runs",
    "board item to automate",
    "never accepted as a residual",
)


def _text() -> str:
    return FRAMEWORK.read_text(encoding="utf-8").replace("\r\n", "\n")


def _section(text: str, start: str, end: str) -> str:
    i = text.index(start)
    return text[i : text.index(end, i + len(start))]


def _flat(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("**", "")).strip().lower()


def principles(text: str) -> list[tuple[int, str]]:
    """(number, body) for every `**Pn. ` paragraph head in §1, in document order."""
    one = _section(text, "\n## 1. Principles\n", "\n## 2. ")
    heads = list(re.finditer(r"^\*\*P(\d+)\. ", one, re.M))
    ends = [m.start() for m in heads[1:]] + [len(one)]
    return [(int(m.group(1)), one[m.start() : end]) for m, end in zip(heads, ends)]


def test_the_principles_run_from_p1_with_no_gap_or_repeat_and_keep_their_numbers():
    ps = principles(_text())
    numbers = [n for n, _ in ps]
    assert numbers == list(range(1, len(numbers) + 1)), (
        f"FRAMEWORK §1's principles must run P1, P2, ... in order, never renumbered (P3): {numbers}"
    )
    bodies = dict(ps)
    moved = {
        n: title
        for n, title in PINNED.items()
        if not _flat(bodies.get(n, "")).startswith(_flat(f"P{n}. {title}"))
    }
    assert not moved, f"a cited principle lost its number or title (P3): {moved}"


def test_the_section_table_names_every_principle():
    text = _text()
    last = principles(text)[-1][0]
    [row] = [ln for ln in text.splitlines() if ln.startswith("| 1 | Principles | ")]
    assert f"P1 to P{last}:" in row, f"the 'What each section covers' row for §1 must say P1 to P{last}: {row}"


@pytest.mark.criterion("AC-184")
def test_p19_makes_a_green_gate_the_whole_release_decision():
    body = _flat(dict(principles(_text())).get(19, ""))
    missing = [p for p in P19_SAYS if p not in body]
    assert not missing, f"P19 must say each of {P19_SAYS}; it lacks {missing}"
    assert "(p8)" in body and "§6.8" in body, (
        "P19 must leave the owner's permission to push with the owner (P8, §6.8)"
    )


@pytest.mark.criterion("AC-184")
def test_p7_section_3_3_and_section_7_4_point_at_p19():
    text = _text()
    bodies = dict(principles(text))
    where = {
        "P7": bodies.get(7, ""),
        "§3.3": _section(text, "\n### 3.3 ", "\n#### 3.3.1 "),
        "§7.4": _section(text, "\n### 7.4 ", "\n### 7.5 "),
    }
    silent = [k for k, s in where.items() if "(P19)" not in s]
    assert not silent, f"these do not point at P19: {silent}"
