"""CE-68 sabotage table (DEC-11): break what each guard the phrasing sweep added protects; every
run must go red, and red for the reason the row names. The checker is CE-49's
(`tools/sabotage_ce49.py::run`).

Run from the repo root: `<interpreter> tools/sabotage_ce68.py [row-number ...]` (no numbers: every
row). It restores every file it touches, byte for byte. The patterns are exact source text from
2026-10-13e; when the text moves, a pattern stops matching and the script stops with an
AssertionError naming it.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from sabotage_ce49 import run  # noqa: E402

FW = "docs/framework/FRAMEWORK.md"
KIT = "src/context_engine/kit/README.md"
GD = "src/context_engine/guards.py"
WORD = "test_no_living_framework_text_says_ritual"
ALIAS = "test_g_d12_a_frozen_map_under_the_old_names_still_owns_what_dec_39_renamed"

# (file, pattern, replacement, pytest selection, the tests that must fail (and only those), reason)
S = [
 # the old word comes back in living text: in the spec, and in a kit file
 (FW, "\n## 6. Procedures\n", "\n## 6. Rituals\n", "tests/test_kit.py -k says_ritual", [WORD], "still says ritual"),
 (KIT, "- `procedures.md`: the order of every procedure", "- `rituals.md`: the order of every procedure", "tests/test_kit.py -k says_ritual", [WORD], "still says ritual"),
 # a frozen map's old column and old component names stop counting
 (GD, '"procedure": (("Procedure", "Ritual"), "§")', '"procedure": (("Procedure",), "§")', "tests/test_guards.py -k old_names_still_owns", [ALIAS], 'reds(e, "G-D12") == []'),
 (GD, '    "Residual-risk register": ("Invariants",),\n', '    "Residual-risk register": (),\n', "tests/test_guards.py -k old_names_still_owns", [ALIAS], 'reds(e, "G-D12") == []'),
 (GD, '    "Non-functional requirements (NFRs)": ("Law / NFRs",),\n', '    "Non-functional requirements (NFRs)": (),\n', "tests/test_guards.py -k old_names_still_owns", [ALIAS], 'reds(e, "G-D12") == []'),
]


if __name__ == "__main__":
    only = {int(a) for a in sys.argv[1:]}
    ok = True
    for n, row in enumerate(S, 1):
        if only and n not in only:
            continue
        red, why = run(*row)
        ok &= red
        print(f"{n:2} {'RED ' if red else 'NOT RED!'} {row[0].rsplit('/', 1)[-1]:12} {row[1].strip().splitlines()[0][:50]!r:54} -> {why}", flush=True)
    print("ALL RED" if ok else "SOME ROWS ARE NOT RED FOR THEIR REASON")
