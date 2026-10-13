"""CE-25 sabotage table (DEC-11): break what each AC-65 to AC-70 test guards (the intent chain:
G-I1, G-I2, G-T1, G-T2, G-T6); every run must go red. The data rows break this repo's own
records, which AC-23 lints (tests/test_repo_records.py).

Run from the repo root: `<interpreter> tools/sabotage_ce25.py [AC-n ...]` (no ids: every row). It
restores every file it touches, byte for byte. The patterns are exact source text from
2026-10-13b; when the code moves, a pattern stops matching and the script stops with an
AssertionError naming it, rather than passing quietly. G-T5 (mutation per criterion) replaces this
hand table.

Each run gets a fresh bytecode cache (PYTHONPYCACHEPREFIX): a same-length sabotage written in the
same second as the previous restore would otherwise run the stale .pyc (seen 2026-10-08d).
"""
import os, pathlib, subprocess, sys, tempfile

PY_EXE = sys.executable
G = "src/context_engine/guards.py"
W = "src/context_engine/working.py"
C = "src/context_engine/config.py"
T = "tests/test_intent.py"
R = "tests/test_repo_records.py"
MARK = "@pytest.mark." + "criterion"  # assembled, so this file is not read as a claim
S = [
 # G-I1 (AC-65)
 ("AC-65", G, "        elif gid not in known:", "        elif False:", T + " -k g_i1_every"),
 ("AC-65", G, "sorted(known - served, key=", "sorted(set(), key=", T + " -k g_i1_every"),
 ("AC-65", G, "        if doc.get(\"story_status\") == \"retired\":", "        if False:", T + " -k g_i1_every"),
 ("AC-65", G, "        return [\"names no goal (`goals` is empty)\"]", "        return []", T + " -k g_i1_every"),
 ("AC-65", G, "GOAL_RE = re.compile(r\"G-?([1-9][0-9]*)\")", "GOAL_RE = re.compile(r\"G-([1-9][0-9]*)\")", T + " -k g_i1_every"),  # a legacy G2 no longer reads as G-2
 ("AC-65", G, "+ coverage(e) + intent(e)", "+ coverage(e)", T + " -k g_i1_every"),
 ("AC-65", G, "    if not found:\n        out.append(Failure(\"G-I1\", rel, \"no goal rows", "    if False:\n        out.append(Failure(\"G-I1\", rel, \"no goal rows", T + " -k g_i1_reds"),
 ("AC-65", G, "        if raw.strip(\"*`\").strip() != gid:", "        if False:", T + " -k g_i1_reds"),
 ("AC-65", G, "        if gid in seen:", "        if False:", T + " -k g_i1_reds"),
 # G-I2 and record new (AC-66)
 ("AC-66", G, "    if not STORY_ACTOR_RE.fullmatch(actor):", "    if False:", T + " -k g_i2_a_story"),
 ("AC-66", G, "    if not re.fullmatch(r\"\\d{4}-\\d{2}-\\d{2}\", str(doc.get(\"date\") or \"\")):", "    if False:", T + " -k g_i2_a_story"),
 ("AC-66", G, "    if status not in STORY_STATUSES:", "    if False:", T + " -k g_i2_a_story"),
 ("AC-66", G, "    elif status == \"unconfirmed\" and not AGENT_ACTOR_RE.fullmatch(actor):", "    elif False:", T + " -k g_i2_a_story"),
 ("AC-66", G, "AGENT_ACTOR_RE = re.compile(r\"agent \\([^()]*reconstructed", "AGENT_ACTOR_RE = re.compile(r\"agent \\(reconstructed", T + " -k g_i2_a_story"),
 ("AC-66", W, "        if kind == self.store.config.guards.stories:", "        if False:", T + " -k record_new_story"),
 ("AC-66", W, "known, legacy=False)", "known, legacy=True)", T + " -k record_new_story"),
 ("AC-66", W, "problems = [] if \"G-I2\" in off else", "problems = [] if False else", T + " -k record_new_story"),
 # G-T1 (AC-67)
 ("AC-67", G, "        if status == \"live\" and rid not in sourced:", "        if False:", T + " -k g_t1_a_live"),
 ("AC-67", G, "sourced = {rid for r in rows if r.status != \"retired\" for rid", "sourced = {rid for r in rows for rid", T + " -k g_t1_a_live"),
 ("AC-67", G, "            if not any(re.search(rf\"(?<![\\w-]){re.escape(rid)}(?![\\w-])\", t) for t in board):", "            if False:", T + " -k g_t1_a_live"),
 ("AC-67", G, "rf\"(?<![\\w-]){re.escape(rid)}(?![\\w-])\"", "rf\"{re.escape(rid)}\"", T + " -k g_t1_a_live"),  # US-40 would name US-4
 ("AC-67", G, "    return [t for t in (_text(p) for p in paths) if not _deprecated(t)]", "    return [_text(p) for p in paths]", T + " -k g_t1_a_live"),
 # G-T2 (AC-68)
 ("AC-68", G, "        elif r.status in CLAIMED and found and r.id not in found:", "        elif False:", T + " -k g_t2_tested"),
 ("AC-68", G, "        if rows and cid not in ids:", "        if False:", T + " -k g_t2_tested"),
 ("AC-68", G, "        if r.status not in CRITERION_STATUSES:", "        if False:", T + " -k g_t2_tested"),
 ("AC-68", G, "sorted(f for f in p.rglob(\"*\")", "sorted(f for f in p.glob(\"*\")", T + " -k g_t2_tested"),
 ("AC-68", C, "CLAIM = r\"\"\"criterion(?:\\(\\s*[\"']|:\\s*)", "CLAIM = r\"\"\"criterion(?:\\(\\s*[\"'])", T + " -k g_t2_tested"),  # the comment form stops counting
 ("AC-68", C, "    if groups != 1:", "    if False:", T + " -k g_t2_claim"),
 ("AC-68", C, "    except re.error as err:", "    except KeyError as err:", T + " -k g_t2_claim"),
 ("AC-68", C, "    if g.get(\"stories\") and g[\"stories\"] not in kinds:", "    if False:", T + " -k g_t2_claim"),
 # G-T6 (AC-69)
 ("AC-69", G, "        if not refs:", "        if False:", T + " -k g_t6"),
 ("AC-69", G, "            if ref not in known:", "            if False:", T + " -k g_t6"),
 ("AC-69", G, "known = {rid for k in kinds for p", "known = {rid for k in st.config.kinds.values() for p", T + " -k g_t6"),  # a task would count as a source
 # empty and missing sources (AC-70)
 ("AC-70", G, "    if not rows and not problems:", "    if False:", T + " -k criteria_file_that"),
 ("AC-70", G, "        if src is None or status is None:", "        if src is None:", T + " -k criteria_file_that"),
 ("AC-70", G, "    if not rows:\n        return out  # no criterion could be read", "    if False:\n        return out  # no criterion could be read", T + " -k criteria_file_that"),
 ("AC-70", G, "    if not found and not out:", "    if False:", T + " -k g_t2_is_red"),
 ("AC-70", G, "        if not p.exists():\n            out.append(Failure(\"G-T2\"", "        if False:\n            out.append(Failure(\"G-T2\"", T + " -k g_t2_is_red"),
 ("AC-70", G, "    if not (g.tests and e.w.criteria):", "    if not e.w.criteria:", T + " -k g_t2_is_red"),
 # data, not code: this repo's own records under the new guards (AC-23 runs lint on them)
 ("AC-23", T, MARK + "(\"AC-69\")\ndef test_g_t6", "def test_g_t6", R),  # a tested criterion loses its claim: G-T2
 ("AC-23", T, "def test_a_whole_chain_is_green", MARK + "(\"AC-999\")\ndef test_a_whole_chain_is_green", R),  # a claim of no row: G-T2
 ("AC-23", "docs/charter.md", "| G-3 |", "| G3 |", R),  # a legacy goal id in the charter: G-I1
 ("AC-23", "docs/stories/US-12-sessions-leave-an-after-action-review-so-the.md", "goals: [G7]", "goals: [G8]", R),  # a goal the charter lacks: G-I1
 ("AC-23", "docs/stories/US-12-sessions-leave-an-after-action-review-so-the.md", "actor: owner", "actor: claude-code/x", R),  # G-I2
 ("AC-23", "docs/criteria.md", "| US-12 | planned |", "| DEC-12 | planned |", R),  # US-12 loses its only criterion: G-T1
 ("AC-23", "docs/criteria.md", "| US-12 | planned |", "| US-12, US-99 | planned |", R),  # a source that is no record: G-T6
 ("AC-23", "context.toml", "charter = \"docs/charter.md\"", "charter = \"HANDOFF.md\"", R),  # no goal rows: G-I1
 ("AC-23", "context.toml", "criteria = \"docs/criteria.md\"", "criteria = \"README.md\"", R),  # no criterion rows: G-T1, G-T2, G-T6
 ("AC-23", "context.toml", "tests = [\"tests\"]", "tests = [\"tests\"]\nclaim = \"covers (AC-[0-9]+)\"", R),  # a pattern that fits nothing: G-T2
]
only = set(sys.argv[1:])
ok = True
for ac, f, old, new, sel in (r for r in S if not only or r[0] in only):
    p = pathlib.Path(f)
    orig = p.read_bytes()
    text = orig.decode("utf-8").replace("\r\n", "\n")  # a CRLF checkout (autocrlf) matches too
    assert text.count(old) == 1, (ac, f, old[:60], text.count(old))
    try:
        broken = text.replace(old, new)
        p.write_bytes((broken.replace("\n", "\r\n") if b"\r\n" in orig else broken).encode("utf-8"))
        path, *k = sel.split(" -k ")
        args = [PY_EXE, "-m", "pytest", "-q", "-p", "no:cacheprovider", path] + (["-k", k[0]] if k else [])
        with tempfile.TemporaryDirectory() as cache:
            r = subprocess.run(args, capture_output=True, text=True, timeout=300, env={**os.environ, "PYTHONPYCACHEPREFIX": cache})
        last = [l for l in r.stdout.splitlines() if "passed" in l or "failed" in l or "error" in l][-1:]
        why = [l.strip()[:110] for l in r.stdout.splitlines() if l.startswith("E ")][:1]
        red = r.returncode != 0
        ok &= red
        print(f"{ac:5} {'RED ' if red else 'GREEN!'} {f.rsplit('/', 1)[-1]:22} {old.strip().splitlines()[0][:50]!r:54} -> {last} {why}")
    finally:
        p.write_bytes(orig)
print("ALL RED" if ok else "SOME SABOTAGE STAYED GREEN")
