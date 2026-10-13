"""CE-49 sabotage table (DEC-11): break what each test of `record retire` and G-I2's retire checks
guards; every run must go red, and red for the reason the row names.

Run from the repo root: `<interpreter> tools/sabotage_ce49.py [row-number ...]` (no numbers: every
row). It restores every file it touches, byte for byte. The patterns are exact source text from
2026-10-13c; when the code moves, a pattern stops matching and the script stops with an
AssertionError naming it, rather than passing quietly. Each row also names a substring its
failure output must hold, so a row that goes red for another reason (an import error, a typo in
the sabotage) does not count. G-T5 (mutation per criterion) replaces this hand table.

Each run gets a fresh bytecode cache (PYTHONPYCACHEPREFIX): a same-length sabotage written in the
same second as the previous restore would otherwise run the stale .pyc (seen 2026-10-08d).
"""
import os, pathlib, subprocess, sys, tempfile

PY_EXE = sys.executable
ST = "src/context_engine/store.py"
WK = "src/context_engine/working.py"
GU = "src/context_engine/guards.py"
CL = "src/context_engine/cli.py"
T = "tests/test_retire.py"
REF = T + " -k refuses_before"
S = [
 # who may retire, and with what
 (WK, "        if not G.RETIRE_BY_RE.fullmatch(by):", "        if False:", REF, "DID NOT RAISE"),
 (WK, "        if not why.strip():\n            raise Refusal(\"no reason\"", "        if False:\n            raise Refusal(\"no reason\"", REF, "DID NOT RAISE"),
 (WK, '        if by == "agent" and not new:', "        if False:", REF, "DID NOT RAISE"),
 # the successor
 (WK, "            if new == rid:", "            if False:", REF, "DID NOT RAISE"),
 (WK, "            if self.store.config.kind_for_id(new).name != kind:", "            if False:", REF, "DID NOT RAISE"),
 (WK, '                if n.get("story_status") == "retired":', "                if False:", REF, "DID NOT RAISE"),
 # a retire is final
 (WK, '            if done is not None and o.get("story_status") == "retired":', "            if False:", REF, "DID NOT RAISE"),
 # what it writes
 (WK, '            o.set("story_status", "retired")\n            o.set("status", "deprecated")\n', '            o.set("story_status", "retired")\n', T + " -k in_one_write", "status: deprecated"),
 (WK, '                n.set("supersedes", [*dict.fromkeys([*D.as_list(n.get("supersedes")), rid])])\n', "", T + " -k in_one_write", "supersedes"),
 (WK, "amend={rid: head + why})", "amend={})", T + " -k in_one_write", "## Amendments"),
 # the store: an amendment in the same write checks the hash, and is logged as a body change
 (ST, '                if bp and r.doc.get("body_sha"):\n                    raise Refusal(f"{i} {bp[0]}", bp[1])', '                if False:\n                    raise Refusal(f"{i} {bp[0]}", bp[1])', REF, "DID NOT RAISE"),
 (ST, '+ (["body"] if i in amend else [])', "+ []", T + " -k in_one_write", "'body'"),
 # a story is never born retired
 (WK, '        if "G-I2" not in off and str(fields.get("story_status")) == "retired":', "        if False:", T + " -k never_born", "DID NOT RAISE"),
 # the CLI reads --file into `why`
 (CL, 'into = ("why" if a.get("op") == "retire" else "body") if args.group == "record" else "text"', 'into = "body" if args.group == "record" else "text"', T + " -k cli_and_the_mcp", "'NoneType' object has no attribute 'strip'"),
 (CL, '    ("record", "retire"): "record_retire",\n', "", "tests/test_mcp.py -k every_cli_subcommand", "assert"),
 # G-I2: a retire by hand, a retire undone, the links
 (GU, '        if status == "retired" and op is None:', "        if False:", T + " -k made_or_undone", "no `record retire` of it is logged"),
 (GU, '        elif op is not None and (status != "retired" or doc.get("status") != "deprecated"):', '        elif op is not None and status != "retired":', T + " -k made_or_undone", "not `deprecated`"),
 (GU, '        elif op is not None and (status != "retired" or doc.get("status") != "deprecated"):', "        elif False:", T + " -k made_or_undone", "story_status: live"),
 (GU, "                if str(ref) not in known:", "                if False:", T + " -k made_or_undone", "which is no story"),
 (GU, '        if D.as_list(doc.get("superseded_by")) and status != "retired":', "        if False:", T + " -k made_or_undone", "not retired"),
 # only the line that set story_status is a retire; the successor's `supersedes` line is not
 (GU, ' and "story_status" in (op.get("fields") or ())', "", T + " -k in_one_write", "US-3 was retired"),
 # G-I2 reads no provenance of a retired story, so following the remedy clears the red
 (GU, '    if str(doc.get("story_status") or "") == "retired":\n        return []', "    if False:\n        return []", T + " -k following_them", "claude-code/x"),
 # the remedies name the op
 (GU, '    return f"`record retire {rid} --by agent --superseded-by <new id> --why \\"<what was wrong>\\"`"', '    return "file a task to retire this one"', T + " -k following_them", "record retire US-3"),
 (GU, "then retire this one: {retire_hint(rid)}\"))", "then retire this one: file a task\"))", T + " -k following_them", "record retire US-4"),
]
only = {int(a) for a in sys.argv[1:]}
ok = True
for n, (f, old, new, sel, reason) in enumerate(S, 1):
    if only and n not in only:
        continue
    p = pathlib.Path(f)
    orig = p.read_bytes()
    text = orig.decode("utf-8").replace("\r\n", "\n")  # a CRLF checkout (autocrlf) matches too
    assert text.count(old) == 1, (n, f, old[:60], text.count(old))
    try:
        broken = text.replace(old, new)
        p.write_bytes((broken.replace("\n", "\r\n") if b"\r\n" in orig else broken).encode("utf-8"))
        path, *k = sel.split(" -k ")
        args = [PY_EXE, "-m", "pytest", "-q", "-p", "no:cacheprovider", path] + (["-k", k[0]] if k else [])
        with tempfile.TemporaryDirectory() as cache:
            r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300, env={**os.environ, "PYTHONPYCACHEPREFIX": cache, "PYTHONIOENCODING": "utf-8"})
        last = [l for l in r.stdout.splitlines() if "passed" in l or "failed" in l or "error" in l][-1:]
        why = [l.strip()[:110] for l in r.stdout.splitlines() if l.startswith("E ")][:1]
        failed = r.returncode == 1 and "failed" in "".join(last)  # a test failed: not a collection error, not "no tests ran"
        named = reason in r.stdout
        red = failed and named
        ok &= red
        verdict = "RED " if red else ("RED, OTHER REASON!" if failed else "GREEN!")
        print(f"{n:2} {verdict} {f.rsplit('/', 1)[-1]:11} {old.strip().splitlines()[0][:50]!r:54} -> {last} {why}")
    finally:
        p.write_bytes(orig)
print("ALL RED" if ok else "SOME SABOTAGE STAYED GREEN OR WENT RED FOR ANOTHER REASON")
