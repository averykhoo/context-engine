"""CE-195 sabotage table (DEC-11): break what each AC-185 test guards (and AC-93's push line);
every run must go red, and the line it prints says why.

Run from the repo root: `<interpreter> tools/sabotage_ce195.py`. It restores every file it
touches. The patterns are exact source lines from 2026-11-06f (fix rounds 1 and 2 included); when the code moves, a pattern
stops matching and the script stops with an AssertionError naming it, rather than passing
quietly. Each run gets a fresh bytecode cache (PYTHONPYCACHEPREFIX), as in sabotage_ce2.py.
"""
import os, pathlib, subprocess, sys, tempfile

PY_EXE = sys.executable
W = "src/context_engine/working.py"
LG = "src/context_engine/ledger.py"
TW = "tests/test_working.py"
TH = "tests/test_housekeeping.py"
TK = "tests/test_kit.py"
S = [
    # G-W1 accepts a close that kept this banner, and only that
    ("AC-185", W, "        return said == [L.BANNER_KEPT, key]", "        return bool(said)", TW + " -k unless_that_close_kept_it"),
    ("AC-185", W, "        return said == [L.BANNER_KEPT, key]", "        return said[:2] == [L.BANNER_KEPT, key]", TW + " -k unless_that_close_kept_it"),  # fix-1: words after the key
    ("AC-185", W, '            receipts["banner"] = f"{L.BANNER_KEPT} {b.key}"', '            pass', TW + " -k unless_that_close_kept_it"),
    # verify-2 D1: no close keeps, and G-W1 accepts no `kept`, until a close wrote the banner under CE-195
    ("AC-185", W, "            elif not self._banner_cut([e for e in self.read_ledger().entries", "            elif False and not self._banner_cut([e for e in self.read_ledger().entries", TW + " -k no_close_wrote_under_ce195"),
    ("AC-185", W, "            if b.key == key:  # written this session", "            if False:  # written this session", TW + " -k no_close_wrote_under_ce195"),
    ("AC-185", W, "                      and not self._banner_cut([e for e in closes if e.key != newest_close], b.key)):", "                      and not self._banner_cut(closes, b.key)):", TW + " -k no_close_wrote_under_ce195"),
    ("AC-185", W, "                      and not self._banner_cut([e for e in closes if e.key != newest_close], b.key)):", "                      and False):", TW + " -k no_close_wrote_under_ce195"),    # the first close writes the first banner; without one it is refused
    ("AC-185", W, "            if b is None:\n                raise Refusal(f\"{self.w.handoff} has no banner yet", "            if False:\n                raise Refusal(f\"{self.w.handoff} has no banner yet", TK + " -k g_w1"),
    # session close runs the close housekeeping, in one commit
    ("AC-185", W, '            done = self.hk_run("close", session=key, actor=actor)', '            done = "hk run close:\\nhk run close: 0 writes"', TH + " -k one_call_and_one_commit"),
    ("AC-185", W, "    @_milestone\n    def session_close(", "    def session_close(", TH + " -k one_call_and_one_commit"),
    # a refused close writes nothing, not even housekeeping
    ("AC-185", W, "        check(self.read_ledger(), self._open_entry(self.read_ledger(), key))  #", "        pass  #", TH + " -k refused_one_call_close"),
    ("AC-185", W, "            self._banner_note(banner, seen, key)  #", "            pass  #", TH + " -k refused_one_call_close"),
    # --continues: the link is kept, refused with --follows, and orient reads the thread
    ("AC-185", W, "e.field(L.TASKS), e.field(L.CONTINUES))  # noqa: E731", "e.field(L.TASKS), None)  # noqa: E731", TW + " -k continues_the_conversation"),
    ("AC-185", "src/context_engine/cli.py", 'link.add_argument("--continues", default="",', 'link.add_argument("--continues", type=lambda s: "", default="",', "tests/test_mcp.py -k session_start---continues"),  # fix-1: MCP parity
    ("AC-185", W, "        if follows and continues:", "        if False:", TW + " -k continues_the_conversation"),
    ("AC-185", LG, "        prev = e.field(CONTINUES) if e else None", "        prev = None", TW + " -k continues_the_conversation"),
    # orient shows the last close
    ("AC-185", W, "        if last is not None and last.key not in (followed, continued):", "        if False:", TW + " -k shows_the_last_close"),
    # fix-1: Last close is served after the banner, and gives way whole when the banner would be cut
    ("AC-185", W, "BANNER_RANK, LAST_CLOSE_RANK = 3, 4", "BANNER_RANK, LAST_CLOSE_RANK = 3, 2", TW + " -k last_close_part_still_fits_whole"),
    ("AC-185", W, '        if f"the rest: {BANNER_REST}]" in out and (past :=', '        if False and f"the rest: {BANNER_REST}]" in out and (past :=', TW + " -k last_close_part_still_fits_whole"),
    # fix-1: the entry's prose is checked before housekeeping writes
    ("AC-185", W, "        if housekeeping:  # CE-63 before housekeeping writes", "        if False:  # CE-63 before housekeeping writes", TH + " -k digest_lint_would_fail_is_refused_before_housekeeping"),
    # the push state
    ("AC-93", W, '                out.append(f"- the last push to {up}: {sha}, at {m.group(1)}")', "                pass", TW + " -k compares_head_with_upstream"),
]
ok = True
for ac, f, old, new, sel in S:
    p = pathlib.Path(f)
    orig = p.read_bytes()
    text = orig.decode("utf-8")
    assert text.count(old) == 1, (ac, old[:60])
    try:
        p.write_bytes(text.replace(old, new).encode("utf-8"))
        path, *k = sel.split(" -k ")
        args = [PY_EXE, "-m", "pytest", "-q", "-p", "no:cacheprovider", path] + (["-k", k[0]] if k else [])
        with tempfile.TemporaryDirectory() as cache:
            r = subprocess.run(args, capture_output=True, text=True, timeout=600, env={**os.environ, "PYTHONPYCACHEPREFIX": cache})
        last = [l for l in r.stdout.splitlines() if "passed" in l or "failed" in l or "error" in l][-1:]
        why = [l for l in r.stdout.splitlines() if l.startswith("E ")][:1]
        red = r.returncode == 1 and bool(last) and "failed" in last[0]  # a test failed: not a collection error, nor none selected
        ok &= red
        print(f"{ac:6} {'RED ' if red else 'GREEN!'} {old.strip().splitlines()[0][:55]!r:60} -> {last} {why}")
    finally:
        p.write_bytes(orig)
print("ALL RED" if ok else "SOME SABOTAGE STAYED GREEN")
