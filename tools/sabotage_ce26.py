"""CE-26 sabotage: each row breaks one thing the method-runbook checks protect, runs the test that
guards it with a fresh bytecode cache and this checkout's own code on the path, checks it went red
for the named reason, and restores the files byte for byte.

Run from anywhere: `<interpreter> tools/sabotage_ce26.py [row-number ...]` (no numbers: every row).
The exit status is the number of rows not red for their reason. When the code moves, a pattern
stops matching and the script stops with an AssertionError naming the row, rather than passing.

The checker is CE-49's (`tools/sabotage_ce49.py::verdict`, since CE-60): a row counts as red only
when (1) pytest exits 1 with a test failed (not a collection error, not "no tests ran"), (2) every
test that failed is one the row names, and each one it names failed, and (3) the row's reason is
in a failing statement pytest marks with `>` or in the first `E` line of a failure. Before CE-60 a
row counted red when its reason appeared anywhere in pytest's output, and pytest prints the test's
source above the failing line, so a test failing for another reason could pass as red.

Rebased on 2026-10-19 (CE-60), when the stricter checker first ran: row 4's reason named a
`rituals.md` the kit no longer ships (the old checker already failed it, as RED (WRONG REASON));
row 18's reason, `assert []`, was in a later `E` line only, and its test is parametrized, so the
row now names the four forms that fail (pytest prints a backslash in a test id doubled) and the
failing statement; row 19 un-fixed the INV-15 leak in the kit's manual-mode.md, which is gone now
(KNOWN_LEAKS is empty), so it plants a stale KNOWN_LEAKS entry: the same guard,
`assert known == KNOWN_LEAKS`."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sabotage_ce49 import verdict  # noqa: E402  (the checker: CE-49's, unchanged)

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
KIT = "src/context_engine/kit"
TPL = f"{KIT}/context.toml.template"
FW = "docs/framework/FRAMEWORK.md"
T = "tests/test_method_runbooks.py::"
K = "tests/test_kit.py::"
LINT = "test_this_repos_records_pass_lint"  # the one test in tests/test_repo_records.py

# (what is broken, [(file, old, new), ...], pytest selection, the reason: a string the failing line
# must show[, the tests that must fail, and only those; by default the one test the node id names])
ROWS = [
    ("a repo id planted in a kit runbook",
     [(f"{KIT}/docs/runbooks/gate.md", "# Gate\n", "# Gate (CE-26)\n")],
     K + "test_the_kit_and_framework_carry_none_of_this_repos_ids_or_paths", "CE-26"),
    ("a kit runbook out of step with this repo's",
     [(f"{KIT}/docs/runbooks/sabotage.md", "No guard is believed", "No guard is trusted")],
     K + "test_the_kit_runbooks_are_this_repos_runbooks", "sabotage.md differs"),
    ("init no longer copies a method runbook",
     [("src/context_engine/bootstrap.py", '    "docs/runbooks/release.md": "docs/runbooks/release.md",\n', "")],
     T + "test_framework_7_5_and_the_kit_name_the_same_runbooks", "init copies"),
    ("FRAMEWORK 7.5 drops a runbook the kit ships",
     [(FW, "- `docs/runbooks/sabotage.md`: seeing", "- the sabotage runbook: seeing")],
     T + "test_framework_7_5_and_the_kit_name_the_same_runbooks", "'procedures.md', 'release.md']; the kit ships"),
    ("FRAMEWORK 7.5 names a runbook the kit lacks",
     [(FW, "install trial of every published release.\n", "install trial of every published release; `docs/runbooks/baselines.md`.\n")],
     T + "test_framework_7_5_and_the_kit_name_the_same_runbooks", "baselines.md"),
    ("a method runbook without its liveness line",
     [("docs/runbooks/release.md", "liveness: LIVING\n", "")],
     T + "test_each_method_runbook_declares_how_it_changes_and_how_alive_it_is[release.md]", "liveness"),
    ("a method runbook with an unknown change mode",
     [("docs/runbooks/gate.md", "mode: replaced\n", "mode: rewritten\n")],
     T + "test_each_method_runbook_declares_how_it_changes_and_how_alive_it_is[gate.md]", "rewritten"),
    ("this repo's config loses a method runbook's route",
     [("context.toml", 'component = "Gate runbook"\npath = "docs/runbooks/gate.md"', 'component = "Gate runbook"\npath = "docs/runbooks"')],
     T + "test_each_method_runbook_has_its_own_route_with_caps[gate.md-context.toml]", "no [[routes]] entry"),
    ("the template's route loses its caps",
     [(TPL, "max_lines = 90     # G-D1; provenance: JUDGEMENT, engine default (the kit's copy", "# max_lines = 90     # G-D1; provenance: JUDGEMENT, engine default (the kit's copy"),
      (TPL, "max_bytes = 8000   # provenance: JUDGEMENT, engine default; wrong as above\n", "")],
     T + "test_an_adopted_repo_that_loses_a_method_runbook_or_outgrows_it_is_red[gate.md]", "lacks a G-D1 cap"),
    ("the template turns G-D1 off",
     [(TPL, "off = []                     # guard ids", 'off = ["G-D1"]               # guard ids')],
     T + "test_an_adopted_repo_that_loses_a_method_runbook_or_outgrows_it_is_red[gate.md]", "must fail G-D1 on that cap alone"),
    ("the template turns G-R1 off",
     [(TPL, "off = []                     # guard ids", 'off = ["G-R1"]               # guard ids')],
     T + "test_an_adopted_repo_that_loses_a_method_runbook_or_outgrows_it_is_red[gate.md]", "must fail G-R1"),
    ("the template routes a method runbook at another file",
     [(TPL, 'component = "Release runbook"\npath = "docs/runbooks/release.md"', 'component = "Release runbook"\npath = "HANDOFF.md"')],
     T + "test_an_adopted_repo_that_loses_a_method_runbook_or_outgrows_it_is_red[release.md]", "must fail G-R1"),
    ("a build-round step reworded",
     [("docs/runbooks/fan-out.md", "| 5 | Integrate, with sabotage |", "| 5 | Integrate |")],
     T + "test_the_fan_out_build_rounds_are_framework_6_6s_steps", "Build rounds must be"),
    ("two build-round steps swapped",
     [("docs/runbooks/fan-out.md", "| 1 | Map |", "| 1 | Plan, with a critic |"),
      ("docs/runbooks/fan-out.md", "| 2 | Plan, with a critic | the plan", "| 2 | Map | the plan")],
     T + "test_the_fan_out_build_rounds_are_framework_6_6s_steps", "Build rounds must be"),
    ("this repo routes a method runbook that is gone",
     [("context.toml", 'path = "docs/runbooks/release.md"', 'path = "docs/runbooks/release-moved.md"')],
     "tests/test_repo_records.py", "G-R1", [LINT]),
    # -- added after the review (false-pass lens) --
    ("a register id planted in a kit runbook",
     [(f"{KIT}/docs/runbooks/release.md", "# Release\n", "# Release (see INV-3)\n")],
     K + "test_the_kit_and_framework_carry_none_of_this_repos_ids_or_paths", "INV-3"),
    ("a Git Bash user path planted in a kit runbook",
     [(f"{KIT}/docs/runbooks/fan-out.md", "# Fan-out\n", "# Fan-out\n\nRun /c/Users/me/x.\n")],
     K + "test_the_kit_and_framework_carry_none_of_this_repos_ids_or_paths", "/c/Users/"),
    ("the leak regex loses its machine-path forms",
     [("tests/test_kit.py", r"|(?i:\b[a-z]:[\\/]users\b|/c/users/|anaconda3)", "")],
     K + "test_the_leak_check_sees_each_form", 'assert leaks(f"see {planted} here")',
     [f"test_the_leak_check_sees_each_form[{form}]" for form in ("C:\\\\Users\\\\me", "c:/users/me", "/c/Users/me/x", "anaconda3/envs/x")]),
    ("the known leak is fixed but still allowed",
     [("tests/test_kit.py", "KNOWN_LEAKS: dict[str, list[str]] = {}",
       'KNOWN_LEAKS: dict[str, list[str]] = {"src/context_engine/kit/docs/runbooks/manual-mode.md": ["INV-15"]}')],
     K + "test_the_kit_and_framework_carry_none_of_this_repos_ids_or_paths", "a known leak was fixed"),
    ("the template's route loses its width cap",
     [(TPL, "max_width = 100    # provenance: JUDGEMENT, engine default (the runbooks' prose wrap)", "# max_width = 100    # provenance: JUDGEMENT, engine default (the runbooks' prose wrap)")],
     T + "test_each_method_runbook_has_its_own_route_with_caps[gate.md-src/context_engine/kit/context.toml.template]", "max_width"),
    ("the template's byte cap made huge",
     [(TPL, "max_bytes = 8000   # provenance: JUDGEMENT, engine default; wrong as above\n", "max_bytes = 999999999   # provenance: JUDGEMENT, engine default; wrong as above\n")],
     T + "test_an_adopted_repo_that_loses_a_method_runbook_or_outgrows_it_is_red[gate.md]", "the byte case must outgrow"),
    ("a frontmatter key repeated, the bad value first",
     [("docs/runbooks/sabotage.md", "liveness: LIVING\n", "liveness: BOGUS\nliveness: LIVING\n")],
     T + "test_each_method_runbook_declares_how_it_changes_and_how_alive_it_is[sabotage.md]", "a frontmatter key repeats"),
    ("a FRAMEWORK step wrapped with a clause fan-out.md lacks",
     [(FW, "2. plan, with a critic;\n", "2. plan, with a critic\n   and a budget;\n")],
     T + "test_the_fan_out_build_rounds_are_framework_6_6s_steps", "Build rounds must be"),
    ("the build rounds moved out of §6.6",
     [(FW, "**Build rounds:**\n", "### 6.6b Elsewhere\n\n**Build rounds:**\n")],
     T + "test_the_fan_out_build_rounds_are_framework_6_6s_steps", "ValueError"),
    ("this repo's runbook over its cap",
     [("context.toml", "max_lines = 90     # G-D1; provenance: MEASURED 2026-10-13c, the longest", "max_lines = 20     # G-D1; provenance: MEASURED 2026-10-13c, the longest")],
     "tests/test_repo_records.py", "G-D1", [LINT]),
]


def run(name: str, edits: list[tuple[str, str, str]], test: str, why: str, tests: list[str] | None = None) -> tuple[bool, str]:
    """Make ``edits``, run ``test``, restore every file byte for byte; (red for ``why``, detail)."""
    tests = tests if tests is not None else [test.split("::", 1)[1]]
    saved: dict[Path, bytes] = {}
    try:
        for rel, old, new in edits:
            path = ROOT / rel
            orig = saved.setdefault(path, path.read_bytes())
            nl = "\r\n" if b"\r\n" in orig else "\n"  # a checkout may be CRLF
            text = path.read_bytes().decode("utf-8").replace("\r\n", "\n")
            assert text.count(old) == 1, (name, rel, "pattern not found once")
            path.write_bytes(text.replace(old, new).replace("\n", nl).encode("utf-8"))
        with tempfile.TemporaryDirectory(prefix="ce26sab-") as cache:
            env = {**os.environ, "PYTHONPYCACHEPREFIX": cache, "PYTHONPATH": str(ROOT / "src"), "PYTHONIOENCODING": "utf-8"}
            r = subprocess.run([PY, "-m", "pytest", "-q", "-p", "no:cacheprovider", test], cwd=ROOT, env=env,
                               capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
        return verdict(r.stdout, r.returncode, tests, why)
    finally:
        for path, orig in saved.items():
            path.write_bytes(orig)
        for path, orig in saved.items():
            assert path.read_bytes() == orig, f"{path} not restored"


if __name__ == "__main__":
    only = {int(a) for a in sys.argv[1:]}
    failed = 0
    for n, row in enumerate(ROWS, 1):
        if only and n not in only:
            continue
        red, detail = run(*row)
        failed += not red
        print(f"{n:2} {'RED ' if red else 'NOT RED!'} {row[0]} -> {row[2].rsplit('/', 1)[-1]}\n    {detail[:200]}", flush=True)
    print("ALL RED" if not failed else f"{failed} ROWS ARE NOT RED FOR THEIR REASON")
    sys.exit(failed)
