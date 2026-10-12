"""CE-5 sabotage table (DEC-11): break what each AC-38 to AC-42 test guards; every run must go red.

Run from the repo root: `<interpreter> tools/sabotage_ce5.py`. It restores every file it touches.
The patterns are exact source lines from 2026-10-12d; when the code moves, a pattern stops
matching and the script stops with an AssertionError naming it, rather than passing quietly.
Each run gets a fresh bytecode cache (PYTHONPYCACHEPREFIX), as in sabotage_ce2.py.
G-T5 (mutation per criterion, CE-14) replaces this hand table.
"""
import os, pathlib, subprocess, sys, tempfile

PY_EXE = sys.executable
O = "src/context_engine/okf.py"
ST = "src/context_engine/store.py"
W = "src/context_engine/working.py"
D = "src/context_engine/decisions.py"
T = "tests/test_decisions.py"
S = [
    # AC-38: corrections only insert, keep the stamp, and can be undone byte for byte
    ("AC-38", O, "return head[: lead + pos] + inserted + head[lead + pos :] + tail, pos, inserted", "return head[: lead + pos] + inserted + head[lead + pos + 1 :] + tail, pos, inserted", T + " -k byte_for_byte"),
    ("AC-38", O, "        i = core.find(after, i + 1)", "        i = -1", T + " -k one_unique_anchor"),
    # a re-stamp (the 2026-10-12d build) would let a dropped `corrected:` line pass a bracket off as typed
    ("AC-38", ST, "            rec.doc.set_body(amended(body, okf.correction_entry(pos, inserted, after), session, actor))\n", '            rec.doc.set_body(amended(body, okf.correction_entry(pos, inserted, after), session, actor))\n            rec.doc.set("body_sha", okf.body_sha(rec.doc.body))\n', T + " -k byte_for_byte"),
    ("AC-38", ST, 'if any(c in after + text for c in "\\r\\n"):', "if False:", T + " -k one_unique_anchor"),
    ("AC-38", O, 'if not (ins.startswith("[") and ins.endswith("]")) or text[pos : pos + len(ins)] != ins:', 'if not (ins.startswith("[") and ins.endswith("]")):', T + " -k corrected_line"),
    ("AC-38", ST, "        if stamped != typed:", "        if False:", T + " -k passed_off"),
    ("AC-38", O, '    return "sha256:" + hashlib.sha256(strip_corrections(body).encode("utf-8")).hexdigest()', "    strip_corrections(body)\n    return body_sha(body)", T + " -k passed_off"),
    # AC-39: supersede and relaxes write both directions
    ("AC-39", W, '            n.set("supersedes", [*dict.fromkeys([*D.as_list(n.get("supersedes")), old])])', "            pass", T + " -k both_directions"),
    ("AC-39", W, '            o.set("status", "deprecated")', "            pass", T + " -k both_directions"),
    ("AC-39", W, 'if str(n.get(D.STATUS_KEY)) in ("SUPERSEDED", "REJECTED"):', "if False:", T + " -k dead_replacement"),
    ("AC-39", W, '                t.set("narrowed_by", [*dict.fromkeys([*D.as_list(t.get("narrowed_by")), rid])])', "                pass", T + " -k narrowed_by"),
    # AC-40: link checks its target; why() and find() answer exactly
    ("AC-40", W, '("::" in target and v == target.split("::")[0])', "False", T + " -k why_lists"),
    ("AC-40", W, '            if missing:\n                raise Refusal(f"{file} has no', '            if False:\n                raise Refusal(f"{file} has no', T + " -k checks_the_target"),
    ("AC-40", W, "            elif target not in self._criteria():", "            elif False:", T + " -k checks_the_target"),
    ("AC-40", W, 'CRITERION_ROW_RE = re.compile(r"^\\|\\s*([A-Z]+-\\d+)\\s*\\|", re.MULTILINE)', 'CRITERION_ROW_RE = re.compile(r"\\b([A-Z]+-\\d+)\\b")', T + " -k checks_the_target"),
    ("AC-40", W, "        path = self.root / self.w.criteria if self.w.criteria else None", '        path = self.root / (self.w.criteria or "criteria.md")', T + " -k no_criteria_file"),
    ("AC-40", W, "if status and str(d.get(D.STATUS_KEY)).upper() != status.upper():", "if False:", T + " -k find_filters"),
    # AC-41: the index is regenerated on every write, in its order, and G-D6 checks it
    ("AC-41", ST, "            self._reindex(kind, session, actor)\n        return Record(rid, kind, path, doc)", "        return Record(rid, kind, path, doc)", T + " -k regenerates_the_index"),
    ("AC-41", D, "key=lambda t: (t == UNTAGGED, t))", "key=lambda t: t)", T + " -k regenerates_the_index"),
    ("AC-41", ST, 'if path.read_bytes().decode("utf-8").replace("\\r\\n", "\\n") != text:', "if False:", T + " -k hand_edited"),
    # AC-42: the import keeps ids and words, links both ways, and is all or nothing
    ("AC-42", D, "        stop = STOP_RE.search(text, start, end)", "        stop = None", T + " -k verbatim"),
    ("AC-42", D, "                back = by_id[t].links.setdefault(BACKLINK[key], [])\n                if e.id not in back:\n                    back.append(e.id)", "                pass", T + " -k verbatim"),
    ("AC-42", ST, "                out.append(Record(rid, kind, path, doc))", "                out.append(Record(rid, kind, path, doc)); path.parent.mkdir(parents=True, exist_ok=True); self._write(path, doc)", T + " -k later_record"),
    ("AC-42", D, "    if foreign:", "    if False:", T + " -k all_or_nothing"),
    ("AC-42", W, "        if dry_run:", "        if False:", T + " -k dry_run"),
]
ok = True
for ac, f, old, new, sel in S:
    p = pathlib.Path(f)
    raw = p.read_bytes()  # restored byte for byte, whatever its line endings
    orig = raw.decode("utf-8").replace("\r\n", "\n")
    assert orig.count(old) == 1, (ac, old[:60])
    try:
        p.write_bytes(orig.replace(old, new).encode("utf-8"))
        path, *k = sel.split(" -k ")
        args = [PY_EXE, "-m", "pytest", "-q", "-p", "no:cacheprovider", path] + (["-k", k[0]] if k else [])
        with tempfile.TemporaryDirectory() as cache:
            r = subprocess.run(args, capture_output=True, text=True, timeout=300, env={**os.environ, "PYTHONPYCACHEPREFIX": cache})
        last = [l for l in r.stdout.splitlines() if "passed" in l or "failed" in l or "error" in l][-1:]
        red = r.returncode != 0
        ok &= red
        print(f"{ac:5} {'RED ' if red else 'GREEN!'} {old.strip().splitlines()[0][:55]!r:60} -> {last}")
    finally:
        p.write_bytes(raw)
print("ALL RED" if ok else "SOME SABOTAGE STAYED GREEN")
