"""CE-24 sabotage table (sabotage rule, CLAUDE.md): break what each rituals-runbook and
shipped-runbook test guards; every run must go red.

Run from the repo root: `<interpreter> tools/sabotage_ce24.py`. It restores every file it touches,
byte for byte. The patterns are exact source text from 2026-10-12d; when the text moves, a pattern
stops matching and the script stops with an AssertionError naming it, rather than passing quietly.
Each run gets a fresh bytecode cache (PYTHONPYCACHEPREFIX), so a same-length sabotage never runs a
stale .pyc. G-T5 (mutation per criterion, CE-14) replaces this hand table.
"""
import os, pathlib, subprocess, sys, tempfile

PY_EXE = sys.executable
RIT = "docs/runbooks/rituals.md"
KRIT = "src/context_engine/kit/docs/runbooks/rituals.md"
KMAN = "src/context_engine/kit/docs/runbooks/manual-mode.md"
FW = "docs/framework/FRAMEWORK.md"
TR = "tests/test_runbook.py"
TK = "tests/test_kit.py"
S = [
    # every FRAMEWORK §6 subsection is in the map, and the map names real ritual sections
    ("map-row", RIT, "| §6.8 Push and CI | § Push and CI |\n", "", TR + " -k has_a_rituals_section"),
    ("ritual-heading", RIT, "## Push and CI (§6.8)\n", "## Push and CI\n", TR + " -k has_a_rituals_section"),
    ("fw-new-section", FW, "### 6.13 Rollback and close (not designed)", "### 6.14 Rollback and close (not designed)", TR + " -k has_a_rituals_section"),
    # every step names a real operation, links its manual-mode section, and has a Why
    ("unknown-op", RIT, "| `context-engine baton expire` | [§ baton expire](", "| `context-engine baton expired` | [§ baton expire](", TR + " -k names_an_existing_operation"),
    ("no-by-hand-link", RIT, "| [§ orient](manual-mode.md#context-engine-orient) | one capped read", "| § orient | one capped read", TR + " -k names_an_existing_operation"),
    ("dead-anchor", RIT, "(manual-mode.md#when-the-engine-and-this-runbook-disagree)", "(manual-mode.md#when-the-engine-and-this-runbook-disagrees)", TR + " -k names_an_existing_operation"),
    ("no-why", RIT, "| scratch is ignored by git, so anything only there is already lost |", "| — |", TR + " -k names_an_existing_operation"),
    ("cell-count", RIT, "| 8 | The owner digest in chat, at most 7 lines |", "| 8 | The owner digest | in chat, at most 7 lines |", TR + " -k names_an_existing_operation"),
    ("dead-section-ref", RIT, "| — | Foreign commits | — | § Foreign reconcile |", "| — | Foreign commits | — | § Foreign reconciles |", TR + " -k names_an_existing_operation"),
    # §6 item numbers the runbook cites exist (P3)
    ("label", RIT, "| 6a | Pre-close housekeeping", "| 6b | Pre-close housekeeping", TR + " -k cites_exists"),
    ("fw-renumber", FW, "   - **6a. Pre-close housekeeping**", "   - **6b. Pre-close housekeeping**", TR + " -k cites_exists"),
    # the kit ships this repo's runbooks, free of its ids, and init copies them
    ("kit-equal", KRIT, "# Rituals\n", "# Rituals!\n", TK + " -k this_repos_runbooks"),
    ("kit-leak", KMAN, "| decision | `D-n` |", "| decision | `DEC-1` |", TK + " -k carry_none"),
    ("init-copies", "src/context_engine/bootstrap.py", '    "docs/runbooks/manual-mode.md": "docs/runbooks/manual-mode.md",\n', "", TK + " -k copies_the_runbooks"),
    ("wheel", "pyproject.toml", '"kit/**/*"', '"kit/*", "kit/docs/*", "kit/docs/ledger/*"', TK + " -k wheel_carries"),
]
ok = True
for name, f, old, new, sel in S:
    p = pathlib.Path(f)
    orig = p.read_bytes()
    text = orig.decode("utf-8")
    crlf = "\r\n" in text
    norm = text.replace("\r\n", "\n")
    assert norm.count(old) == 1, (name, f, old[:60])
    try:
        bad = norm.replace(old, new)
        p.write_bytes((bad.replace("\n", "\r\n") if crlf else bad).encode("utf-8"))
        path, *k = sel.split(" -k ")
        args = [PY_EXE, "-m", "pytest", "-q", "-p", "no:cacheprovider", path] + (["-k", k[0]] if k else [])
        with tempfile.TemporaryDirectory() as cache:
            r = subprocess.run(args, capture_output=True, text=True, timeout=300, env={**os.environ, "PYTHONPYCACHEPREFIX": cache})
        last = [l for l in r.stdout.splitlines() if "passed" in l or "failed" in l or "error" in l][-1:]
        red = r.returncode != 0 and "1 failed" in (last[0] if last else "")
        ok &= red
        print(f"{name:16} {'RED ' if red else 'GREEN!'} {old.strip().splitlines()[0][:50]!r:55} -> {last}")
    finally:
        p.write_bytes(orig)
print("ALL RED" if ok else "SOME SABOTAGE STAYED GREEN")
sys.exit(0 if ok else 1)
