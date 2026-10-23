"""CE-113 sabotage table (DEC-11): break what each AC-98 to AC-100 test guards; every run must go red.

Run from the repo root: `<interpreter> tools/sabotage_ce113.py`. It restores every file it touches,
byte for byte. The patterns are exact source text from 2026-10-23f; when the code moves, a pattern
stops matching and the script stops with an AssertionError naming it, rather than passing quietly.

Each run gets a fresh bytecode cache (PYTHONPYCACHEPREFIX): a same-length sabotage written in the
same second as the previous restore would otherwise run the stale .pyc (seen 2026-10-08d).
"""
import os, pathlib, subprocess, sys, tempfile

PY_EXE = sys.executable
G = "src/context_engine/guards.py"
W = "src/context_engine/working.py"
D = "src/context_engine/decisions.py"
C = "src/context_engine/cli.py"
T = "tests/test_decisions.py"
NEW = T + " -k record_new_refuses_a_delegated"
SECTION = T + " -k ruling_section_with_no_ruled_by"
ASK = T + " -k ask_answer_records_a_delegated"
ASK_NO = T + " -k ask_answer_refuses_a_ruling"
LINT = T + " -k g_i3_fails"
S = [
 # the shared check (guards.py::delegation_problems): each clause
 ("AC-99", G, '    if LONE_HUMAN_RE.fullmatch(actor):\n        out.append(f"is a ruling by', '    if False:\n        out.append(f"is a ruling by', NEW + " and actor-"),
 ("AC-100", G, '    if LONE_HUMAN_RE.fullmatch(actor):\n        out.append(f"is a ruling by', '    if False:\n        out.append(f"is a ruling by', LINT),
 ("AC-99", G, '    elif who == "owner":', '    elif False:', NEW + " and ruled_by-owner"),
 ("AC-98", G, '    elif who == "owner":', '    elif False:', ASK_NO + " and ruled_by-owner"),
 ("AC-99", G, '    if not who:\n        out.append("has a blank', '    if False:\n        out.append("has a blank', NEW + " and ruled_by-blank"),
 ("AC-99", G, '    if ruling is None:\n        out.append("names `ruled_by` but', '    if False:\n        out.append("names `ruled_by` but', NEW + " and no-ruling-section"),
 ("AC-100", G, '    if ruling is None:\n        out.append("names `ruled_by` but', '    if False:\n        out.append("names `ruled_by` but', LINT),
 ("AC-99", G, '        if not text[: ruling.start()].strip():', '        if False:', NEW + " and nothing-above"),
 ("AC-99", G, '        if not text[ruling.end():].strip():', '        if False:', NEW + " and empty-ruling"),
 ("AC-99", G, '        return [] if ruling is None else ["has a `## Ruling` section but no `ruled_by`', '        return [] if True else ["has a `## Ruling` section but no `ruled_by`', SECTION),
 ("AC-98", G, '        return [] if ruling is None else ["has a `## Ruling` section but no `ruled_by`', '        return [] if True else ["has a `## Ruling` section but no `ruled_by`', ASK_NO + " and heading-in-words"),
 ("AC-100", G, '        return [] if ruling is None else ["has a `## Ruling` section but no `ruled_by`', '        return [] if True else ["has a `## Ruling` section but no `ruled_by`', LINT),
 ("AC-100", G, "    text = text[: m.start()] if m else text\n    ruling = RULING_RE", "    text = text\n    ruling = RULING_RE", SECTION),
 # the lint guard (guards.py::delegated_rulings) and its wiring
 ("AC-100", G, "goals(e) + story_fields(e) + delegated_rulings(e) + specified(e)", "goals(e) + story_fields(e) + specified(e)", LINT),
 ("AC-100", G, '        if doc.get("status") == "deprecated":\n            continue\n        rid = doc.get("id")', '        rid = doc.get("id")', LINT),
 # the write-time twins
 ("AC-99", W, 'if kind == self.w.decision and "G-I3" not in self.store.config.guards.off and (bad := G.delegation_problems(fields, body)):', 'if False:', NEW),
 ("AC-98", W, '        if bool(ruling.strip()) != bool(ruled_by):', '        if False:', ASK_NO + " and (ruling-alone or ruled_by-alone)"),
 ("AC-98", W, 'if "G-I3" not in self.store.config.guards.off and (bad := G.delegation_problems(fields, body)):\n            raise Refusal(f"the decision answering', 'if False:\n            raise Refusal(f"the decision answering', ASK_NO + " and heading-in-words"),
 # what ask answer writes
 ("AC-98", W, 'fields = {**fields, "actor": G.DELEGATED_ACTOR, G.RULED_BY: ruled_by}', 'fields = {**fields, G.RULED_BY: ruled_by}', ASK),
 ("AC-98", W, """f"## Ruling\\n\\nRuled by {ruled_by} on the owner's delegation; only the quote above is the owner's words.\\n\\n{ruling}\\n")""", """f"## Ruling\\n\\nRuled by {ruled_by}.\\n\\n{ruling}\\n")""", ASK),
 ("AC-98", W, """body = (f'Owner, answering {rid} by delegating the ruling to {ruled_by}: *"{words.strip()}"*\\n\\n'""", """body = (f'Owner, answering {rid}: *"{words.strip()}\\n\\n{ruling}"*\\n\\n'""", ASK),
 ("AC-98", W, '**({G.RULED_BY: ruled_by} if ruled_by else {})}', '}', ASK),
 ("AC-98", W, """how = f"answered on the owner's delegation, ruled by {ruled_by}" if ruled_by else "answered by the owner\"""", """how = "answered by the owner\"""", ASK),
 ("AC-98", D, """ruled = f"ruled by {r.get('ruled_by')}" if r.get("ruled_by") else None""", "ruled = None", ASK),
 ("AC-98", C, '        a["ruling"] = _read(a["ruling_file"])', '        pass', ASK),
 # decision set refuses ruled_by (AC-53's table, extended for CE-113)
 ("AC-99", W, '"imported_from", "generated", "ruled_by")}', '"imported_from", "generated")}', T + " -k decision_set_refuses_keys and ruled_by"),
 # `[guards] off` may name G-I3, and it switches off the lint and both write-time twins
 ("AC-100", "src/context_engine/config.py", '"G-I2", "G-I3", "G-T1"', '"G-I2", "G-T1"', T + " -k guards_off_g_i3"),
 ("AC-100", W, 'if kind == self.w.decision and "G-I3" not in self.store.config.guards.off and (bad', 'if kind == self.w.decision and (bad', T + " -k guards_off_g_i3"),
 ("AC-100", W, '        if "G-I3" not in self.store.config.guards.off and (bad := G.delegation_problems(fields, body)):\n            raise Refusal(f"the decision answering', '        if (bad := G.delegation_problems(fields, body)):\n            raise Refusal(f"the decision answering', T + " -k guards_off_g_i3"),
 # the CLI flag reaches the operation's parameter (tests/test_mcp.py's CLI-to-parameter table)
 ("AC-98", C, '    aa.add_argument("--ruled-by", default="",', '    aa.add_argument("--ruled-by-x", default="",', "tests/test_mcp.py"),
]
ok = True
for ac, f, old, new, sel in S:
    p = pathlib.Path(f)
    orig = p.read_bytes()
    text = orig.decode("utf-8")
    assert text.count(old) == 1, (ac, f, old[:70])
    try:
        p.write_bytes(text.replace(old, new).encode("utf-8"))
        path, *k = sel.split(" -k ")
        args = [PY_EXE, "-m", "pytest", "-q", "-p", "no:cacheprovider", path] + (["-k", k[0]] if k else [])
        with tempfile.TemporaryDirectory() as cache:
            r = subprocess.run(args, capture_output=True, text=True, timeout=300, env={**os.environ, "PYTHONPYCACHEPREFIX": cache})
        last = [l for l in r.stdout.splitlines() if "passed" in l or "failed" in l or "error" in l][-1:]
        red = r.returncode == 1 and "failed" in "".join(last)  # 5 is "no tests collected": not a red
        ok &= red
        print(f"{ac:6} {'RED ' if red else 'GREEN!'} {f.rsplit('/', 1)[-1]:13} {old.strip().splitlines()[0][:55]!r:60} -> {last}", flush=True)
    finally:
        p.write_bytes(orig)
print("ALL RED" if ok else "SOME SABOTAGE STAYED GREEN")
