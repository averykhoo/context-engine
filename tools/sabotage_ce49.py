"""CE-49 sabotage table (DEC-11): break what each test of `record retire` and G-I2's retire checks
guards; every run must go red, and red for the reason the row names.

Run from the repo root: `<interpreter> tools/sabotage_ce49.py [row-number ...]` (no numbers: every
row). It restores every file it touches, byte for byte. The patterns are exact source text from
2026-10-13c; when the code moves, a pattern stops matching and the script stops with an
AssertionError naming it, rather than passing quietly. G-T5 (mutation per criterion) replaces this
hand table.

A row counts as red only when (1) pytest exits 1 with a test failed (not a collection error, not
"no tests ran"), (2) every test that failed is one the row names, and each one it names failed,
and (3) the row's reason is in a failing statement pytest marks with `>` or in the first `E`
line of a failure. Matching the whole output would count a row red for another failure, since
pytest prints the test's source above the failing line (review of 2026-10-13c).

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
REF = T + " -k refuses_before_writing_anything"
R = "test_record_retire_refuses_before_writing_anything"
ONE = "test_record_retire_writes_the_status_the_links_and_the_reason_in_one_write"
OTHER = "test_record_retire_refuses_a_hash_mismatch_a_record_that_fails_its_schema_and_a_repo_with_no_stories"
RETRY = "test_a_retire_whose_second_write_fails_is_completed_by_a_retry"
STORE = "test_the_store_amends_only_append_only_records_and_never_with_nothing"
BORN = "test_a_story_is_never_born_retired_deprecated_or_linked"
HAND = "test_g_i2_reds_a_retire_made_or_undone_by_hand_and_a_story_link_that_resolves_to_no_story"
REMEDY = "test_the_g_i1_and_g_i2_remedies_name_record_retire_and_following_them_clears_the_red"
T1 = "test_g_t1_tells_a_successor_to_take_over_the_criteria_of_the_story_it_replaced"
CLI = "test_the_cli_and_the_mcp_tool_retire_and_commit_by_path"
NR = "DID NOT RAISE"
# (file, pattern, replacement, pytest selection, the tests that must fail (and only those), reason)
S = [
 # who may retire, and with what
 (WK, "        if not G.RETIRE_BY_RE.fullmatch(by):", "        if False:", REF, [f"{R}[by-vocabulary]", f"{R}[by-agent-with-a-model]"], NR),
 (WK, '        if not why.strip():\n            raise Refusal("no reason"', '        if False:\n            raise Refusal("no reason"', REF, [f"{R}[no-reason]"], NR),
 (WK, '        if by == "agent" and not new:', "        if False:", REF, [f"{R}[agent-without-successor]"], NR),
 (WK, '                if by == "agent" and not _same_words(o, n):', "                if False:", REF, [f"{R}[agent-other-words]"], NR),
 (WK, "        if self.store.config.kind_for_id(rid).name != kind:", "        if False:", REF, [f"{R}[not-a-story]"], NR),
 (WK, '        if not kind:\n            raise Refusal("no kind holds the stories', '        if False:\n            raise Refusal("no kind holds the stories', T, [OTHER], "Regex pattern did not match"),
 # the successor
 (WK, "            if new == rid:", "            if False:", REF, [f"{R}[self]"], NR),
 (WK, "            if self.store.config.kind_for_id(new).name != kind:", "            if False:", REF, [f"{R}[successor-not-a-story]"], NR),
 (WK, '                if n.get("story_status") == "retired":', "                if False:", REF, [f"{R}[successor-retired]"], NR),
 # a retire is final, even after a hand edit undid it
 (WK, "            if done is not None:  # final", "            if False:  # final", REF, [f"{R}[already-retired]", f"{R}[undone-by-hand]"], NR),
 (WK, "            if done is not None:  # final", '            if done is not None and o.get("story_status") == "retired":  # final', REF, [f"{R}[undone-by-hand]"], NR),
 # what it writes, and in which order
 (WK, '            o.set("status", "deprecated")\n            keys = {rid: ["story_status", "status"]}', '            keys = {rid: ["story_status", "status"]}', T, [ONE, RETRY, HAND, REMEDY], "head.endswith("),
 (WK, '                n.set("supersedes", [*dict.fromkeys([*D.as_list(n.get("supersedes")), rid])])\n', "", T, [ONE, RETRY, T1, CLI], '"supersedes: [US-1]'),
 (WK, "amend={rid: head + why})", "amend={})", T, [ONE, OTHER, CLI], "old.endswith("),
 (WK, "self.store.update([*([new] if new else []), rid], mutate,", "self.store.update([rid, *([new] if new else [])], mutate,", T, [ONE, RETRY], "assert log =="),
 # the store: an amendment in the same write is checked as `amend` checks it, logged as a body
 # change, and nothing is written until every record validates
 (ST, '                if bp and r.doc.get("body_sha"):\n                    raise Refusal(f"{i} {bp[0]}", bp[1])', '                if False:\n                    raise Refusal(f"{i} {bp[0]}", bp[1])', T, [OTHER], NR),
 (ST, '                if r.kind.mode != "append-only":\n                    raise Refusal(f"{i} is a {r.kind.mode} record", "only append-only records take amendments")', '                if False:\n                    raise Refusal(f"{i} is a {r.kind.mode} record", "only append-only records take amendments")', T, [STORE], NR),
 (ST, '                if not text.strip():\n                    raise Refusal("empty amendment"', '                if False:\n                    raise Refusal("empty amendment"', T, [STORE], NR),
 (ST, '+ (["body"] if i in amend else [])', "+ []", T, [ONE], "assert log =="),
 (ST, "                self._validate(r.kind, r.doc, r.path)\n            for i, r in recs.items():\n                if changed.get(i) or i in amend:\n                    self._write(r.path, r.doc)",
      "                self._validate(r.kind, r.doc, r.path)\n                if changed.get(i) or i in amend:\n                    self._write(r.path, r.doc)\n            for i, r in recs.items():\n                if changed.get(i) or i in amend:\n                    pass", T, [OTHER], "snapshot(chain) == before"),
 # a story is never born retired, deprecated or linked
 (WK, '            if str(fields.get("story_status")) == "retired":', "            if False:", T + " -k never_born", [f"{BORN}[retired]"], NR),
 (WK, "            if born:\n", "            if False:\n", T + " -k never_born", [f"{BORN}[deprecated]", f"{BORN}[superseded_by]", f"{BORN}[supersedes]"], NR),
 # the CLI reads --file into `why`, without a BOM; its verb maps to the operation
 (CL, 'into = ("why" if a.get("op") == "retire" else "body") if args.group == "record" else "text"', 'into = "body" if args.group == "record" else "text"', T, [CLI], "'NoneType' object has no attribute 'strip'"),
 (CL, 'read_text(encoding="utf-8-sig")', 'read_text(encoding="utf-8")', T, [CLI], 'doc(chain, "US-2").endswith('),
 (CL, '    ("record", "retire"): "record_retire",\n', "", "tests/test_mcp.py -k every_cli_subcommand", ["test_every_cli_subcommand_is_one_operation_and_every_operation_one_tool"], "_cli_subcommands() == set(cli.CLI_OPS)"),
 # G-I2: a retire by hand, a retire undone, deprecated but not retired, the links
 (GU, '        if status == "retired" and op is None:', "        if False:", T, [HAND], "US-3 is `retired`, but no `record retire` of it is logged"),
 (GU, '        elif op is not None and (status != "retired" or doc.get("status") != "deprecated"):', '        elif op is not None and status != "retired":', T, [HAND], "not `deprecated`"),
 (GU, '        elif op is not None and (status != "retired" or doc.get("status") != "deprecated"):', "        elif False:", T, [HAND], "now says `story_status: live`"),
 (GU, '        elif op is None and status != "retired" and doc.get("status") == "deprecated":', "        elif False:", T, [HAND], "only a retired story is deprecated"),
 (GU, "                if str(ref) not in known:", "                if False:", T, [HAND], "names US-9, which is no story"),
 (GU, '        if D.as_list(doc.get("superseded_by")) and status != "retired":', "        if False:", T, [HAND], "has `superseded_by` but is `live`, not retired"),
 # only the line that set story_status is a retire; the successor's `supersedes` line is not
 (GU, ' and "story_status" in (op.get("fields") or ())', "", T, [ONE, RETRY, REMEDY], 'reds(e, "G-I2") == []'),
 # G-I2 reads no provenance of a retired story, so following the remedy clears the red
 (GU, '    if str(doc.get("story_status") or "") == "retired":\n        return []', "    if False:\n        return []", T, [REMEDY], 'reds(e, "G-I2") == []'),
 # the remedies name the op
 (GU, '    return f"`record retire {rid} --by agent --superseded-by <new id> --why \\"<what was wrong>\\"`"', '    return "file a task to retire this one"', T, [REMEDY], "record retire US-3 --by agent"),
 (GU, "then retire this one: {retire_hint(rid)}\"))", "then retire this one: file a task\"))", T, [REMEDY], "record retire US-4 --by agent"),
 # G-T1 tells the successor to take over the criteria
 (GU, "                      if old else f\"draft its criteria", "                      if False else f\"draft its criteria", T, [T1], "t1[0].remedy.startswith("),
]


def verdict(out: str, rc: int, tests: list[str], reason: str) -> tuple[bool, str]:
    lines = out.splitlines()
    last = [l for l in lines if "passed" in l or "failed" in l or "error" in l][-1:]
    if rc != 1 or "failed" not in "".join(last):
        return False, f"no test failed {last}"
    failed = [l.split(" ", 1)[1].split(" - ", 1)[0].split("::", 1)[-1] for l in lines if l.startswith("FAILED ")]
    if sorted(failed) != sorted(tests):
        return False, f"failed {failed}, not {tests}"
    firsts, seen = [], False
    for l in lines:  # the first `E` line of each failure
        if l.startswith("E ") and not seen:
            firsts.append(l)
        seen = l.startswith("E ")
    marked = [l for l in lines if l.startswith(">")] + firsts
    if not any(reason in l for l in marked):
        return False, f"reason {reason!r} not in a failing statement or its first error line"
    return True, (firsts[0].strip()[:100] if firsts else "")


def run(f: str, old: str, new: str, sel: str, tests: list[str], reason: str) -> tuple[bool, str]:
    """Break ``f`` (``old`` -> ``new``), run ``sel``, restore byte for byte; (red, why)."""
    p = pathlib.Path(f)
    orig = p.read_bytes()
    text = orig.decode("utf-8").replace("\r\n", "\n")  # a CRLF checkout (autocrlf) matches too
    assert text.count(old) == 1, (f, old[:60], text.count(old))
    try:
        broken = text.replace(old, new)
        p.write_bytes((broken.replace("\n", "\r\n") if b"\r\n" in orig else broken).encode("utf-8"))
        path, *k = sel.split(" -k ")
        args = [PY_EXE, "-m", "pytest", "-q", "-p", "no:cacheprovider", path] + (["-k", k[0]] if k else [])
        with tempfile.TemporaryDirectory() as cache:
            r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600, env={**os.environ, "PYTHONPYCACHEPREFIX": cache, "PYTHONIOENCODING": "utf-8"})
        return verdict(r.stdout, r.returncode, tests, reason)
    finally:
        p.write_bytes(orig)


if __name__ == "__main__":
    only = {int(a) for a in sys.argv[1:]}
    ok = True
    for n, row in enumerate(S, 1):
        if only and n not in only:
            continue
        red, why = run(*row)
        ok &= red
        print(f"{n:2} {'RED ' if red else 'NOT RED!'} {row[0].rsplit('/', 1)[-1]:11} {row[1].strip().splitlines()[0][:50]!r:54} -> {why}", flush=True)
    print("ALL RED" if ok else "SOME ROWS ARE NOT RED FOR THEIR REASON")
